from flag_data.FlaggingMongo import FlaggingMongo
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
from flagging.FlaggingValidation import validate_flag_logic_information
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.FlagErrorInformation import FlagErrorInformation

#A call to get flag dependencies
def get_flag_dependencies(*args, **kwargs):
    #api endpoint of db endpoint
    #hard code dependencies for now
    flag_dependencies = {"Flag1": {"Flag8"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {},
     "Flag9": {"Flag10"},
     "Flag10": {"Flag9"}}

    dummy_flag_deps = kwargs.get("dummy_flag_deps", None)
    if dummy_flag_deps:
        flag_dependencies = dummy_flag_deps
    return flag_dependencies

#function to add depedency to flag
def add_flag_dependencies(flag, new_deps: [], existing_flags: [], current_flag_dependencies, flagging_mongo: FlaggingMongo):
    flag_schema_object = None
    #remove any possible duplicates from new_deps
    new_deps = list(dict.fromkeys(new_deps))

    # make sure each flag in new_deps exists
    new_deps_flag_does_not_exist = []
    for new_dep in new_deps:
        if new_dep not in existing_flags:
            new_deps_flag_does_not_exist.append(new_dep)

    #make sure flag is not None
    if flag is None:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag name not specified")
    #make sure new_deps is not None
    elif new_deps is None or len(new_deps) == 0:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="no new flag dependencies were identified")
    #make sure flag exists
    elif flag not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag " + flag + " does not exist")

    elif len(new_deps_flag_does_not_exist) > 0:
        if len(new_deps_flag_does_not_exist) == 1:
            flagging_message = "the following flag attempting to be added as new dependencies do not exist: " + new_deps_flag_does_not_exist[0]
        else:
            flagging_message = "the following flags attempting to be added as new dependencies do not exist: " + (", ".join(new_deps_flag_does_not_exist))
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message=flagging_message)

    #get current dependency in flag
    current_flag_deps = flagging_mongo.get_specific_flag_dependencies(flag)

    #check if any of the new deps already exist as dependecy in flag
    duplicate_deps = []
    for new_dep in new_deps:
        if new_dep in current_flag_deps:
            duplicate_deps.append(new_dep)
    if len(duplicate_deps) > 0:
        if len(duplicate_deps) == 1:
            flagging_message = "the follow flag attempting to be added as a new dependency already exists as a dependency (duplicate dependency): " + duplicate_deps[0]
        else:
            flagging_message = "the follow flags attempting to be added as a new dependency already exists as a dependency (duplicate dependency): " + (", ".join(duplicate_deps))
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message=flagging_message)

    #get the full set of deps for each flag in new_deps
    #note, this might not be necessary
    new_deps_dict = {}
    for new_dep in new_deps:
        new_deps_dict[new_dep] = flagging_mongo.get_specific_flag_dependencies(new_dep)

    #run cyclical check for as each new deps is added as dep to flag
    '''
    flag_name = current_flag
    flag_feeders = None
    flag_dependencies = all flag dependencies
    flag_info = FlagLogicInformation(referenced_flags = current flags deps and new flag deps
    '''

    all_deps = current_flag_deps + new_deps
    all_deps_dict = {}
    for dep in all_deps:
        all_deps_dict[dep] = {CodeLocation(0, 0)}
    cyclical_check = validate_flag_logic_information(flag_name=flag,
                                                     flag_feeders=None,
                                                     flag_dependencies=current_flag_dependencies,
                                                     flag_info=FlagLogicInformation(referenced_flags=all_deps_dict))

    cyclical_errors = []
    for k, v in cyclical_check.items():
        if FlagErrorInformation in v:
            cyclical_errors.append(k)
    if len(cyclical_errors) > 0:
        if len(cyclical_errors) == 1:
            flagging_message = "the following flag dependency resulted in cyclical dependencies: " + cyclical_errors[0]
        else:
            flagging_message = "the following flag dependencies resulted in cyclical dependencies: " + (", ".join(cyclical_errors))
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message=flagging_message)

    if flag_schema_object == None:
        #no errors, update flag dependenceis
        flag_with_updated_deps = flagging_mongo.add_specific_flag_dependencies(flag, new_deps=new_deps, dependent_flag_column="DEPENDENT_FLAGS")
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="the following flag has been updated with new dependencies: " + flag,
                                                       uuid=flag_with_updated_deps)

    return flag_schema_object
