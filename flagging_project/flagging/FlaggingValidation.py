from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidationMyPy import validate_returns_boolean
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.FlagErrorInformation import FlagErrorInformation
import pkg_resources
import platform
from stdlib_list import stdlib_list



def validate_flag_logic(flag_name, flag_feeders, flag_dependencies, flag_logic):

    return validate_flag_logic_information(flag_name=flag_name,
                                           flag_feeders=flag_feeders,
                                           flag_dependencies=flag_dependencies,
                                           flag_logic_info=determine_variables(flag_logic))

def validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_logic_info: FlagLogicInformation, **kwargs):
    og_flag_included_in_flag_dep = kwargs.get("og_flag_included_in_flag_dep", False)
    results = FlaggingValidationResults()
    flag_dependencies = flag_dependencies if flag_dependencies else {}
    my_py_output = validate_returns_boolean(flag_logic_info, flag_feeders if flag_feeders else {})


    for used_lambda, cl in flag_logic_info.used_lambdas.items():
        results.add_error(used_lambda, cl)

    used_variables = dict(flag_logic_info.used_variables)
    for used_var, cl in flag_logic_info.used_variables.items():
        if used_var.name in flag_feeders:
            del used_variables[used_var]
        elif used_var.name == "f":
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


    def check_flag_dependency(cyclical_flags, flag_dependencies, flag_history, flag_check):
        '''
        :param cyclical_flags: flags marked as cyclical
        :param flag_dependencies: full set of flag dependicies
        :param og_flag_dependencies: copy of full set of flag dependicies, to maintain original dependency
        :param flag_history: set of lists containing iterations of flag dependicies based on each dependency
        :param flag_check: check mark to determine if flag has been checked for dependency,
        flags not contained as referenced_flags in logic do not need to be checked for cyclical dependency
        :return: None
        '''
        og_flag_dependencies = flag_dependencies
        #if no flag_depencies, move to next original flag
        for original_flag, flag_deps in flag_dependencies.items():
            if not flag_check[original_flag]:
                # has depencies, parse dpendicies
                if flag_deps:

                    #check if flag is dependent on itself
                    if original_flag in flag_deps:
                        #found cyclical flag, mark flag as checkd and add to cyclical flag set
                        flag_check[original_flag] = True
                        cyclical_flags.append(original_flag)

                    new_flag_dependencies = []
                    #make sure each depedendent flag exists in flag depdency set
                    #otherwise we do not know if there is cyclical flag
                    #not necessary, only checking flags in flag group now
                    # for flag in flag_deps:
                    #     try:
                    #         for new_flag in list(flag_dependencies[flag]):
                    #             new_flag_dependencies.append(new_flag)
                    #     except KeyError as ke:
                    #         results.add_flag_error(flag, FlagErrorInformation(flag=flag,
                    #                                                           err_info="missing_flag",
                    #                                                           cl={CodeLocation(None, None)}))
                            # results.add_flag_error(str(ke).replace("'", ""), FlagErrorInformation(flag=str(ke).replace("'", "")),
                            #                                                                   err_info="missing_flag",
                            #                                                                   cl=CodeLocation(None, None))
                            # results.add_error(str(ke).replace("'", "") + "_missing_flag", {CodeLocation(None, None)})

                    #update with new iteration of flag depednecy
                    flag_dependencies[original_flag] = set(new_flag_dependencies)
                    flag_history[original_flag].append(set(new_flag_dependencies))

                    # check if flag history contains any duplicate sets,
                    # indicates cyclical logic outside of original flag
                    for i in range(len(flag_history[original_flag])):
                        if len(flag_history[original_flag]) - 1 != i:
                            if flag_history[original_flag][len(flag_history[original_flag])-1] == flag_history[original_flag][i]:
                                cyclical_flags.append(original_flag)
                                flag_check[original_flag] = True

                    #iterate with update flag_dependencies, flag_history, and flag_check
                    check_flag_dependency(cyclical_flags, flag_dependencies,
                                          flag_history, flag_check)
                else:
                    #flag check completed, move to next flag and restore orginal flag dependency for future validation
                    flag_check[original_flag] = True
                    flag_dependencies[original_flag] = og_flag_dependencies[original_flag]


    cyclical_flags = []
    flag_check = {}
    flag_history = {}
    #add flag_name and passed referenced_flags to flag_dependcies
    if not og_flag_included_in_flag_dep:
        flag_dependencies[flag_name] = flag_logic_info.referenced_flags.keys()
    if flag_dependencies:
        for flag in flag_dependencies.keys():
            #only check referenced_flags for cyclical flag dependicies
            (flag_check.update({flag: False}))
            if not og_flag_included_in_flag_dep:
                (flag_check.update({flag: False}) if flag in flag_logic_info.referenced_flags.keys() else flag_check.update({flag: True}))
            flag_history.update({flag: list()})

        check_flag_dependency(cyclical_flags, flag_dependencies, flag_history, flag_check)
        for flag in set(cyclical_flags):
            try:
                results.add_flag_error(flag, FlagErrorInformation(flag=flag,
                                                                  err_info="cyclical_flag",
                                                                  cl=flag_logic_info.referenced_flags[flag]))
                # results.add_error(flag + "_cyclical_flag", flag_logic_info.referenced_flags[flag])
            except KeyError as ke:
                results.add_flag_error(flag, FlagErrorInformation(flag=flag,
                                                                  err_info="cyclical_flag",
                                                                  cl={CodeLocation(None, None)}))


    # remove ref_functions that are built-ins
    ref_functions = dict(flag_logic_info.referenced_functions)
    for ref_func, ref_cl in dict(flag_logic_info.referenced_functions).items():
        if ref_func.name in __builtins__:
            del ref_functions[ref_func]

    #if non built in refereenced_funtion not in referenced_modules error
    ref_modules = dict(flag_logic_info.referenced_modules)
    for ref_func, cl in dict(flag_logic_info.referenced_functions).items():
        # remove functions that are part of imported modules
        if ref_func.name in [ref_modules.name for ref_modules, cl in ref_modules.items()] \
                or ref_func.name in [ref_modules.asname for ref_modules, cl in ref_modules.items()]:
            del ref_functions[ref_func]

    #add error for remaining functions, these are not imported
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
            ref_functions_list = sorted(["%s" % (i.name) for i in ref_functions.keys()])
            if ref_mod.name not in ref_functions_list and ref_mod.asname not in ref_functions_list:
                results.add_warning(ref_mod, cl_mod)
        else:
            results.add_warning(ref_mod, cl_mod)


    #check if imported modules are installed
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s" % (i.key)
                                      for i in installed_packages])

    # get list of standard built in modules, like math and os
    standard_mods = stdlib_list(str(platform.python_version())[0:3])
    standard_mods = sorted(standard_mods)



    for imported_module, cl_mod in dict(flag_logic_info.referenced_modules).items():
        #imported module is not installed nor is it part of standard library list
        if imported_module.name not in installed_packages_list and imported_module.name not in standard_mods:
            results.add_error(imported_module, cl_mod)

    # do not allow modules name and as name to appear in assigned variables
    for assigned_var, cl_av in dict(flag_logic_info.assigned_variables).items():
        if assigned_var.name in [key.name for key, cl in dict(flag_logic_info.referenced_modules).items()]\
                or assigned_var.name in [key.asname for key, cl in dict(flag_logic_info.referenced_modules).items()]:
            results.add_error(assigned_var, cl_av)







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

    def add_flag_error(self, flag, feo):
        self.errors[flag] = feo



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






