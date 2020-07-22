from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidationMyPy import validate_returns_boolean

from flagging.FlagLogicInformation import FlagLogicInformation


def validate_flag_logic(flag_feeders, flag_logic):

    return validate_flag_logic_information(flag_feeders=flag_feeders, flag_logic_info=determine_variables(flag_logic))

def validate_flag_logic_information(flag_feeders, flag_logic_info: FlagLogicInformation):
    results = FlaggingValidationResults()
    my_py_output = validate_returns_boolean(flag_logic_info, flag_feeders if flag_feeders else {})

    used_variables = dict(flag_logic_info.used_variables)
    for used_var in flag_logic_info.used_variables:
        if used_var.name in flag_feeders:
            del used_variables[used_var]

    for used_var in flag_logic_info.assigned_variables:
        try:
            del used_variables[used_var]
        except KeyError:
            # Assigned variable but has not been used
            results.add_warning(used_var)

    if used_variables:
        for unused in used_variables:
            results.add_error(unused)

    # do not allow user defined functions
    for func in dict(flag_logic_info.defined_functions):
        results.add_error(func)


    if my_py_output:
        #TODO
        # errors are a mix of VariableInformation objects and mypy dictionary output
        # check with Adam if that needs to change
        if my_py_output.validation_errors:
            for validation_error in my_py_output.validation_errors:
                results.add_error(validation_error)
        if my_py_output.other_errors:
            for other_error in my_py_output.other_errors:
                results.add_error(other_error)
        if my_py_output.warnings:
            for warning in my_py_output.warnings:
                results.add_warning(warning)


    return results


class FlaggingValidationResults:

    def __init__(self, errors=None, warnings=None):
        self.errors = errors if errors else []
        self.warnings = warnings if warnings else []

    def add_error(self, error):
        self.errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)

