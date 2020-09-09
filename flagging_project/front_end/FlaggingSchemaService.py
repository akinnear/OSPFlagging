#imports
import pandas as pd

from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names
from flag_names.FlagGroupService import pull_flag_group_names
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation

#TODO
# interface design, html5 + bootstrap4

#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.

def validate_logic(flag_id:str, flag_logic_information:FlagLogicInformation()):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})

    #TODO
    # need flag_dependiceis from api call or direct query
    flag_dependencies = get_flag_dependencies()


    #TODO
    # perform full validation on user_logic via nodevisitor, mypy, and validation
    # mypy validation is part of full validation method, do not need explicit mypy validation call



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
     "Flag8": {},
     "Flag9": {"Flag10"},
     "Flag10": {"Flag9"}}
    return flag_dependencies

#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error

def create_flag(flag_id: str, flag_logic_information:FlagLogicInformation()):
    #store flag name and flag logic in db

    if flag_id is None:
        # return error message, no flag name specified
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag id not specified")

    else:

        #validate flag logic
        flag_validation = validate_logic(flag_id, flag_logic_information)
        if flag_validation.errors == {} and flag_validation.mypy_errors == {}:
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="new flag created",
                                                           uuid=flag_id + "_primary_key_id")
        else:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
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
def update_flag_logic(flag_id, new_flag_logic_information:FlagLogicInformation(), existing_flags):

    #check if primary_key is contained in existing flags
    #query to get existing flags or existing UUID, whichever is passed by user

    if flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify existing flag: " + flag_id)
    if flag_id in existing_flags:
        #run validation on new_flag_logic
        validation_results = validate_logic(flag_id, new_flag_logic_information)
        if validation_results.errors() == {} and validation_results.mypy_errors == {}:
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
def add_flag_to_flag_group(flag_group_id: str, new_flags:[], existing_flags: [], existing_flag_groups, flags_in_flag_group):
    #for each new_flag in new_flags, check to see if flag exists already
    #if flag does not exist, call add method

    missing_flags = []
    duplicate_flags = []
    validation_results = FlaggingValidationResults()

    #check that flag_group_name exists
    if flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag_group " + flag_group_id + " does not exist",
                                                       uuid=flag_group_id+"_primary_key_id")
    else:
        for new_flag in new_flags:
            #query to get UUID for each new_flag
            if new_flag not in existing_flags:
                missing_flags.append(new_flag)
            if new_flag in flags_in_flag_group:
                duplicate_flags.append(new_flag)

        if len(missing_flags) == 0 and len(duplicate_flags) == 0:
            flag_set = flags_in_flag_group + new_flags

            #need dummy dictionary
            ref_flag_dict = {}
            for flag in flag_set:
                ref_flag_dict[flag] = {CodeLocation(None, None)}

            flag_logic_information = FlagLogicInformation(referenced_flags=ref_flag_dict)
            validation_results = validate_logic("dummy_flag", flag_logic_information)


        if len(validation_results.errors) != 0:
            #errors in flags, do not update existing flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="cyclical flag detected: " + validation_results.errors,
                                                           uuid=flag_group_id + "_primary_key_id")

        elif len(missing_flags) != 0:
            # return error message that flag must be created first before added to flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, missing_flags)) + " do not exist",
                                                           uuid=flag_group_id + "_primary_key_id")

        elif len(duplicate_flags) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, duplicate_flags)) + " already exist in flag group",
                                                           uuid=flag_group_id + "_primary_key_id")

        else:
            #check that flag uuid does not already exist in flag_group


            #update existing flag group with UUID for each flag

            #return new flag_group UUID
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="flag group " + flag_group_id + " has been updated with flag(s) " + " ,".join(map(str, new_flags)),
                                                           uuid=flag_group_id + "_primary_key_id")


    return flag_schema_object





#A call to remove flags from a group provided a UUID for the group and UUIDs for the flags to remove
def remove_flag_from_flag_group(flag_group_id: str, del_flags: [], existing_flags, existing_flag_groups, flags_in_flag_group):

    #check that flag_group_name exists
    if flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag_group " + flag_group_id + " does not exist",
                                                       uuid=flag_group_id + "_primary_key_id")
    else:

        #flag group name does exist
        #for ech flag in del_flags, make sure flag exists in passed flag_group_name

        #only attempt to delete flags that exist in flag_group_name
        missing_flags = []
        flags_not_in_group = []
        for del_flag in del_flags:
            if del_flag not in existing_flags:
                missing_flags.append(del_flag)
            if del_flag not in flags_in_flag_group:
                flags_not_in_group.append(del_flag)
        if len(missing_flags) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, missing_flags)) + " do not exist",
                                                           uuid=flag_group_id + "_primary_key_id")

        elif len(flags_not_in_group) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, flags_not_in_group)) + " do not exist in " + flag_group_id,
                                                           uuid=flag_group_id + "_primary_key_id")

        else:
            #delete flag from flag group

            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="Flag(s) " + ", ".join(map(str, del_flags)) + " removed from " + flag_group_id,
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
    if og_flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group " + og_flag_group_id + " does not exist")

    #check that new_flag_group_id does not already exist
    if new_flag_group_id in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="new flag group " + new_flag_group_id + " already exists")

    if og_flag_group_id in existing_flag_groups and new_flag_group_id not in existing_flag_groups:
        #duplicate flag group
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag group " + new_flag_group_id + " created off of " + og_flag_group_id)

    return flag_schema_object



#TODO,
# write new tests in tests module