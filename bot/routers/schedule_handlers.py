from aiogram import F, Router, types
from aiogram.filters import Command

from bot.keyboards.common_keyboards import (
    main_kb,
    ButtonText,
)
from scripts.date import (
    get_week_date_range,
    get_current_date,
    get_date_by_weekday,
)
from scripts.schedule import (
    get_full_schedule,
    get_schedule_for_day,
    get_teacher_schedule,
)

router = Router(name=__name__)


def _get_schedule(user_id: int, is_tomorrow: bool = False) -> str:
    _, current_date = get_current_date(is_tomorrow)
    schedule = get_schedule_for_day(user_id, str(current_date))
    days = ["сегодня", "завтра"]
    return schedule or f"На {days[is_tomorrow]} расписания нет 😽"


@router.message(F.text == ButtonText.TODAY)
async def handle_today(message: types.Message) -> None:
    schedule = _get_schedule(user_id=message.from_user.id, is_tomorrow=False)
    await message.answer(
        text=schedule,
        reply_markup=main_kb(),
    )


@router.message(F.text == ButtonText.TOMORROW)
async def handle_tomorrow(message: types.Message) -> None:
    schedule = _get_schedule(user_id=message.from_user.id, is_tomorrow=True)
    await message.answer(
        text=schedule,
        reply_markup=main_kb(),
    )


@router.message(F.text == ButtonText.ALL_WEEK)
async def handle_all_week(message: types.Message) -> None:
    schedule = get_full_schedule(message.from_user.id)
    if not schedule:
        start, end = get_week_date_range()
        await message.answer(
            text=f"С {start} по {end} расписания нет 😽",
            reply_markup=main_kb(),
        )
    else:
        for item in schedule:
            await message.answer(
                text=item,
                reply_markup=main_kb(),
            )


@router.message(F.text.in_(ButtonText.DAYS))
async def handle_day_of_week(message: types.Message) -> None:
    number_of_day = ButtonText.DAYS.index(message.text)
    date_for_day = get_date_by_weekday(number_of_day)
    schedule = get_schedule_for_day(message.from_user.id, date_for_day)

    not_found_day = [
        "понедельник",
        "вторник",
        "среду",
        "четверг",
        "пятницу",
        "субботу",
    ]
    await message.answer(
        text=schedule or f"Расписание на {not_found_day[number_of_day]} не найдено 😽",
        reply_markup=main_kb(),
    )


@router.message(Command("find"))
async def handle_find_teacher(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) <= 1:
        await message.reply("Пожалуйста, укажите ФИО. Например: /find Иванов И И")
    else:
        teacher_name = parts[1]
        schedule = get_teacher_schedule(teacher_name)

        if not schedule:
            await message.answer(
                text=f"Расписание для <i><u>{teacher_name}</u></i> не найдено",
                reply_markup=main_kb(),
            )
        else:
            for item in schedule:
                await message.answer(
                    text=item,
                    reply_markup=main_kb(),
                )
