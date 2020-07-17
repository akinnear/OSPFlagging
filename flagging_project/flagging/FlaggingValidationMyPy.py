from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlagLogicInformation import FlagLogicInformation
import os
from mypy import api


def validate_returns_boolean(flagLogicInformation: FlagLogicInformation, flag_feeders) -> TypeValidationResults:
    """
    This function will attempt to run mypy and get the results out.
    A resulting warning is something like this:
    "Expected type 'bool', got 'int' instead"

    If nothing is returned from mypy then the result is valid else we return
    an error.

    :param flag_logic: The logic to test
    :return: An error object that shows possible typing errors
    """

    # Determine if we have a single line
    is_single_line = len(flagLogicInformation.flag_logic.strip().splitlines()) == 1

    spaced_flag_logic = os.linesep.join(
        [_process_line(is_single_line, line, flagLogicInformation.return_points) for line in flagLogicInformation.flag_logic.splitlines()])

    used_var_names = {str(var) for var in flagLogicInformation.used_variables}
    assigned_var_names = {str(var) for var in flagLogicInformation.assigned_variables}

    must_define_flag_feeders = used_var_names - assigned_var_names

    function_params = [f"{flag_feeder_name}: {flag_feeder_type.__name__}"
                       for (flag_feeder_name, flag_feeder_type) in flag_feeders.items()
                       if flag_feeder_name in must_define_flag_feeders]
    #TODO
    # ask Adam about inclusion of "account for extra passed parameters to pass mypy testing"
    # else assigned variables can cause "no-any-return other_error"
    # see test_FlaggingValidationMypy.test_mypy_normal_expression_explicit and remove "z:int" and
    # "account for extra passed parameters to pass mypy testing" code portion
    # to show error/issue
    ##account for extra passed parameters to pass mypy testing
    extra_function_params = [f"{flag_feeder_name}: {flag_feeder_type.__name__}"
                             for (flag_feeder_name, flag_feeder_type) in flag_feeders.items()
                             if flag_feeder_name not in must_define_flag_feeders]
    ##



    flag_feeder_names = {name for name in flag_feeders}
    must_define_flag_feeders = must_define_flag_feeders - flag_feeder_names

    function_params.extend([name for name in must_define_flag_feeders])

    func_variables = ", ".join(function_params)

    #TODO
    # ask Adam about inclusion of "account for extra passed parameters to pass mypy testing"
    # else assigned variables can cause "no-any-return other_error"
    # see test_FlaggingValidationMypy.test_mypy_normal_expression_explicit and remove "z:int" and
    # "account for extra passed parameters to pass mypy testing" code portion
    # to show error/issue
    ##account for extra passed parameters to pass mypy testing
    func_variables = func_variables + ", " + ", ".join(extra_function_params)
    ##

    typed_flag_logic_function = f"""\
def flag_function({func_variables}) -> bool:
{spaced_flag_logic}"""
    flag_function_lines = spaced_flag_logic.split('\n')
    result = api.run(["--show-error-codes", "--ignore-missing-imports", "--no-error-summary", "--strict-equality", "--show-column-numbers", "--warn-return-any", "--warn-unreachable", "-c", typed_flag_logic_function])
    type_validation = TypeValidationResults()

    if result[2] != 0:
        errors = [line.replace("<string>:", "") for line in result[0].split("\n") if line]
        for error in errors:
            error_code = error[error.find("[")+1:error.find("]")]
            #TODO
            # error_code_full, provides more information to
            # front end user to identify source of error
            error_code_full = error_code + ", " + error[error.find("error: ") + len("error: ")
                                                       : error.find(" [") - 1]
            orig_code_location = error[:error.find("error")-2]
            error_code_location_line = int(orig_code_location[:orig_code_location.find(":")]) - 1
            if error_code == "return-value":
                #incompatible return types, return something other than bool
                #column offset for "return" keyword
                type_validation.add_validation_error(error_code, CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=0))
            else:
                type_validation.add_other_error(error_code, CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=0))

    return type_validation


def _process_line(is_single_line, line, return_points):
    new_line = line
    if is_single_line and line.strip() and len(return_points) == 0:
        new_line = f"return {line}"
    return f"    {new_line}"
