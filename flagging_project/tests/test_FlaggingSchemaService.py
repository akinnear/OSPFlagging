from flag_names.FlagService import pull_flag_names, \
    pull_flag_names_in_flag_group
from flag_names.FlagGroupService import pull_flag_group_names
from front_end.FlaggingSchemaService import validate_logic, get_flag_dependencies, \
    create_flag, create_flag, update_flag_name, update_flag_logic, \
    delete_flag, create_flag_group, delete_flag_group, add_flag_to_flag_group, \
    remove_flag_from_flag_group, duplicate_flag, duplicate_flag_group
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.FlaggingValidation import FlaggingValidationResults

from unittest import mock

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
def test_create_flag(mvrb):
    flag_name = "Flag1"
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
    assert result.valid == True
    assert result.message == "new flag create"
    assert result.uuid == "Flag1_primary_key_id"

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



#test update flag name


#test update flag logic


#test delete flag


#test create flag group


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
    print("hello")
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
    print('hello')
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
    print('hello')
    assert result.valid == False
    assert result.message == "Flag(s) Flag3, Flag4 already exist in flag group"
    assert result.uuid == "FG1A1A_primary_key_id"



#test duplicate flag group





