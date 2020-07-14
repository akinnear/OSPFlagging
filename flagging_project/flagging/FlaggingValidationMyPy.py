from flagging.FlaggingNodeVisitor import FlagFeederNodeVisitor, CodeLocation
import os
from mypy import api

class TypeValidationResults:
    def __init__(self, validation_errors=None, other_errors=None, warnings=None):
        self.validation_errors = validation_errors if validation_errors else []
        self.other_errors = other_errors if other_errors else []
        self.warnings = warnings if warnings else []

    def add_validation_error(self, error):
        self.validation_errors.append(error)

    def add_other_error(self, error):
        self.other_errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)

def _validate_returns_boolean(flag_logic, is_single_line, return_points, nv: FlagFeederNodeVisitor,
                              flag_feeders):
    """
    This function will attempt to run mypy and get the results out.
    A resulting warning is something like this:
    "Expected type 'bool', got 'int' instead"

    If nothing is returned from mypy then the result is valid else we return
    an error.

    :param flag_logic: The logic to test
    :return: An error object that shows possible typing errors
    """

    spaced_flag_logic = os.linesep.join(
        [_process_line(is_single_line, line, return_points) for line in flag_logic.splitlines()])

    used_var_names = {str(var) for var in nv.used_variables}
    assigned_var_names = {str(var) for var in nv.assigned_variables}

    must_define_flag_feeders = used_var_names - assigned_var_names

    function_params = [f"{flag_feeder_name}: {flag_feeder_type.__name__}"
                       for (flag_feeder_name, flag_feeder_type) in flag_feeders.items()
                       if flag_feeder_name in must_define_flag_feeders]

    flag_feeder_names = {name for name in flag_feeders}
    must_define_flag_feeders = must_define_flag_feeders - flag_feeder_names

    function_params.extend([name for name in must_define_flag_feeders])

    func_variables = ", ".join(function_params)

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
                type_validation.add_validation_error({error_code: CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=0)})
            else:
                type_validation.add_other_error({error_code: CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=0)})

    return type_validation


def _process_line(is_single_line, line, return_points):
    new_line = line
    if is_single_line and line.strip() and len(return_points) == 0:
        new_line = f"return {line}"
    return f"    {new_line}"
