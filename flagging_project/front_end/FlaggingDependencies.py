from flag_data.FlaggingMongo import FlaggingMongo
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation

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
def add_flag_dependencies(flag, new_deps: [], existing_flags: [], flagging_mongo: FlaggingMongo):
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
    elif new_deps is None or new_deps.empty:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="no new flag dependencies were identified")
    #make sure flag exists
    elif flag not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag " + flag + " does not exist")

    elif len(new_deps_flag_does_not_exist) > 0:
        if len(new_deps_flag_does_not_exist) == 1:
            flagging_message = "the following flags attempting to be added as new dependencies do not exist: " + new_deps_flag_does_not_exist[0]
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flagging_message)
        else:
            flagging_message = "the following flags attempting to be added as new dependencies do not exist: " + (", ".join(new_deps_flag_does_not_exist))
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message=flagging_message)

    #get current dependency in flag


    #check if any of the new deps already exist as dependecy in flag

    #get the full set of deps for each flag in new_deps

    #run cyclical check for as each new deps is added as dep to flag
