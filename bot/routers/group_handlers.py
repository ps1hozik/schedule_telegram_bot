from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from bot.keyboards.common_keyboards import (
    main_kb,
)
from bot.keyboards.inline_keyboards.course_kb import (
    build_course_kb,
    Courses,
)
from bot.keyboards.inline_keyboards.faculty_kb import (
    build_faculty_kb,
    Faculties,
)
from bot.keyboards.inline_keyboards.group_kb import (
    build_group_kb,
)
from database.user import (
    upsert_user,
    get_user,
    get_subgroups as user_get_subgroups,
)
from scripts.group import (
    get_groups,
    get_subgroups,
)

router = Router(name=__name__)


class GroupForm(StatesGroup):
    faculty = State()
    course = State()
    group = State()
    subgroup = State()


def validate_faculty(faculty: str) -> str:
    faculty = faculty.split(" ", maxsplit=1)
    if faculty[0] != "Факультет":
        return f"<i><b>{faculty[0]}</b></i> {faculty[1]}\n"

    return f"{faculty[0]} <i><b>{faculty[1]}</b></i>\n"


@router.callback_query(F.data == "back_course")
async def handle_back_course(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    settings_text = "⚙️ Выберите факультет:"
    await callback_query.message.edit_text(
        text=settings_text,
        reply_markup=build_faculty_kb(),
    )
    await state.set_state(GroupForm.faculty)


@router.callback_query(F.data == "back_group")
async def handle_back_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    user_data = await state.get_data()
    faculty = user_data["faculty"]
    await callback_query.message.edit_text(
        text=f"{validate_faculty(faculty)} ⚙️ Выберите курс:",
        reply_markup=build_course_kb(faculty),
    )
    await state.set_state(GroupForm.course)


@router.callback_query(F.data == "back_subgroup")
async def handle_back_subgroup(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    await callback_query.answer()
    user_data = await state.get_data()
    faculty = user_data["faculty"]
    course = user_data["course"]
    groups = user_data["groups"]
    await callback_query.message.edit_text(
        text=(
            f"{validate_faculty(faculty)}"
            f"Курс <i><b>#{course}</b></i>\n"
            "⚙️ Выберите группу:"
        ),
        reply_markup=build_group_kb(groups, "group"),
    )
    await state.set_state(GroupForm.group)


@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext) -> None:
    user = get_user(message.from_user.id)

    if not user:
        await message.answer(
            text="⚙️Настройка группы.\nВыберите факультет:",
            reply_markup=build_faculty_kb(),
        )
        await state.set_state(GroupForm.faculty)
    else:
        await message.answer(
            text=f"С возвращением <i><b>{message.from_user.full_name}</b></i> 👋",
            reply_markup=main_kb(),
        )


@router.callback_query(
    GroupForm.faculty, F.data.in_(Faculties.__dict__["_member_names_"])
)
async def handle_course(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()

    faculty = Faculties[f"{callback_query.data}"]
    await state.update_data(faculty=faculty)

    await callback_query.message.edit_text(
        text=f"{validate_faculty(faculty)} ⚙️ Выберите курс:",
        reply_markup=build_course_kb(faculty),
    )
    await state.set_state(GroupForm.course)


@router.callback_query(GroupForm.course, F.data.in_(Courses))
async def handle_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()

    data = callback_query.data.strip()
    course = int(data[0])

    user_data = await state.get_data()
    faculty = user_data["faculty"]

    groups = get_groups(faculty, course)

    await state.update_data(groups=groups)
    await state.update_data(course=course)

    await callback_query.message.edit_text(
        text=(
            f"{validate_faculty(faculty)}"
            f"Курс <i><b>#{course}</b></i>\n"
            "⚙️ Выберите группу:"
        ),
        reply_markup=build_group_kb(groups, "group"),
    )
    await state.set_state(GroupForm.group)


@router.callback_query(GroupForm.group)
async def handle_group(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()

    user_data = await state.get_data()
    groups = user_data["groups"]
    course = user_data["course"]
    if callback_query.data in groups:
        faculty = user_data["faculty"]

        selected_group = callback_query.data
        subgroups = get_subgroups(faculty, selected_group)

        await state.update_data(group=selected_group)
        await state.update_data(group=selected_group, subgroups=subgroups)

        await callback_query.message.edit_text(
            text=(
                f"{validate_faculty(faculty)}"
                f"Курс <i><b>#{course}</b></i>\n"
                f"Группа <i><b>{selected_group}</b></i>\n"
                "⚙️ Выберите подгруппу:"
            ),
            reply_markup=build_group_kb(subgroups, "subgroup"),
        )
        await state.set_state(GroupForm.subgroup)


@router.callback_query(GroupForm.subgroup)
async def handle_subgroup(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    user_id = callback_query.from_user.id
    subgroup = callback_query.data

    faculty = user_data["faculty"]
    group = user_data["group"]
    course = user_data.get("course")

    upsert_user(user_id=user_id, group=group, subgroup=subgroup, faculty=faculty)

    await callback_query.message.answer(
        text="Теперь вам доступно расписание",
        reply_markup=main_kb(),
    )
    await callback_query.message.edit_text(
        text=(
            (
                f"{validate_faculty(faculty)}"
                f"Курс <i><b>#{course}</b></i>\n"
                f"Группа <i><b>{group}</b></i>\n"
                f"Подгруппа <b><i>{subgroup}</i></b>"
            )
            if course
            else (
                f"{validate_faculty(faculty)}"
                f"Группа <i><b>{group}</b></i>\n"
                f"Подгруппа <b><i>{subgroup}</i></b>"
            )
        ),
    )

    await state.clear()


@router.message(Command("cancel"))
async def cancel_state(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if not current_state:
        await message.delete()
    else:
        await state.clear()
        await message.answer(text=f"Выбор отменен", reply_markup=main_kb())


variants: dict[State, str] = {
    GroupForm.faculty: "факультет",
    GroupForm.course: "курс",
    GroupForm.group: "группу",
    GroupForm.subgroup: "подгруппу",
}


@router.message(
    StateFilter(
        GroupForm.faculty, GroupForm.course, GroupForm.group, GroupForm.subgroup
    )
)
async def clear_current_state(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    current_state = await state.get_state()
    await message.answer(
        text=f"Выберите {variants[current_state]} или нажмите /cancel для отмены"
    )


@router.message(Command("change_group"))
async def handle_change_faculty(message: types.Message, state: FSMContext) -> None:
    settings_text = "⚙️ Выберите факультет:"
    await message.answer(
        text=settings_text,
        reply_markup=build_faculty_kb(),
    )
    await state.set_state(GroupForm.faculty)


@router.message(Command("change_subgroup"))
async def handle_change_subgroup(message: types.Message, state: FSMContext) -> None:
    subgroups = user_get_subgroups(message.from_user.id)
    user_data = get_user(message.from_user.id)
    await message.answer(
        text="⚙️ Выберите подгруппу:",
        reply_markup=build_group_kb(subgroups),
    )
    await state.update_data(faculty=user_data["faculty"], group=user_data["group"])
    await state.set_state(GroupForm.subgroup)
