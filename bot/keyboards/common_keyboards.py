from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ButtonText:
    TODAY = "Сегодня"
    TOMORROW = "Завтра"
    ALL_WEEK = "Вся неделя"
    DAYS = [
        "Пн",
        "Вт",
        "Ср",
        "Чт",
        "Пт",
        "Сб",
    ]


def main_kb() -> ReplyKeyboardMarkup:
    button_today = KeyboardButton(text=ButtonText.TODAY)
    button_tomorrow = KeyboardButton(text=ButtonText.TOMORROW)
    button_week = KeyboardButton(text=ButtonText.ALL_WEEK)

    builder = ReplyKeyboardBuilder()
    for day in ButtonText.DAYS:
        builder.button(text=day)

    day_buttons = list(builder.buttons)

    buttons_first_row = [button_today, button_tomorrow, button_week]
    buttons_second_row = day_buttons

    markup = ReplyKeyboardMarkup(
        keyboard=[buttons_first_row, buttons_second_row],
        resize_keyboard=True,
        input_field_placeholder=" ",
    )
    return markup
