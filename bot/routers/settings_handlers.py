import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.common_keyboards import (
    main_kb,
)
from bot.keyboards.inline_keyboards.faculty_kb import (
    build_faculty_kb,
)
from database.user import (
    get_user,
)
from .group_handlers import (
    GroupForm,
    validate_faculty,
)

router = Router(name=__name__)


@router.message(Command("keyboard"))
async def handle_keyboard(message: types.Message) -> None:
    await message.answer(text="Клавиатура отображена", reply_markup=main_kb())


@router.message(Command("current_group"))
async def handle_get_group(message: types.Message) -> None:
    user_id = message.from_user.id
    user_info = get_user(user_id)
    logging.info(user_id)
    await message.answer(
        text=f"{validate_faculty(user_info["faculty"])}Группа <b><i>{user_info["group"]}</i></b>\nПодгруппа <b><i>{user_info["subgroup"]}</i></b>",
        reply_markup=main_kb(),
    )


@router.message(Command("change_group"))
async def handle_course_number(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="⚙️Настройка группы.\nВыберите факультет:",
        reply_markup=build_faculty_kb(),
    )
    await state.set_state(GroupForm.faculty)


@router.message(Command("help"))
@router.message(Command("info"))
async def handle_help_info(message: types.Message) -> None:
    text_message = """
Неофициальный бот расписания ВГУ
Могут присутствовать баги, неточности
"""
    await message.answer(
        text=text_message,
        reply_markup=main_kb(),
    )
