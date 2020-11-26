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
from front_end.TransferFlagLogicInformation import TransferFlagLogicInformation, _convert_FLI_to_TFLI
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
                                                           message="flag_id not specified",
                                                           simple_message="flag id not specified")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag: " + flag_id + " does not exist",
                                                               simple_message="flag does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting flag id to Object ID type",
                                                           simple_message="error converting flag id to Object ID type")
            response_code = 400
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

    if flag_schema_object is None:
        if flag_name is None:
            # return error message, no flag name specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag name not specified",
                                                           simple_message="flag name not specified")
            response_code = 400
    if flag_schema_object is None:
        flag_validation = validate_logic(flag_name, flag_logic_information, flagging_mongo)
        if flag_validation.errors != {} or flag_validation.mypy_errors != {}:
            
            #test for transfer
            transfer_flag_logic_information = _convert_FLI_to_TFLI(flag_logic_information)
            add_flag_id = flagging_mongo.add_flag({flag_name_col_name: flag_name,
                                                   flag_logic_col_name: transfer_flag_logic_information,
                                                   referenced_flag_col_name: transfer_flag_logic_information["referenced_flags"],
                                                   flag_status_col_name: "DRAFT",
                                                   flag_error_col_name: "ERROR"})
            specific_flag_logic = flagging_mongo.get_flag_logic_information(add_flag_id)
            specific_flag_name = flagging_mongo.get_flag_name(add_flag_id)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           simple_message="error in flag logic",
                                                           uuid=add_flag_id,
                                                           name=specific_flag_name,
                                                           logic=specific_flag_logic)
            response_code = 200
    if flag_schema_object is None:
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
                                                       simple_message="new flag created",
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
                                                       message="flag id must be specified",
                                                       simple_message="flag id must be specified")
        response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(original_flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag " + str(
                                                                   original_flag_id) + " does not exist",
                                                               simple_message="flag does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in duplicating flag: " + str(original_flag_id),
                                                           simple_message="error in duplicating flag")
            response_code = 400
    if flag_schema_object is None:
        flag_id_object = ObjectId(original_flag_id)
        duplicated_flag_new_id = flagging_mongo.duplicate_flag(flag_id_object)
        specific_flag_logic = flagging_mongo.get_flag_logic_information(duplicated_flag_new_id)
        specific_flag_name = flagging_mongo.get_flag_name(duplicated_flag_new_id)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=str(original_flag_id) + " has be duplicated",
                                                       simple_message="flag has been duplicated",
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
                                                       message="user must specify id of original flag",
                                                       simple_message="missing flag id")
        response_code = 400
    if flag_schema_object is None:
        if new_flag_name is None:
            # return error to user that original_flag_name and new_flag_name have to be specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify name of new flag",
                                                           simple_message="missing new flag name")
            response_code = 404
    #query to get existing flag names
    if flag_schema_object is None:
        try:
            if ObjectId(original_flag_id) not in existing_flags:
                # return error to user that original_flag_name does not exist
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="original flag id " + str(original_flag_id) + " does not exist",
                                                               simple_message="flag id does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(original_flag_id) + " to object Id type",
                                                           simple_message="error updating flag name")
            response_code = 400
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
                                                               simple_message="flag can not be modified",
                                                               uuid=original_flag_id)
                response_code = 405
    if flag_schema_object is None:
        og_flag_name = flagging_mongo.get_flag_name(ObjectId(original_flag_id))
        if og_flag_name == new_flag_name:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag id: " + original_flag_id + " with name: " + og_flag_name + " must be given a new unique name",
                                                           simple_message="new flag name must be different than original flag name",
                                                           name=og_flag_name,
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
                                                       simple_message="flag has been renamed",
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
                                                           message="user must specify flag id",
                                                           simple_message="user must specify flag id")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag id " + str(flag_id) + " does not exist",
                                                               simple_message="flag id does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(flag_id) + " to object Id type",
                                                           simple_message="error in updating flag logic")
            response_code = 400
    if flag_schema_object is None:
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
                                                               simple_message="flag logic can not be modified",
                                                               uuid=flag_id)
                response_code = 405

    if flag_schema_object is None:
        validation_results = validate_logic(flag_id, new_flag_logic_information, flagging_mongo)
        if validation_results.errors != {} or validation_results.mypy_errors != {}:
            #check if flag is part of flag group
            flag_group_ids = flagging_mongo.get_flag_group_ids()
            flag_in_flag_group_bool = False
            if len(flag_group_ids) > 0:
                for flag_group_idx in flag_group_ids:
                    flags_in_flag_group_idx = flagging_mongo.get_flag_group_flag(flag_group_idx)
                    if ObjectId(flag_id) in flags_in_flag_group_x:
                        flag_in_flag_group_bool = True
                        flag_group_id = flag_group_idx
                        # delete previous dep entry
                        flagging_mongo.remove_specific_flag_dependencies_via_flag_id_and_flag_group_id(ObjectId(flag_id),ObjectId(flag_group_id))

            if flag_in_flag_group_bool:
                #create new entry flag dep entry for flag_id in flag_group_id
                flag_name = flagging_mongo.get_flag_name(ObjectId(flag_group_id))
                flag_ids = flagging_mongo.get_flag_ids()
                existing_flag_dep_keys = flagging_mongo.get_flag_dependencies_ids()
                flag_schema_object_flag_dep, fdi_rc = create_flag_dependency(flag_id=flag_id,
                                                                             flag_name=flag_name,
                                                                             flag_group_id=flag_group_id,
                                                                             existing_flag_ids=flag_ids,
                                                                             existing_flag_dep_keys=existing_flag_dep_keys,
                                                                             flag_dependencies=[],
                                                                             flagging_mongo=flagging_mongo)

                #add new referenced flags to flag dependeny entry
                #check for cyclical errors
                flag_set = flagging_mongo.get_flag_group_flag()
                ref_flag_dict = {}
                for flag in flag_set:
                    ref_flag_dict[flag] = {CodeLocation(None, None)}
                referenced_flags_names = [x["name"] for x in flagging_mongo.get_flag_logic_information(ObjectId(flag_id))]
                ref_flag_dict = {}
                for rf_name in referenced_flags_names:
                    ref_flag_dict[rf_name] = {CodeLocation(None, None)}
                flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=ref_flag_dict)
                validation_results = validate_cyclical_logic(ObjectId(flag_id), flag_group_id, flag_logic_cyclical_check, flagging_mongo)
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
                        #update flag group that flag is part of with cyclcial error
                        flagging_mongo.update_flag_group(ObjectId(flag_group_id), "CYCLICAL ERROR", flag_group_error_col_name)

                # get referenced flags from flag logic information, only have to do if flag in flag group
                if len(new_flag_logic_information.referenced_flags) > 0:
                    referenced_flags_names_in_flag_id = [x for x in new_flag_logic_information.referenced_flags]
                    referenced_flags = []
                    for x in referenced_flags_names_in_flag_id:
                        referenced_flags.append(ReferencedFlag(flag_name=x, flag_group_id=flag_group_id))

                    #update existing flag dep keys
                    existing_flag_dep_keys = flagging_mongo.get_flag_dependencies_ids()
                    updated_flag_dep_id, ufdi_rc = add_dependencies_to_flag(flag_dep_id=str(flag_schema_object_flag_dep.uuid),
                                                                               existing_flag_dep_keys=existing_flag_dep_keys,
                                                                               new_dependencies=referenced_flags,
                                                                               flagging_mongo=flagging_mongo)

            #update flag
            new_transfer_flag_logic_information = _convert_FLI_to_TFLI(new_flag_logic_information)
            flag_id_object = ObjectId(flag_id)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object, update_value=new_transfer_flag_logic_information,
                                                         update_column=flag_logic_col_name)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="DRAFT",
                                                         update_column=flag_status_col_name)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="ERROR",
                                                         update_column=flag_error_col_name)
            specific_flag_name = flagging_mongo.get_flag_name(updated_flag_id)
            specific_flag_logic = flagging_mongo.get_flag_logic_information(updated_flag_id)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic",
                                                           simple_message="new logic updated but has errors",
                                                           uuid=updated_flag_id,
                                                           name=specific_flag_name,
                                                           logic=specific_flag_logic)
            response_code = 200
        else:
            # check if flag is part of flag group
            flag_group_ids = flagging_mongo.get_flag_group_ids()
            flag_in_flag_group_bool = False
            if len(flag_group_ids) > 0:
                for flag_group_idx in flag_group_ids:
                    flags_in_flag_group_idx = flagging_mongo.get_flag_group_flag(flag_group_idx)
                    if ObjectId(flag_id) in flags_in_flag_group_x:
                        flag_in_flag_group_bool = True
                        flag_group_id = flag_group_idx
                        # delete previous dep entry
                        flagging_mongo.remove_specific_flag_dependencies_via_flag_id_and_flag_group_id(ObjectId(flag_id),ObjectId(flag_group_id))

            if flag_in_flag_group_bool:
                # create new entry flag dep entry for flag_id in flag_group_id
                flag_name = flagging_mongo.get_flag_name(ObjectId(flag_group_id))
                flag_ids = flagging_mongo.get_flag_ids()
                existing_flag_dep_keys = flagging_mongo.get_flag_dependencies_ids()
                flag_schema_object_flag_dep, fdi_rc = create_flag_dependency(flag_id=flag_id,
                                                                             flag_name=flag_name,
                                                                             flag_group_id=flag_group_id,
                                                                             existing_flag_ids=flag_ids,
                                                                             existing_flag_dep_keys=existing_flag_dep_keys,
                                                                             flag_dependencies=[],
                                                                             flagging_mongo=flagging_mongo)

                # add new referenced flags to flag dependeny entry
                # check for cyclical errors
                flag_set = flagging_mongo.get_flag_group_flag()
                ref_flag_dict = {}
                for flag in flag_set:
                    ref_flag_dict[flag] = {CodeLocation(None, None)}
                referenced_flags_names = [x["name"] for x in
                                          flagging_mongo.get_flag_logic_information(ObjectId(flag_id))]
                ref_flag_dict = {}
                for rf_name in referenced_flags_names:
                    ref_flag_dict[rf_name] = {CodeLocation(None, None)}
                flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=ref_flag_dict)
                validation_results = validate_cyclical_logic(ObjectId(flag_id), flag_group_id,
                                                             flag_logic_cyclical_check, flagging_mongo)
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
                        # update flag group that flag is part of with cyclcial error
                        flagging_mongo.update_flag_group(ObjectId(flag_group_id), "CYCLICAL ERROR",
                                                         flag_group_error_col_name)

                # get referenced flags from flag logic information
                if len(new_flag_logic_information.referenced_flags) > 0:
                    referenced_flags_names_in_flag_id = [x for x in new_flag_logic_information.referenced_flags]
                    referenced_flags = []
                    for x in referenced_flags_names_in_flag_id:
                        referenced_flags.append(ReferencedFlag(flag_name=x, flag_group_id=flag_group_id))

                    # update existing flag dep keys
                    existing_flag_dep_keys = flagging_mongo.get_flag_dependencies_ids()
                    updated_flag_dep_id, ufdi_rc = add_dependencies_to_flag(
                        flag_dep_id=str(flag_schema_object_flag_dep.uuid),
                        existing_flag_dep_keys=existing_flag_dep_keys,
                        new_dependencies=referenced_flags,
                        flagging_mongo=flagging_mongo)

            # update flag
            new_transfer_flag_logic_information = _convert_FLI_to_TFLI(new_flag_logic_information)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id, update_value=new_transfer_flag_logic_information,
                                                         update_column=flag_logic_col_name)
            flag_id_object = ObjectId(flag_id)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="PRODUCTION READY",
                                                         update_column=flag_status_col_name)
            updated_flag_id = flagging_mongo.update_flag(flag=flag_id_object,
                                                         update_value="",
                                                         update_column=flag_error_col_name)
            specific_flag_logic = flagging_mongo.get_flag_logic_information(updated_flag_id)
            specific_flag_name = flagging_mongo.get_flag_name(updated_flag_id)
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="logic for flag " + str(
                                                               updated_flag_id) + " has been updated",
                                                           simple_message="flag logic has been updated",
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
                                                       message="user must specify flag id",
                                                       simple_message="missing flag id")
        response_code = 400
    #check if primary_key exists in db
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag id specified does not exist",
                                                               simple_message="flag id does not exist")
                response_code = 404
        except Exception as e:
            print(e)
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(
                                                               flag_id) + " to object Id type",
                                                           simple_message="error in deleting flag")
            response_code = 400


    if flag_schema_object is None:
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
                                                               simple_message="flag can not be deleted",
                                                               uuid=flag_id)
                response_code = 405
    if flag_schema_object is None:
        #delete flag from flag dependency set
        flag_schema_object_flag_dep, fsofd_rc = delete_flag_dependency(flag_id=flag_id,
                                                                       flag_group_id=None,
                                                                       flagging_mongo=flagging_mongo)
        flag_id_object = ObjectId(flag_id)
        specific_flag_name = flagging_mongo.get_flag_name(flag_id_object)
        removed_flag = flagging_mongo.remove_flag(flag=flag_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message=str(flag_id) + " has been deleted",
                                                       simple_message="flag has been deleted",
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
                                                           message="user must specify flag id",
                                                           simple_message="user must specifiy flag id")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_id) not in existing_flags:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag id: " + flag_id + " does not exist",
                                                               simple_message="flag id does not exist",
                                                               uuid=ObjectId(flag_id),
                                                               name=None)
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error converting: " + str(
                                                               flag_id) + " to object Id type",
                                                           simple_message="error moving flag to production")
            response_code = 400

    if flag_schema_object is None:
        #only flags with no errors can be moved to production
        flag_error = flagging_mongo.get_specific_flag_error(ObjectId(flag_id))
        if flag_error != "":
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag can not be moved to production due to flag errors",
                                                           simple_message="flag can not be moved to production due to flag errors",
                                                           uuid=ObjectId(flag_id),
                                                           name=flagging_mongo.get_flag_name(ObjectId(flag_id)))

            response_code = 405
    if flag_schema_object is None:
        updated_flag_id = flagging_mongo.update_flag(flag=ObjectId(flag_id),
                                                     update_value="PRODUCTION",
                                                     update_column=flag_status_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag has been moved to production",
                                                       simple_message="flag has been moved to production",
                                                       uuid=ObjectId(flag_id),
                                                       name=flagging_mongo.get_flag_name(ObjectId(flag_id)))
        response_code = 200
    return flag_schema_object, response_code

#A call to delete all
def delete_all_flags(flagging_mongo):
    flagging_mongo.delete_all_flags()
    flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                   message="all flags have been deleted",
                                                   simple_message="all flags have been deleted")
    return flag_schema_object, 200

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

# def get_flag_ids_in_flag_group(flag_group_id, flagging_mongo):
#     return flagging_mongo.get_flag_group_flag(flag_group_id), 200

def get_flag_group_flags(flag_group_id, existing_flag_groups, flagging_mongo):
    flag_schema_object = None
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group id must be specified",
                                                       simple_message="flag group id must be specified")
        response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag group does not exist",
                                                               simple_message="flag group does not exist",
                                                               uuid=ObjectId(flag_group_id))
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in getting flags for flag group " + flag_group_id,
                                                           simple_message="error pulling flags for flag group")
            response_code = 400
    if flag_schema_object is None:
        flags_in_flag_group = flagging_mongo.get_flag_group_flag(ObjectId(flag_group_id))
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       logic=flags_in_flag_group,
                                                       message="return flags for flag group" + flag_group_id,
                                                       simple_message="return flags for flag group",
                                                       uuid=ObjectId(flag_group_id),
                                                       name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
        response_code = 200
    return flag_schema_object, response_code

#get specific flag_group
def get_specific_flag_group(flag_group_id: str, existing_flag_groups: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group id must be specified",
                                                       simple_message="flag group id must be specified")
        response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag group does not exist",
                                                               simple_message="flag group does not exist")
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error pull flag group " + flag_group_id,
                                                           simple_message="invalid flag group id type")
            response_code = 400
    if flag_schema_object is None:
        flag_group_id_object = ObjectId(flag_group_id)
        found_flag_group_id = flagging_mongo.get_specific_flag_group(flag_group_id_object)
        found_flag_group_name = flagging_mongo.get_flag_group_name(flag_group_id_object)
        flags_in_flag_group = flagging_mongo.get_flag_group_flag(flag_group_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="found flag group id",
                                                       simple_message="flag flag group id",
                                                       uuid=found_flag_group_id,
                                                       name=found_flag_group_name,
                                                       logic=[str(x) for x in flags_in_flag_group])
        response_code = 200
    return flag_schema_object, response_code

#A call to create a named flag group, returns a UUID, name cannot be empty if so error
def create_flag_group(flag_group_name: str, existing_flag_groups, flagging_mongo: FlaggingMongo):
    if flag_group_name is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="unique flag group name must be specified",
                                                       simple_message="missing flag group name")
        response_code = 400
    elif flag_group_name in existing_flag_groups:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="new flag group name must be unique",
                                                       simple_message="new flag group name must be unique")
        response_code = 404
    else:
        new_flag_group_id = flagging_mongo.add_flag_group({flag_group_name_col_name: flag_group_name,
                                               flag_group_flags_col_name: dict(),
                                               flag_group_status_col_name: "PRODUCTION_READY",
                                                           flag_group_error_col_name: ""})
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="unique flag group " + flag_group_name + " created",
                                                       simple_message="new flag group created",
                                                       uuid=new_flag_group_id,
                                                       name=flag_group_name)
        response_code = 200
    return flag_schema_object, response_code

#A call to delete a flag group provided a UUID, return true/false
def delete_flag_group(flag_group_id, existing_flag_groups, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag group name must be specified",
                                                       simple_message="flag group name must be specified")
        response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="could not identify flag group " + flag_group_id + " in database",
                                                               simple_message="could not identify flag group",
                                                               uuid=ObjectId(flag_group_id))
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="could not identify flag group " + flag_group_id + " to delete",
                                                           simple_message="error deleting flag group, invalid id type")
            response_code = 400
    if flag_schema_object is None:
        #remove flag deps for group
        flag_schema_object_flag_dep, fsofd_rc = delete_flag_dependency(flag_id=None,
                                                                       flag_group_id=flag_group_id,
                                                                       flagging_mongo=flagging_mongo)
        flag_group_id_object = ObjectId(flag_group_id)
        removed_flag_group = flagging_mongo.remove_flag_group(flag_group_id_object)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag group " + flag_group_id + " deleted from database",
                                                       simple_message="flag group has been deleted",
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
                                                       message="flag group must be specified",
                                                       simple_message="flag group must be specified")
        response_code = 400

    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag_group " + flag_group_id + " does not exist",
                                                               simple_message="flag group does not exist")

                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error adding flag to flag group " + flag_group_id + ".  Error converting to ObjectId type",
                                                           simple_message="error converting flag group id to ObjectId type")
            response_code = 400

    #check that new flags is not empty
    if flag_schema_object is None:
        if len(new_flags) == 0 or new_flags == [None]:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="no new flags were specified",
                                                           simple_message="missing flags to add to flag group")
            response_code = 404
        else:
            new_flags = list(dict.fromkeys(new_flags))
            # new_flags = [ObjectId(x) for x in new_flags]

    if flag_schema_object is None:
        #make sure flag id is valid
        try:
            test_new_flags = [ObjectId(x) for x in new_flags]
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error adding flag to flag group" + flag_group_id + ", error converting flag id to ObjectId type",
                                                           simple_message="error adding flag to flag group",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 400
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
                    flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                                 update_value=flag_group_error_col_name,
                                                                                 update_column="CYCLICAL FLAG ERROR")
                    flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                                   message=flagging_message,
                                                                   simple_message="flags in flag group has been updated",
                                                                   uuid=flag_with_updated_deps_id,
                                                                   name=flagging_mongo.get_flag_group_name(flag_with_updated_deps_id))
                    response_code = 200

        elif len(missing_flags) != 0:
            # return error message that flag must be created first before added to flag group
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, missing_flags)) + " do not exist",
                                                           simple_message="flag does not exist",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 404

        elif len(duplicate_flags) != 0:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="Flag(s) " + ", ".join(map(str, duplicate_flags)) + " already exist in flag group",
                                                           simple_message='flag already in flag group',
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 405

        if flag_schema_object is None:
            #get names of flags in flag group
            #get name of flag being added
            flag_names_in_flag_group = flagging_mongo.get_flag_names_from_flag_group(ObjectId(flag_group_id))
            flag_name_being_added = flagging_mongo.get_flag_name(ObjectId(new_flags[0]))
            found_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(flag_group_id))
            if flag_name_being_added in flag_names_in_flag_group:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag: " + str(new_flags[0]) + " with name: " + flag_name_being_added + " already exists in flag group: " + flag_group_id,
                                                               simple_message="flag already exists in flag group",
                                                               uuid=ObjectId(flag_group_id),
                                                               name=found_flag_group_name)
                response_code = 405

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
                        # response_code = 400

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
                    flag_dep_id = flagging_mongo.get_specific_flag_dep_id_by_flag_id_and_flag_group_id(ObjectId(new_flags[0]), ObjectId(flag_group_id))
                    if flag_dep_id is None:
                        flag_schema_object_flag_dep, fdi_rc = create_flag_dependency(flag_id=new_flags[0],
                                                                            flag_name=flag_name,
                                                                            flag_group_id=flag_group_id,
                                                                            existing_flag_ids=flag_ids,
                                                                     existing_flag_dep_keys=existing_flag_dep_keys,
                                                                     flag_dependencies=[], flagging_mongo=flagging_mongo)
                        flag_dep_id = flag_schema_object_flag_dep.uuid
                        existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)


                    else:
                        flag_dep_id = flagging_mongo.get_specific_flag_dep_id_by_flag_id_and_flag_group_id(ObjectId(new_flags[0]), ObjectId(flag_group_id))["_id"]
                        existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)
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
                                                               simple_message="flag added to flag group",
                                                               name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)),
                                                               uuid=ObjectId(flag_group_id))
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
            else:
                cyclical_errors = []
            flag_spec_schema_object, fli_rc = get_specific_flag(flag_id=ObjectId(new_flags[0]), existing_flags=existing_flags, flagging_mongo=flagging_mongo)
            referenced_flag_names_in_flag_id = flag_spec_schema_object.logic['referenced_flags']
            referenced_flags = []
            for x in referenced_flag_names_in_flag_id:
                referenced_flags.append(ReferencedFlag(flag_name=x, flag_group_id=ObjectId(flag_group_id)))

            flag_ids, firc = get_all_flag_ids(flagging_mongo)
            existing_flag_dep_keys, efdkrc = get_flag_dep_ids(flagging_mongo)
            flag_name = flagging_mongo.get_flag_name(ObjectId(new_flags[0]))
            if ObjectId(new_flags[0]) not in existing_flag_dep_keys:
                flag_dep_schema_object, fdi_rc = create_flag_dependency(flag_id=new_flags[0],
                                                             flag_name=flag_name,
                                                             flag_group_id=flag_group_id,
                                                             existing_flag_ids=flag_ids, existing_flag_dep_keys=existing_flag_dep_keys, flag_dependencies=[], flagging_mongo=flagging_mongo)



            updated_flag_dep_id, ufdirc = add_dependencies_to_flag(flag_dep_id=str(flag_dep_schema_object.uuid), existing_flag_dep_keys=existing_flag_dep_keys, new_dependencies=referenced_flags, flagging_mongo=flagging_mongo)

            full_flag_set = new_flags + list(dict.fromkeys(flags_in_flag_group))
            full_flag_set = [ObjectId(x) for x in full_flag_set]
            found_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(flag_group_id))
            flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id), update_value=full_flag_set, update_column="FLAGS_IN_GROUP")
            if len(cyclical_errors) > 0:
                flag_group_set_to_draft = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value="DRAFT",
                                                                             update_column=flag_group_status_col_name)
                flag_group_set_to_draft = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                           update_value="CYCLICAL FLAG ERROR",
                                                                           update_column=flag_group_error_col_name)
                flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                               message="flag group " + flag_group_id + " has been updated with flag(s) " + (
                                                                   ", ".join(
                                                                       map(str, new_flags))) + "\n" + flagging_message,
                                                               simple_message="flags added to flag group",
                                                               uuid=flag_with_updated_deps_id,
                                                               name=found_flag_group_name)
                response_code = 200
        if flag_schema_object is None:
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="flag group " + flag_group_id + " has been updated with flag(s) " + (
                                                               ", ".join(map(str, new_flags))) + "\n" + flagging_message,
                                                           simple_message="flags added to flag group",
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
                                                           message="flag group not specified",
                                                           simple_message="flag group not specified")
            response_code = 400
    #check that flag_group_name exists
    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag group does not exist",
                                                               simple_message="flag group does not exist")
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error removing flag from flag group, error converting flag group id " + flag_group_id + " to ObjectId type",
                                                           simple_message="error removing flag from flag group")
            response_code = 400

    if flag_schema_object is None:
        if len(del_flags) == 0 or del_flags is None or del_flags == [None]:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="no flags to remove were specified",
                                                           simple_message="missing flags to remove from flag group")
            response_code = 400

    #verify flag id is object id compatible
    try:
        test_flags = [ObjectId(x) for x in del_flags]
    except Exception as e:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="error removing flag " + del_flags[0] + " from flag group " + flag_group_id + ", error converting flag id to proper ObjectId type",
                                                       simple_message="error removing flag from flag group")
        response_code = 405


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
            missing_flags = [str(x) for x in missing_flags]
            if len(missing_flags) == 1:
                flag_message = "the following flag does not exist: " + missing_flags[0]
            else:
                flag_message = "the following flags do not exists: " + (", ".join(missing_flags))
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flag_message,
                                                           simple_message="error removing flags from flag group",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 405
        if flag_schema_object is None and len(flags_not_in_group) > 0:
            if len(flags_not_in_group) == 0:
                flag_message = "the following flag is not part of flag group " + flag_group_id + ": " + str(flags_not_in_group[0])
            else:
                flag_message = "the following flags are not part of flag group " + flag_group_id + ": " + (", ".join([str(x) for x in flags_not_in_group]))
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flag_message,
                                                           simple_message="error removing flags from flag group",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 405

    if flag_schema_object is None:
        #get flag_id being removed
        for flag_id in del_flags:
            flag_schema_object_flag_dep, fsofd_rc = delete_flag_dependency(flag_id=str(del_flags[0]), flag_group_id=flag_group_id, flagging_mongo=flagging_mongo)
            flagging_mongo.remove_specific_flag_dependencies_via_flag_id_and_flag_group_id(flag_id, ObjectId(flag_group_id))

        new_flag_set = (list(list(set(del_flags)-set(flags_in_flag_group)) + list(set(flags_in_flag_group)-set(del_flags))))
        new_flag_set = [ObjectId(x) for x in new_flag_set]
        #method to remove flag(s) from flag group
        flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                     update_value=new_flag_set,
                                                                     update_column="FLAGS_IN_GROUP")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="Flag(s) " + ", ".join(map(str, del_flags)) + " removed from " + flag_group_id,
                                                       simple_message="flags removed from flag group",
                                                       name=flagging_mongo.get_flag_group_name(flag_with_updated_deps_id),
                                                       uuid=flag_with_updated_deps_id)

        #check if new flag set contains any cyclical flag errors
        # flag dependency check here
        flag_logic_cyclical_check = FlagLogicInformation(referenced_flags=set())
        validation_results = validate_cyclical_logic(None,
                                                     ObjectId(flag_group_id), flag_logic_cyclical_check, flagging_mongo)
        flagging_message = ""
        if len(validation_results.errors) != 0:
            cyclical_errors = []
            for k, v in validation_results.errors.items():
                if isinstance(v, FlagErrorInformation):
                    cyclical_errors.append(k)
            if len(cyclical_errors) > 0:
                flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value="CYCLICAL FLAG ERRORS",
                                                                             update_column=flag_group_error_col_name)
            else:
                flag_with_updated_deps_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                             update_value="",
                                                                             update_column="flag_group_error_col_name")

        response_code = 200

    return flag_schema_object, response_code

#A call to duplicate a flag group provided a new name and UUID
def duplicate_flag_group(original_flag_group_id: str, existing_flag_groups, new_flag_group_name, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    #make sure ids are past
    if original_flag_group_id is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="user must specify flag group id",
                                                       simple_message="user must specify flag group")
        response_code = 400
    #make sure og_flag_group_name exists
    if flag_schema_object is None:
        try:
            if ObjectId(original_flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag group " + str(original_flag_group_id) + " does not exist",
                                                               simple_message="flag group does not exist")
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error duplicating flag group " + original_flag_group_id + ", error converting flag group id to proper OjbectId type",
                                                           simple_message="error duplicating flag group")
            response_code = 400

    if flag_schema_object is None:
        if new_flag_group_name is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error duplicating flag group " + original_flag_group_id + ", missing new flag group name",
                                                           simple_message="error duplicating flag group",
                                                           uuid=ObjectId(original_flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(original_flag_group_id)))
            response_code = 400
    if flag_schema_object is None:
        original_flag_group_name = flagging_mongo.get_flag_group_name(ObjectId(original_flag_group_id))
        if original_flag_group_name == new_flag_group_name:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="can not duplicate flag group " + original_flag_group_id + " must be given a unique name",
                                                           simple_message="new name for flag group must be unique",
                                                           uuid=original_flag_group_id,
                                                           name=original_flag_group_name)
            response_code = 405

    if flag_schema_object is None:
        #get new id
        new_flag_group_id = flagging_mongo.duplicate_flag_group(ObjectId(original_flag_group_id))
        #edit new flag group to have new name passed
        new_flag_group_id = flagging_mongo.update_flag_group(ObjectId(new_flag_group_id), new_flag_group_name, flag_group_name_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag group " + str(new_flag_group_id)+ " created off of " + str(original_flag_group_id),
                                                       simple_message="new flag group created",
                                                       uuid=new_flag_group_id,
                                                       name=new_flag_group_name)
        response_code = 200
    return flag_schema_object, response_code

#move flag group to production
def move_flag_group_to_production(flag_group_id, existing_flag_groups, flagging_mongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_group_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group id must be specified",
                                                           simple_message="flag id must be specified")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_group_id) not in existing_flag_groups:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag group does not exist",
                                                               simple_message="flag group does not exists",
                                                               uuid=ObjectId(flag_group_id))
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error moving flag group " + flag_group_id + " to production, error converting flag group id to proper ObjectId type",
                                                           simple_message="error moving flag group to production")
            response_code = 400
    if flag_schema_object is None:
        if flagging_mongo.get_flag_group_errors(ObjectId(flag_group_id)) != "":
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group can not be moved to production due to errors in flag group",
                                                           simple_message="flag group can not be moved to production due to errors in flag group",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 405
    if flag_schema_object is None:
        flag_error_bool = False
        for flag in flagging_mongo.get_flag_group_flag(ObjectId(flag_group_id)):
            if flagging_mongo.get_specific_flag_error(flag) != "":
                flag_error_bool = True
        if flag_error_bool:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag group " + flag_group_id + " can not be moved to production due to errors in flags found in flag group",
                                                           simple_message="flag group can not be moved to production due to error in flag in flag group",
                                                           uuid=ObjectId(flag_group_id),
                                                           name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))
            response_code = 405
    if flag_schema_object is None:
        updated_flag_group_id = flagging_mongo.update_flag_group(flag_group=ObjectId(flag_group_id),
                                                                 update_value="PRODUCTION",
                                                                 update_column=flag_group_status_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag group has been moved to production",
                                                       simple_message="flag group has been moved to production",
                                                       uuid=ObjectId(flag_group_id),
                                                       name=flagging_mongo.get_flag_group_name(ObjectId(flag_group_id)))

        response_code = 200
    return flag_schema_object, response_code

#A call to delete all flag groups
def delete_all_flag_groups(flagging_mongo):
    flagging_mongo.delete_all_flag_groups()
    flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                   message="all flag groups have been deleted",
                                                   simple_message="all flag groups have been deleted")
    return flag_schema_object, 200



#FLAG DEPENDENCY
#get flag dependenceis
def get_flag_dependencies(flagging_mongo: FlaggingMongo):
    return flagging_mongo.get_flag_dependencies(), 200

#get specifi flag depedency
def get_specific_flag_dependency(flag_dep_id, existing_flag_deps: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_dep_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep id not specified",
                                                           simple_mesage="flag dep id not specified")
            response_code = 400
    if flag_schema_object is None:
        if ObjectId(flag_dep_id) not in existing_flag_deps:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="could not identify dependencies for flag",
                                                           simple_message="flag dep id does not exist",
                                                           uuid=ObjectId(flag_dep_id))
            response_code = 400
    if flag_schema_object is None:
        flag_dep_id = flagging_mongo.get_specific_flag_dependency(ObjectId(flag_dep_id))
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="identified flag dependencies",
                                                       simple_message="identified flag dependencies",
                                                       uuid=ObjectId(flag_dep_id))
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
                                                           message="flag id not specified",
                                                           simple_message="flag id not specified")
            response_code = 400

    #make sure flag exists
    if flag_schema_object is None:
        if ObjectId(flag_id) not in existing_flag_ids:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag: " + flag_id + " must be created first",
                                                           simple_message="flag does not exist",
                                                           uuid=ObjectId(flag_id))
            response_code = 405

    #make sure flag dependency entry does not already exist, if exist, need to update
    if flag_schema_object is None:
        flag_dep_entry = flagging_mongo.get_specific_flag_dep_id_by_flag_id_and_flag_group_id(flag_id=ObjectId(flag_id), flag_group_id=ObjectId(flag_group_id))
        try:
            flag_dep_id = flag_dep_entry["_id"]
            if flag_dep_id in existing_flag_dep_keys:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag dependencies for flag " + flag_id + " in flag group " + flag_group_id + " already exist",
                                                               simple_message="flag dep entry already exists",
                                                               uuid=flag_dep_id,
                                                               name="flag name: " + flag_name + ", flag group id: " + flag_group_id)
                response_code = 405
        except Exception as e:
            print(e)
    if flag_schema_object is None:
        #creat new flag dependency entry based on passed flag and flag_dependencies
        new_flag_dependency_id = flagging_mongo.add_flag_dependencies({flag_dep_flag_id_col_name: ObjectId(flag_id),
                                                                       flag_name_col_name: flag_name,
                                                                       flag_dep_flag_group_id_col_name: ObjectId(flag_group_id),
                                                                       flag_dep_dep_flags_col_name: []})
        #add specific depdencies to new entry
        updated_flag_dependency_id = flagging_mongo.add_specific_flag_dependencies(new_flag_dependency_id, [], flag_dep_dep_flags_col_name)
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag dependency data for flag " + flag_id + " in flag group " + flag_group_id + " has been created",
                                                       simple_message="flag dependency entry created",
                                                       uuid=new_flag_dependency_id,
                                                       name="flag name: " + flag_name + ", flag group id: " + flag_group_id)
        response_code = 200
    return flag_schema_object, response_code

#call to delete flag dependnecy
def delete_flag_dependency(flag_id, flag_group_id, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_id is None and flag_group_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="missing flag id and flag group id",
                                                           simple_message="missing flag id and flag group id")
            response_code = 400
    if flag_schema_object is None:
        if flag_id is None:
            #make sure entries for flag group id
            flag_dep_ids = flagging_mongo.get_flag_dep_by_flag_group_id(ObjectId(flag_group_id))
            if len(flag_dep_ids) == 0:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="could not find any flag dep entries based on flag group: " + flag_group_id,
                                                               simple_message="no flag dep entries found")
                response_code = 400
            else:
                removed_flag_dep_ids = flagging_mongo.remove_specific_flag_dependencies_via_flag_group_id(ObjectId(flag_group_id))
                flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                               message="the following flag dep entries based on flag group id: " + flag_group_id + " have been removed" + ", ".join([str(x) for x in removed_flag_dep_ids]),
                                                               simple_message="flag dep entries removed")
                response_code = 200
    if flag_schema_object is None:
        if flag_group_id is None:
            flag_dep_ids = flagging_mongo.get_flag_dep_by_flag_id(ObjectId(flag_id))
            if len(flag_dep_ids) == 0:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="could not find any flag dep entries based on flag id: " + flag_id,
                                                               simple_message="no flag dep entries found")
                response_code = 400
            else:
                removed_flag_dep_ids = flagging_mongo.remove_specific_flag_dependencies_via_flag_id(ObjectId(flag_id))
                flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                               message="the following flag dep entries based on flag id: " + flag_id + " have been removed" + ", ".join([str(x) for x in removed_flag_dep_ids]),
                                                               simple_message="flag dep entries removed")
                response_code = 200
    if flag_schema_object is None:
        flag_dep_entry = flagging_mongo.get_specific_flag_dep_id_by_flag_id_and_flag_group_id(flag_id=ObjectId(flag_id), flag_group_id=ObjectId(flag_group_id))
        try:
            flag_dep_id = flag_dep_entry["_id"]
            flagging_mongo.remove_flag_dependencies(flag_dep_id)
            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="flag dep id: " + str(flag_dep_id) + " based on flag id: " + flag_id + " and flag group id: " + flag_group_id + " has been removed",
                                                           simple_message="flag dep has been removed")
            response_code = 200

        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep entry could not be found based on flag id: " + flag_id + " and flag group id: " + flag_group_id,
                                                           simple_message="flag dep entry could not be found")
            response_code = 400

    # if flag_schema_object is None:
    #     removed_flag_dep_id = flagging_mongo.remove_flag_dependencies(flag_dep_id)
    #     flag_schema_object = FlaggingSchemaInformation(valid=True,
    #                                                    message="flag " + str(removed_flag_dep_id) + "has been removed from flag dependency database",
    #                                                    uuid=removed_flag_dep_id,
    #                                                    name="flag_id: ")
    #     response_code = 200


    return flag_schema_object, response_code

#call to add deps to flag dependencies set
def add_dependencies_to_flag(flag_dep_id, existing_flag_dep_keys: [], new_dependencies: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_dep_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep id not specified",
                                                           simple_message="flag dep id not specified")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_dep_id) not in existing_flag_dep_keys:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag dep does not exist in flag dependency database",
                                                               simple_message="flag dep does not exist in flag dependency database")
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in add dependencies to flag, improper flag dep id, " + flag_dep_id,
                                                           simple_message="error in add dependency to flag")
            response_code = 400
    # if flag_schema_object is None:
    #     existing_flags = flagging_mongo.get_flag_ids()
    #     missing_flags = []
    #     for flag_x in new_dependencies:
    #         if flag_x not in existing_flags:
    #             missing_flags.append(flag_x)
    #     if len(missing_flags) != 0:
    #         flag_schema_object = FlaggingSchemaInformation(valid=False,
    #                                                        message="flag(s): " + ", ".join([str(x) for x in missing_flags]) + " do not exist")
    #         response_code = 400
    if flag_schema_object is None:
        new_dependencies = _convert_RF_to_TRF(new_dependencies)
        updated_flag_dep_id = flagging_mongo.add_specific_flag_dependencies(ObjectId(flag_dep_id), new_dependencies, "DEPENDENT_FLAGS")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="dependencies have been updated",
                                                       simple_message="dependencies have been updated",
                                                       uuid=updated_flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code

#call to remove dependencies from flag
def remove_dependencies_from_flag(flag_dep_id, existing_flag_dep_keys: [], rm_dependencies: [], flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    if flag_schema_object is None:
        if flag_dep_id is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="flag dep id not specified",
                                                           simple_message="flag dep id not specified")
            response_code = 400
    if flag_schema_object is None:
        try:
            if ObjectId(flag_dep_id) not in existing_flag_dep_keys:
                flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                               message="flag dep does not exist in flag dependency database",
                                                               simple_message="flag des does not exist in flag dependency database")
                response_code = 404
        except Exception as e:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in remove dependencies from flag, improper flag dep id, " + flag_dep_id,
                                                           simple_message="error in remove dependency from flag")
            response_code = 400

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
                                                       simple_message="dependencies have been updated",
                                                       uuid=updated_flag_dep_id)
        response_code = 200
    return flag_schema_object, response_code

#A call to delete all flag dependencies
def delete_all_flag_dependencies(flagging_mongo):
    flagging_mongo.delete_all_flag_dependencies()
    flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                   message="all flag dependencies have been deleted",
                                                   simple_message="all flag dependencies have been deleted")
    return flag_schema_object, 200




