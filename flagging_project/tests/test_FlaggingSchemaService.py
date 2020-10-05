from flag_names.FlagService import pull_flag_names, \
    pull_flag_names_in_flag_group
from flag_names.FlagGroupService import pull_flag_group_names
from front_end.FlaggingDependencies import get_flag_dependencies
from front_end.FlaggingValidateLogic import validate_logic
from front_end.FlaggingSchemaService import create_flag, create_flag, \
    update_flag_name, update_flag_logic, \
    delete_flag, create_flag_group, delete_flag_group, add_flag_to_flag_group, \
    remove_flag_from_flag_group, duplicate_flag, duplicate_flag_group
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.FlaggingValidation import FlaggingValidationResults
from flag_data.FlaggingMongo import FlaggingMongo
from unittest import mock
import pymongo
import mongomock


# def _get_connection_string(container):
#     return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)
#
# def _create_flagging_mongo(container):
#     return FlaggingMongo(_get_connection_string(container))
#
# def _create_mongo_client(container):
#     return MongoClient(_get_connection_string(container))

# notes
# pass errors as such
@mock.patch("front_end.FlaggingSchemaService.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(other_errors={"mock_error": {CodeLocation(1,1)}}),
            autospec=True)
def test_validation_user_defined_func_error(mock_determine_variables, mock_validate_returns_boolean):
    #blah
    return None


#test validate logic
# @mock.patch("front_end.FlaggingSchemaService.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(), autospec=True)
def test_validate_logic_valid(mock_validate_returns_boolean):
    flag_id = "Flag_1A1A"
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation(1, 1)}}
    )
    result = validate_logic(flag_id, flag_info)
    assert result.errors == {}
    assert result.mypy_errors == {}
    assert result.warnings == {}
    assert result.mypy_warnings == {}

# @mock.patch("front_end.FlaggingSchemaService.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(validation_errors={"mock_validation_error": {CodeLocation(2, 2)}}), autospec=True)
def test_validate_logic_w_exp_errors(mock_validate_returns_boolean):
    flag_id = "Flag_1A1A"
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation(1, 1)}}
    )
    result = validate_logic(flag_id, flag_info)
    assert result.errors == {}
    assert result.mypy_errors == {"mock_validation_error": {CodeLocation(2,2)}}
    assert result.warnings == {}
    assert result.mypy_warnings == {}

#test get_flag_deps
def test_get_flag_deps():
    flag_dependencies = get_flag_dependencies()
    assert flag_dependencies == {"Flag1": {"Flag8"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {},
     "Flag9": {"Flag10"},
     "Flag10": {"Flag9"}}

#test pull flags
def test_pull_flags():
    flag_names = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    assert flag_names == ["Flag1", "Flag2"]


#test pull flag_groups
def test_pull_flag_groups():
    flag_groups = pull_flag_group_names(dummy_flag_group_names=['FG1A1A', "FG2B2B"])
    assert flag_groups == ["FG1A1A", "FG2B2B"]

#test pull flags in flag_group
def test_pull_flags_in_flag_group():
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    assert flags_in_flag_group == ["Flag1", "Flag2"]


#test create flag, valid flag
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag(flagging_mongo, mvrb):
    flag_name = "Flag1"
    flagging_mongo.add_flag.return_value = "Flag_1_ID"
    flag_logic_information = FlagLogicInformation(
    used_variables={VariableInformation("FF1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
                                                 CodeLocation(9, 5), CodeLocation(17, 15)},
                    VariableInformation("FF2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
                    VariableInformation("FF3"): {CodeLocation(7, 9)},
                    VariableInformation("FF4"): {CodeLocation(2, 3), CodeLocation(8, 15)}},
    assigned_variables={VariableInformation("a"): {CodeLocation(12, 4), CodeLocation(16, 8)},
                        VariableInformation("b"): {CodeLocation(13, 4)},
                        VariableInformation("c"): {CodeLocation(14, 4)}},
    referenced_functions=dict(),
    defined_functions=dict(),
    defined_classes=dict(),
    referenced_modules=dict(),
    referenced_flags=dict(),
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result = create_flag(flag_name, flag_logic_information, flagging_mongo=flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag created"
    assert result.uuid == "Flag_1_ID"

#test create new flag, missing flag id
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_create_flag_no_flag_name(mvrb):
    flag_name = None
    flag_logic_information = FlagLogicInformation(
    used_variables={VariableInformation("FF1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
                                                 CodeLocation(9, 5), CodeLocation(17, 15)},
                    VariableInformation("FF2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
                    VariableInformation("FF3"): {CodeLocation(7, 9)},
                    VariableInformation("FF4"): {CodeLocation(2, 3), CodeLocation(8, 15)}},
    assigned_variables={VariableInformation("a"): {CodeLocation(12, 4), CodeLocation(16, 8)},
                        VariableInformation("b"): {CodeLocation(13, 4)},
                        VariableInformation("c"): {CodeLocation(14, 4)}},
    referenced_functions=dict(),
    defined_functions=dict(),
    defined_classes=dict(),
    referenced_modules=dict(),
    referenced_flags=dict(),
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result = create_flag(flag_name, flag_logic_information)
    assert result.valid == False
    assert result.message == "flag id not specified"
    assert result.uuid == None



#test create new flag, invalid logic
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_create_flag_with_errors(mvrb):
    flag_name = "Flag1"
    flag_logic_information = FlagLogicInformation(
    used_variables={VariableInformation("FF1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
                                                 CodeLocation(9, 5), CodeLocation(17, 15)},
                    VariableInformation("FF2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
                    VariableInformation("FF3"): {CodeLocation(7, 9)},
                    VariableInformation("ff4"): {CodeLocation(2, 3), CodeLocation(8, 15)}},
    assigned_variables={VariableInformation("a"): {CodeLocation(12, 4), CodeLocation(16, 8)},
                        VariableInformation("b"): {CodeLocation(13, 4)},
                        VariableInformation("c"): {CodeLocation(14, 4)}},
    referenced_functions=dict(),
    defined_functions=dict(),
    defined_classes=dict(),
    referenced_modules=dict(),
    referenced_flags=dict(),
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result = create_flag(flag_name, flag_logic_information)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == "Flag1_primary_key_id"




#test update flag name, valid update
def test_update_flag_name_valid():
    original_flag_name = "Flag1"
    new_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    result = update_flag_name(original_flag_name, new_flag_name, existing_flags)
    assert result.valid == True
    assert result.message == "original flag Flag1 updated to Flag2"
    assert result.uuid == "Flag2_primary_key_id"

def test_update_flag_name_valid_2():
    original_flag_name = "Flag1"
    new_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag3"])
    result = update_flag_name(original_flag_name, new_flag_name, existing_flags)
    assert result.valid == True
    assert result.message == "original flag Flag1 updated to Flag2"
    assert result.uuid == "Flag2_primary_key_id"


#test update flag name, missing orginal flag name
def test_update_flag_name_missing_original_flag():
    original_flag_name = None
    new_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag3"])
    result = update_flag_name(original_flag_name, new_flag_name, existing_flags)
    assert result.valid == False
    assert result.message == "user must specify name of original flag"
    assert result.uuid == None


#test update flag name, missing new flag name
def test_update_flag_name_missing_new_flag():
    original_flag_name = "Flag1"
    new_flag_name = None
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag3"])
    result = update_flag_name(original_flag_name, new_flag_name, existing_flags)
    assert result.valid == False
    assert result.message == "user must specify name of new flag"
    assert result.uuid == None

#test update flag name, orignal flag name does not exist
def test_update_flag_name_does_not_exist():
    original_flag_name = "Flag2"
    new_flag_name = "Flag3"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag3"])
    result = update_flag_name(original_flag_name, new_flag_name, existing_flags)
    assert result.valid == False
    assert result.message == "original flag id Flag2 does not exist"
    assert result.uuid == None

#test update flag logic, valid
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_update_flag_logic(mvrb):
    flag_name = "Flag1"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    new_flag_logic = FlagLogicInformation(used_variables={VariableInformation("FF1"): {CodeLocation(1, 1)},
                                                          VariableInformation("FF2"): {CodeLocation(2, 2)}})
    result = update_flag_logic(flag_name, new_flag_logic, existing_flags)
    assert result.valid == True
    assert result.message == "logic for flag " + flag_name + " has been updated"
    assert result.uuid == flag_name + "_primary_key_id"

#test update flag logic, flag does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_update_flag_logic_missing_flag(mvrb):
    flag_name = "Flag3"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    new_flag_logic = FlagLogicInformation(used_variables={VariableInformation("FF1"): {CodeLocation(1, 1)},
                                                          VariableInformation("FF2"): {CodeLocation(2, 2)}})
    result = update_flag_logic(flag_name, new_flag_logic, existing_flags)
    assert result.valid == False
    assert result.message == "could not identify existing flag " + flag_name
    assert result.uuid == flag_name + "_primary_key_id"

#test update flag logic, error in new logic
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_update_flag_logic_error(mvrb):
    flag_name = "Flag1"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    new_flag_logic = FlagLogicInformation(used_variables={VariableInformation("FF1"): {CodeLocation(1, 1)},
                                                          VariableInformation("ff1"): {CodeLocation(2, 2)}})
    result = update_flag_logic(flag_name, new_flag_logic, existing_flags)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == flag_name + "_primary_key_id"


#test delete flag valid
def test_delete_flag_valid():
    flag_name = "Flag1"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    result = delete_flag(flag_name, existing_flags)
    assert result.valid == True
    assert result.message == flag_name + " has been deleted"
    assert result.uuid == flag_name + "_primary_key_id"

#test delete flag, invalid, flag name does not exist
def test_delete_flag_does_not_exist():
    flag_name = "Flag3"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2"])
    result = delete_flag(flag_name, existing_flags)
    assert result.valid == False
    assert result.message == "flag name specified does not exist"
    assert result.uuid == flag_name + "_primary_key_id"

#test create flag group, valid
def test_create_flag_group_valid():
    flag_group_id = "FG3AC3C"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = create_flag_group(flag_group_id, existing_flag_groups)
    assert result.valid == True
    assert result.message == "Unique flag group " + flag_group_id + " created"
    assert result.uuid == flag_group_id + "_primary_key_id"


#test create flag group, flag group id already exists
def test_create_flag_group_duplicate_groups():
    flag_group_id = "FG1A1A"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = create_flag_group(flag_group_id, existing_flag_groups)
    assert result.valid == False
    assert result.message == flag_group_id + " already exists"
    assert result.uuid == flag_group_id + "_primary_key_id"



#test create flag group, missing flag group name
def test_create_flag_group_missing_name():
    flag_group_id = None
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = create_flag_group(flag_group_id, existing_flag_groups)
    assert result.valid == False
    assert result.message == "unique flag group name must be created"
    assert result.uuid == None


#test delete flag group


#test add flag to flag group
def test_validation_user_defined_func_error():
    result = add_flag_to_flag_group(flag_group_id="FG1A1A",
                                   new_flags=["Flag3"],
                                   existing_flags=pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"]),
                                   existing_flag_groups=pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"]),
                                   flags_in_flag_group=pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"]))
    assert result.valid == True
    assert result.message == "flag group FG1A1A has been updated with flag(s) Flag3"
    assert result.uuid == "FG1A1A_primary_key_id"

#flag group does not exist
def test_validation_flag_group_no_exist():
    flag_group_id = "FG1A1A"
    new_flags = ["Flag3"]
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=['FG2B2B'])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    result = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                    new_flags=new_flags,
                                    existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups,
                                    flags_in_flag_group=flags_in_flag_group)

    assert result.valid == False
    assert result.message == "flag_group " + flag_group_id + " does not exist"
    assert result.uuid == "FG1A1A_primary_key_id"


#flag does not exist
def test_validation_flag_group_flag_no_exist():
    flag_group_id = "FG1A1A"
    new_flags = ['Flag3', "Flag4"]
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    result = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                    new_flags=new_flags,
                                    existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups,
                                    flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag4 do not exist"
    assert result.uuid == "FG1A1A_primary_key_id"


def test_validation_flag_group_flag_no_exist_2():
    flag_group_id = "FG1A1A"
    new_flags = ['Flag3', "Flag4", "Flag5"]
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    result = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                    new_flags=new_flags,
                                    existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups,
                                    flags_in_flag_group=flags_in_flag_group)

    assert result.valid == False
    assert result.message == "Flag(s) Flag4, Flag5 do not exist"
    assert result.uuid == "FG1A1A_primary_key_id"




#test remove flag from flag group
def test_validation_remove_flag_from_flag_group():
    flag_group_id = "FG1A1A"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    flags_2_remove = ["Flag2"]
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == True
    assert result.message == "Flag(s) Flag2 removed from FG1A1A"
    assert result.uuid == "FG1A1A_primary_key_id"

def test_validation_remove_flag_from_flag_group_2():
    flag_group_id = "FG1A1A"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3", "Flag4", "Flag5"])
    flags_2_remove = ["Flag2", "Flag5"]
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2", "Flag5"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == True
    assert result.message == "Flag(s) Flag2, Flag5 removed from FG1A1A"
    assert result.uuid == "FG1A1A_primary_key_id"

def test_validation_remove_flag_from_flag_group_no_flag_group():
    flag_group_id = "FG1A1A"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    flags_2_remove = ["Flag2"]
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "flag_group " + flag_group_id + " does not exist"
    assert result.uuid == "FG1A1A_primary_key_id"

#test removal of flags that do not exist in flag group
def test_validation_remove_flag_from_flag_group_no_flag():
    flag_group_id = "FG1A1A"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    flags_2_remove = ["Flag2"]
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag2 do not exist in FG1A1A"
    assert result.uuid == "FG1A1A_primary_key_id"

def test_validation_remove_flag_from_flag_group_no_flag_2():
    flag_group_id = "FG1A1A"
    existing_flags = pull_flag_names(dummy_flag_names=["Flag1", "Flag2", "Flag3"])
    flags_2_remove = ["Flag2", "Flag3"]
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag2, Flag3 do not exist in FG1A1A"
    assert result.uuid == "FG1A1A_primary_key_id"

#test removal of flags from flag group where flags are not defined
def test_validation_remove_flag_from_flag_group_missing_flag():
    flag_group_id = "FG1A1A"
    existing_flags = ["Flag1", "Flag3"]
    flags_2_remove = pull_flag_names(dummy_flag_names=["Flag2"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag2 do not exist"
    assert result.uuid == "FG1A1A_primary_key_id"

def test_validation_remove_flag_from_flag_group_missing_flag_2():
    flag_group_id = "FG1A1A"
    existing_flags = ["Flag1"]
    flags_2_remove = pull_flag_names(dummy_flag_names=["Flag2", "Flag3"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1"])
    result = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                         del_flags=flags_2_remove,
                                         existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups,
                                         flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag2, Flag3 do not exist"
    assert result.uuid == "FG1A1A_primary_key_id"

#test duplicate flag
def test_validation_flag_group_duplicate_flag():
    flag_group_id = "FG1A1A"
    new_flags = ["Flag3"]
    existing_flags = pull_flag_names(dummy_flag_names=['Flag1', "Flag2", "Flag3"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag3"])
    result = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                    new_flags=new_flags,
                                    existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups,
                                    flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag3 already exist in flag group"
    assert result.uuid == "FG1A1A_primary_key_id"

def test_validation_flag_group_duplicate_flag_2():
    flag_group_id = "FG1A1A"
    new_flags = ["Flag3", "Flag4"]
    existing_flags = pull_flag_names(dummy_flag_names=['Flag1', "Flag2", "Flag3", "Flag4"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag3", "Flag4"])
    result = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                    new_flags=new_flags,
                                    existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups,
                                    flags_in_flag_group=flags_in_flag_group)
    assert result.valid == False
    assert result.message == "Flag(s) Flag3, Flag4 already exist in flag group"
    assert result.uuid == "FG1A1A_primary_key_id"



#test duplicate flag group, valid
def test_duplicate_flag_group_valid():
    original_flag_group_id = "FG1A1A"
    new_flag_group_id = "FG1A1B"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = duplicate_flag_group(original_flag_group_id, new_flag_group_id, existing_flag_groups)
    result.valid == True
    result.message == "new flag group " + new_flag_group_id + " created off of " + original_flag_group_id
    result.uuid == "FG1A1B" + "_primary_key_id"

#test duplicate flag group, flag group does not exist
def test_duplicate_flag_group_invalid_original_flag_group():
    original_flag_group_id = "FG3C3C"
    new_flag_group_id = "FG1A1B"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = duplicate_flag_group(original_flag_group_id, new_flag_group_id, existing_flag_groups)
    result.valid == False
    result.message == "flag group " + original_flag_group_id + " does not exist"
    result.uuid == None

#test duplicate flag group, new name of flag group already exists
def test_duplicate_flag_group_invalid_new_flag_group():
    original_flag_group_id = "FG1A1A"
    new_flag_group_id = "FG2B2B"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FG1A1A", "FG2B2B"])
    result = duplicate_flag_group(original_flag_group_id, new_flag_group_id, existing_flag_groups)
    result.valid == False
    result.message == "new flag group " + new_flag_group_id + " already exists"
    result.uuid == new_flag_group_id + "_primary_key_id"



#test interface, simple mock pull
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo", return_value=FlaggingMongo("mock_url"), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo.get_flags", return_value="FlagID", autospec=True)
def test_pull_flag_interface(mfm, mgf):
    flag_mongo = FlaggingMongo(connection_url="mock_url")
    flags = flag_mongo.get_flags()
    assert "FlagID" in flags

#utilize mongomock as Mongo DB client
def test_mongomock():
    flagging_mongo = FlaggingMongo(connection_url="mongodb://test:test@localhost:27017")
    flagging_mongo.client = mongomock.MongoClient()
    add_id = flagging_mongo.add_flag({"_id": "FlagID1"})
    flags = flagging_mongo.get_flags()
    assert len(flags) == 1
    assert flags[0]['_id'] == "FlagID1"




















