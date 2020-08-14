from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidationMyPy import validate_returns_boolean

from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation


def validate_flag_logic(flag_feeders, flag_dependencies, flag_logic):

    return validate_flag_logic_information(flag_feeders=flag_feeders,
                                           flag_dependencies=flag_dependencies,
                                           flag_logic_info=determine_variables(flag_logic))

def validate_flag_logic_information(flag_feeders, flag_dependencies, flag_logic_info: FlagLogicInformation):
    results = FlaggingValidationResults()
    flag_dependencies = flag_dependencies if flag_dependencies else {}
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
    # flag dependeny
    # use recursion,
    # flag depenencies are equivelent to referenced_flags.keys() for the logic
    # therefore, flag dependencies will look like
    # {"FLAG NAME": {referenced_flags.keys()}
    # will need to parse the flag depencies for each flag in referenced_flags.keys()
    # if FLAG Name is contained at any point in referenced_flags.keys() for all flags,
    # then error
    def check_flag_dependency(cyclic_flags, flag_dependencies, og_flag_dependencies,
                              flag_history, flag_check):

        #if no flag_depencies, move to next original flag
        for original_flag, flag_deps in flag_dependencies.items():
            if not flag_check[original_flag]:
                if flag_deps:

                    #has depencies, parse dpendicies
                    if original_flag in flag_deps:

                        #stop, cyclic error
                        flag_check[original_flag] = True
                        cyclic_flags.append(original_flag)

                    new_flag_dependencies = []
                    for flag in flag_deps:
                        try:
                            for new_flag in list(flag_dependencies[flag]):
                                new_flag_dependencies.append(new_flag)
                        except KeyError as ke:
                            results.add_error(str(ke).replace("'", "") + "_missing_flag", {CodeLocation(0, 0)})


                    flag_dependencies[original_flag] = set(new_flag_dependencies)
                    flag_history[original_flag].append(set(new_flag_dependencies))

                    # check if flag history contains any duplicate sets,
                    # indicates cyclic logic outside of original flag
                    for i in range(len(flag_history[original_flag])):
                        if len(flag_history[original_flag]) - 1 != i:
                            if flag_history[original_flag][len(flag_history[original_flag])-1] == flag_history[original_flag][i]:
                                cyclic_flags.append(original_flag)
                                flag_check[original_flag] = True

                    check_flag_dependency(cyclic_flags, flag_dependencies, og_flag_dependencies,
                                          flag_history, flag_check)
                else:
                    flag_check[original_flag] = True
                    flag_dependencies[original_flag] = og_flag_dependencies[original_flag]


    cyclic_flags = []
    flag_check = {}
    flag_history = {}
    if flag_dependencies:
        for flag in flag_dependencies.keys():
            flag_check.update({flag: False})
            flag_history.update({flag: list()})
        og_flag_dependencies = flag_dependencies

        check_flag_dependency(cyclic_flags, flag_dependencies, og_flag_dependencies,
                              flag_history, flag_check)
        for flag in set(cyclic_flags):
            #TODO
            # proper code location for cyclic flag
            results.add_error(flag + "_cyclic_flag", {CodeLocation(0,0)})


    # remove ref_functions that are built-ins
    ref_functions = dict(flag_logic_info.referenced_functions)
    for ref_func, ref_cl in dict(flag_logic_info.referenced_functions).items():
        if ref_func.name in __builtins__:
            del ref_functions[ref_func]

    #if non built in refereenced_funtion not in referenced_modules, error
    ref_modules = dict(flag_logic_info.referenced_modules)
    for ref_func, cl in dict(flag_logic_info.referenced_functions).items():
        # if ref_func.name in ref_modules:
        #     del ref_functions[ref_func]
        # if ref_func in ref_modules:
        #     del ref_functions[ref_func]
        if ref_func.name in [ref_modules.name for ref_modules, cl in ref_modules.items()] \
                or ref_func.name in [ref_modules.asname for ref_modules, cl in ref_modules.items()]:
            del ref_functions[ref_func]


    #add error
    if ref_functions:
        for unused, cl in ref_functions.items():
            results.add_error(unused, cl)

    #check if imported modules in non built in referenced fucntions
    ref_functions = dict(flag_logic_info.referenced_functions)
    for ref_func, ref_cl in dict(flag_logic_info.referenced_functions).items():
        if ref_func.name in __builtins__:
            del ref_functions[ref_func]
    for ref_mod, cl_mod in flag_logic_info.referenced_modules.items():
        if ref_functions:
            for ref_func, cl_func in ref_functions.items():
                if ref_mod.name != ref_func.name and ref_mod.asname != ref_func.name:
                    results.add_warning(ref_mod, cl_mod)
        else:
            results.add_warning(ref_mod, cl_mod)

    #TODO
    # check if imported modules are installed


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






