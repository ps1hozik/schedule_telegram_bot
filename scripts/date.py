from datetime import timedelta, datetime, date

import pytz


# Получение диапазона дат недели
def get_week_date_range() -> tuple[str, str]:
    current_weekday, current_date_minsk = get_current_date()
    #                           3
    if 0 <= current_weekday <= 1:
        start_date = current_date_minsk - timedelta(days=current_weekday)
    else:
        start_date = current_date_minsk + timedelta(days=(7 - current_weekday))

    end_date = start_date + timedelta(days=5)

    return start_date.strftime("%d.%m"), end_date.strftime("%d.%m")


# Получение даты по номеру дня недели
def get_date_by_weekday(day_number: int) -> str:
    current_weekday, current_date_minsk = get_current_date()
    #                           3
    if 0 <= current_weekday <= 1:
        start_date = current_date_minsk - timedelta(days=current_weekday)
    else:
        start_date = current_date_minsk + timedelta(days=(7 - current_weekday))

    target_date = start_date + timedelta(days=day_number)

    return str(target_date)


# Получение текущей даты и дня недели в Минске
def get_current_date(days: int = 0) -> tuple[int, date]:
    current_utc_time = datetime.now(pytz.timezone("UTC")) + timedelta(days=days)
    minsk_timezone = pytz.timezone("Europe/Minsk")
    current_datetime_minsk = current_utc_time.astimezone(minsk_timezone)
    current_date_minsk = current_datetime_minsk.date()
    weekday_minsk = current_date_minsk.weekday()

    return weekday_minsk, current_date_minsk


# Проверка соответствия даты с понедельником недели
def is_same_week(lesson_date: date) -> bool:
    current_weekday, current_date_minsk = get_current_date()
    lesson_weekday = lesson_date.weekday()
    #                           3
    if 0 <= current_weekday <= 1:
        current_monday = current_date_minsk - timedelta(days=current_weekday)
    else:
        current_monday = current_date_minsk + timedelta(days=(7 - current_weekday))

    lesson_monday = lesson_date - timedelta(days=lesson_weekday)

    return current_monday == lesson_monday
