from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names
from flag_names.FlagGroupService import pull_flag_group_names
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flag_data.FlaggingMongo import FlaggingMongo
from front_end.FlaggingValidateLogic import validate_logic, validate_cyclical_logic
from flagging.FlagErrorInformation import FlagErrorInformation
from flagging.TypeValidationResults import TypeValidationResults
from flag_data.FlaggingColumnNames import flag_name_col_name, flag_logic_col_name, \
    referenced_flag_col_name, flag_status_col_name, flag_group_name_col_name, \
    flag_group_flags_col_name, flag_group_status_col_name, flag_dep_flag_id_col_name, \
    flag_dep_dep_flags_col_name, flag_dep_flag_group_id_col_name, flag_error_col_name, \
    flag_group_error_col_name
from front_end.TransferFlagLogicInformation import TransferFlagLogicInformation, _convert_FLI_to_TFLI, \
    _convert_TFLI_to_FLI
from bson.objectid import ObjectId
from front_end.ReferencedFlag import ReferencedFlag, _convert_RF_to_TRF


# def _make_fli_dictionary(fli):
#     fli_dict = {}
#     for attr, value in fli.__dict__.items():
#         if not attr.startswith("__"):
#             if attr == "validation_results":
#                 for attr_x, value_x in value.__dict__.items():
#                     if attr_x != "validation_results":
#                         fli_dict[attr_x] = str(value_x)
#             else:
#                 fli_dict[attr] = str(value)
#     return fli_dict


#FLAG
def get_all_flags(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flags(), 200

def get_all_flag_ids(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_ids(), 200

def get_specific_flag(flag_id, existing_flags: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag_id not specified")
            response_code = 401
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error coverting flag id to Object ID type")
            response_code = 406
    if flag_schema_object is None:
        flag_id_object = ObjectId(flag_id)
        specific_flag_id = flagging_mongo.get_specific_flag(flag_id_object)
        specific_flag_logic = flagging_mongo.get_flag_logic_information(flag_id_object)
        specific_flag_name = flagging_mongo.get_flag_name(flag_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message='found flag id',
                                                       uuid=str(specific_flag_id),
                                                       name=specific_flag_name,
                                                       logic=specific_flag_logic)
        response_code = 200
    return flag_schema_object, response_code

def create_flag(flag_name: str, flag_logic_information:FlagLogicInformation, flagging_mongo:FlaggingMongo):
    flag_schema_object = None
    #store flag name and flag logic in db

    #call databse to get id based on name


    if flag_schema_object is None:
        if flag_name is None:
            # return error message, no flag name specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag name not specified")
            response_code = 401
    if flag_schema_object is None:
        flag_validation = validate_logic(flag_name, flag_logic_information, flagging_mongo)
        if flag_validation.errors != {} or flag_validation.mypy_errors != {}:
            
            #test for transfer
            transfer_flag_logic_information = _convert_FLI_to_TFLI(flag_logic_information)
            test_flag = _convert_TFLI_to_FLI(transfer_flag_logic_information)
            add_flag_id = flagging_mongo.add_flag({flag_name_col_name: flag_name,
                                                   flag_logic_col_name: transfer_flag_logic_information,
                                                   referenced_flag_col_name: transfer_flag_logic_information["referenced_flags"],
                                                   flag_status_col_name: "DRAFT",
                                                   flag_error_col_name: "ERROR"})
            specific_flag_logic = flagging_mongo.get_flag_logic_information(add_flag_id)
            specific_flag_name = flagging_mongo.get_flag_name(add_flag_id)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           uuid=add_flag_id,
                                                           name=specific_flag_name,
                                                           logic=specific_flag_logic)
            response_code = 200
    if flag_schema_object is None:
        #TODO
        # create flag dependency set

        transfer_flag_logic_information = _convert_FLI_to_TFLI(flag_logic_information)
        add_flag_id = flagging_mongo.add_flag({flag_name_col_name: flag_name,
                                               flag_logic_col_name: transfer_flag_logic_information,
                                               referenced_flag_col_name: transfer_flag_logic_information["referenced_flags"],
                                               flag_status_col_name: "PRODUCTION_READY",
                                               flag_error_col_name: ""})
        specific_flag_logic = flagging_mongo.get_flag_logic_information(add_flag_id)
        specific_flag_name = flagging_mongo.get_flag_name(add_flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag created",
                                                       uuid=add_flag_id,
                                                       name=specific_flag_name,
                                                       logic=specific_flag_logic)
        response_code = 200
    return flag_schema_object, response_code

#A call to duplicate a flag provided a new name and UUID
def duplicate_flag(original_flag_id, existing_flags, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    #check that original flag already exists
    if original_flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag id must be specified")
        response_code = 401
    if flag_schema_object is None:
        try:
            if ObjectId(original_flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag " + str(
                                                                   original_flag_id) + " does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in duplicating flag: " + str(original_flag_id))
            response_code = 406
    if flag_schema_object is None:
        flag_id_object = ObjectId(original_flag_id)
        duplicated_flag_new_id = flagging_mongo.duplicate_flag(flag_id_object)
        specific_flag_logic = flagging_mongo.get_flag_logic_information(duplicated_flag_new_id)
        specific_flag_name = flagging_mongo.get_flag_name(duplicated_flag_new_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=str(original_flag_id) + " has be duplicated",
                                                       uuid=duplicated_flag_new_id,
                                                       name=specific_flag_name,
                                                       logic=specific_flag_logic)
        response_code = 200
    return flag_schema_object, response_code

#One call for flag name
def update_flag_name(original_flag_id: str, new_flag_name: str, existing_flags, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if original_flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify id of original flag")
        response_code = 401
    if flag_schema_object is None:
        if new_flag_name is None:
            # return error to user that original_flag_name and new_flag_name have to be specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify name of new flag")
            response_code = 404
    #query to get existing flag names
    if flag_schema_object is None:
        try:
            if ObjectId(original_flag_id) not in existing_flags:
                # return error to user that original_flag_name does not exist
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="original flag id " + str(original_flag_id) + " does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(original_flag_id) + " to object Id type")
            response_code = 406
    if flag_schema_object is None:
        flag_group_ids = flagging_mongo.get_flag_group_ids()
        flags_in_flag_group = dict()
        if len(flag_group_ids) > 0:
            for flag_group_id in flag_group_ids:
                flags_in_flag_group_schema, response_code_get_flags = get_flag_group_flags(str(flag_group_id), flag_group_ids, flagging_mongo)
                flags_in_flag_group_x = flags_in_flag_group_schema.logic
                if ObjectId(original_flag_id) in flags_in_flag_group_x:
                    flags_in_flag_group[flag_group_id] = flags_in_flag_group_x
            if len(flags_in_flag_group) > 1:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag id: " + original_flag_id + " can not be modified because it is contained in the following flag groups: " + ", ".join([str(x) for x in flags_in_flag_group.keys()]),
                                                               uuid=original_flag_id)
                response_code = 405
    if flag_schema_object is None:
        original_flag_id_object = ObjectId(original_flag_id)
        new_flag_id = flagging_mongo.update_flag(flag=original_flag_id_object, update_value=new_flag_name,
                                                 update_column="FLAG_NAME")
        specific_flag_logic = flagging_mongo.get_flag_logic_information(new_flag_id)
        specific_flag_name = flagging_mongo.get_flag_name(new_flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="original flag " + str(original_flag_id) + " has been renamed " + new_flag_name,
                                                       uuid=new_flag_id,
                                                       name=specific_flag_name,
                                                       logic=specific_flag_logic)
        response_code = 200
    return flag_schema_object, response_code

#Another call for flag logic
def update_flag_logic(flag_id, new_flag_logic_information:FlagLogicInformation(), existing_flags, flagging_mongo:FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify flag id")
            response_code = 401
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="could not identify existing flag " + flag_id)
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(flag_id) + " to object Id type")
            response_code = 401
    flag_group_ids = flagging_mongo.get_flag_group_ids()
    flags_in_flag_group = dict()
    if len(flag_group_ids) > 0:
        for flag_group_id in flag_group_ids:
            flags_in_flag_group_schema, response_code_get_flags = get_flag_group_flags(str(flag_group_id),
                                                                                       flag_group_ids, flagging_mongo)
            flags_in_flag_group_x = flags_in_flag_group_schema.logic
            if ObjectId(flag_id) in flags_in_flag_group_x:
                flags_in_flag_group[flag_group_id] = flags_in_flag_group_x
        if len(flags_in_flag_group) > 1:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id: " + flag_id + " can not be modified because it is contained in the following flag groups: " + ", ".join(
                                                               [str(x) for x in flags_in_flag_group.keys()]),
                                                           uuid=flag_id)
            response_code = 405

    if flag_schema_object is None:
        validation_results = validate_logic(flag_id, None, new_flag_logic_information, flagging_mongo)
        if validation_results.errors != {} or validation_results.mypy_errors != {}:
            new_transfer_flag_logic_information = _convert_FLI_to_TFLI(new_flag_logic_information)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id, update_value=new_transfer_flag_logic_information,
                                                         update_column=flag_logic_col_name)
            flag_id_object = ObjectId(flag_id)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="DRAFT",
                                                         update_column=flag_status_col_name)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="ERROR",
                                                         update_column=flag_group_error_col_name)
            specific_flag_name = flagging_mongo.get_flag_name(updated_flag_id)
            specific_flag_logic = flagging_mongo.get_flag_logic_information(updated_flag_id)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           uuid=updated_flag_id,
                                                           name=specific_flag_name,
                                                           logic=specific_flag_logic)
            response_code = 200
    if flag_schema_object is None:
        #TODO
        # update flag dependency set

        flag_id_object = ObjectId(flag_id)
        new_transfer_flag_logic_information = _convert_FLI_to_TFLI(new_flag_logic_information)
        updated_flag_id = flagging_mongo.update_flag(flag=flag_id,
                                                     update_value=new_transfer_flag_logic_information,
                                                     update_column=flag_logic_col_name)
        updated_flag_id = flagging_mongo.update_flag(flag=flag_id,
                                                     update_value="PRODUCTION_READY",
                                                     update_column=flag_status_col_name)
        updated_flag_id = flagging_mongo.update_flag(flag=flag_id,
                                                     update_value="",
                                                     update_column=flag_group_error_col_name)
        specific_flag_logic = flagging_mongo.get_flag_logic_information(updated_flag_id)
        specific_flag_name = flagging_mongo.get_flag_name(updated_flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="logic for flag " + str(
                                                           updated_flag_id) + " has been updated",
                                                       uuid=updated_flag_id,
                                                       name=specific_flag_name,
                                                       logic=specific_flag_logic)
        response_code = 200
    return flag_schema_object, response_code

#A call to delete a flag provided a UUID, return true/false
def delete_flag(flag_id, existing_flags, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag id")
        response_code = 401
    #check if primary_key exists in db
    if flag_schema_object is None:
        if ObjectId(flag_id) not in existing_flags:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id specified does not exist")
            response_code = 404
    if flag_schema_object is None:
        #TODO
        # delete flag from flag dependency set


        flag_id_object = ObjectId(flag_id)
        specific_flag_name = flagging_mongo.get_flag_name(flag_id_object)
        removed_flag = flagging_mongo.remove_flag(flag=flag_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=str(flag_id) + " has been deleted",
                                                       uuid=removed_flag,
                                                       name=specific_flag_name)
        response_code = 200
    return flag_schema_object, response_code

#A call to move a flag to production, must not have any errors
def move_flag_to_production(flag_id, existing_flags, flagging_mongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None or "":
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify flag id")
            response_code = 401
    if flag_schema_object is None:
        if ObjectId(flag_id) not in existing_flags:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id does not exist",
                                                           uuid=ObjectId(flag_id),
                                                           name=flagging_mongo.get_flag_name(ObjectId(flag_id)))
            response_code = 404

    if flag_schema_object is None:
        #only flags with no errors can be moved to production
        flag_error = flagging_mongo.get_specific_flag_error(ObjectId(flag_id))
        if flag_error != "":
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag can not be moved to production due to flag errors",
                                                           uuid=ObjectId(flag_id),
                                                           name=flagging_mongo.get_flag_name(ObjectId(flag_id)))

            response_code = 405
    if flag_schema_object is None:
        updated_flag_id = flagging_mongo.update_flag(flag=ObjectId(flag_id),
                                                     update_value="PRODUCTION",
                                                     update_column=flag_status_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag has been moved to production",
                                                       uuid=ObjectId(flag_id),
                                                       name=flagging_mongo.get_flag_name(ObjectId(flag_id)))

#FLAG_GROUP
#get flag_groups
def get_flag_groups(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_groups(), 200

def get_flag_group_ids(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_group_ids(), 200

def get_flag_group_names(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_group_names(), 200

def get_flag_names_in_flag_group(flag_group_id, flagging_mongo):
    return flagging_mongo.get_flag_names_from_flag_group(flag_group_id), 200

def get_flag_ids_in_flag_group(flag_group_id, flagging_mongo):
    return flagging_mongo.get_flag_group_flag(flag_group_id), 200

def get_flag_group_flags(flag_group_id, existing_flag_groups, flagging_mongo):
    flag_schema_object = None
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       messge="flag group id must be specified")
        response_code = 401
    if flag_schema_object is None:
        if ObjectId(flag_group_id) not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group does not exist",
                                                           uuid=flag_group_id)
            response_code = 404
    if flag_schema_object is None:
        flags_in_flag_group = flagging_mongo.get_flag_group_flag(ObjectId(flag_group_id))
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       logic=flags_in_flag_group,
                                                       message="return flags for flag group",
                                                       uuid=flag_group_id)
        response_code = 200
    return flag_schema_object, response_code

#get specific flag_group
def get_specific_flag_group(flag_group_id: str, existing_flag_groups: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group id must be specified")
        response_code = 401
    if flag_schema_object is None:
        if ObjectId(flag_group_id) not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group does not exist")
            response_code = 404
    if flag_schema_object is None:
        flag_group_id_object = ObjectId(flag_group_id)
        found_flag_group_id = flagging_mongo.get_specific_flag_group(flag_group_id_object)
        found_flag_group_name = flagging_mongo.get_flag_group_name(flag_group_id_object)
        flags_in_flag_group = flagging_mongo.get_flag_group_flag(flag_group_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="found flag group id",
                                                       uuid=found_flag_group_id,
                                                       name=found_flag_group_name,
                                                       logic=[str(x) for x in flags_in_flag_group])
        response_code = 200
    return flag_schema_object, response_code

#A call to create a named flag group, returns a UUID, name cannot be empty if so error
def create_flag_group(flag_group_name: str, existing_flag_groups, flagging_mongo: FlaggingMongo):
    if flag_group_name is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="unique flag group name must be specified")
        response_code = 401
    elif flag_group_name in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="new flag group name must be unique")
        response_code = 404
    else:
        new_flag_group_id = flagging_mongo.add_flag_group({flag_group_name_col_name: flag_group_name,
                                               flag_group_flags_col_name: dict(),
                                               flag_group_status_col_name: "PRODUCTION_READY"})
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="unique flag group " + flag_group_name + " created",
                                                       uuid=new_flag_group_id,
                                                       name=flag_group_name)
        response_code = 200
    return flag_schema_object, response_code

#A call to delete a flag group provided a UUID, return true/false
def delete_flag_group(flag_group_id, existing_flag_groups, flagging_mongo: FlaggingMongo):
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group name must be specified")
        response_code = 401
    elif ObjectId(flag_group_id) not in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify flag group " + flag_group_id + " in database")
        response_code = 404
    else:
        flag_group_id_object = ObjectId(flag_group_id)
        removed_flag_group = flagging_mongo.remove_flag_group(flag_group_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag group " + flag_group_id + " deleted from database",
                                                       uuid=removed_flag_group)
        response_code = 200
    return flag_schema_object, response_code

#Flag Groups Updating, within these calls cyclic and existing flag name checks need to occur.
# They should both return validation information such describing possible errors
# in the group such as missing and cyclic flags

#A call to add flags to a group provided a UUID for the group and UUIDs for the flags to add
def add_flag_to_flag_group(flag_group_id, new_flags: [], existing_flags: [], existing_flag_groups, flags_in_flag_group, flagging_mongo: FlaggingMongo):
    #for each new_flag in new_flags, check to see if flag exists already
    #if flag does not exist, call add method

    flag_schema_object = None
    validation_results = FlaggingValidationResults()

    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group must be specified")
        response_code = 401

    if flag_schema_object is None:
        if ObjectId(flag_group_id) not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag_group " + flag_group_id + " does not exist")
            response_code = 404

    #check that new flags is not empty
    if flag_schema_object is None:
        if len(new_flags) == 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="no new flags were specified")
            response_code = 404
        else:
            new_flags = list(dict.fromkeys(new_flags))
            # new_flags = [ObjectId(x) for x in new_flags]

    if flag_schema_object is None:
        missing_flags = []
        duplicate_flags = []
        for new_flag in [ObjectId(x) for x in new_flags]:
            #query to get UUID for each new_flag
            if new_flag not in existing_flags:
                missing_flags.append(new_flag)
            if new_flag in flags_in_flag_group:
                duplicate_flags.append(new_flag)

        if len(missing_flags) == 0 and len(duplicate_flags) == 0:
            flag_set = flags_in_flag_group + [new_flag]

            #CYCLICAL CHECK
            #need dummy dictionary
            ref_flag_dict = {}
            for flag in flag_set:
                ref_flag_dict[flag] = {CodeLocation(None, None)}

            referenced_flags_names = [x["name"] for x in flagging_mongo.get_flag_logic_information(new_flag)["referenced_flags"]]
            ref_flag_dict = {}
            for rf_name in referenced_flags_names:
                ref_flag_dict[rf_name] = {CodeLocation(None, None)}
            flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=ref_flag_dict)
            validation_results = validate_cyclical_logic(ObjectId(new_flags[0]),
                                                ObjectId(flag_group_id), flag_logic_cyclical_check, flagging_mongo)
            if len(validation_results.errors) != 0:
                cyclical_errors = []
                for k, v in validation_results.errors.items():
                    if isinstance(v, FlagErrorInformation):
                        cyclical_errors.append(k)
                if len(cyclical_errors) > 0:
                    if len(cyclical_errors) == 1:
                        flagging_message = "the following flag dependency resulted in cyclical dependencies: " + \
                                           str(cyclical_errors[0])
                    else:
                        flagging_message = "the following flag dependencies resulted in cyclical dependencies: " + (
                            ", ".join(str(x) for x in cyclical_errors))
                    full_flag_set = new_flags + list(dict.fromkeys(existing_flags))
                    flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                                 update_value=full_flag_set,
                                                                                 update_column="FLAGS_IN_GROUP")
                    flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                                   message=flagging_message,
                                                                   uuid=flag_with_updated_deps_id)
                    response_code = 401

        elif len(missing_flags) != 0:
            # return error message that flag must be created first before added to flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, missing_flags)) + " do not exist")
            response_code = 401

        elif len(duplicate_flags) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, duplicate_flags)) + " already exist in flag group")
            response_code = 401

        if flag_schema_object is None:
            #get names of flags in flag group
            #get name of flag being added
            flag_names_in_flag_group = flagging_mongo.get_flag_names_from_flag_group(ObjectId(flag_group_id))
            flag_name_being_added = flagging_mongo.get_flag_name(ObjectId(new_flags[0]))
            found_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(flag_group_id))
            if flag_name_being_added in flag_names_in_flag_group:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag: " + str(new_flags[0]) + " with name: " + flag_name_being_added + " already exists in flag group: " + str(flag_group_id),
                                                               uuid=flag_group_id,
                                                               name=found_flag_group_name)
                response_code = 404

        if flag_schema_object is None:
            #create full valid flag logic information object
            flag_status = flagging_mongo.get_flag_status(ObjectId(new_flags[0]))
            if flag_status == "DRAFT":

                #flag dependency check here
                ref_flag_dict = {}
                for flag in flag_set:
                    ref_flag_dict[flag] = {CodeLocation(None, None)}

                referenced_flags_names = [x["name"] for x in
                                          flagging_mongo.get_flag_logic_information(new_flag)["referenced_flags"]]
                ref_flag_dict = {}
                for rf_name in referenced_flags_names:
                    ref_flag_dict[rf_name] = {CodeLocation(None, None)}
                flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=ref_flag_dict)
                validation_results = validate_cyclical_logic(ObjectId(new_flags[0]),
                                                    ObjectId(flag_group_id), flag_logic_cyclical_check, flagging_mongo)
                flagging_message = ""
                if len(validation_results.errors) != 0:
                    cyclical_errors = []
                    for k, v in validation_results.errors.items():
                        if isinstance(v, FlagErrorInformation):
                            cyclical_errors.append(k)
                    if len(cyclical_errors) > 0:
                        if len(cyclical_errors) == 1:
                            flagging_message = "the following flag dependency resulted in cyclical dependencies: " + \
                                               str(cyclical_errors[0])
                        else:
                            flagging_message = "the following flag dependencies resulted in cyclical dependencies: " + (
                                ", ".join(str(x) for x in cyclical_errors))
                        # full_flag_set = new_flags + list(dict.fromkeys(existing_flags))
                        # flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                        #                                                              update_value=full_flag_set,
                        #                                                              update_column="FLAGS_IN_GROUP")
                        # flag_schema_object = FlaggingSchemaInformation(valid=False,
                        #                                                message=flagging_message,
                        #                                                uuid=flag_with_updated_deps_id)
                        # response_code = 401

                #

                # create flag dependency data based on flag_names + flag group id
                existing_flag_ids, rc = get_all_flag_ids(flagging_mongo)
                flag_schema_object, fli_rc = get_specific_flag(flag_id=new_flags[0],
                                                                   existing_flags=existing_flag_ids,
                                                                   flagging_mongo=flagging_mongo)
                if len(flag_schema_object.logic["referenced_flags"]) > 0:
                    referenced_flag_names_in_flag_id = [x["name"] for x in flag_schema_object.logic["referenced_flags"]]
                    referenced_flags = []
                    for x in referenced_flag_names_in_flag_id:
                        referenced_flags.append(ReferencedFlag(flag_name=x, flag_group_id=ObjectId(flag_group_id)))

                    flag_ids, firc = get_all_flag_ids(flagging_mongo)
                    existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)
                    flag_name = flagging_mongo.get_flag_name(ObjectId(new_flags[0]))
                    if ObjectId(new_flags[0]) not in existing_flag_dep_keys:
                        flag_schema_object_flag_dep, fdi_rc = create_flag_dependency(flag_id=new_flags[0],
                                                                            flag_name=flag_name,
                                                                            flag_group_id=flag_group_id,
                                                                            existing_flag_ids=flag_ids,
                                                                     existing_flag_dep_keys=existing_flag_dep_keys,
                                                                     flag_dependencies=[], flagging_mongo=flagging_mongo)
                        flag_dep_id = flag_schema_object.uuid
                        existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)


                    else:
                        flag_dep_id = FlaggingMongo.get_specific_flag_dep_id_by_flag_id(ObjectId(new_flags[0]))

                    updated_flag_dep_id, ufdirc = add_dependencies_to_flag(flag_dep_id=str(flag_dep_id),
                                                                           existing_flag_dep_keys=existing_flag_dep_keys,
                                                                           new_dependencies=referenced_flags,
                                                                           flagging_mongo=flagging_mongo)

                full_flag_set = new_flags + list(dict.fromkeys(flags_in_flag_group))
                full_flag_set = [ObjectId(x) for x in full_flag_set]
                found_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(flag_group_id))
                flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value=full_flag_set,
                                                                             update_column="FLAGS_IN_GROUP")
                flag_group_set_to_draft = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value="DRAFT",
                                                                             update_column=flag_group_status_col_name)
                flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                               message="flag: " + str(new_flags[0]) + " is in DRAFT status but was added to flag group: " + str(flag_group_id) + "\n" + flagging_message,
                                                               uuid=str(flag_group_id))
                response_code = 200

        if flag_schema_object is None:
            # flag dependency check here
            ref_flag_dict = {}
            for flag in flag_set:
                ref_flag_dict[flag] = {CodeLocation(None, None)}

            referenced_flags_names = [x["name"] for x in
                                      flagging_mongo.get_flag_logic_information(new_flag)["referenced_flags"]]
            ref_flag_dict = {}
            for rf_name in referenced_flags_names:
                ref_flag_dict[rf_name] = {CodeLocation(None, None)}
            flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=ref_flag_dict)
            validation_results = validate_cyclical_logic(ObjectId(new_flags[0]),
                                                ObjectId(flag_group_id), flag_logic_cyclical_check, flagging_mongo)
            flagging_message = ""
            if len(validation_results.errors) != 0:
                cyclical_errors = []
                for k, v in validation_results.errors.items():
                    if isinstance(v, FlagErrorInformation):
                        cyclical_errors.append(k)
                if len(cyclical_errors) > 0:
                    if len(cyclical_errors) == 1:
                        flagging_message = "the following flag dependency resulted in cyclical dependencies: " + \
                                           str(cyclical_errors[0])
                    else:
                        flagging_message = "the following flag dependencies resulted in cyclical dependencies: " + (
                            ", ".join(str(x) for x in cyclical_errors))
            flag_schema_object, fli_rc = get_specific_flag(flag_id=ObjectId(new_flags[0]), existing_flags = get_all_flag_ids(flagging_mongo), flagging_mongo=flagging_mongo)
            referenced_flag_names_in_flag_id = flag_schema_object.logic.referenced_flags.keys()
            referenced_flags = []
            for x in referenced_flag_names_in_flag_id:
                referenced_flags.append(ReferencedFlag(flag_name=x, flag_group_id=ObjectId(flag_group_id)))

            flag_ids, firc = get_all_flag_ids(flagging_mongo)
            existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)
            flag_name = flagging_mongo.get_flag_name(ObjectId(new_flags[0]))
            if ObjectId(new_flags[0]) not in existing_flag_dep_keys:
                flag_dep_id, fdi_rc = create_flag_dependency(flag_id=new_flags[0],
                                                             flag_name=flag_name,
                                                             flag_group_id=flag_group_id,
                                                             existing_flag_ids=flag_ids, existing_flag_dep_keys=existing_flag_dep_keys, flag_dependencies=[], flagging_mongo=flagging_mongo)



            updated_flag_dep_id, ufdirc = add_dependencies_to_flag(flag_dep_id=flag_dep_id, existing_flag_dep_keys=existing_flag_dep_keys, new_dependencies=referenced_flags, flagging_mongo=flagging_mongo)

            full_flag_set = new_flags + list(dict.fromkeys(flags_in_flag_group))
            full_flag_set = [ObjectId(x) for x in full_flag_set]
            found_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(flag_group_id))
            flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id), update_value=full_flag_set, update_column="FLAGS_IN_GROUP")
            if len(cyclical_errors) > 0:
                flag_group_set_to_draft = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value="DRAFT",
                                                                             update_column=flag_group_status_col_name)
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="flag group " + flag_group_id + " has been updated with flag(s) " + (", ".join(map(str, new_flags))) + "\n" + flagging_message,
                                                           uuid=flag_with_updated_deps_id,
                                                           name=found_flag_group_name)
            response_code = 200
    return flag_schema_object, response_code

#A call to remove flags from a group provided a UUID for the group and UUIDs for the flags to remove
def remove_flag_from_flag_group(flag_group_id, del_flags: [], existing_flags: [], existing_flag_groups: [], flags_in_flag_group:[], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_group_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group not specified")
            response_code = 401
    #check that flag_group_name exists
    if flag_schema_object is None:
        if ObjectId(flag_group_id) not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group does not exist")
            response_code = 404

    if flag_schema_object is None:
        if len(del_flags) == 0 or del_flags is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="no flags to remove were specified")
            response_code = 401
    if flag_schema_object is None:
        #for each flag to remove from group,
        #make sure the flag exists and is part of flag group
        missing_flags = []
        flags_not_in_group = []
        del_flags = [ObjectId(x) for x in del_flags]
        for del_flag in del_flags:
            if del_flag not in existing_flags:
                missing_flags.append(del_flag)
            if del_flag not in flags_in_flag_group:
                flags_not_in_group.append(del_flag)
        if len(missing_flags) > 0:
            if len(missing_flags) == 1:
                flag_message = "the following flag does not exist: " + missing_flags[0]
            else:
                flag_message = "the following flags do not exists: " + (", ".join(missing_flags))
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flag_message)
            response_code = 401
        if flag_schema_object is None and len(flags_not_in_group) > 0:
            if len(flags_not_in_group) == 0:
                flag_message = "the following flag is not part of flag group " + flag_group_id + ": " + str(flags_not_in_group[0])
            else:
                flag_message = "the following flags are not part of flag group " + flag_group_id + ": " + (", ".join([str(x) for x in flags_not_in_group]))
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flag_message)
            response_code = 401

    if flag_schema_object is None:
        #TODO
        # update flag dependency data for flag being removed
        #get flag_id being removed
        for flag_id in del_flags:
            flagging_mongo.remove_specific_flag_dependencies_via_flag_id(flag_id, ObjectId(flag_group_id))






        new_flag_set = (list(list(set(del_flags)-set(flags_in_flag_group)) + list(set(flags_in_flag_group)-set(del_flags))))
        new_flag_set = [ObjectId(x) for x in new_flag_set]
        #method to remove flag(s) from flag group
        flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                     update_value=new_flag_set,
                                                                     update_column="FLAGS_IN_GROUP")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="Flag(s) " + ", ".join(map(str, del_flags)) + " removed from " + flag_group_id,
                                                       uuid=flag_with_updated_deps_id)
        response_code = 200
    return flag_schema_object, response_code

#A call to duplicate a flag group provided a new name and UUID
def duplicate_flag_group(original_flag_group_id: str, existing_flag_groups, new_flag_group_name, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    #make sure ids are past
    if original_flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag group id")
        response_code = 401
    #make sure og_flag_group_name exists
    if flag_schema_object is None:
        if ObjectId(original_flag_group_id) not in existing_flag_groups:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group " + str(original_flag_group_id) + " does not exist")
            response_code = 404
    if flag_schema_object is None:
        original_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(original_flag_group_id))
        if original_flag_group_name == new_flag_group_name:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="can not duplicate flag group " + original_flag_group_id + " must be given a unique name",
                                                           uuid=original_flag_group_id,
                                                           name=original_flag_group_name)
            response_code = 403

    if flag_schema_object is None:
        #get new id
        new_flag_group_id = flagging_mongo.duplicate_flag_group(ObjectId(original_flag_group_id))
        #edit new flag group to have new name passed
        new_flag_group_id = flagging_mongo.update_flag_group(ObjectId(new_flag_group_id), new_flag_group_name, flag_group_name_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag group " + str(new_flag_group_id)+ " created off of " + str(original_flag_group_id),
                                                       uuid=new_flag_group_id,
                                                       name=new_flag_group_name)
        response_code = 200
    return flag_schema_object, response_code

#FLAG DEPENDENCY
#get flag dependenceis
def get_flag_dependencies(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_dependencies(), 200

#get specifi flag depedency
def get_specific_flag_dependency(flag_id, existing_flag_deps: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id not specified")
            response_code = 400
    if flag_schema_object is None:
        if flag_id not in existing_flag_deps:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="could not identify dependencies for flag")
            response_code = 404
    if flag_schema_object is None:
        flag_dep_id = flagging_mongo.get_specific_flag_dependency(flag_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="identified flag dependencies",
                                                       uuid=flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code

#get all flag dep ids
def get_flag_dep_ids(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_dependencies_ids(), 200

#call to create flag dependnecy
def create_flag_dependency(flag_id: str, flag_name:str, flag_group_id, existing_flag_ids: [], existing_flag_dep_keys: [], flag_dependencies: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id not specified")
            response_code = 400

    #make sure flag exists
    if flag_schema_object is None:
        if ObjectId(flag_id) not in existing_flag_ids:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag: " + flag_id + " must be created first")
            response_code = 405

    #make sure flag dependency entry does not already exist, if exist, need to update
    if flag_schema_object is None:
        if ObjectId(flag_id) in existing_flag_dep_keys:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dependencies for flag " + flag_id + " already exist")
            response_code = 405
    if flag_schema_object is None:
        #creat new flag dependency entry based on passed flag and flag_dependencies
        new_flag_dependency_id = flagging_mongo.add_flag_dependencies({flag_dep_flag_id_col_name: ObjectId(flag_id),
                                                                       flag_name_col_name: flag_name,
                                                                       flag_dep_flag_group_id_col_name: ObjectId(flag_group_id),
                                                                       flag_dep_dep_flags_col_name: []})
        #add specific depdencies to new entry
        updated_flag_dependency_id = flagging_mongo.add_specific_flag_dependencies(new_flag_dependency_id, flag_dependencies, flag_dep_dep_flags_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag dependency data for flag " + flag_id + " has been created",
                                                       uuid=new_flag_dependency_id)
        response_code = 200
    return flag_schema_object, response_code

#call to delete flag dependnecy
def delete_flag_dependency(flag_id, existing_flag_dep_set: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id not specified")
            response_code = 400
    if flag_schema_object is None:
        if ObjectId(flag_id) not in existing_flag_dep_set:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dependencies for flag " + flag_id + " do not exist")
            response_code = 404
    if flag_schema_object is None:
        #remove flag from depedency set
        removed_flag_dep_id = flagging_mongo.remove_flag_dependencies(ObjectId(flag_id))
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag " + flag_id + "has been removed from flag dependency database",
                                                       uuid=removed_flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code

#call to add deps to flag dependencies set
def add_dependencies_to_flag(flag_dep_id, existing_flag_dep_keys: [], new_dependencies: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_dep_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep id not specified")
            response_code = 400
    if flag_schema_object is None:
        if ObjectId(flag_dep_id) not in existing_flag_dep_keys:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag_dep does not exist in flag dependency database")
            response_code = 404
    # if flag_schema_object is None:
    #     existing_flags = flagging_mongo.get_flag_ids()
    #     missing_flags = []
    #     for flag_x in new_dependencies:
    #         if flag_x not in existing_flags:
    #             missing_flags.append(flag_x)
    #     if len(missing_flags) != 0:
    #         flag_schema_object = FlaggingSchemaInformation(valid=False,
    #                                                        message="flag(s): " + ", ".join([str(x) for x in missing_flags]) + " do not exist")
    #         response_code = 404
    if flag_schema_object is None:
        new_dependencies = _convert_RF_to_TRF(new_dependencies)
        updated_flag_dep_id = flagging_mongo.add_specific_flag_dependencies(ObjectId(flag_dep_id), new_dependencies, "DEPENDENT_FLAGS")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="dependencies have been updated",
                                                       uuid=updated_flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code

#call to remove dependencies from flag
def remove_dependencies_from_flag(flag_dep_id, existing_flag_dep_keys: [], rm_dependencies: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_dep_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep id not specified")
            response_code = 400
    if flag_schema_object is None:
        if ObjectId(flag_dep_id) not in existing_flag_dep_keys:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep does not exist in flag dependency database")
            response_code = 404
    # if flag_schema_object is None:
    #     existing_flag_dep_flags = flagging_mongo.get_specific_flag_dependency_flags(ObjectId(flag_dep_id))
    #     missing_flags = []
    #     for flag_x in rm_dependencies:
    #         if flag_x not in existing_flag_dep_flags:
    #             missing_flags.append(flag_x)
    #     if len(missing_flags) != 0:
    #         flag_schema_object = FlaggingSchemaInformation(valid=False,
    #                                                        message="flag(s): " + ", ".join([str(x) for x in missing_flags]) + " not current flag dependents")
    #         response_code = 404
    if flag_schema_object is None:
        rm_dependencies = _convert_RF_to_TRF(rm_dependencies)
        updated_flag_dep_id = flagging_mongo.remove_specific_flag_dependencies(ObjectId(flag_dep_id), rm_dependencies, "DEPENDENT_FLAGS")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="dependencies have been updated",
                                                       uuid=updated_flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code






