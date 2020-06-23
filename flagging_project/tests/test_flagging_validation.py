from flagging.flagging_validation import validate_flag_logic_information
from flagging.FlagFeederApp import FlagLogicInformation, VariableInformation, CodeLocation

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