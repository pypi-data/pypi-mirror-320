import sys
import time

from rich import print as rich_print
from rich.console import Console

from src.river_print import rprint, set_print_method

console = Console()


class TimeCost:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.cost = time.perf_counter() - self.start


# 测试代码
def test_performance(test_count: int = 1000, test_message: str = "test message"):
    TEST_COUNT = test_count
    TEST_MESSAGE = test_message

    _map_rich_backend = {
        "print": [lambda x: print(x), 0],
        "rich_print": [lambda x: rich_print(x), 0],
        "rich_console_print": [lambda x: console.print(x), 0],
        "cprint_use_rich": [lambda x: rprint(x), 0],
        "cprint_use_rich_with_color": [lambda x: rprint(x, c="red"), 0],
    }
    _map_print_backend = {
        "cprint_use_print": [lambda x: rprint(x), 0],
        "cprint_use_print_with_color": [
            lambda x: rprint(x, c="red"),
            0,
        ],
    }

    _other_backend = {
        "sys_print": [lambda x: sys.stdout.write(x + "\n"), 0],
    }
    for key, value in _map_rich_backend.items():
        with TimeCost() as print_time:
            for _ in range(TEST_COUNT):
                value[0](TEST_MESSAGE)
        value[1] = print_time.cost
    set_print_method("print")

    for key, value in _map_print_backend.items():
        with TimeCost() as print_time:
            for _ in range(TEST_COUNT):
                value[0](TEST_MESSAGE)
        value[1] = print_time.cost

    for key, value in _other_backend.items():
        with TimeCost() as print_time:
            for _ in range(TEST_COUNT):
                value[0](TEST_MESSAGE)
        value[1] = print_time.cost

    for key, value in _map_rich_backend.items():
        print(f"{key}: {value[1] * 1000:.2f}ms")

    for key, value in _map_print_backend.items():
        print(f"{key}: {value[1] * 1000:.2f}ms")

    for key, value in _other_backend.items():
        print(f"{key}: {value[1] * 1000:.2f}ms")


# python -m test.test_performance
# uv run -m test.test_performance
if __name__ == "__main__":
    test_performance()
