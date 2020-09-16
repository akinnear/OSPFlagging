from typing import Callable

from pymongo import MongoClient
import datetime

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
        return flag_id

    def remove_flag(self, query):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.find_and_modify(query=query, remove=True, new=False)["_id"]
        return flag_id

    def update_flag(self, query, update):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.find_and_modify(query=query, remove=False, update=update)["_id"]
        return flag_id

    def duplicate_flag(self, flag_name):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_2_duplicate = flagging.find_one({"FLAG_NAME": flag_name})
        flag_2_duplicate.update({"UPDATE_TIMESTAMP": datetime.datetime.now()})
        flag_2_duplicate.pop("_id", None)
        flag_id = flagging.insert_one(flag_2_duplicate).inserted_id
        return flag_id


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

    def remove_flag_dependency(self, query):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies.delete_one(query)

