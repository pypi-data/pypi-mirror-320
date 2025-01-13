from typing import TypedDict
import logging

HAS_RICH = True

try:
    from rich.logging import RichHandler
    from rich.highlighter import Highlighter
    from rich.text import Text
except ImportError:
    HAS_RICH = False

class DriverOptionsStdout(TypedDict):
    ...

def driver_stdout(driver_option: DriverOptionsStdout = None):
    if not HAS_RICH:
        raise ImportError(
        "You must install rich to use the stdout driver. "
        "Run: pip install rich"
    )

    class LogNameHighlighter(Highlighter):
        def highlight(self, text: Text) -> None:
            text.highlight_regex(r"^\w+ - ", style="black italic")

    rich_handler = RichHandler(
        highlighter=LogNameHighlighter(),
        level=logging.DEBUG,
        omit_repeated_times=False,
        tracebacks_show_locals=True,
        tracebacks_extra_lines=True,
        tracebacks_word_wrap=True,
        rich_tracebacks=True,
    )

    formatter_string = "%(name)s - %(message)s"

    formatter = logging.Formatter(formatter_string)
    rich_handler.setFormatter(formatter)

    return rich_handler
