import functools
import math
from typing import Any, assert_never

from aiogram import html

from src.bot.keyboards import confirmation_keyboard
from src.modules.printing.entity_models import JobAttributes, JobStateEnum


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


def format_printing_message(
    data: dict[str, Any],
    job_attributes: JobAttributes | None = None,
    iteration: int = 0,
    canceled_manually: bool = False,
    timed_out: bool = False,
) -> str:
    """Format the complete message including job info and status with throbber."""
    LAYOUT = {"1": "1x1", "4": "2x2", "9": "3x3"}.get(data["number_up"], "1x1")

    job_info = (
        html.italic("Job\n")
        + html.italic(f"⦁ Printer: {html.bold(html.quote(data["printer"]))}\n")
        + html.italic(f"⦁ Copies: {html.bold(html.quote(data["copies"]))}\n")
        + html.italic(
            f"⦁ Pages: {html.bold(html.quote(data["page_ranges"]))} (in document: {html.bold(html.quote(data["pages"]))})\n"
        )
        + html.italic(
            f"⦁ Print on: {html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")}\n"
        )
        + html.italic(f"⦁ Layout: {html.bold(html.quote(LAYOUT))}\n")
    )

    if job_attributes:
        if job_attributes.job_state == JobStateEnum.pending:
            throbber = "⏳"
        elif job_attributes.job_state == JobStateEnum.pending_held:
            throbber = "⏳⏸"
        elif job_attributes.job_state == JobStateEnum.processing:
            throbber = "⤹⤿⤻⤺"[iteration % 4]
        elif job_attributes.job_state == JobStateEnum.processing_stopped:
            throbber = "⏸"
        elif job_attributes.job_state == JobStateEnum.canceled:
            throbber = "❌"
        elif job_attributes.job_state == JobStateEnum.aborted:
            throbber = "☠️"
        elif job_attributes.job_state == JobStateEnum.completed:
            throbber = "✅"
        else:
            assert_never(job_attributes.job_state)
    else:
        throbber = ""

    caption = f"{job_info} {throbber}"

    if canceled_manually:
        caption = (
            f"{caption}\n\n{html.bold("Cancelled on demand")}"
            "\nHowever, we unable to revoke partially printed jobs."
            f"\nYou should try this with printer"
        )

    if timed_out:
        caption = f"{caption}\n\n{html.bold('Job is timed out ☠️')}"

    return caption


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


def without_throbber(string: str | None):
    if string is None:
        return string
    for elem in "⤹⤿⤻⤺":
        string = string.replace(elem, "")
    return string.replace("Status", "Last status")
