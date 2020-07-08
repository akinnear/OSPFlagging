from flagging.FlaggingValidation import validate_flag_logic_information
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.FlagFeederApp import FlagLogicInformation, determine_variables
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation

def test_flag_feeder_availble():
    flag_feeders = {'FF1'}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_flag_feeder_not_availble():
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 1
    assert len(result.warnings) == 0


def test_variable_defined_and_used():
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation()}},
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_variable_defined_and_not_used():
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 1

def test_variable_valid_return():
    logic = """return FF1 """
    test_output = determine_variables(logic, {"FF1": bool})
    assert len(test_output.validation_results.validation_errors) == 0

def test_variable_numerical_compare():
    logic = """return FF1 > 10 """
    test_output = determine_variables(logic, {"FF1": int})
    assert len(test_output.validation_results.validation_errors) == 0

def test_variable_numerical_invalid():
    logic = """return FF1"""
    test_output = determine_variables(logic, {"FF1": int})
    assert len(test_output.validation_results.validation_errors) != 0

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
    test_output = determine_variables(logic, {"c": int, "d": bool})
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

def test_mypy_integration():
    flag_feeders = {'cat'}
    logic = """return cat or dog"""
    test_output = determine_variables(logic, {"cat": bool, "dog": int})
    flag_info = FlagLogicInformation(
        used_variables=test_output.used_variables,
        assigned_variables=test_output.assigned_variables,
        validation_results=test_output.validation_results
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)

    assert len(result.errors) == 0
    assert len(result.warnings) == 0
