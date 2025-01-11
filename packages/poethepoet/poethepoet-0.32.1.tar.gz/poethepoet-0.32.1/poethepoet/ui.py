import os
import sys
from collections.abc import Mapping, Sequence
from typing import IO, TYPE_CHECKING, Optional, Union

from .__version__ import __version__
from .exceptions import ConfigValidationError, ExecutionError, PoeException

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace

    from pastel import Pastel


def guess_ansi_support(file):
    if os.environ.get("NO_COLOR", "0")[0] != "0":
        # https://no-color.org/
        return False

    if (
        os.environ.get("GITHUB_ACTIONS", "false") == "true"
        and "PYTEST_CURRENT_TEST" not in os.environ
    ):
        return True

    return (
        (sys.platform != "win32" or "ANSICON" in os.environ)
        and hasattr(file, "isatty")
        and file.isatty()
    )


STDOUT_ANSI_SUPPORT = guess_ansi_support(sys.stdout)


class PoeUi:
    args: "Namespace"
    _color: "Pastel"

    def __init__(self, output: IO, program_name: str = "poe"):
        self.output = output
        self.program_name = program_name
        self._init_colors()

    def _init_colors(self):
        from pastel import Pastel

        self._color = Pastel(guess_ansi_support(self.output))
        self._color.add_style("u", "default", options="underline")
        self._color.add_style("hl", "light_gray")
        self._color.add_style("em", "cyan")
        self._color.add_style("em2", "cyan", options="italic")
        self._color.add_style("em3", "blue")
        self._color.add_style("h2", "default", options="bold")
        self._color.add_style("h2-dim", "default", options="dark")
        self._color.add_style("action", "light_blue")
        self._color.add_style("error", "light_red", options="bold")

    def __getitem__(self, key: str):
        """Provide easy access to arguments"""
        return getattr(self.args, key, None)

    def build_parser(self) -> "ArgumentParser":
        import argparse

        parser = argparse.ArgumentParser(
            prog=self.program_name,
            description="Poe the Poet: A task runner that works well with poetry.",
            add_help=False,
            allow_abbrev=False,
        )

        parser.add_argument(
            "-h",
            "--help",
            dest="help",
            action="store_true",
            default=False,
            help="Show this help page and exit",
        )

        parser.add_argument(
            "--version",
            dest="version",
            action="store_true",
            default=False,
            help="Print the version and exit",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            dest="increase_verbosity",
            action="count",
            default=0,
            help="Increase command output (repeatable)",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            dest="decrease_verbosity",
            action="count",
            default=0,
            help="Decrease command output (repeatable)",
        )

        parser.add_argument(
            "-d",
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Print the task contents but don't actually run it",
        )

        parser.add_argument(
            "-C",
            "--directory",
            dest="project_root",
            metavar="PATH",
            type=str,
            default=os.environ.get("POE_PROJECT_DIR", None),
            help="Specify where to find the pyproject.toml",
        )

        parser.add_argument(
            "-e",
            "--executor",
            dest="executor",
            metavar="EXECUTOR",
            type=str,
            default="",
            help="Override the default task executor",
        )

        # legacy --root parameter, keep for backwards compatibility but help output is
        # suppressed
        parser.add_argument(
            "--root",
            dest="project_root",
            metavar="PATH",
            type=str,
            default=None,
            help=argparse.SUPPRESS,
        )

        ansi_group = parser.add_mutually_exclusive_group()
        ansi_group.add_argument(
            "--ansi",
            dest="ansi",
            action="store_true",
            default=STDOUT_ANSI_SUPPORT,
            help="Force enable ANSI output",
        )
        ansi_group.add_argument(
            "--no-ansi",
            dest="ansi",
            action="store_false",
            default=STDOUT_ANSI_SUPPORT,
            help="Force disable ANSI output",
        )

        parser.add_argument("task", default=tuple(), nargs=argparse.REMAINDER)

        return parser

    def parse_args(self, cli_args: Sequence[str]):
        self.parser = self.build_parser()
        self.args = self.parser.parse_args(cli_args)
        self.verbosity: int = self["increase_verbosity"] - self["decrease_verbosity"]
        self._color.with_colors(self.args.ansi)

    def set_default_verbosity(self, default_verbosity: int):
        self.verbosity += default_verbosity

    def print_help(
        self,
        tasks: Optional[
            Mapping[str, tuple[str, Sequence[tuple[tuple[str, ...], str, str]]]]
        ] = None,
        info: Optional[str] = None,
        error: Optional[PoeException] = None,
    ):
        # TODO: See if this can be done nicely with a custom HelpFormatter

        # Ignore verbosity mode if help flag is set
        verbosity = 0 if self["help"] else self.verbosity

        result: list[Union[str, Sequence[str]]] = []
        if verbosity >= 0:
            result.append(
                (
                    "Poe the Poet - A task runner that works well with poetry.",
                    f"version <em>{__version__}</em>",
                )
            )

        if info:
            result.append(f"{f'<em2>Result: {info}</em2>'}")

        if error:
            # TODO: send this to stderr instead?
            error_lines = []
            if isinstance(error, ConfigValidationError):
                if error.task_name:
                    if error.context:
                        error_lines.append(
                            f"{error.context} in task {error.task_name!r}"
                        )
                    else:
                        error_lines.append(f"Invalid task {error.task_name!r}")
                    if error.filename:
                        error_lines[-1] += f" in file {error.filename}"
                elif error.global_option:
                    error_lines.append(f"Invalid global option {error.global_option!r}")
                    if error.filename:
                        error_lines[-1] += f" in file {error.filename}"
            error_lines.extend(error.msg.split("\n"))
            if error.cause:
                error_lines.append(error.cause)
            if error.__cause__:
                error_lines.append(f"From: {error.__cause__!r}")

            result.append(self._format_error_lines(error_lines))

        if verbosity >= 0:
            result.append(
                (
                    "<h2>Usage:</h2>",
                    f"  <u>{self.program_name}</u>"
                    " [global options]"
                    " task [task arguments]",
                )
            )

            # Use argparse for optional args
            formatter = self.parser.formatter_class(prog=self.parser.prog)
            action_group = self.parser._action_groups[1]
            formatter.start_section(action_group.title)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
            result.append(
                ("<h2>Global options:</h2>", *formatter.format_help().split("\n")[1:])
            )

            if tasks:
                max_task_len = max(
                    max(
                        len(task),
                        max(
                            [
                                len(", ".join(str(opt) for opt in opts))
                                for (opts, _, _) in args
                            ]
                            or (0,)
                        )
                        + 2,
                    )
                    for task, (_, args) in tasks.items()
                )
                col_width = max(20, min(30, max_task_len))

                tasks_section = ["<h2>Configured tasks:</h2>"]
                for task, (help_text, args_help) in tasks.items():
                    if task.startswith("_"):
                        continue
                    tasks_section.append(
                        f"  <em>{self._padr(task, col_width)}</em>  "
                        f"{self._align(help_text, col_width)}"
                    )
                    for options, arg_help_text, default in args_help:
                        formatted_options = ", ".join(str(opt) for opt in options)
                        task_arg_help = [
                            "   ",
                            f"<em3>{self._padr(formatted_options, col_width-1)}</em3>",
                        ]
                        if arg_help_text:
                            task_arg_help.append(self._align(arg_help_text, col_width))
                        if default:
                            if "\n" in (arg_help_text or ""):
                                task_arg_help.append(
                                    self._align(f"\n{default}", col_width, strip=False)
                                )
                            else:
                                task_arg_help.append(default)
                        tasks_section.append(" ".join(task_arg_help))

                result.append(tasks_section)

            else:
                result.append("<h2-dim>NO TASKS CONFIGURED</h2-dim>")

        if error and os.environ.get("POE_DEBUG", "0") == "1":
            import traceback

            result.append("".join(traceback.format_exception(error)).strip())

        self._print(
            "\n\n".join(
                section if isinstance(section, str) else "\n".join(section).strip("\n")
                for section in result
            )
            + "\n"
            + ("\n" if verbosity >= 0 else "")
        )

    @staticmethod
    def _align(text: str, width: int, *, strip: bool = True) -> str:
        text = text.replace("\n", "\n" + " " * (width + 4))
        return text.strip() if strip else text

    @staticmethod
    def _padr(text: str, width: int):
        if len(text) >= width:
            return text
        return text + " " * (width - len(text))

    def print_msg(self, message: str, verbosity=0, end="\n"):
        if verbosity <= self.verbosity:
            self._print(message, end=end)

    def print_error(self, error: Union[PoeException, ExecutionError]):
        error_lines = error.msg.split("\n")
        if error.cause:
            error_lines.append(f"From: {error.cause}")
        if error.__cause__:
            error_lines.append(f"From: {error.__cause__!r}")

        for line in self._format_error_lines(error_lines):
            self._print(line)

        if os.environ.get("POE_DEBUG", "0") == "1":
            import traceback

            self._print("".join(traceback.format_exception(error)).strip())

    def _format_error_lines(self, lines: Sequence[str]):
        return (
            f"<error>Error: {lines[0]}</error>",
            *(f"<error>     | {line}</error>" for line in lines[1:]),
        )

    def print_version(self):
        if self.verbosity >= 0:
            result = f"Poe the Poet - version: <em>{__version__}</em>\n"
        else:
            result = f"{__version__}\n"
        self._print(result)

    def _print(self, message: str, *, end: str = "\n"):
        print(self._color.colorize(message), end=end, file=self.output, flush=True)
