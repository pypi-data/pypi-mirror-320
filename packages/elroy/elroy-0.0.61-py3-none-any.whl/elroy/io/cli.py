import logging
from contextlib import contextmanager
from itertools import product
from typing import Generator, Iterator, List, Text, Union

from prompt_toolkit import HTML, Application, PromptSession, print_formatted_text
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import Completion, WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.special import TextLexer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text
from toolz import concatv, pipe
from toolz.curried import map

from ..config.constants import REPO_ISSUES_URL
from ..config.paths import get_prompt_history_path
from ..db.db_models import FunctionCall, Goal, Memory
from ..io.base import ElroyIO
from ..repository.data_models import ContextMessage


class SlashCompleter(WordCompleter):
    def get_completions(self, document, complete_event):
        text = document.text
        if not text.startswith("/"):
            return

        words = text.split()

        exact_cmd_prefix = False
        # If we just have "/" or are typing the command part
        if len(words) <= 1:
            cmds = {c.split()[0] for c in self.words}  # type: ignore # Get just the command parts
            for cmd in cmds:
                if cmd.startswith(text) and text != cmd:
                    yield Completion(cmd, start_position=-len(text))
                    exact_cmd_prefix = True
            if exact_cmd_prefix:
                return

        # If we have a command and are typing arguments
        cmd = words[0]
        # Get the full command templates that start with this command
        matching_commands = [w for w in self.words if w.startswith(cmd)]  # type: ignore
        if matching_commands:
            # Create a completer just for the arguments of this command
            arg_text = " ".join(words[1:])
            # Extract just the argument parts from the matching commands
            arg_options = [" ".join(m.split()[1:]) for m in matching_commands if len(m.split()) > 1]
            if arg_options:
                # Complete from the start of the argument portion
                arg_start_position = -len(arg_text) if arg_text else 0
                for arg in arg_options:
                    if arg.startswith(arg_text):
                        yield Completion(arg, start_position=arg_start_position)


class CliIO(ElroyIO):
    def __init__(
        self,
        show_internal_thought: bool,
        system_message_color: str,
        assistant_message_color: str,
        user_input_color: str,
        warning_color: str,
        internal_thought_color: str,
    ) -> None:
        self.console = Console()
        self.show_internal_thought = show_internal_thought
        self.system_message_color = system_message_color
        self.assistant_message_color = assistant_message_color
        self.warning_color = warning_color
        self.user_input_color = user_input_color
        self.internal_thought_color = internal_thought_color
        self.style = Style.from_dict(
            {
                "prompt": "bold",
                "user-input": self.user_input_color + " bold",
                "": self.user_input_color,
                "pygments.literal.string": f"bold italic {self.user_input_color}",
            }
        )

        self.prompt_session = PromptSession(
            history=FileHistory(get_prompt_history_path()),
            style=self.style,
            lexer=PygmentsLexer(TextLexer),
        )
        self.is_streaming_output = False

    def print(self, message) -> None:
        self.console.print(message)

    def internal_thought_msg(self, message):
        if self.is_streaming_output:
            # hack, should be replaced with a buffer
            logging.info("Dropping internal monologue message since we are streaming assistant output")
        elif not self.show_internal_thought:
            logging.info("Not showing internal monologue since show_internal_thought is False")
        else:
            print_formatted_text(HTML(f'<style fg="{self.internal_thought_color}"><i>{message}</i></style>'))

    def assistant_msg(self, message: Union[str, Pretty, Iterator[str], Generator[str, None, None]]) -> None:

        if isinstance(message, (Iterator, Generator)):
            self.is_streaming_output = True
            try:
                for chunk in message:
                    self.console.print(chunk, style=self.assistant_message_color, end="")
            except KeyboardInterrupt:
                self.console.print()
                return
            finally:
                self.console.print()
                self.is_streaming_output = False

        elif isinstance(message, Pretty):
            self.console.print(message)
        else:
            self.console.print(message, style=self.assistant_message_color, end="")
        self.console.print()  # New line after complete response

    def sys_message(self, message: Union[str, Text, Pretty, Table]) -> None:
        if isinstance(message, str):
            message = Text(str(message), style=self.system_message_color)
        self.console.print(message)

    def notify_function_call(self, function_call: FunctionCall) -> None:
        self.console.print()
        msg = f"[{self.system_message_color}]Executing function call: [bold]{function_call.function_name}[/bold]"

        if function_call.arguments:
            self.console.print(msg + f" with arguments:[/]", Pretty(function_call.arguments))
        else:
            self.console.print(msg + "[/]")

    def notify_warning(self, message: str) -> None:
        self.console.print(Text(message, justify="center", style=self.warning_color))  # type: ignore
        self.console.print(Text(f"Please provide feedback at {REPO_ISSUES_URL}", style=self.warning_color))
        self.console.print()

    def print_memory_panel(self, titles: List[str]):
        if titles:
            panel = Panel("\n".join(titles), title="Relevant Context", expand=False, border_style=self.user_input_color)
            self.console.print(panel)

    def print_title_ruler(self):
        self.console.rule(
            Text("Elroy", justify="center", style=self.user_input_color),
            style=self.user_input_color,
        )

    def rule(self):
        self.console.rule(style=self.user_input_color)

    async def prompt_user(self, prompt=">", prefill: str = "", keyboard_interrupt_count: int = 0) -> str:
        try:
            return await self.prompt_session.prompt_async(HTML(f"<b>{prompt} </b>"), default=prefill, style=self.style)
        except KeyboardInterrupt:
            keyboard_interrupt_count += 1
            if keyboard_interrupt_count == 3:
                self.assistant_msg("To exit, type /exit, exit, or press Ctrl-D.")

            elif keyboard_interrupt_count >= 5:
                raise EOFError
            return await self.prompt_user(prompt, prefill, keyboard_interrupt_count)

    def update_completer(self, goals: List[Goal], memories: List[Memory], context_messages: List[ContextMessage]) -> None:
        from ..repository.embeddable import is_in_context
        from ..system_commands import (
            ALL_ACTIVE_GOAL_COMMANDS,
            ALL_ACTIVE_MEMORY_COMMANDS,
            IN_CONTEXT_GOAL_COMMANDS,
            IN_CONTEXT_MEMORY_COMMANDS,
            NON_ARG_PREFILL_COMMANDS,
            NON_CONTEXT_GOAL_COMMANDS,
            NON_CONTEXT_MEMORY_COMMANDS,
            USER_ONLY_COMMANDS,
        )

        in_context_goal_names = sorted([g.get_name() for g in goals if is_in_context(context_messages, g)])
        non_context_goal_names = sorted([g.get_name() for g in goals if g.get_name() not in in_context_goal_names])

        in_context_memories = sorted([m.get_name() for m in memories if is_in_context(context_messages, m)])
        non_context_memories = sorted([m.get_name() for m in memories if m.get_name() not in in_context_memories])

        self.prompt_session.completer = pipe(  # type: ignore
            concatv(
                product(IN_CONTEXT_GOAL_COMMANDS, in_context_goal_names),
                product(NON_CONTEXT_GOAL_COMMANDS, non_context_goal_names),
                product(ALL_ACTIVE_GOAL_COMMANDS, [g.get_name() for g in goals]),
                product(IN_CONTEXT_MEMORY_COMMANDS, in_context_memories),
                product(NON_CONTEXT_MEMORY_COMMANDS, non_context_memories),
                product(ALL_ACTIVE_MEMORY_COMMANDS, [m.get_name() for m in memories]),
            ),
            map(lambda x: f"/{x[0].__name__} {x[1]}"),
            list,
            lambda x: x + [f"/{f.__name__}" for f in NON_ARG_PREFILL_COMMANDS | USER_ONLY_COMMANDS],
            lambda x: SlashCompleter(words=x),  # type: ignore
        )

    def get_current_input(self) -> str:
        """Get the current content of the input buffer"""
        # The current buffer is accessed through the app property
        if hasattr(self.prompt_session, "app") and self.prompt_session.app:
            return self.prompt_session.app.current_buffer.text
        return ""

    @contextmanager
    def suspend_input(self) -> Generator[str, None, None]:
        """
        Temporarily suspend input, returning current input text.
        If no input session is active, yields empty string.
        """
        try:
            app = get_app()
            if app.is_running:
                assert isinstance(app, Application)
                current_text = self.get_current_input()
                with app.suspend_to_background():  # type: ignore
                    yield current_text
            else:
                yield ""
        except Exception as e:
            # This catches cases where there's no active prompt_toolkit application
            logging.debug(f"No active prompt session to suspend: {e}")
            yield ""
