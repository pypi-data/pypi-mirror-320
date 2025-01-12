import os
from functools import lru_cache, wraps
from io import StringIO
from typing import Any, Callable, Literal, Optional

from rich import print as rich_print


# 使用私有类存储颜色映射
class _Maps:
    """内部使用的颜色映射类"""

    RICH: dict[str, str] = {
        "red": "[red]",
        "r": "[red]",
        "green": "[green]",
        "g": "[green]",
        "yellow": "[yellow]",
        "y": "[yellow]",
        "blue": "[blue]",
        "b": "[blue]",
        "magenta": "[magenta]",
        "m": "[magenta]",
        "cyan": "[cyan]",
        "c": "[cyan]",
        "end": "[/]",
    }

    ANSI: dict[str, str] = {
        "red": "\033[31m",
        "r": "\033[31m",
        "green": "\033[32m",
        "g": "\033[32m",
        "yellow": "\033[33m",
        "y": "\033[33m",
        "blue": "\033[34m",
        "b": "\033[34m",
        "magenta": "\033[35m",
        "m": "\033[35m",
        "cyan": "\033[36m",
        "c": "\033[36m",
        "end": "\033[0m",
    }

    ICON: dict[str, str] = {
        "success": "✅",
        "question": "❓",
        "action": "🔄",
        "warning": "⚠️",
        "error": "❌",
        "tip": "💡",
        "note": "📝",
    }


# 默认设置
_print_method = rich_print
_using_map = _Maps.RICH


def set_print_method(method: Literal["rich", "print"]) -> None:
    """Set print method

    Args:
        method: print method, 'rich' or 'print'

    Raises:
        ValueError: when invalid print method is passed
    """
    global _print_method, _using_map
    if method == "rich":
        _print_method = rich_print
        _using_map = _Maps.RICH
    elif method == "print":
        _print_method = print
        _using_map = _Maps.ANSI
    else:
        raise ValueError(f"Invalid print method: {method}, must be 'rich' or 'print'")


def rprint(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
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
) -> None:
    """Colorful print function

    Args:
        *objects: objects to print
        sep (str, optional): Separator between printed objects. Defaults to " ".
        end (str, optional): Character to write at end of output. Defaults to "\n".
        file (IO[str], optional): File to write to, or None for stdout. Defaults to None.
        flush (bool, optional): Has no effect as Rich always flushes output. Defaults to False.
        c: color name, support 'red'/'r', 'green'/'g', etc.

    Examples:
    ```python
        >>> cprint("Hello", "World", c="red")
        >>> cprint("Success!", c="g")  # use short name
        >>> cprint("Normal text")  # no color
        >>> cprint("Normal text", file=f)  # print and write to file
    ```
    """
    if c is None:
        _print_method(*objects, sep=sep, end=end, flush=flush)
        return

    try:
        c_start = _using_map[c]
        c_end = _using_map["end"]
    except KeyError:
        raise ValueError(f"Invalid color: {c}")

    # 优化：单个对象时避免 join
    if len(objects) == 1:
        text = str(objects[0])
    else:
        text = sep.join(str(obj) for obj in objects)

    _print_method(f"{c_start}{text}{c_end}", end=end, flush=flush)

    if file:
        file.write(f"{c_start}{text}{c_end}")


def cpint_icon_color(icon: str, color: str | None = None) -> Callable[..., Any]:
    """Create a log function with icon and color"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)  # 保留原函数的签名和文档
        def wrapper(
            *objects,
            sep: str = " ",
            end: str = "\n",
            file: Optional[StringIO] = None,
            flush: bool = False,
        ) -> None:
            rprint(
                _Maps.ICON[icon],
                *objects,
                sep=sep,
                end=end,
                file=file,
                flush=flush,
                c=color,
            )

        return wrapper  # type: ignore

    return decorator


@cpint_icon_color(icon="action", color="cyan")
def action(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> None: ...


@cpint_icon_color(icon="question", color="yellow")
def question(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> None: ...


@cpint_icon_color(icon="success", color="green")
def success(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> None: ...


@cpint_icon_color(icon="warning", color="yellow")
def warning(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> None: ...


@cpint_icon_color(icon="error", color="red")
def error(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file: Optional[StringIO] = None,
    flush: bool = False,
) -> None: ...


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


@lru_cache(maxsize=1)
def get_terminal_width() -> int:
    return os.get_terminal_size().columns


# python -m src.river_print.main
# uv run -m src.river_print.main
if __name__ == "__main__":
    rprint("Hello, world!", "Hello, world!", sep="|", c="red")
    set_print_method("print")
    rprint("Hello, world!", "Hello, world!", sep="|", c="green")
    set_print_method("rich")
    list = [
        "Hello, world!",
        "Hello, world!",
        654,
        12.0,
        {"a": 1, "b": 2},
        (1, 2, 3),
        {1, 2, 3},
        [1, 2, 3],
        True,
        False,
        None,
        rprint,
        _Maps,
    ]
    rprint(list, sep="|")
    success("Success!")

    warning("Warning!")
    error("Error!")
    separator("Hello, world! Hello, world!Hello, world!Hello, world!", c="red")
    separator(
        "Hello, world! Hello, world!Hello, world!Hello, world!", width="full", c="red"
    )
    separator("Hello, world!")
    action("Action!")
    question("Question!")
    separator()

    separator("Hello, world!")
    action("Action!")
    question("Question!")
    separator()

    sep________("Hello, world!").________________________________

    dict_ = {"a": 1, "b": 2}
    action(f"Action! {dict_}")
    question("Question!")

    sep________().________________________________
