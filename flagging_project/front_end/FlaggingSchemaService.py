#imports
import pandas as pd

from flagging.FlaggingNodeVisitor import determine_variables
from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
from flag_names.FlagService import pull_flag_names
from flag_names.FlagGroupService import pull_flag_group_names

#TODO
# interface design, html5 + bootstrap4

#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.

def validate_logic(flag_id:str, user_logic: str):
    #get flag feeders
    flag_feeders = pull_flag_feeders(mock_api_endpiong="dummy_text_endpoint")

    #perform full validation on user_logic via nodevisitor, mypy, and validation

    #nodeivisitor on user_logic
    #determine variables form FlaggingNodeVisitor
    flag_logic_information = determine_variables(user_logic)

    #mypy validation is part of full validation method, do not need explicit mypy validation call

    #need flag_dependiceis from api call or direct query
    flag_dependencies = get_flag_dependencies()

    #validation
    validation_result = validate_flag_logic_information(flag_id, flag_feeders, flag_dependencies, flag_logic_information)

    #return errors and warning information
    return validation_result


#A call to get flag dependencies
def get_flag_dependencies():
    #api endpoint of db endpoint
    #hard code dependencies for now
    flag_dependencies = {"Flag1": {"Flag8"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    return flag_dependencies

#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error

def create_flag(flag_id: str, flag_logic: str):
    #store flag name and flag logic in db

    if flag_id is None:
        # return error message, no flag name specified
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag id not specified")

    else:

        # write query, with new primary key
        # cursor.execute("""INSERT into TABLE FLAG_NAME_COL= :flag_name, FLAG_LOGIC_COL= :flag_logic""",
        # flag_name=flag_name,
        # flag_logic=flag_logic)

        # cursor.execute("""SELECT PRIMARY_KEY_COL FROM TABLE
        # WHERE FLAG_NAME_COL = :flag_name
        # AND FLAG_LOGIC_COL = :flag_logic""",
        # flag_name=flag_name,
        # flag_logic=flag_logic)

        # df_new_flag = df_from_cursor.cursor()
        # return df_new_flag['PRIMARY_KEY_COL'].values[0]

        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag created",
                                                       uuid=flag_id + "_primary_key_id")
    return flag_schema_object



#A call to save changes to a flag, this will take in the change and a UUID
#One call for flag name
def update_flag_name(original_flag_id: str, new_flag_id: str, existing_flags):

    #query to get existing flag names
    if original_flag_id in existing_flags and original_flag_id is not None and new_flag_id is not None:
        # query to update existing flag_name with new flag_name
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="original flag  " + original_flag_id + " updated to " + new_flag_id,
                                                       uuid=new_flag_id + "_primary_key_id")
    else:
        if original_flag_id not in existing_flags:
            #return error to user that original_flag_name does not exist
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="original flag id: " + original_flag_id + " does not exist")
        if original_flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify name of original flag")
        if new_flag_id is None:
            #return error to user that original_flag_name and new_flag_name have to be specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify new flag name")
    return flag_schema_object

#Another call for flag logic
def update_flag_logic(flag_id, new_flag_logic: str, existing_flags):

    #check if primary_key is contained in existing flags
    #query to get existing flags or existing UUID, whichever is passed by user

    if flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify existing flag: " + flag_id)
    if flag_id in existing_flags:
        #run validation on new_flag_logic
        validation_results = validate_logic(flag_id, new_flag_logic)
        if validation_results.errors() is None and validation_results.mypy_errors is None:
            #query to update existing flag logic
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="logic for flag has been updated",
                                                           uuid=flag_id + "primary_key_id")
        else:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic")
    return flag_schema_object



#A call to delete a flag provided a UUID, return true/false
def delete_flag(flag_id, existing_flags):
    #check if primary_key exists in db
    if flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag name specified does not exist")
    else:
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag " + flag_id + " has been deleted",
                                                       uuid=flag_id + "_primary_key_id")
    return flag_schema_object


#A call to create a named flag group, returns a UUID, name cannot be empty if so error
def create_flag_group(flag_group_id: str, existing_flag_groups):
    if flag_group_id in existing_flag_groups:
        #flag group already exists, should update existing flag group
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group " + flag_group_id + " already exists")

    if flag_group_id is None or flag_group_id.replace(" ", "") == "":
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="unique flag group name must be created")
    else:
        #create flag group with unique Primary_key
        #insert statment here with
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="Unique flag group " + flag_group_id + " created",
                                                       uuid=flag_group_id + "_primary_key_id")
    return flag_schema_object


#A call to delete a flag group provided a UUID, return true/false
def delete_flag_group(flag_group_id: str, existing_flag_groups):
    #check that flag group exists in db


    if flag_group_id in existing_flag_groups:
        #query to delete entry from db via matching flag group name or uuid in try except for error hand

        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag group " + flag_group_id + " deleted from database",
                                                       uuid=flag_group_id + "_primary_key_id")

    else:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify flag group " + flag_group_id + " in database",
                                                       uuid=flag_group_id + "_primary_key_id")

    return flag_schema_object


#Flag Groups Updating, within these calls cyclic and existing flag name checks need to occur.
# They should both return validation information such describing possible errors
# in the group such as missing and cyclic flags

#A call to add flags to a group provided a UUID for the group and UUIDs for the flags to add
def add_flag_to_flag_group(flag_group_id: str, new_flags: [], existing_flags, existing_flag_groups):
    #for each new_flag in new_flags, check to see if flag exists already
    #if flag does not exist, call add method

    missing_flags = []
    #create default flag_logic_dictionary
    new_flag_logic = {}
    flag_errors = []

    #check that flag_group_name exists
    if flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="Flag Group Name does not exist",
                                                       uuid=flag_group_id+"_primary_key_id")
    for new_flag in new_flags:
        #query to get UUID for each new_flag
        if new_flag not in existing_flags:
            missing_flags.append(new_flag)
        if len(missing_flags) != 0:
            #return error message that flag must be created first before added to flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag (s) " + missing_flags + " do not exist")

        else:
            #run validation checks on flag and flag_logic
            #query db to get flag logic for each flag_name
            # query to get flag logic
            flag_logic = "flag_logic"
            new_flag_logic.setdefault(new_flag, flag_logic)

            #run validation on flag_logic
            flag_validation_result = validate_logic(new_flag, flag_logic)

            #if there are any errors, do not update flag_group
            if flag_validation_result.errors():
                flag_errors.append(flag_validation_result.errors())
            if flag_validation_result.mypy_errors():
                flag_errors.append(flag_validation_result.mypy_errors())

            if len(flag_errors) != 0:
                #errors in flags, do not update existing flag group
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="error in flag logic")
            else:
                #update existing flag group with UUID for each flag

                #return new flag_group UUID
                flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                               message="flag group " + flag_group_id + " has been updated with flag(s) " + new_flags,
                                                               uuid=flag_group_id + "_primary_key_id")
    return flag_schema_object





#A call to remove flags from a group provided a UUID for the group and UUIDs for the flags to remove
def remove_flag_from_flag_group(flag_group_id: str, del_flags: [], existing_flags, existing_flag_groups, flags_in_group):

    #check that flag_group_name exists
    if flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag_group " + flag_group_id + " does not exist")



    #flag group name does exist
    #for ech flag in del_flags, make sure flag exists in passed flag_group_name

    #only attempt to delete flags that exist in flag_group_name
    missing_flags = []
    flags_not_in_group = []
    for del_flag in del_flags:
        if del_flag not in existing_flags:
            missing_flags.append(del_flag)
        if del_flag not in flags_in_group:
            flags_not_in_group.append(del_flag)
    if len(missing_flags) != 0:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag(s) " + missing_flags + " do not exist")

    if len(flags_not_in_group) != 0:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag(s) " + flags_not_in_group + " do not exist in " + flag_group_name)

    if len(missing_flags) == 0 and len(flags_not_in_group) == 0:
        #delete flag from flag group

        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag(s) " + del_flags + " removed from " + flag_group_id,
                                                       uuid=flag_group_id + "_primary_key_id")

    return flag_schema_object






#A call to duplicate a flag provided a new name and UUID
def duplicate_flag(og_flag_id:str, new_flag_id: str, existing_flags):
    #check that original flag already exists
    if og_flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag " + og_flag_id + " does not exist")
    else:
        #make sure new name does not already exist
        if new_flag_id in existing_flags:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="new flag " + new_flag_id + " already exists")
        else:
            #create a new flag with new name
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="new flag " + new_flag_id + " based off of " + og_flag_id + " has been created",
                                                           uuid=new_flag_id + "_primary_key_id")
    return flag_schema_object


#A call to duplicate a flag group provided a new name and UUID
def duplicate_flag_group(og_flag_group_id: str, new_flag_group_id:str, existing_flag_groups):
    #make sure og_flag_group_name exists:

    #if df_of_flag_group:
        #query to insert copy with new name
        #cursor.execute("""INSERT INTO TABLE(PRIMARY_KEY, :new_flag_group_name, TABLE.EVERYTING_ELSE)
        #SELECT (TABLE.EVERYTHING_ELSE FROM TABLE WHERE FLAG_GROUP_NAME = :og_flag_group_name""",
        #og_flag_group_name=og_flag_group_name, new_flag_group_name=new_flag_group_name)

        #return new primary key to user for duplicated flag group

    #else:
        #return error message to user that og_flag_group does not exist


    return None





#TODO,
# write new tests in tests module