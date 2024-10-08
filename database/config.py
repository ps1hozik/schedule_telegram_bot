import os


from pymongo import MongoClient


def get_database():
    client = MongoClient(os.getenv("CONNECTION_STRING"))
    return client["schedule_bot"]


if __name__ == "__main__":
    dbname = get_database()
