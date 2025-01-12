from contextlib import redirect_stdout
from io import StringIO

from river_print import rprint, separator, set_print_method


def test_rprint_default():
    with redirect_stdout(StringIO()) as output:
        rprint("Hello, world!")
    assert output.getvalue() == "Hello, world!\n"


def test_rprint_with_color():
    with redirect_stdout(StringIO()) as output:
        rprint("Hello, world!", c="red")
    assert output.getvalue() == "Hello, world!\n"


def test_rprint_with_file():
    """print to file and console"""
    f = StringIO()
    with redirect_stdout(StringIO()) as console:
        rprint("Hello, world!", file=f)
    assert f.getvalue() == "Hello, world!\n"
    assert console.getvalue() == "Hello, world!\n"


def test_set_print_method():
    """set print method = print or rich_print"""
    set_print_method("print")
    output = StringIO()
    rprint("Hello, world!", file=output)
    assert output.getvalue() == "Hello, world!\n"

    set_print_method("rich")
    output = StringIO()
    rprint("Hello, world!", c="green", file=output)
    assert output.getvalue() == "Hello, world!\n"


def test_separator():
    output = StringIO()
    separator("Test", style="*", width=20, file=output)
    assert output.getvalue() == "*" * 7 + " Test " + "*" * 7 + "\n"


def test_separator_no_message():
    output = StringIO()
    separator(style="*", width=20, file=output)
    assert output.getvalue() == "*" * 20 + "\n"
