from typing import Callable

from pymongo import MongoClient
import datetime
import pandas as pd

FLAGGING_DATABASE = 'flagging_test'
FLAGGING_COLLECTION = 'flagging'
FLAG_DEPENDENCIES = "flag_dependencies"
FLAG_GROUPS = "flag_groups"


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
    UPDATE_TIMESTAMP: datetime flag was last updated -> datetime object
    '''
    def get_flags(self):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        return list(flagging.find())

    def add_flag(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.insert_one(flag).inserted_id
        return flag_id

    #TODO,
    # remove query, make generic
    def remove_flag(self, query):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.find_and_modify(query=query, remove=True, new=False)["_id"]
        return flag_id

    #TODO,
    # remove query, make generic
    def update_flag(self, query, update):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_id = flagging.find_and_modify(query=query, remove=False, update=update)["_id"]
        return flag_id

    #TODO,
    # remove FLAG_NAME, can use "_id"
    def duplicate_flag(self, flag_name):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAGGING_COLLECTION]
        flag_2_duplicate = flagging.find_one({"FLAG_NAME": flag_name})
        flag_2_duplicate.update({"UPDATE_TIMESTAMP": datetime.datetime.now()})
        flag_2_duplicate.pop("_id", None)
        flag_id = flagging.insert_one(flag_2_duplicate).inserted_id
        return flag_id


    #flag groups
    '''
    FLAG_GROUPS
    _id: unique user id
    FLAG_GROUP_NAME: flag group name -> str
    FLAGS_IN_GROUP: flags in flag group -> [str]
    FLAG_GROUP_STATUS: is flag_group ready for production or in development -> bool
    UPDATE_TIMESTAMP: datetime flag group was last updated -> datetime object
    '''
    def get_flag_groups(self):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        return list(flag_groups.find())

    def add_flag_group(self, flag_group):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAG_GROUPS]
        flag_id = flagging.insert_one(flag_group).inserted_id
        return flag_id

    #TODO,
    # remove query, make generic
    def remove_flag_group(self, query):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        flag_group_id = flag_groups.find_and_modify(query=query, remove=True, new=False)["_id"]
        return flag_group_id

    #TODO,
    # remove query, make generic
    def update_flag_group(self, query, update):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        flag_group_id = flag_groups.find_and_modify(query=query, remove=False, update=update)["_id"]
        return flag_group_id

    #TODO,
    # remove FLAG_GROUP_NAME, can use _id
    def duplicate_flag_groups(self, flag_group):
        db = self.client[FLAGGING_DATABASE]
        flag_groups = db[FLAG_GROUPS]
        flag_group_2_duplicate = flag_groups.find_one({"FLAG_GROUP_NAME": flag_group})
        flag_group_2_duplicate.update({"UPDATE_TIMESTAMP": datetime.datetime.now()})
        flag_group_2_duplicate.pop("_id", None)
        flag_group_id = flag_groups.insert_one(flag_group_2_duplicate).inserted_id
        return flag_group_id


    #flag dependencies
    '''
    FLAG_DEPENDENCIES
    _id: unique user id 
    FLAG_NAME: flag_name -> str
    DEPENDENT_FLAGS: flags that flag_name is dependent on -> [str]
    UPDATE_TIMESTAMP: datetime flag dependency was last updated -> datetime object
    '''
    def get_flag_dependencies(self):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        return list(flagging_dependencies.find())

    def add_flag_dependencies(self, flag_deps):
        db = self.client[FLAGGING_DATABASE]
        flagging = db[FLAG_DEPENDENCIES]
        flagging.insert_one(flag_deps)

    #TODO,
    # remove query, make generic
    def remove_flag_dependency(self, query):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies.delete_one(query)

    #TODO,
    # remove FLAG_NAME, can use _id
    def get_specific_flag_dependencies(self, flag):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flagging_dependencies = flagging_dependencies.find_one({"FLAG_NAME": flag})
        return list(flagging_dependencies)

    #TODO,
    # remove FLAG_NAME, DEPDENDENT_FLAGS
    def add_specific_flag_dependencies(self, flag, new_deps: []):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag = flagging_dependencies.find_one({"FLAG_NAME": flag})["DEPENDENT_FLAGS"][0]
        flag_deps_list = []
        if isinstance(flag_deps_flag, list):
            for x in flag_deps_flag:
                flag_deps_list.append(x)
        else:
            flag_deps_list.append(flag_deps_flag)
        for new_dep in new_deps:
            if new_dep not in flag_deps_list:
                flag_deps_list.append(new_dep)
        updated_id = flagging_dependencies.find_and_modify(query={"FLAG_NAME": flag}, remove=False, update={"DEPENDENT_FLAGS": flag_deps_list})["_id"]
        return updated_id

    #TODO
    # debugg remove_specific_flag_dependencies
    def remove_specific_flag_dependencies(self, flag, rm_deps: []):
        db = self.client[FLAGGING_DATABASE]
        flagging_dependencies = db[FLAG_DEPENDENCIES]
        flag_deps_flag = list(flagging_dependencies.find_on({"FLAG_NAME": flag}))
        df_flagging_dependencies = pd.DataFrame(list(flagging_dependencies.find()))
        df_flag_deps_flag = df_flagging_dependencies[df_flagging_dependencies["FLAG_NAME"] == flag]
        for rm_dep in rm_deps:
            if not df_flag_deps_flag[df_flag_deps_flag["FLAG_DEPENDENCIES"].astype(str).str.contains(rm_dep)].empty:
                for item in df_flag_deps_flag.items():
                    item[1].remove(rm_dep)
        item[1] = set(item[1])
        item[1] = list(item[1])
        flag_id = flagging_dependencies.find_and_modify(query={"FLAG_NAME": flag}, remove=False, update=item[1])["_id"]
        return flag_id



    #def update_flag_depenency