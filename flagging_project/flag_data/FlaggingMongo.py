from typing import Callable

from pymongo import MongoClient
import datetime
import pandas as pd

FLAGGING_DATABASE = 'flagging_test'
FLAGGING_COLLECTION = 'flagging'
FLAG_DEPENDENCIES = "flag_dependencies"
FLAG_GROUPS = "flag_groups"

flag_id = "_id"
flag_group_id = "_id"
flag_timestamp = "FLAG_TIMESTAMP"
flag_group_timestamp = "FLAG_GROUP_TIMESTAMP"


class FlaggingMongo:

    def __init__(self, connection_url: str):
        self.connection_url = connection_url

    def __enter__(self):
        self.client = MongoClient(self.connection_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    #TODO
    # set up index on flag name


    #flags
    '''
    FLAGS
    _id: unique user id
    FLAG_NAME: common flag_name -> str
    FLAG_VALIDATION_RESULTS: results of flag validation (errors.__str__(), mypy errors.__str__())
    REFERENCED_FLAGS: flags in flag logic -> [str]
    FLAG_STATUS: is flag in production or in draft status -> bool
    FLAG_TIMESTAMP: datetime flag was last updated -> datetime object
    '''
    def get_flags(self):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        return list(flagging.find())

    def add_flag(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        inserted_flag = flagging.insert_one(flag).inserted_id
        return inserted_flag

    def remove_flag(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        removed_id = flagging.remove({flag_id: flag})[flag_id]
        return removed_id

    def update_flag(self, flag, update_value, update_column):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        updated_flag = flagging.find_one_and_update({flag_id: flag}, {"$set": {update_column: update_value}}, upsert=True)[flag_id]
        return updated_flag

    def duplicate_flag(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_2_duplicate = flagging.find_one({flag_id: flag})
        flag_2_duplicate.update({flag_timestamp: datetime.datetime.now()})
        flag_2_duplicate.pop(flag_id, None)
        duplicated_flag = flagging.insert_one(flag_2_duplicate).inserted_id
        return duplicated_flag

    #flag groups
    '''
    FLAG_GROUPS
    _id: unique user id
    FLAG_GROUP_NAME: flag group name -> str
    FLAGS_IN_GROUP: flags in flag group -> [str]
    FLAG_GROUP_STATUS: is flag_group ready for production or in development -> bool
    FLAG_TIMESTAMP: datetime flag group was last updated -> datetime object
    '''
    def get_flag_groups(self):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        return list(flag_groups.find())

    def add_flag_group(self, flag_group):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAG_GROUPS]
        new_flag_group = flagging.insert_one(flag_group).inserted_id
        return new_flag_group

    def remove_flag_group(self, flag_group):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        removed_flag_group_id = flag_groups.remove({flag_group_id: flag_group})[flag_id]
        return removed_flag_group_id

    def update_flag_group(self, flag_group, update_value, update_column):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        updated_flag_group = flag_groups.find_one_and_update({flag_group_id: flag_group}, {"$set": {update_column: update_value}}, upsert=True)[flag_group_id]
        return updated_flag_group

    def duplicate_flag_group(self, flag_group):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        flag_group_2_duplicate = flag_groups.find_one({flag_group_id: flag_group})
        flag_group_2_duplicate.update({flag_group_timestamp: datetime.datetime.now()})
        flag_group_2_duplicate.pop(flag_group_id, None)
        duplicated_flag_groups = flag_groups.insert_one(flag_group_2_duplicate).inserted_id
        return duplicated_flag_groups

    #flag dependencies
    '''
    FLAG_DEPENDENCIES
    _id: unique user id 
    FLAG_NAME: flag_name -> str
    DEPENDENT_FLAGS: flags that flag_name is dependent on -> [str]
    FLAG_TIMESTAMP: datetime flag dependency was last updated -> datetime object
    '''
    def get_flag_dependencies(self):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        return list(flagging_dependencies.find())

    def add_flag_dependencies(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAG_DEPENDENCIES]
        new_flag_dep = flagging.insert_one(flag).inserted_id
        return new_flag_dep

    def remove_flag_dependencies(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        modified_flag_id = flagging_dependencies.remove({flag_id: flag})[flag_id]
        return modified_flag_id

    def get_specific_flag_dependencies(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies = flagging_dependencies.find_one({flag_id: flag})
        return list(flagging_dependencies)


    def add_specific_flag_dependencies(self, flag, new_deps: [], dependent_flag_column):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag = flagging_dependencies.find_one({flag_id: flag})[dependent_flag_column]
        flag_deps_list = []
        if isinstance(flag_deps_flag, list):
            for x in flag_deps_flag:
                flag_deps_list.append(x)
        else:
            flag_deps_list.append(flag_deps_flag)
        for new_dep in new_deps:
            if new_dep not in flag_deps_list:
                flag_deps_list.append(new_dep)
        updated_id = flagging_dependencies.find_one_and_update({flag_id: flag}, {"$set": {dependent_flag_column: flag_deps_list}}, upsert=True)[flag_group_id]
        return updated_id

    def remove_specific_flag_dependencies(self, flag, rm_deps: [], dependent_flag_column):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag = flagging_dependencies.find_one({flag_id: flag})[dependent_flag_column]
        flag_deps_list = []
        if isinstance(flag_deps_flag, list):
            for x in flag_deps_flag:
                flag_deps_list.append(x)
        else:
            flag_deps_list.append(flag_deps_flag)
        for rm_dep in rm_deps:
            if rm_dep in flag_deps_list:
                flag_deps_list.remove(rm_dep)
        modified_flag = flagging_dependencies.find_one_and_update({flag_id: flag}, {"$set": {dependent_flag_column: flag_deps_list}}, upsert=True)[flag_id]
        return modified_flag

    def update_flag_dependencies(self, flag, dependent_flag_value: [], dependent_flag_column: str):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        matching_flag = flagging_dependencies.find_one({flag_id: flag})[flag_id]
        modified_flag = None
        if matching_flag:
            modified_flag = flagging_dependencies.find_one_and_update({flag_id: flag}, {"$set": {dependent_flag_column: dependent_flag_value}}, upsert=True)[flag_id]
        return modified_flag