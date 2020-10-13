import os
from flask import Flask, jsonify
from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specif_flag_dependnecy, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names_in_flag_group, pull_flag_names
from flag_data.FlaggingMongo import FlaggingMongo






#intialize app
app = Flask(__name__)


#configure secret key
app.secret_key = os.urandom(24).hex()

def _create_flagging_mongo():
    return FlaggingMongo("mongodb://localhost:27017/flagging")

#hello world
@app.route('/')
def hello_world():
    return "Hello, World!"


#flags
@app.route("/flag/", methods=["GET"])
#@app.route("/flag/<string:function>/", methods=["GET", "POST", "PUT"])
#@app.route("/flag/<string:function>/<string:flag_id>/", methods=["GET", "POST", "PUT"])
@app.route("/flag/<string:function>/<string:flag_name>/", methods=["GET", "POST", "PUT"])
#@app.route("/flag/<string:function>/<string:flag_id>/<string:flag_name>/", methods=["GET", "POST", "PUT"])
def flag_action(function=None, flag_id=None, flag_name=None):
    if function is None:
        #route to flag home pag
        return jsonify
        return "flag_home_page"

    else:
        if function == "get_all_flags":
            print("in get_all_flags")
            print("flagging_mongo: " + str(flagging_mongo))
            flags = get_all_flags(flagging_mongo)
            print("have flags")
            print(flags)
            return jsonify({'flags': flags})


        if function == "get_specific_flag":
            existing_flags = get_all_flags(flagging_mongo)
            return(get_specific_flag(flag_id, existing_flags, flagging_mongo))


        if function == "create_flag":
            #TODO
            # need to pull flag logic,
            # need method and function to return flag logic without direct reference
            # to mongo db in function
            try:
                flag_schema_object = create_flag(flag_name, FlagLogicInformation(), flagging_mongo)
                return(jsonify({"new uuid": flag_schema_object.uuid,
                                "flagging_mongo_url": flagging_mongo.connection_url}))
            except Exception as e:
                return("error: " + str(e))


        if function == "update_flag_name":
            existing_flags = get_all_flags(flagging_mongo)
            return(update_flag_name(flag_id, flag_name, existing_flags, flagging_mongo))

        if function == "update_flag_logic":
            #TODO
            # need to pull flag logic,
            # need method and function to return flag logic without direct reference
            # to mongo db in function

            existing_flags = get_all_flags(flagging_mongo)
            return(update_flag_logic(flag_id, FlagLogicInformation(), existing_flags, flagging_mongo))

        if function == "delete_flag":
            existing_flags = get_all_flags(flagging_mongo)
            return(delete_flag(flag_id, existing_flags, flagging_mongo))

        if function == "duplicate_flag":
            existing_flags = get_all_flags(flagging_mongo)
            return(duplicate_flag(flag_id, existing_flags, flagging_mongo))

        else:
             return "flag_home_page"

#flag groups
@app.route("/flag_group/", methods=["GET"])
@app.route("/flag_group/<string:function>/", methods=["GET", "POST", "PUT"])
@app.route("/flag_group/<string:function>/<string:flag_group_id>/", methods=["GET", "POST", "PUT"])
@app.route("/flag_group/<string:function>/<string:flag_group_name>/", methods=["GET", "POST", "PUT"])
@app.route("/flag_group/<string:function>/<string:flag_group_id>/<string:flag_group_name>/", methods=["GET", "POST", "PUT"])
def flag_group_action(function=None, flag_group_id=None, flag_group_name=None):
    if function is None:
        #route to flag home pag
        return "flag_group_home_page"

    else:
        if function == "get_flag_groups":
            return(get_flag_groups(flagging_mongo))

        if function == "get_specific_flag_group":
            existing_flag_groups=get_flag_groups(flagging_mongo)
            return(get_specific_flag_group(flag_group_id, existing_flag_groups, flagging_mongo))

        if function == "create_flag_group":
            existing_flag_groups=get_flag_groups(flagging_mongo)
            return(create_flag_group(flag_group_name, existing_flag_groups, flagging_mongo))

        if function == "delete_flag_group":
            existing_flag_groups=get_flag_groups(flagging_mongo)
            return(delete_flag_group(flag_group_id, existing_flag_groups, flagging_mongo))

        if function == "add_flag_to_flag_group":
            #TODO
            # need method and function
            # to get existing flags in flag groups
            # and flags to be added (new flags)
            new_flags = []
            flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["FLAG1A"])
            existing_flags = get_all_flags(flagging_mongo)
            existing_flag_groups = get_flag_groups(flagging_mongo)
            return(add_flag_to_flag_group(flag_group_id=flag_group_id, new_flags=new_flags,
                                          existing_flags=existing_flags, existing_flag_groups=existing_flag_groups,
                                          flags_in_flag_group=flags_in_flag_group, flagging_mongo=flagging_mongo))

        if function == "remove_flag_from_flag_group":
            #TODO
            # need method and function
            # to get existing flags in flag groups
            # and flags to be removed (del_flags)
            del_flags = []
            flags_in_flag_group = pull_flag_names_in_flag_group(dummy_flag_names=["FLAG1A"])
            existing_flags = get_all_flags(flagging_mongo)
            existing_flag_groups = get_flag_groups(flagging_mongo)
            return(remove_flag_from_flag_group(flag_group_id=flag_group_id, del_flags=del_flags,
                                               existing_flags=existing_flags, existing_flag_groups=existing_flag_groups,
                                               flags_in_flag_group=flags_in_flag_group, flagging_mongo=flagging_mongo))

        if function == "duplicate_flag_group":
            existing_flag_groups = get_flag_groups(flagging_mongo)
            return(duplicate_flag_group(flag_group_id, existing_flag_groups, flagging_mongo))

        else:
             return "flag_group_home_page"

#flag_dependency
@app.route("/flag_dependency/", methods=["GET"])
@app.route("/flag_dependency/<string:function>/", methods=["GET", "POST", "PUT"])
@app.route("/flag_dependency/<string:function>/<string:flag_id>/", methods=["GET", "POST", "PUT"])
@app.route("/flag_dependency/<string:function>/<string:flag_name>/", methods=["GET", "POST", "PUT"])
def flag_dependency_action(function=None, flag_id=None, flag_name=None):
    if function is None:
        return "flag_dependency_home_page"
    else:
        if function == "get_flag_dependencies":
            return(get_flag_dependencies(flagging_mongo))

        if function == "get_specif_flag_dependnecy":
            existing_flag_deps = get_flag_dependencies(flagging_mongo)
            return(get_specif_flag_dependnecy(flag_id, existing_flag_deps, flagging_mongo))

        if function == "create_flag_dependency":
            #TODO
            # need to get dependent flags
            # flag_dependencies

            existing_flag_deps = get_flag_dependencies(flagging_mongo)
            flag_dependencies = pull_flag_names(dummy_flag_names=["FLAG1A"])
            return(create_flag_dependency(flag_name, existing_flag_deps, flag_dependencies, flagging_mongo))

        if function == "delete_flag_dependency":
            existing_flag_deps = get_flag_dependencies(flagging_mongo)
            return(delete_flag_dependency(flag_id, existing_flag_deps, flagging_mongo))

        if function == "add_dependencies_to_flag":
            #TODO
            # need to get dependent flags
            # new_dependencies

            new_dependencies = pull_flag_names(dummy_flag_names=["FLAG1A"])
            existing_flag_dep_keys = get_flag_dependencies(flagging_mongo)
            return(add_dependencies_to_flag(flag_id, existing_flag_dep_keys,
                                            new_dependencies, flagging_mongo))

        if function == "remove_dependencies_from_flag":
            #TODO
            # need to get dependent flags
            # rm_dependencies

            rm_dependencies = pull_flag_names(dummy_flag_names=["FLAG1A"])
            existing_flag_dep_keys = get_flag_dependencies(flagging_mongo)
            return(remove_dependencies_from_flag(flag_id, existing_flag_dep_keys,
                                                 rm_dependencies, flagging_mongo))

        else:
            return "flag_dependency_home_page"


#housekeeeping
if __name__ == "__main__":
    flagging_mongo = _create_flagging_mongo()
    app.run(debug=True)