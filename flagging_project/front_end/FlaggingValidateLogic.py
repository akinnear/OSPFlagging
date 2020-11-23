from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlagLogicInformation import FlagLogicInformation
from front_end.FlaggingDependencies import get_flag_dependencies
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.ReferencedFlag import ReferencedFlag


#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.


def validate_cyclical_logic(flag_id, flag_group_id, flag_logic_information:FlagLogicInformation(), flagging_mongo):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})

    #TODO
    # need flag_dependiceis from api call or direct query
    # only need to look at flags in flag group

    #dependenceis via name
    flag_deps_for_flag_group = flagging_mongo.get_flag_dep_by_flag_group_id(flag_group_id)
    flag_dependencies = {}
    if flag_id is not None:
        flag_name = flagging_mongo.get_flag_name(flag_id)
        flag_dependencies[flag_name] = {x for x in flag_logic_information.referenced_flags}
    for i in range(len(flag_deps_for_flag_group)):
        rf_key = flag_deps_for_flag_group[i]["FLAG_NAME"]
        rf_value = set()
        for j in range(len(flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"])):
            rf_value.add(flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"][j]["FLAG_NAME"])

        flag_dependencies[rf_key] = rf_value

    # depndenceis via RF object,
    # flag_deps_for_flag_group = flagging_mongo.get_flag_dep_by_flag_group_id(flag_group_id)
    # flag_dependencies = {}
    # flag_dependencies[ReferencedFlag(flag_name=flag_id, flag_group_id=flag_group_id)] = {x for x in flag_logic_information.referenced_flags}
    # for i in range(len(flag_deps_for_flag_group)):
    #     rf_key = ReferencedFlag(flag_name=flag_deps_for_flag_group[i]["FLAG_NAME"],
    #                        flag_group_id=flag_deps_for_flag_group[i]["FLAG_GROUP_ID"])
    #     rf_value = set()
    #     for j in range(len(flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"])):
    #         rf_value.add(ReferencedFlag(flag_name=flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"][j]["FLAG_NAME"],
    #                                    flag_group_id=flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"][j]["FLAG_GROUP_ID"]))
    #         if j == 0:
    #             rf_value.add(ReferencedFlag(flag_name="Flag1M",
    #             flag_group_id=flag_deps_for_flag_group[i]["DEPENDENT_FLAGS"][j]["FLAG_GROUP_ID"]))
    #
    #     flag_dependencies[rf_key] = rf_value

    #flag dependences becomes {RF(orgiinal_flag_name, flag_group_id): {RF(reference_flag_name, flag_grop_id), .... )},
    #                         {RF (flag_names from flag_deps_for_flag_group, flag_group_id)}
    #                         ...
    #                         {RF (flag_name from flag_deps_for_flag_group, flag_group_id)}}


    #TODO
    # perform full validation on user_logic via nodevisitor, mypy, and validation
    # mypy validation is part of full validation method, do not need explicit mypy validation call



    #validation
    validation_result = validate_flag_logic_information(flag_id, flag_feeders, flag_dependencies, flag_logic_information,
                                                        og_flag_included_in_flag_dep=True)

    #return errors and warning information
    return validation_result


def validate_logic(flag_name, flag_logic_information:FlagLogicInformation(), flagging_mongo):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})

    #TODO
    # need flag_dependiceis from api call or direct query
    # only need to look at flags in flag group




    #TODO
    # perform full validation on user_logic via nodevisitor, mypy, and validation
    # mypy validation is part of full validation method, do not need explicit mypy validation call



    #validation
    validation_result = validate_flag_logic_information(flag_name, flag_feeders, {}, flag_logic_information,
                                                        og_flag_included_in_flag_dep=False)

    #return errors and warning information
    return validation_result