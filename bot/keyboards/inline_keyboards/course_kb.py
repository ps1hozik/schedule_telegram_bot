from enum import StrEnum

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .faculty_kb import Faculties


class Courses(StrEnum):
    one = "1⃣"
    two = "2⃣"
    three = "3⃣"
    four = "4⃣"
    five = "5⃣"


def build_course_kb(faculty: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    is_five = faculty == Faculties.hud or faculty == Faculties.gum
    for idx, course in enumerate(Courses):
        if not is_five:
            if idx == 4:
                break
        builder.button(text=course, callback_data=course)

    builder.button(text="↩️ Назад", callback_data="back_course")
    builder.adjust(5) if is_five else builder.adjust(4)

    return builder.as_markup(resize_keyboard=True, input_field_placeholder=" ")
