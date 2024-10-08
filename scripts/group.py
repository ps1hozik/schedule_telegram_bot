from os import getenv


from database.config import get_database


db = get_database()
collection_users = db[getenv("USERS_DB")]


# Получение списка групп для факультета и курса
def get_groups(faculty: str, course: int):
    group_collection = db[f"Группы {faculty}"]
    groups_cursor = group_collection.find({"course": str(course)}).sort("_id", 1)

    return [doc["group_name"] for doc in groups_cursor]


# Получение списка подгрупп для группы
def get_subgroups(faculty: str, group: str):
    group_collection = db[f"Группы {faculty}"]
    return group_collection.find_one({"group_name": group})["sub_groups"]
