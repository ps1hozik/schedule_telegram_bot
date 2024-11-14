from enum import StrEnum

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Faculties(StrEnum):
    ped = "Педагогический факультет"
    gum = "Факультет гуманитарного знания и коммуникаций"
    fmiit = "Факультет математики и информационных технологий"
    soc = "Факультет социальной педагогики и психологии"
    fiz = "Факультет физической культуры и спорта"
    him = "Факультет химико-биологических и географических наук"
    hud = "Художественно-графический факультет"
    ur = "Юридический факультет"


def build_faculty_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faculty in Faculties:
        builder.button(text=faculty, callback_data=faculty.__dict__["_name_"])
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=" ")
