from datetime import datetime
from os import getenv

from database.config import get_database
from scripts.date import is_same_week

db = get_database()
collection_users = db[getenv("USERS_DB")]


# Получение расписания для пользователя по его ID
def get_user_schedule(user_id: int) -> list:
    user_data = collection_users.find_one({"user_id": user_id})
    if not user_data:
        return []
    group_name = user_data.get("subgroup")
    faculty_name = user_data.get("faculty")
    if not group_name or not faculty_name:
        return []
    collection_schedule = db[f"Расписание {faculty_name}"]

    user_schedule = collection_schedule.find_one({"group_name": group_name})["schedule"]

    return user_schedule


# Получение расписания на один день
def get_schedule_for_day(user_id: int, lesson_date: str) -> str | None:
    full_schedule = get_user_schedule(user_id)
    for daily_schedule in full_schedule:
        if daily_schedule["date"] == lesson_date:
            # valid_lessons = []
            #
            # for schedule in daily_schedule["lessons"]:
            #     if schedule["lesson"] is not None:
            #         valid_lessons.append(schedule)
            #
            # if valid_lessons:
            #     return _format_schedule(
            #         lessons=valid_lessons,
            #         day_name=daily_schedule["day"],
            #         lesson_date=daily_schedule["date"],
            #     )
            return _format_schedule(
                lessons=daily_schedule["lessons"],
                day_name=daily_schedule["day"],
                lesson_date=daily_schedule["date"],
            )

    return None


# Получение полного расписания пользователя
def get_full_schedule(user_id: int) -> list:
    formatted_schedule = []
    full_schedule = get_user_schedule(user_id)

    if full_schedule:
        last_lesson_date = full_schedule[-1]["date"]

        if is_same_week(datetime.strptime(last_lesson_date, "%Y-%m-%d").date()):
            if full_schedule[0]["day"] == "Суббота":
                del full_schedule[0]

            for daily_schedule in full_schedule:
                formatted_schedule.append(
                    _format_schedule(
                        daily_schedule["lessons"],
                        daily_schedule["day"],
                        daily_schedule["date"],
                    )
                )
    return formatted_schedule


# Получение расписания учителя
def get_teacher_schedule(teacher_name: str) -> list[str] | None:
    if len(teacher_name) < 3:
        return None

    # Приведение имени учителя к нижнему регистру и форматирование
    teacher_name_check = teacher_name.lower().replace(".", "").split()
    if len(teacher_name_check) > 1:
        teacher_name_check[1:] = [s[0] for s in teacher_name_check[1:]]
    formatted_teacher_name = " ".join(teacher_name_check[:3])

    collections = db.list_collection_names()
    schedule_list = []

    # Поиск учителя по всем коллекциям расписаний
    for collection in collections:
        if "расписание" in collection.lower():
            schedule_data = db[collection].find()

            for group_data in schedule_data:
                for daily_schedule in group_data["schedule"]:
                    lesson_data = None
                    for lesson in daily_schedule["lessons"]:
                        if lesson["lesson"] and formatted_teacher_name in " ".join(
                                lesson["lesson"]["teacher"].lower().replace(".", "").split()
                        ):
                            if lesson_data is None:
                                lesson_data = {
                                    "day": daily_schedule["day"],
                                    "date": daily_schedule["date"],
                                    "lessons": [],
                                }
                            if lesson not in lesson_data["lessons"]:
                                lesson["group"] = group_data["group_name"]
                                lesson_data["lessons"].append(lesson)

                    if lesson_data:
                        date_found = False
                        for existing_data in schedule_list:
                            if existing_data["date"] == lesson_data["date"]:
                                for lesson in lesson_data["lessons"]:
                                    lesson_found = False
                                    for existing_lesson in existing_data["lessons"]:
                                        if (
                                                existing_lesson["lesson"]["name"]
                                                == lesson["lesson"]["name"]
                                                and existing_lesson["number"]
                                                == lesson["number"]
                                        ):
                                            existing_lesson["group"] = ", ".join(
                                                [
                                                    existing_lesson["group"],
                                                    lesson["group"],
                                                ]
                                            )
                                            lesson_found = True
                                            break
                                    if not lesson_found:
                                        existing_data["lessons"].append(lesson)
                                date_found = True
                                break
                        if not date_found:
                            schedule_list.append(lesson_data)

    # Сортировка расписаний
    for item in schedule_list:
        item["lessons"].sort(key=lambda x: x["number"])
    schedule_list.sort(key=lambda x: x["date"])

    formatted_schedule = []
    for item in schedule_list:
        formatted_schedule.append(
            _format_schedule(item["lessons"], item["day"], item["date"])
        )

    return formatted_schedule


# Форматирование расписания для отображения
def _format_schedule(lessons: list, day_name: str, lesson_date: str) -> str:
    while lessons and lessons[-1]["lesson"] is None:
        lessons.pop()

    space = "⠀⠀"
    formatted_date = lesson_date[5:][3:] + "." + lesson_date[5:][:2]
    formatted_lessons = f"<b><u>{day_name} ({formatted_date})</u></b>\n\n"

    for _, lesson_info in enumerate(lessons):
        lesson_name = lesson_info["lesson"]["name"] if lesson_info["lesson"] else " "
        lesson_teacher = (
            lesson_info["lesson"]["teacher"] if lesson_info["lesson"] else " "
        )
        lesson_auditorium = (
            lesson_info["lesson"]["auditorium"] if lesson_info["lesson"] else " "
        )
        lesson_group = ": " + lesson_info["group"] if "group" in lesson_info else ""
        lesson_time = lesson_info["time"]
        lesson_number = lesson_info["number"]

        formatted_lessons += (
            f"<i><u>№{lesson_number} {lesson_time}</u> {lesson_group} </i> \n\n"
        )
        formatted_lessons += "<b>"
        formatted_lessons += f"{space}{lesson_name}\n" if lesson_name != " " else ""
        formatted_lessons += (
            f"{space * 2}{lesson_teacher}\n" if lesson_teacher != " " else ""
        )
        formatted_lessons += (
            f"{space * 2}{lesson_auditorium}\n\n</b>"
            if lesson_auditorium != " "
            else "</b>"
        )

    if formatted_lessons != f"{day_name} ({formatted_date})\n\n":
        return formatted_lessons
