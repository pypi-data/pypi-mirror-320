import os
from functools import lru_cache
from io import StringIO
from typing import Literal, Optional

from river_print.main import rprint


@lru_cache(maxsize=1)
def get_terminal_width() -> int:
    return os.get_terminal_size().columns


class _Separator:
    """
    just to make the code more readable, provide a separator in editor
    """

    def ____(self, msg: str):
        """
        just to make the code more readable, provide a separator in editor,
        you can pass any string to it, but nothing will happen in running,
        it appears just like comment in editor
        ```python
        sep________("Hello, world!").________________________________
        sep________().________________________________("Goodbye,world!")
        ```

        result in terminal:
        ```shell
        ----- Hello, world! -----
        -------------------------
        ```
        """
        return self

    def ________(self):
        """
        just to make the code more readable, provide a separator in editor,
        you can pass any string to it, but nothing will happen in running,
        it appears just like comment in editor
        ```python
        sep________("Hello, world!").________________________________
        sep________().________________________________("Goodbye,world!")
        ```

        result in terminal:
        ```shell
        ----- Hello, world! -----
        -------------------------
        ```
        """
        return self

    def ________________(self):
        """
        just to make the code more readable, provide a separator in editor,
        you can pass any string to it, but nothing will happen in running,
        it appears just like comment in editor
        ```python
        sep________("Hello, world!").________________________________
        sep________().________________________________("Goodbye,world!")
        ```

        result in terminal:
        ```shell
        ----- Hello, world! -----
        -------------------------
        ```
        """
        return self

    def ________________________________(self):
        """
        just to make the code more readable, provide a separator in editor,
        you can pass any string to it, but nothing will happen in running,
        it appears just like comment in editor
        ```python
        sep________("Hello, world!").________________________________
        sep________().________________________________("Goodbye,world!")
        ```

        result in terminal:
        ```shell
        ----- Hello, world! -----
        -------------------------
        ```
        """
        return self


def separator(
    msg: str = "",
    style: str = "-",
    width: int | Literal["full", "half"] = "half",
    c: Literal[
        "red",
        "r",
        "green",
        "g",
        "yellow",
        "y",
        "blue",
        "b",
        "magenta",
        "m",
        "cyan",
        "c",
    ] = None,
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> _Separator:
    """Print separator"""

    if width == "full":
        width = get_terminal_width()
    elif width == "half":
        width = get_terminal_width() // 2
    else:
        width = width

    modifier = 0 if msg == "" else 2
    msg_len = len(msg) + modifier

    if msg_len > width:
        # 消息太长时截断
        msg = msg[: width - 12] + "..."
        msg_len = len(msg) + modifier

    msg = " " + msg + " " if msg_len != 0 else ""

    length_left = (width - msg_len) // 2
    length_right = width - length_left - msg_len

    rprint(
        style * length_left,
        msg,
        style * length_right,
        sep="",
        end=end,
        file=file,
        flush=flush,
        c=c,
    )
    return _Separator


sep________ = separator
