from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names
from flag_names.FlagGroupService import pull_flag_group_names
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flag_data.FlaggingMongo import FlaggingMongo
from front_end.FlaggingValidateLogic import validate_logic




#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error

def create_flag(flag_name: str, flag_logic_information:FlagLogicInformation, flagging_mongo:FlaggingMongo):
    #store flag name and flag logic in db

    #call databse to get id based on name

    if flag_name is None:
        # return error message, no flag name specified
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag name not specified")

    else:

        add_flag_id = flagging_mongo.add_flag({"flag_name": flag_name,
                                 "flag_logic_information": flag_logic_information})

        #validate flag logic
        flag_validation = validate_logic(flag_name, flag_logic_information)
        if flag_validation.errors == {} and flag_validation.mypy_errors == {}:
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="new flag created",
                                                           uuid=add_flag_id)


        else:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           uuid=add_flag_id)
    return flag_schema_object



#A call to save changes to a flag, this will take in the change and a UUID
#One call for flag name
def update_flag_name(original_flag_id: str, new_flag_name: str, existing_flags, flagging_mongo: FlaggingMongo):
    if original_flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify id of original flag")
    elif new_flag_name is None:
        # return error to user that original_flag_name and new_flag_name have to be specified
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify name of new flag")
    #query to get existing flag names
    else:
        if original_flag_id in existing_flags:
            new_flag_id = flagging_mongo.update_flag(flag=original_flag_id, update_value=new_flag_name, update_column="FLAG_NAME")
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="original flag " + original_flag_id + " has been renamed " + new_flag_name,
                                                           uuid=new_flag_id)
        else:
            if original_flag_id not in existing_flags:
                #return error to user that original_flag_name does not exist
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="original flag id " + original_flag_id + " does not exist",
                                                               uuid=original_flag_id)
    return flag_schema_object

#Another call for flag logic
def update_flag_logic(flag_id, new_flag_logic_information:FlagLogicInformation(), existing_flags, flagging_mongo:FlaggingMongo):

    if flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag id")
    elif flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify existing flag " + flag_id,
                                                       uuid=flag_id)
    else:
        #run validation on new_flag_logic
        validation_results = validate_logic(flag_id, new_flag_logic_information)
        if validation_results.errors == {} and validation_results.mypy_errors == {}:
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id, update_value=new_flag_logic_information,
                                                     update_column="FLAG_LOGIC_INFORMATION")
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="logic for flag " + str(updated_flag_id)+ " has been updated",
                                                           uuid=updated_flag_id)
        else:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           uuid=flag_id)
    return flag_schema_object



#A call to delete a flag provided a UUID, return true/false
def delete_flag(flag_id, existing_flags, flagging_mongo: FlaggingMongo):
    if flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag id")
    #check if primary_key exists in db
    elif flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag id specified does not exist")
    else:
        removed_flag = flagging_mongo.remove_flag(flag=flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=flag_id + " has been deleted",
                                                       uuid=removed_flag)
    return flag_schema_object


#A call to create a named flag group, returns a UUID, name cannot be empty if so error
def create_flag_group(flag_group_name: str, existing_flag_groups, flagging_mongo: FlaggingMongo):
    if flag_group_name is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="unique flag group name must be specified")
    elif flag_group_name in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="new flag group name must be unique")
    else:
        new_flag_group_id = flagging_mongo.add_flag_group(flag_group_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="unique flag group " + flag_group_name + " created",
                                                       uuid=new_flag_group_id)
    return flag_schema_object


#A call to delete a flag group provided a UUID, return true/false
def delete_flag_group(flag_group_name: str, existing_flag_groups, flagging_mongo: FlaggingMongo):
    if flag_group_name is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group name must be specified")
    elif flag_group_name not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify flag group " + flag_group_name + " in database")
    else:
        removed_flag_group = flagging_mongo.remove_flag_group(flag_group_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag group " + flag_group_name + " deleted from database",
                                                       uuid=removed_flag_group)
    return flag_schema_object


#Flag Groups Updating, within these calls cyclic and existing flag name checks need to occur.
# They should both return validation information such describing possible errors
# in the group such as missing and cyclic flags

#A call to add flags to a group provided a UUID for the group and UUIDs for the flags to add
def add_flag_to_flag_group(flag_group_name: str, new_flags: [], existing_flags: [], existing_flag_groups, flags_in_flag_group, flagging_mongo: FlaggingMongo):
    #for each new_flag in new_flags, check to see if flag exists already
    #if flag does not exist, call add method

    flag_schema_object = None
    validation_results = FlaggingValidationResults()

    if flag_group_name is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group must be specified")

    if flag_schema_object is None:
        if flag_group_name not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag_group " + flag_group_name + " does not exist")

    #check that new flags is not empty
    if flag_schema_object is None:
        if len(new_flags) == 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="no new flags were detected")
        else:
            new_flags = list(dict.fromkeys(new_flags))

    if flag_schema_object is None:
        missing_flags = []
        duplicate_flags = []
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

            #perform cyclical flag check with flags in group and flags attempted to be added to group

            flag_logic_information = FlagLogicInformation(referenced_flags=ref_flag_dict)
            validation_results = validate_logic("dummy_flag", flag_logic_information)


        if len(validation_results.errors) != 0:
            #errors in flags, do not update existing flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="cyclical flag detected: " + validation_results.errors)

        elif len(missing_flags) != 0:
            # return error message that flag must be created first before added to flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, missing_flags)) + " do not exist")

        elif len(duplicate_flags) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, duplicate_flags)) + " already exist in flag group")

        else:
            full_flag_set = new_flags + list(dict.fromkeys(existing_flags))
            flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=flag_group_name, update_value=full_flag_set, update_column="FLAGS_IN_GROUP")
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="flag group " + flag_group_name + " has been updated with flag(s) " + " ,".join(map(str, new_flags)),
                                                           uuid=flag_with_updated_deps_id)
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
            #TODO
            # delete flag from flag group

            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="Flag(s) " + ", ".join(map(str, del_flags)) + " removed from " + flag_group_id,
                                                           uuid=flag_group_id + "_primary_key_id")

    return flag_schema_object



#A call to duplicate a flag provided a new name and UUID
def duplicate_flag(original_flag_id:str, existing_flags, flagging_mongo: FlaggingMongo):
    #check that original flag already exists
    if original_flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag id must be specified")
    elif original_flag_id not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag " + original_flag_id + " does not exist")
    else:
        duplicated_flag_new_id = flagging_mongo.duplicate_flag(original_flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=original_flag_id + " has be duplicated",
                                                       uuid=duplicated_flag_new_id)
    return flag_schema_object


#A call to duplicate a flag group provided a new name and UUID
def duplicate_flag_group(original_flag_group_id: str, existing_flag_groups, flagging_mongo: FlaggingMongo):
    #make sure ids are past
    if original_flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag group id")

    #make sure og_flag_group_name exists:
    elif original_flag_group_id not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group " + original_flag_group_id + " does not exist")

    else:
        #get new id
        new_flag_group_id = flagging_mongo.duplicate_flag_group(original_flag_group_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag group " + new_flag_group_id + " created off of " + original_flag_group_id,
                                                       uuid=new_flag_group_id)

    return flag_schema_object



