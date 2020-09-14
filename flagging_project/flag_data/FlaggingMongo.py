from typing import Callable

from pymongo import MongoClient

FLAGGING_DATABASE = 'flagging_test'
FLAGGING_COLLECTION = 'flagging'


class FlaggingMongo:

    def __init__(self, connection_url: str):
        self.connection_url = connection_url

    def __enter__(self):
        self.client = MongoClient(self.connection_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def add_flag(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.insert_one(flag).inserted_id

        # TODO Remove this portion
        flag = flagging.find_one({"_id": flag_id})
        print(flag)

    def get_flags(self):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        return list(flagging.find())
