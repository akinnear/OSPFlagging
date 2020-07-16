from flagging_project.flagging import FlaggingValidation, FlaggingNodeVisitor
from flagging.FlaggingValidation import validate_flag_logic_information
from flagging.FlaggingNodeVisitor import CodeLocation, determine_variables
from flagging.VariableInformation import VariableInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from unittest import mock
from mock import patch
from unittest.mock import MagicMock





#TODO
# test fail
def test_flag_feeder_availble(func):
    print(func)
    flag_feeders = {'FF1'}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0

#TODO
# test fails
@mock.patch(FlaggingValidation.determine_variables, return_value=FlagLogicInformation(), autospec=True)
@mock.patch(FlaggingValidation.validate_returns_boolean, return_value=TypeValidationResults(), autospec=True)
def test_flag_feeder_not_availble(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0

#TODO
# test fails
# @patch.object(FlaggingValidation.determine_variables, autospec=True, return_value=FlagLogicInformation())
# @patch.object(FlaggingValidation.validate_returns_boolean, autospec=True, return_value=TypeValidationResults())
def test_variable_defined_and_used(FlaggingValidation, mocker):
    # mocker.patch.object(FlaggingValidation.determine_variables, return_value=FlagLogicInformation())
    # mocker.patch.object(FlaggingValidation.validate_returns_boolean, return_value=TypeValidationResults())

    mocker.patch.object(FlaggingValidation, 'determine_variables', return_value=FlagLogicInformation())
    mocker.patch.object(FlaggingValidation, 'validate_returns_boolean', return_value=TypeValidationResults())
    # mocker.patch(FlaggingValidation, "determine_variables", return_value=FlagLogicInformation())
    # mocker.patch(FlaggingValidation, "validate_returns_boolean", return_value=TypeValidationResults())
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation()}},
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)



    assert len(result.errors) == 0
    assert len(result.warnings) == 0

#TODO
# test fails
def test_variable_defined_and_not_used():
    FlaggingValidation.determine_variables = MagicMock(return_value=FlagLogicInformation())
    FlaggingValidation.validate_returns_boolean = MagicMock(return_value=TypeValidationResults())
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 1

def test_variable_valid_return(mocker):

    mocker.patch.object(FlaggingValidation, 'determine_variables')
    FlaggingValidation.determine_variables.return_value = FlagLogicInformation()

    mocker.patch.object(FlaggingValidation, 'validate_returns_boolean')
    FlaggingValidation.validate_returns_boolean.return_value = TypeValidationResults()

    flag_feeders = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 1

def test_variable_numerical_compare():
    logic = """return FF1 > 10 """
    test_output = determine_variables(logic)
    assert len(test_output.validation_results.validation_errors) == 0

#TODO
# test fails
def test_variable_numerical_invalid():
    logic = """return FF1"""
    test_output = determine_variables(logic)
    assert len(test_output.validation_results.validation_errors) != 0

#TODO
# test fails
def test_variable_any():
    logic = """return FF1"""
    test_output = determine_variables(logic)
    assert len(test_output.validation_results.validation_errors) != 0

def test_determine_validation_location_1():
    logic = """cat and dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None),
                                                 VariableInformation("dog", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {
        CodeLocation(line_number=1, column_offset=0)}
    assert test_output.used_variables[VariableInformation("dog", None)] == {
        CodeLocation(line_number=1, column_offset=8)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []
    assert len(test_output.validation_results.validation_errors) == 0

def test_determine_validation_location_2():
    logic = """return cat and dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None),
                                                 VariableInformation("dog", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {
        CodeLocation(line_number=1, column_offset=7)}
    assert test_output.used_variables[VariableInformation("dog", None)] == {
        CodeLocation(line_number=1, column_offset=15)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []
    assert len(test_output.validation_results.validation_errors) == 0

def test_determine_validation_location_3():
    logic = """c and d"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("c", None),
                                                 VariableInformation("d", None)}
    assert test_output.used_variables[VariableInformation("c", None)] == {
        CodeLocation(line_number=1, column_offset=0)}
    assert test_output.used_variables[VariableInformation("d", None)] == {
        CodeLocation(line_number=1, column_offset=6)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []
    assert len(test_output.validation_results.validation_errors) == 0

def test_determine_validation_location_4():
    logic = """return c and d"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("c", None),
                                                 VariableInformation("d", None)}
    assert test_output.used_variables[VariableInformation("c", None)] == {
        CodeLocation(line_number=1, column_offset=7)}
    assert test_output.used_variables[VariableInformation("d", None)] == {
        CodeLocation(line_number=1, column_offset=13)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []
    assert len(test_output.validation_results.validation_errors) == 0

#TODO
# test fails
def test_mypy_integration():
    flag_feeders = {'cat'}
    logic = """return cat or dog"""
    test_output = determine_variables(logic)
    flag_info = FlagLogicInformation(
        used_variables=test_output.used_variables,
        assigned_variables=test_output.assigned_variables,
        validation_results=test_output.validation_results
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0
