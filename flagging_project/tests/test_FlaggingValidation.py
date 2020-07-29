from flagging_project.flagging import FlaggingValidation, FlaggingNodeVisitor
from flagging.FlaggingValidation import validate_flag_logic_information
from flagging.FlaggingNodeVisitor import CodeLocation, determine_variables
from flagging.VariableInformation import VariableInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from unittest import mock



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


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_flag_feeder_not_available(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {"FF1"}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_variable_defined_and_used_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation()}},
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_variable_defined_and_not_used(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) == 0
    assert len(result.warnings) == 1


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_variable_valid_return(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) == 0
    assert len(result.warnings) == 1


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_user_defined_func_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {"ff1"}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2, 25)},
                        VariableInformation("y"): {CodeLocation(2, 29)},
                        VariableInformation("ff1"): {CodeLocation(4, 7)},
                        VariableInformation("z"): {CodeLocation(4, 13)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 11)},
                            VariableInformation("y"): {CodeLocation(2, 14)},
                            VariableInformation("z"): {CodeLocation(3, 0)}},
        referenced_functions={VariableInformation("my_add"): {CodeLocation(3, 4)}},
        defined_functions={VariableInformation("my_add"): {CodeLocation(2, 2)}},
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(4, 0), CodeLocation(2, 18)},
        errors=[],
        flag_logic="""
        def my_add(x, y): return x + y
        z = my_add(2, 3)   
        return ff1 > z""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) != 0
    assert len(result.warnings) == 0

@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_lambda_use_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2, 26)},
                        VariableInformation("y"): {CodeLocation(2, 30)},
                        VariableInformation("cat"): {CodeLocation(2, 41), CodeLocation(2, 34)},
                        VariableInformation("sum"): {CodeLocation(3, 7)}},
        assigned_variables={VariableInformation("sum"): {CodeLocation(2, 0)},
                            VariableInformation("cat"): {CodeLocation(2, 49)},
                            VariableInformation("x"): {CodeLocation(2, 20)},
                            VariableInformation("y"): {CodeLocation(2, 23)}},
        referenced_functions={VariableInformation("reduce"): {CodeLocation(2, 6)},
                              VariableInformation("range"): {CodeLocation(2, 56)}},
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(3, 0)},
        used_lambdas={"LAMBDA": {CodeLocation(2, 13)}},
        errors=[],
        flag_logic="""
sum = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
return sum > 10""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) != 0
    assert len(result.warnings) == 0



@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_lambda_use_error_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_feeders = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2, 26),
                                                   CodeLocation(3, 26)},
                        VariableInformation("y"): {CodeLocation(2, 30),
                                                   CodeLocation(3, 30)},
                        VariableInformation("cat"): {CodeLocation(2, 41), CodeLocation(2, 34),
                                                     CodeLocation(3, 41), CodeLocation(3, 34)},
                        VariableInformation("sum"): {CodeLocation(4, 7)},
                        VariableInformation("mki"): {CodeLocation(4, 13)}},
        assigned_variables={VariableInformation("sum"): {CodeLocation(2, 0)},
                            VariableInformation("mki"): {CodeLocation(3, 0)},
                            VariableInformation("cat"): {CodeLocation(2, 49), CodeLocation(3, 49)},
                            VariableInformation("x"): {CodeLocation(2, 20), CodeLocation(3, 20)},
                            VariableInformation("y"): {CodeLocation(2, 23), CodeLocation(3, 23)}},
        referenced_functions={VariableInformation("reduce"): {CodeLocation(2, 6), CodeLocation(3, 6)},
                              VariableInformation("range"): {CodeLocation(2, 56), CodeLocation(3, 56)}},
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(4, 0)},
        used_lambdas={"LAMBDA": {CodeLocation(2, 13), CodeLocation(3, 13)}},
        errors=[],
        flag_logic="""
sum = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
mki = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
return sum + mki > 10""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_feeders, flag_info)
    assert len(result.errors) != 0
    assert len(result.warnings) == 0







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
    flag_feeders = {'cat': bool, 'dog': bool}
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
