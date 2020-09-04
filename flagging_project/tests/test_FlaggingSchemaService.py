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
@mock.patch("front_end.FlaggingSchemaService.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(), autospec=True)
def test_validate_logic_valid(mock_determine_variables, mock_validate_returns_boolean):
    flag_id = "Flag_1A1A"
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation(1, 1)}}
    )
    result = validate_logic(flag_id, flag_info)
    assert result.errors == {}
    assert result.mypy_errors == {}
    assert result.warnings == {}
    assert result.mypy_warnings == {}

@mock.patch("front_end.FlaggingSchemaService.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(validation_errors={"mock_validation_error": {CodeLocation(2, 2)}}), autospec=True)
def test_validate_logic_w_exp_errors(mock_determine_variables, mock_validate_returns_boolean):
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



#test pull flag_groups


#test pull flags in flag_group


#test create flags



#test update flag name


#test update flag logic


#test delete flag


#test create flag group


#test delete flag group


#test add flag to flag group
def test_validation_user_defined_func_error():
    result = add_flag_to_flag_group(flag_group_id="FG1A1A",
                                   new_flags=["Flag3"],
                                   existing_flags=["Flag1", "Flag2", "Flag3"],
                                   existing_flag_groups=["FG1A1A", "FG2B2B"],
                                   flags_in_flag_group=pull_flag_names_in_flag_group(dummy_flag_names=["Flag1", "Flag2"]))
    assert result.valid == True
    assert result.message == "flag group FG1A1A has been updated with flag(s) Flag3"
    assert result.uuid == "FG1A1A_primary_key_id"



#test remove flag from flag group


#test duplicate flag



#test duplicate flag group





