from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_group_kb(groups: list, data: str = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(text=group, callback_data=group)
    if data:
        builder.button(text="↩️ Назад", callback_data=f"back_{data}")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=" ")
