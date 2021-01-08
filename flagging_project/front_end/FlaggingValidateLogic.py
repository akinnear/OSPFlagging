from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlagLogicInformation import FlagLogicInformation
from front_end.FlaggingDependencies import get_flag_dependencies
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.ReferencedFlag import ReferencedFlag


#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.


def validate_cyclical_logic(flag_id, flag_group_id, flag_logic_information:FlagLogicInformation(), flagging_dao):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})


    #dependenceis via name
    flag_deps_for_flag_group = flagging_dao.get_flag_dep_by_flag_group_id(flag_group_id)
    flag_dependencies = {}
    if flag_id is not None:
        flag_name = flagging_dao.get_flag_name(flag_id)
        flag_dependencies[flag_name] = {x for x in flag_logic_information.referenced_flags}
    for i in range(len(flag_deps_for_flag_group)):
        rf_key = flag_deps_for_flag_group[i]["FLAG_NAME"]
        rf_value = set()
        for j in range(len(flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"])):
            rf_value.add(flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"][j])

        flag_dependencies[rf_key] = rf_value


    #validation
    validation_result = validate_flag_logic_information(flag_id, flag_feeders, flag_dependencies, flag_logic_information,
                                                        og_flag_included_in_flag_dep=True)

    #return errors and warning information
    return validation_result


def validate_logic(flag_name, flag_logic_information:FlagLogicInformation(), flagging_dao):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})


    #validation
    validation_result = validate_flag_logic_information(flag_name, flag_feeders, {}, flag_logic_information,
                                                        og_flag_included_in_flag_dep=False)

    #return errors and warning information
    return validation_result