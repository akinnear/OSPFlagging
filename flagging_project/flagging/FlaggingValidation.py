from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidationMyPy import validate_returns_boolean

from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation


def validate_flag_logic(flag_feeders, flag_logic):

    return validate_flag_logic_information(flag_feeders=flag_feeders,
                                           flag_logic_info=determine_variables(flag_logic))

def validate_flag_logic_information(flag_feeders, flag_logic_info: FlagLogicInformation):
    results = FlaggingValidationResults()
    # flag_dependency = flag_dependency if flag_dependency else {}
    my_py_output = validate_returns_boolean(flag_logic_info, flag_feeders if flag_feeders else {})


    for used_lambda, cl in flag_logic_info.used_lambdas.items():
        results.add_error(used_lambda, cl)

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

    # do not allow classes
    for def_class, cl in dict(flag_logic_info.defined_classes).items():
        results.add_error(def_class, cl)

    #add errors from node visitor output, FlagLogicInformation.Errors
    for fli_error in flag_logic_info.errors:
        results.add_error("FlagLogicInformationError " + str(fli_error.msg), {fli_error})

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

    #TODO
    # parse flag_dependency and assigned variables,
    # check if assigned variable is flag feeder and has reference to flag_dependency

    #TODO
    # if referenced_function not in defined_function,
    # then referenced_function must be in referenced_modules, else error
    ref_functions = dict(flag_logic_info.referenced_functions)
    def_functions = dict(flag_logic_info.defined_functions)
    ref_modules = dict(flag_logic_info.referenced_modules)
    for ref_func, cl in dict(flag_logic_info.referenced_functions):
        if ref_func.name in def_functions:
            del ref_functions[ref_func]
        if ref_func.name in ref_modules:
            del ref_functions[ref_func]

    #add error
    if ref_functions:
        for unused, cl in ref_functions.items():
            results.add_error(unused, cl)

    #warning if defined function is not used as referenced fucntion
    for def_func, cl in flag_logic_info.defined_functions.items():
        try:
            del ref_functions[def_func]
        except KeyError:
            # Assigned variable but has not been used
            results.add_warning(def_func, cl)




    return results


class FlaggingValidationResults:

    def __init__(self, errors=None, mypy_errors=None, warnings=None, mypy_warnings=None):
        self.errors = errors if errors else dict()
        self.mypy_errors = mypy_errors if mypy_errors else dict()
        self.warnings = warnings if warnings else dict()
        self.mypy_warnings = mypy_warnings if mypy_warnings else dict()


    def add_error(self, error, cl):
        if error not in self.errors.keys():
            self.errors.setdefault(error, set())
        self.errors[error].update(cl)


    def add_mypy_error(self, error, cl):
        if error not in self.mypy_errors.keys():
            self.mypy_errors.setdefault(error, set())
        self.mypy_errors[error].update(cl)

    def add_warning(self, warning, cl):
        if warning not in self.warnings.keys():
            self.warnings.setdefault(warning, set())
        self.warnings[warning].update(cl)

    def add_mypy_warning(self, warning, cl):
        if warning not in self.mypy_warnings.keys():
            self.mypy_warnings.setdefault(warning, set())
        self.mypy_warnings[warning].update(cl)






