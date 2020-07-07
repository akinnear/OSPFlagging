from flagging.FlagFeederApp import determine_variables


def validate_flag_logic(flag_logic):
    return validate_flag_logic_information(determine_variables(flag_logic))


def validate_flag_logic_information(flag_feeders, flag_logic_info):
    results = FlaggingValidationResults()
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

    return results


class FlaggingValidationResults:

    def __init__(self, errors=None, warnings=None):
        self.errors = errors if errors else []
        self.warnings = warnings if warnings else []

    def add_error(self, error):
        self.errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)