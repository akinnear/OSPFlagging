from flagging_project.flagging import FlaggingValidation, FlaggingNodeVisitor
from flagging.FlaggingValidation import validate_flag_logic_information, FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation, determine_variables
from flagging.VariableInformation import VariableInformation
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.ModuleInformation import ModuleInformation
from flagging.ErrorInformation import ErrorInformation
from flagging.FlagErrorInformation import FlagErrorInformation
from unittest import mock





# notes
# pass errors as such
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(other_errors={"mock_error": {CodeLocation(1,1)}}),
            autospec=True)
def test_validation_user_defined_func_error(mock_determine_variables, mock_validate_returns_boolean):
    #blah
    return None

#TODO
# 11) error if referenced flags are not defined, ???





#explicity mypy other_error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(other_errors={"mock_other_error": {CodeLocation(1,1)}}),
            autospec=True)
def test_validation_explicit_mypy_other_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {"mock_other_error": {CodeLocation(1, 1)}}
    assert result.mypy_warnings == {}

#explict mypy validation_error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(validation_errors={"mock_validation_error": {CodeLocation(1,1)}}),
            autospec=True)
def test_validation_explicit_mypy_validation_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {"mock_validation_error": {CodeLocation(1, 1)}}
    assert result.mypy_warnings == {}


#explicit mypy validation error, return non bool
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(validation_errors={"mock_return_value": {CodeLocation(3,1)}}),
            autospec=True)
def test_validation_non_bool_return(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": str, "FF2": bool}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("FF1"): {CodeLocation(1, 1)},
                        VariableInformation("FF2"): {CodeLocation(2, 1)}},
        flag_logic="""FF1 > FF2""")
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {"mock_return_value": {CodeLocation(3, 1)}}
    assert result.mypy_warnings == {}


#user defined function error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_user_defined_func_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1"}
    flag_dependencies = {}
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
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"my_add": {CodeLocation(2, 2)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#user defined class error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_user_defined_class_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("ff1"): {CodeLocation(4, 7)}},
        assigned_variables={},
        referenced_functions={},
        defined_functions={},
        defined_classes={VariableInformation("my_class"): {CodeLocation(1,1)}},
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(4, 0), CodeLocation(2, 18)},
        errors=[],
        flag_logic="""
            does not matter""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"my_class": {CodeLocation(1, 1)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#lambda use error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_lambda_use_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
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
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"LAMBDA": {CodeLocation(2, 13)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}



#missing flag feeders, used variables not in flag feeders or assigned variablres
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_flagfeeders(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation(1, 1)},
                        VariableInformation("FF2"): {CodeLocation(2, 2)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation("FF2"): {CodeLocation(2, 2)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#missing variable assignment/flagfeeder
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_variable_assignment(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)},
                        VariableInformation("y"): {CodeLocation(2, 2)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation("y"): {CodeLocation(2, 2)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#incorrect variable set, unused assigned variable
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_non_used_variable_assignment(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)},
                            VariableInformation("y"): {CodeLocation(2, 2)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {VariableInformation("y"): {CodeLocation(2, 2)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#node visitor error
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_node_visitor_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation(1, 1)}},
        errors=[ErrorInformation(cl=CodeLocation(3, 5), msg="invalid syntax", text="x = == = 5")]
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"FlagLogicInformationError invalid syntax":
                                 {ErrorInformation(CodeLocation(3,5),
                                                   "invalid syntax",
                                                   "x = == = 5")}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}



#referenced function not defined or imported,
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_non_imported_or_defined_function(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2,2)},
                        VariableInformation("FF1"): {CodeLocation(3, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(1, 1)}},
        referenced_functions={VariableInformation.create_var(["math", "sqrt"]): {CodeLocation(1, 5)},
                              VariableInformation.create_var(["matplotlib", "plot"]): {CodeLocation(2, 5)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation.create_var(["matplotlib", "plot"]): {CodeLocation(2, 5)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#referenced function not defined or imported, min is built in
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_non_imported_or_defined_function(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2,2)},
                        VariableInformation("FF1"): {CodeLocation(3, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(1, 1)}},
        referenced_functions={VariableInformation.create_var(["math", "sqrt"]): {CodeLocation(1, 5)},
                              VariableInformation("min"): {CodeLocation(1, 10)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation.create_var(["math", "sqrt"]): {CodeLocation(1, 5)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#referenced function IS defined, 2 errors, one for defined function and one for use without import
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_defined_function(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(2,2)},
                        VariableInformation("FF1"): {CodeLocation(3, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(1, 1)}},
        referenced_functions={VariableInformation.create_var(["my", "func"]): {CodeLocation(2, 5)},
                              VariableInformation("max"): {CodeLocation(2, 10)}},
        defined_functions={VariableInformation.create_var(["my", "func"]): {CodeLocation(1, 5)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation.create_var(["my", "func"]): {CodeLocation(1, 5),
                                                                              CodeLocation(2, 5)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#referenced function IS imported, but not installed
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_imported_function(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(3, 2)},
                        VariableInformation("FF1"): {CodeLocation(4, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 1)}},
        referenced_functions={VariableInformation.create_var(["math", "sqrt"]): {CodeLocation(3, 5)},
                              VariableInformation("sns"): {CodeLocation(3, 10)}},
        referenced_modules={ModuleInformation("seaborn", "sns"): {CodeLocation(1, 5)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation.create_var(["math", "sqrt"]): {CodeLocation(3, 5)},
                             ModuleInformation("seaborn", "sns"): {CodeLocation(1, 5)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#referenced function IS imported, but not installed, asname usage
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_imported_function_asname(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(3, 2)},
                        VariableInformation("FF1"): {CodeLocation(4, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 1)}},
        referenced_functions={VariableInformation.create_var(["m", "sqrt"]): {CodeLocation(3, 5)},
                              VariableInformation.create_var(["sns", "replot"]): {CodeLocation(5, 5)}},
        referenced_modules={ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                            ModuleInformation("seaborn", "sns"): {CodeLocation(1, 10)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("seaborn", "sns"): {CodeLocation(1, 10)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#referenced function IS imported, but not installed, and not used
#installed referenced modules are not used
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_unused_import_module(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(3, 2)},
                        VariableInformation("FF1"): {CodeLocation(4, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 1)}},
        referenced_functions={VariableInformation.create_var(['mpl', 'plt']): {CodeLocation(5,20)}},
        referenced_modules={ModuleInformation("matplotlib", "mpl"): {CodeLocation(4, 10)},
                            ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                            ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                            ModuleInformation("numpy"): {CodeLocation(3, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("matplotlib", "mpl"): {CodeLocation(4, 10)}}
    assert result.warnings == {ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                               ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                               ModuleInformation("numpy"): {CodeLocation(3, 10)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}

#non standard modules not installd
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_non_standard_install_mod(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(3, 2)},
                        VariableInformation("FF1"): {CodeLocation(4, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 1)}},
        referenced_functions={VariableInformation("matplotlib"): {CodeLocation(5, 10)}},
        referenced_modules={ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                            ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                            ModuleInformation("numpy"): {CodeLocation(3, 10)},
                            ModuleInformation("matplotlib"): {CodeLocation(4, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("matplotlib"): {CodeLocation(4, 10)}}
    assert result.warnings == {ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                               ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                               ModuleInformation("numpy"): {CodeLocation(3, 10)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#unused import module, mixed
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_unused_import_module_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("x"): {CodeLocation(3, 2)},
                        VariableInformation("FF1"): {CodeLocation(4, 3)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 1)}},
        referenced_functions={VariableInformation.create_var(["m", "sqrt"]): {CodeLocation(3, 5)},
                              VariableInformation.create_var(["sns", "img"]): {CodeLocation(4, 5)}},
        referenced_modules={ModuleInformation("seaborn", "sns"): {CodeLocation(1, 10)},
                            ModuleInformation("math", "m"): {CodeLocation(1, 5)},
                            ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                            ModuleInformation("numpy"): {CodeLocation(3, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("seaborn", "sns"): {CodeLocation(1, 10)}}
    assert result.warnings == {ModuleInformation("pandas", "pd"): {CodeLocation(2, 10)},
                               ModuleInformation("numpy"): {CodeLocation(3, 10)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


## cyclical fail with no referenced flags, should pass because none of the flags are used
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_no_ref_flags(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag9", "Flag3"},
     "Flag2": {"Flag4", "Flag5", "Flag6"},
     "Flag3": {"Flag7"},
     "Flag4": {"Flag3"},
     "Flag5": {"Flag8"},
     "Flag6": set(),
     "Flag7": {"Flag2"},
     "Flag8": {"Flag3"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


## cyclical flag
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_ref_flags(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag9", "Flag3"},
     "Flag2": {"Flag4", "Flag5", "Flag6"},
     "Flag3": {"Flag7"},
     "Flag4": {"Flag3"},
     "Flag5": {"Flag8"},
     "Flag6": set(),
     "Flag7": {"Flag2"},
     "Flag8": {"Flag3"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag2": {CodeLocation(2, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag2": FlagErrorInformation(flag="Flag2",
                                                            err_info="cyclical_flag",
                                                            cl={CodeLocation(2, 10)})}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


## cyclical flag, multiple code loctions
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_ref_flags_multi_cls(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag9", "Flag3"},
     "Flag2": {"Flag4", "Flag5", "Flag6"},
     "Flag3": {"Flag7"},
     "Flag4": {"Flag3"},
     "Flag5": {"Flag8"},
     "Flag6": set(),
     "Flag7": {"Flag2"},
     "Flag8": {"Flag3"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag2": {CodeLocation(2, 10), CodeLocation(3, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag2": FlagErrorInformation(flag="Flag2",
                                                            err_info="cyclical_flag",
                                                            cl={CodeLocation(2, 10), CodeLocation(3, 10)})}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


#cyclical flags and missing flags
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_ref_flags_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag9", "Flag3"},
     "Flag2": {"Flag4", "Flag5", "Flag6"},
     "Flag3": {"Flag7"},
     "Flag4": {"Flag3"},
     "Flag5": {"Flag8"},
     "Flag6": set(),
     "Flag7": {"Flag3"},
     "Flag8": {"Flag3"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag1": FlagErrorInformation(flag="Flag1",
                                                           err_info="cyclical_flag",
                                                           cl={CodeLocation(1, 10)}),
                             "Flag2": FlagErrorInformation(flag="Flag2",
                                                           err_info="cyclical_flag",
                                                           cl={CodeLocation(2, 10)}),
                             "Flag9": FlagErrorInformation(flag="Flag9",
                                                           err_info="missing_flag",
                                                           cl={CodeLocation(None, None)})}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}

## cyclical fail
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_fail(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag9", "Flag3"},
     "Flag2": {"Flag4", "Flag5", "Flag6"},
     "Flag3": {"Flag7"},
     "Flag4": {"Flag3"},
     "Flag5": {"Flag8"},
     "Flag6": set(),
     "Flag7": {"Flag2"},
     "Flag8": {"Flag3"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag1_cyclical_flag": {CodeLocation(1, 10)},
                             "Flag2_cyclical_flag": {CodeLocation(2, 10)},
                             "Flag3_cyclical_flag": {CodeLocation(3, 10)},
                             "Flag4_cyclical_flag": {CodeLocation(4, 10)},
                             "Flag5_cyclical_flag": {CodeLocation(5, 10)},
                             "Flag7_cyclical_flag": {CodeLocation(7, 10)},
                             "Flag8_cyclical_flag": {CodeLocation(8, 10)},
                             "Flag9_missing_flag": {CodeLocation(None, None)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


## cyclical fail catch
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_cyclical_fail_catch(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag2"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {"Flag1"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag6": {CodeLocation(6, 10)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag1_cyclical_flag": {CodeLocation(1, 10)},
                             "Flag2_cyclical_flag": {CodeLocation(2, 10)},
                             "Flag6_cyclical_flag": {CodeLocation(6, 10)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}

## zero cycical flags
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_zero_cyclical(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag2"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": set()}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}

## missing flag reference in dependency
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_flag_dependency_key(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag2"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {"Flag9"}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag9_missing_flag": {CodeLocation(None, None)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


##clyclical dependency in created flag, math and functools are standar modules, do not need to be installed
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_created_flag_cyclical_dependency(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"FlagNameDefault"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}},
        referenced_modules={ModuleInformation("math"): {CodeLocation(1, 5)},
                            ModuleInformation("functools"): {CodeLocation(1, 7)},
                            ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"Flag1_cyclical_flag": {CodeLocation(1, 10)},
                             ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.warnings == {ModuleInformation("math"): {CodeLocation(1, 5)},
                               ModuleInformation("functools"): {CodeLocation(1, 7)},
                               ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


##import module erors
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_module_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag8"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}},
        referenced_modules={ModuleInformation("math"): {CodeLocation(1, 5)},
                            ModuleInformation("functools"): {CodeLocation(1, 7)},
                            ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.warnings == {ModuleInformation("math"): {CodeLocation(1, 5)},
                               ModuleInformation("functools"): {CodeLocation(1, 7)},
                               ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


##not imported module
@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_module_install(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag2"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}},
        referenced_modules={ModuleInformation("math"): {CodeLocation(1, 5)},
                            ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                            ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)},
                            ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                             ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.warnings == {ModuleInformation("math"): {CodeLocation(1, 5)},
                               ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                               ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)},
                               ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",return_value=TypeValidationResults(), autospec=True)
def test_validation_missing_module_install_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {"Flag1": {"Flag2"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
        referenced_flags={"Flag1": {CodeLocation(1, 10)},
                          "Flag2": {CodeLocation(2, 10)},
                          "Flag3": {CodeLocation(3, 10)},
                          "Flag4": {CodeLocation(4, 10)},
                          "Flag5": {CodeLocation(5, 10)},
                          "Flag6": {CodeLocation(6, 10)},
                          "Flag7": {CodeLocation(7, 10)},
                          "Flag8": {CodeLocation(8, 10)}},
        referenced_functions={VariableInformation.create_var(['functools', 'my_funky_tools']): {CodeLocation(2, 7)},
                              VariableInformation("badmodule2dfs"): {CodeLocation(3, 7)}},
        referenced_modules={ModuleInformation("math"): {CodeLocation(1, 5)},
                            ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)},
                            ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)},
                            ModuleInformation("flask"): {CodeLocation(2, 9)}})
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {ModuleInformation("badmodule2dfs"): {CodeLocation(1, 9)}}
    assert result.warnings == {ModuleInformation("math"): {CodeLocation(1, 5)},
                               ModuleInformation("flask"): {CodeLocation(2, 9)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}

########################################################

@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_flag_feeder_not_available(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"FF1"}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('FF1'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_variable_defined_and_used_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation('x'): {CodeLocation()}},
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_variable_valid_return(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        assigned_variables={VariableInformation('x'): {CodeLocation()}}
    )
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {VariableInformation("x"): {CodeLocation(None, None)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean",
            return_value=TypeValidationResults(other_errors={"mock_error": {CodeLocation(1,1)}}),
            autospec=True)
def test_validation_user_defined_func_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1"}
    flag_dependencies = {}
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
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation("my_add"): {CodeLocation(3, 4), CodeLocation(2, 2)}}
    assert result.warnings == {}
    assert result.mypy_errors == {"mock_error": {CodeLocation(1, 1)}}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_lambda_use_error(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
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
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"LAMBDA": {CodeLocation(2, 13)},
                             VariableInformation("reduce"): {CodeLocation(2, 6)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_lambda_use_error_2(mock_determine_variables, mock_validate_returns_boolean):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
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
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"LAMBDA": {CodeLocation(2, 13), CodeLocation(3, 13)},
                             VariableInformation("reduce"): {CodeLocation(2, 6), CodeLocation(3, 6)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_determine_flag_feeders_logic_and(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"cat": bool, "dog": bool}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("cat"): {CodeLocation(line_number=1, column_offset=0)},
                        VariableInformation("dog"): {CodeLocation(line_number=1, column_offset=8)}},
        assigned_variables=dict(),
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(1, 0)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""cat and dog""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_determine_flag_feeders_logic_or(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"man": bool, "woman": bool}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("man"): {CodeLocation(2, 0)},
                        VariableInformation("woman"): {CodeLocation(2, 7)}},
        assigned_variables=dict(),
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""man or woman""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_determine_flag_feeder_conditional(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("cat"): {CodeLocation(3, 7)}},
        assigned_variables={VariableInformation("cat"): {CodeLocation(2, 0)}},
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""
        cat = 100
        return cat < 10""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_determine_flag_feeder_if_statement(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": bool, "ff2": bool, "ff3": int, "ff4": int, "ff5": bool}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("y"): {CodeLocation(4, 3)},
                        VariableInformation("x"): {CodeLocation(5, 18), CodeLocation(7, 18)},
                        VariableInformation("ff1"): {CodeLocation(2, 5)},
                        VariableInformation("ff2"): {CodeLocation(2, 12)},
                        VariableInformation("ff3"): {CodeLocation(3, 5)},
                        VariableInformation("ff4"): {CodeLocation(3, 11)},
                        VariableInformation("ff5"): {CodeLocation(5, 11),
                                                     CodeLocation(7, 11)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 0)},
                            VariableInformation("y"): {CodeLocation(3, 0)}},
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(5, 4), CodeLocation(7, 4)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""
        x = (ff1 or ff2)
        y = (ff3 + ff4)
            if y > 100:
                return ff5 != x
            else:
                return ff5 == x""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_normal_expression_error_defined_function(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("y"): {CodeLocation(2, 29)},
                        VariableInformation("x"): {CodeLocation(2, 25)},
                        VariableInformation("ff1"): {CodeLocation(4, 7)},
                        VariableInformation("z"): {CodeLocation(4, 13)}},
        assigned_variables={VariableInformation("x"): {CodeLocation(2, 11)},
                            VariableInformation("y"): {CodeLocation(2, 14)},
                            VariableInformation("z"): {CodeLocation(3, 0)}},
        referenced_functions={VariableInformation("my_add"): {CodeLocation(3, 4)}},
        defined_functions={VariableInformation("my_add"): {CodeLocation(2, 4)}},
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(4, 0)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""
        def my_add(x, y): return x + y
        z = my_add(2, 3)
        return ff1 > z""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {VariableInformation("my_add"): {CodeLocation(2, 4),
                                                             CodeLocation(3, 4)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}



@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_equals_operation(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": int, "ff2": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("ff1"): {CodeLocation(1, 7)},
                        VariableInformation("ff2"): {CodeLocation(1, 14)}},
        assigned_variables=dict(),
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(1, 0)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""return ff1 == ff2""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_validation_add_operation(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": int, "ff2": int, "ff3": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("test_1"): {CodeLocation(3, 13)},
                        VariableInformation("ff1"): {CodeLocation(2, 9)},
                        VariableInformation("ff2"): {CodeLocation(2, 15)},
                        VariableInformation("ff3"): {CodeLocation(3, 7)}},
        assigned_variables={VariableInformation("test_1"): {CodeLocation(2, 0)}},
        referenced_functions=dict(),
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(3, 0)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""
        test_1 = ff1 + ff2
        return ff3 < test_1""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}


@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_determine_flag_feeder_for_loop_CodeLocation(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": int, "ff2": bool, "ff3": int, "ff4": int, "ff5": str}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("ff1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
                                                     CodeLocation(9, 5), CodeLocation(17, 15)},
                        VariableInformation("ff2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
                        VariableInformation("ff3"): {CodeLocation(7, 9)},
                        VariableInformation("ff4"): {CodeLocation(2, 3), CodeLocation(8, 15)},
                        VariableInformation("ff5"): {CodeLocation(10, 11), CodeLocation(15, 7)},
                        VariableInformation("a"): {CodeLocation(16, 12), CodeLocation(17, 21)}},
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
        flag_logic="""
        if ff4 >= 50:                                              
            if ff1 > 10:                                           
                return ff2 == True                                 
            elif ff2:                                              
                return ff1 < 10                                    
            elif ff3 > ff1:                                        
                return ff4 < 50                                    
        elif ff1 < 10:                                             
            return ff5 == 'CAT'                                    
        else:                                                      
            a = 10                                                 
            b = True                                               
            c = "CAR"                                              
            if ff5 == "DOG":                                       
                a = a + 10                                         
                return ff1 < a""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {}
    assert result.warnings == {VariableInformation("b"): {CodeLocation(13, 4)},
                               VariableInformation("c"): {CodeLocation(14, 4)}}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}



@mock.patch("flagging.FlaggingValidation.determine_variables", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
def test_reduce_lambda_CodeLocation(mock_determine_variables, mock_validate_returns_bool):
    flag_name = "FlagNameDefault"
    flag_feeders = {"ff1": int, "ff2": int}
    flag_dependencies = {}
    flag_info = FlagLogicInformation(
        used_variables={VariableInformation("ff1"): {CodeLocation(4, 11)},
                        VariableInformation("ff2"): {CodeLocation(6, 11)},
                        VariableInformation("a"): {CodeLocation(2, 16), CodeLocation(2, 22)},
                        VariableInformation("b"): {CodeLocation(2, 26), CodeLocation(2, 34)},
                        VariableInformation("f"): {CodeLocation(3, 10), CodeLocation(4, 24), CodeLocation(6, 24)}},
        assigned_variables={VariableInformation("f"): {CodeLocation(2, 0)},
                            VariableInformation("a"): {CodeLocation(2, 11)},
                            VariableInformation('b'): {CodeLocation(2, 13)}},
        referenced_functions={VariableInformation("reduce"): {CodeLocation(3, 3), CodeLocation(4, 17), CodeLocation(6, 17)}},
        defined_functions=dict(),
        defined_classes=dict(),
        referenced_modules=dict(),
        referenced_flags=dict(),
        return_points={CodeLocation(4, 4), CodeLocation(6, 4)},
        used_lambdas={"LAMBDA": {CodeLocation(2, 4)}},
        errors=[],
        flag_logic="""
        f = lambda a,b: a if (a > b) else b
        if reduce(f, [47,11,42,102,13]) > 100:
            return ff1 > reduce(f, [47,11,42,102,13])
        else:
            return ff2 < reduce(f, [47,11,42,102,13])""",
        validation_results=TypeValidationResults())
    result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_info)
    assert result.errors == {"LAMBDA": {CodeLocation(2, 4)},
                             VariableInformation("reduce"): {CodeLocation(3, 3),
                                                             CodeLocation(4, 17),
                                                             CodeLocation(6, 17)}}
    assert result.warnings == {}
    assert result.mypy_errors == {}
    assert result.mypy_warnings == {}
