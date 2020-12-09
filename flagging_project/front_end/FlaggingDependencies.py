dependent_flag_column = "DEPENDENT_FLAGS"

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


