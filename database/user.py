from os import getenv


from database.config import get_database


db = get_database()
collection_users = db[getenv("USERS_DB")]


def upsert_user(
    user_id: int, group: str = None, subgroup: str = None, faculty: str = None
) -> None:
    user = collection_users.find_one({"user_id": user_id})
    if user:
        collection_users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "group": group or user["group"],
                    "subgroup": subgroup or user["subgroup"],
                    "faculty": faculty or user["faculty"],
                }
            },
        )
    else:
        collection_users.insert_one(
            {
                "user_id": user_id,
                "group": group,
                "subgroup": subgroup,
                "faculty": faculty,
            }
        )


def get_user(user_id: int) -> dict | None:
    user = collection_users.find_one({"user_id": user_id})
    if not user:
        return None

    return {
        "faculty": user["faculty"],
        "group": user["group"],
        "subgroup": user["subgroup"],
    }


def get_subgroups(user_id: int) -> enumerate | None:
    user = collection_users.find_one({"user_id": user_id})
    if not user:
        return None

    groups = db[f"Группы {user["faculty"]}"].find()
    for g in groups:
        if user["group"] == g["group_name"]:
            return g["sub_groups"]
