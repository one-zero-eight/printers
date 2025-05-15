import functools
import math
from typing import Any

from src.bot.keyboards import confirmation_keyboard


def update_confirmation_keyboard(data: dict[str, Any]) -> None:
    def empty_inline_space_remainder(string):
        return string + " " * (100 - len(string)) + "."

    layout = {"1": "1x1", "4": "2x2", "9": "3x3"}.get(data["number_up"], None)
    confirmation_keyboard.inline_keyboard[0][1].text = empty_inline_space_remainder(f"✏️ {data["printer"]}")
    confirmation_keyboard.inline_keyboard[1][1].text = empty_inline_space_remainder(f"✏️ {data["copies"]}")
    confirmation_keyboard.inline_keyboard[2][1].text = empty_inline_space_remainder(f"✏️ {data["page_ranges"]}")
    confirmation_keyboard.inline_keyboard[3][1].text = empty_inline_space_remainder(
        f"✏️ {"One side" if data["sides"] == "one-sided" else "Both sides"}"
    )
    confirmation_keyboard.inline_keyboard[4][1].text = empty_inline_space_remainder(f"✏️ {layout}")


def sub(integers: map) -> int:
    try:
        return -next(integers) + next(integers) + 1
    except StopIteration:
        return 1


def count_of_papers_to_print(page_ranges: str, number_up: str, sides: str, copies: str, sides_impact: bool = True):
    return math.ceil(
        count_of_pages_to_print(recalculate_page_ranges(page_ranges, number_up))
        * (1 if sides == "one-sided" or not sides_impact else 0.5)
    ) * int(copies)


def count_of_pages_to_print(page_ranges: str) -> int:
    return functools.reduce(lambda result, elem: result + sub(map(int, elem.split("-"))), page_ranges.split(","), 0)


def recalculate_page_ranges(page_range: str, number_up: str) -> str:
    return ",".join(
        map(
            lambda elem: "-".join((str(math.ceil(int(el) / int(number_up)))) for el in elem.split("-")),
            page_range.split(","),
        )
    )


def without_throbber(string: str):
    for elem in "⤹⤿⤻⤺":
        string = string.replace(elem, "")
    return string.replace("Status", "Last status")
