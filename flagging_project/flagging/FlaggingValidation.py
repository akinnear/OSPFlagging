from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidationMyPy import validate_returns_boolean

from flagging.FlagLogicInformation import FlagLogicInformation


def validate_flag_logic(flag_feeders, flag_logic):

    return validate_flag_logic_information(flag_feeders=flag_feeders, flag_logic_info=determine_variables(flag_logic))

def validate_flag_logic_information(flag_feeders, flag_logic_info: FlagLogicInformation):
    results = FlaggingValidationResults()
    my_py_output = validate_returns_boolean(flag_logic_info, flag_feeders if flag_feeders else {})

    used_variables = dict(flag_logic_info.used_variables)
    for used_var, cl in flag_logic_info.used_variables.items():
        if used_var.name in flag_feeders:
            del used_variables[used_var]

    for used_var, cl in flag_logic_info.assigned_variables.items():
        try:
            del used_variables[used_var]
        except KeyError:
            # Assigned variable but has not been used
            results.add_warning(used_var, cl)

    if used_variables:
        for unused, cl in used_variables.items():
            results.add_error(unused, cl)

    # do not allow user defined functions
    for func, cl in dict(flag_logic_info.defined_functions).items():
        results.add_error(func, cl)


    if my_py_output:
        #TODO
        # errors are a mix of VariableInformation objects and mypy dictionary output
        # check with Adam if that needs to change
        if my_py_output.validation_errors:
            for validation_error, cl in my_py_output.validation_errors.items():
                results.add_mypy_error(validation_error, cl)
        if my_py_output.other_errors:
            for other_error, cl in my_py_output.other_errors.items():
                results.add_mypy_error(other_error, cl)
        if my_py_output.warnings:
            for warning, cl in my_py_output.warnings.items():
                results.add_mypy_warning(warning, cl)


    return results


class FlaggingValidationResults:

    def __init__(self, errors=None, mypy_errors=None, warnings=None, mypy_warnings=None):
        self.errors = errors if errors else dict()
        self.mypy_errors = mypy_errors if mypy_errors else dict()
        self.warnings = warnings if warnings else dict()
        self.mypy_warnings = mypy_warnings if mypy_warnings else dict()

    def add_error(self, error, cl):
        self.errors[error] = cl

    def add_mypy_error(self, error, cl):
        self.mypy_errors[error].add(cl)

    def add_warning(self, warning, cl):
        self.warnings[warning] = cl

    def add_mypy_warning(self, warning, cl):
        self.mypy_warnings[warning].add(cl)




