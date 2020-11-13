from typing import Callable

from pymongo import MongoClient
import datetime
import pandas as pd
from flag_data.FlaggingColumnNames import flag_name_col_name, flag_logic_col_name, \
    referenced_flag_col_name, flag_status_col_name, flag_group_name_col_name, \
    flag_group_flags_col_name, flag_group_status_col_name, flag_dep_dep_flags_col_name, \
    flag_dep_flag_id_col_name, flag_dep_flag_group_id_col_name, flag_error_col_name, \
    flag_group_error_col_name


FLAGGING_DATABASE = 'flagging_test'
FLAGGING_COLLECTION = 'flagging'
FLAG_DEPENDENCIES = "flag_dependencies"
FLAG_GROUPS = "flag_groups"

flag_id = "_id"
flag_group_id = "_id"
flag_group_timestamp = "FLAG_GROUP_TIMESTAMP"
flag_logic = "FLAG_LOGIC"
flag_dep_id = "_id"



class FlaggingMongo:

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.client = MongoClient(self.connection_url)

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
    FLAG_LOGIC: jsonify flag logic information
    REFERENCED_FLAGS: flags in flag logic -> [str]
    FLAG_STATUS: is flag in production or in draft status -> bool
    '''
    def get_flags(self):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        print(list(flagging.find()))
        return list(flagging.find())

    def get_flag_ids(self):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flags = list(flagging.find())
        flag_ids = [x["_id"] for x in flags]
        return flag_ids

    def get_specific_flag(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        found_id = flagging.find_one({flag_id: flag})[flag_id]
        return found_id

    def get_specific_flag_error(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flag_error = flagging.find_one({flag_id: flag})[flag_error_col_name]
        return flag_error

    def get_flag_logic_information(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flag_logic = flagging.find_one({flag_id: flag})[flag_logic_col_name]
        return flag_logic

    def get_flag_name(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flag_name = flagging.find_one({flag_id: flag})[flag_name_col_name]
        return flag_name

    def get_flag_status(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flag_status = flagging.find_one({flag_id: flag})[flag_status_col_name]
        return flag_status

    def add_flag(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        inserted_flag = flagging.insert_one(flag).inserted_id
        return inserted_flag

    def remove_flag(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flagging.remove({flag_id: flag})
        return flag

    def update_flag(self, flag, update_value, update_column):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        updated_flag = flagging.find_one_and_update({flag_id: flag}, {"$set": {update_column: update_value}}, upsert=True)[flag_id]
        return updated_flag

    def duplicate_flag(self, flag):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flag_2_duplicate = flagging.find_one({flag_id: flag})
        flag_2_duplicate.pop(flag_id, None)
        duplicated_flag = flagging.insert_one(flag_2_duplicate).inserted_id
        return duplicated_flag

    def delete_all_flags(self):
        db = get_db(self)
        flagging = db[FLAGGING_COLLECTION]
        flagging.delete({})


    #flag groups
    '''
    FLAG_GROUPS
    _id: unique user id
    FLAG_GROUP_NAME: flag group name -> str
    FLAGS_IN_GROUP: flags in flag group -> [str]
    FLAG_GROUP_STATUS: is flag_group ready for production or in development -> bool
    '''
    def get_flag_groups(self):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        return list(flag_groups.find())

    def get_flag_group_ids(self):
        db = get_db(self)
        flag_group = db[FLAG_GROUPS]
        flag_group_list = list(flag_group.find())
        flag_group_ids = [x["_id"] for x in flag_group_list]
        return flag_group_ids

    def get_flag_group_names(self):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flag_group_list = list(flag_groups.find())
        flag_group_names = [x[flag_group_name_col_name] for x in flag_group_list]
        return flag_group_names

    def get_flag_group_flag(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        found_flags = flag_groups.find_one({flag_group_id: flag_group})[flag_group_flags_col_name]
        return list(found_flags)

    def get_flag_names_from_flag_group(self, flag_group):
        flag_name_list = []
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flagging = db[FLAGGING_COLLECTION]
        flags_in_flag_group_ids = flag_groups.find_one({flag_group_id: flag_group})[flag_group_flags_col_name]
        for flag in flags_in_flag_group_ids:
            flag_name = flagging.find_one({flag_id: flag})[flag_name_col_name]
            flag_name_list.append(flag_name)
        return flag_name_list

    def get_specific_flag_group(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        found_id = flag_groups.find_one({flag_id: flag_group})[flag_group_id]
        return found_id

    def get_flag_group_name(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        found_name = flag_groups.find_one({flag_group_id: flag_group})[flag_group_name_col_name]
        return found_name

    def add_flag_group(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        new_flag_group = flag_groups.insert_one(flag_group).inserted_id
        return new_flag_group

    def remove_flag_group(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flag_groups.remove({flag_group_id: flag_group})
        return flag_group

    def update_flag_group(self, flag_group, update_value, update_column):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        updated_flag_group = flag_groups.find_one_and_update({flag_group_id: flag_group}, {"$set": {update_column: update_value}}, upsert=True)[flag_group_id]
        return updated_flag_group

    def duplicate_flag_group(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flag_group_2_duplicate = flag_groups.find_one({flag_group_id: flag_group})
        flag_group_2_duplicate.pop(flag_group_id, None)
        duplicated_flag_groups = flag_groups.insert_one(flag_group_2_duplicate).inserted_id
        return duplicated_flag_groups

    def get_flag_group_errors(self, flag_group):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flag_group_error = flag_groups.find_one({flag_id: flag_group})[flag_group_error_col_name]
        return flag_group_error

    def delete_all_flag_groups(self):
        db = get_db(self)
        flag_groups = db[FLAG_GROUPS]
        flag_groups.delete({})

    #flag dependencies
    '''
    FLAG_DEPENDENCIES
    _id: unique user id 
    FLAG_ID: unique flag id
    FLAG_GROUP_ID: unique flag group id
    DEPENDENT_FLAGS: [(flag_name, flag_group_id), (flag_name, flag_group_id)...]
    '''
    def get_flag_dependencies(self):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        return list(flagging_dependencies.find())

    def get_flag_dependencies_ids(self):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies_list = list(flagging_dependencies.find())
        flagging_dependencies_ids = [x["_id"] for x in flagging_dependencies_list]
        return flagging_dependencies_ids

    def get_flag_dependencies_names(self):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies_list = list(flagging_dependencies.find())
        flagging_dependencies_names = [x[flag_name_col_name] for x in flagging_dependencies_list]
        return flagging_dependencies_names

    def add_flag_dependencies(self, flag):
        db = get_db(self)
        flagging = db[FLAG_DEPENDENCIES]
        new_flag_dep = flagging.insert_one(flag).inserted_id
        return new_flag_dep

    def remove_flag_dependencies(self, flag_dep_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies.remove({"_id": flag_dep_id})
        return flag_dep_id

    def get_specific_flag_dependencies(self, flag):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies = flagging_dependencies.find_one({flag_id: flag})
        return list(flagging_dependencies)

    def get_specific_flag_dep_id_by_flag_id(self, flag):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_dep_key = flagging_dependencies.find_one({"FLAG_ID": flag})
        return flag_dep_key

    def get_specific_flag_dep_id_by_flag_id_and_flag_group_id(self, flag_id, flag_group_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_dep_key = flagging_dependencies.find_one({flag_dep_flag_id_col_name: flag_id,
                                                       flag_dep_flag_group_id_col_name: flag_group_id})
        return flag_dep_key

    def get_flag_dep_by_flag_group_id(self, flag_group_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps = list(flagging_dependencies.find({flag_dep_flag_group_id_col_name: flag_group_id}))
        return flag_deps

    def get_flag_dep_by_flag_id(self, flag_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps = list(flagging_dependencies.find({flag_dep_flag_id_col_name: flag_id}))
        return flag_deps

    def add_specific_flag_dependencies(self, flag, new_deps: [], dependent_flag_column):
        db = get_db(self)
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
        updated_id = flagging_dependencies.find_one_and_update({flag_id: flag}, {"$set": {dependent_flag_column: flag_deps_list}}, upsert=True)["_id"]
        return updated_id

    def remove_specific_flag_dependencies(self, flag, rm_deps: [], dependent_flag_column):
        db = get_db(self)
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


    def remove_specific_flag_dependencies_via_flag_id_and_flag_group_id(self, flag, flag_group_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag_rm_list = list(flagging_dependencies.find({flag_dep_flag_id_col_name: flag,
                            flag_dep_flag_group_id_col_name: flag_group_id}))
        for rm_id in [x["_id"] for x in flag_deps_flag_rm_list]:
            flagging_dependencies.remove({flag_dep_id: rm_id})
        return [x["_id"] for x in flag_deps_flag_rm_list]

    def remove_specific_flag_dependencies_via_flag_id(self, flag):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag_rm_list = list(flagging_dependencies.find({flag_dep_flag_id_col_name: flag}))
        for rm_id in [x["_id"] for x in flag_deps_flag_rm_list]:
            flagging_dependencies.remove({flag_dep_id: rm_id})
        return [x["_id"] for x in flag_deps_flag_rm_list]

    def remove_specific_flag_dependencies_via_flag_group_id(self, flag_group_id):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag_rm_list = list(flagging_dependencies.find({flag_dep_flag_group_id_col_name: flag_group_id}))
        for rm_id in [x["_id"] for x in flag_deps_flag_rm_list]:
            flagging_dependencies.remove({flag_dep_id: rm_id})
        return [x["_id"] for x in flag_deps_flag_rm_list]




    def update_flag_dependencies(self, flag, dependent_flag_value: [], dependent_flag_column: str):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        matching_flag = flagging_dependencies.find_one({flag_id: flag})[flag_id]
        modified_flag = None
        if matching_flag:
            modified_flag = flagging_dependencies.find_one_and_update({flag_id: flag}, {"$set": {dependent_flag_column: dependent_flag_value}}, upsert=True)[flag_id]
        return modified_flag

    def get_specific_flag_dependency_flags(self, flag):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps = flagging_dependencies.find_one({flag_id: flag})[flag_dep_dep_flags_col_name]
        return flag_deps

    def delete_all_flag_dependencies(self):
        db = get_db(self)
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies.delete({})

def get_db(flagging_mongo):
    print('in get_db')
    return flagging_mongo.client[FLAGGING_DATABASE]