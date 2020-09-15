from typing import Callable

from pymongo import MongoClient

FLAGGING_DATABASE = 'flagging_test'
FLAGGING_COLLECTION = 'flagging'
FLAG_DEPENDENCIES = "flag_dependencies"


class FlaggingMongo:

    def __init__(self, connection_url: str):
        self.connection_url = connection_url

    def __enter__(self):
        self.client = MongoClient(self.connection_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    #TODO,
    # define data structure for flag
    # Flag ID (default, do not need to specify), Flag Name,
    # validtion_results.errors, validation_results.mypy_errors
    # referenced_flags,
    # Flag Update Date
    # set up index on flag name




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


    def add_flag_dependencies(self, flag_deps):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAG_DEPENDENCIES]
        flagging.insert_one(flag_deps)

    def get_flag_dependencies(self):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        return list(flagging_dependencies.find())
