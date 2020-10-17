import os
from flask import Flask, jsonify, redirect
from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specif_flag_dependnecy, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag, get_all_flag_ids, get_specific_flag_logic
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names_in_flag_group, pull_flag_names, pull_flag_logic_information
from flag_data.FlaggingMongo import FlaggingMongo
# from api_service.FlaggingService import flag_api
from bson.objectid import ObjectId
import json

app = Flask(__name__)
# app.register_blueprint(flag_api)



#configure secret key
app.secret_key = os.urandom(24).hex()

def _create_flagging_mongo():
    return FlaggingMongo("mongodb://localhost:27017/flagging")



#hello world
@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route("/flag")
def flag_home_page():
    return "flag home page to go here"

@app.route("/flag_group")
def flag_group_home_page():
    return "flag group home page to go here"

@app.route("/flag_dependencies")
def flag_dependencies_home_page():
    return "flag dependencies home page to go here"


#flags
@app.route("/flag", methods=["GET"])
@app.route("/flag/<string:function>", methods=["GET", "POST", "PUT"])
@app.route("/flag/<string:function>/<string:flag_id>", methods=["GET"])
@app.route("/flag/<string:function>/<string:flag_id>/<string:flag_name>", methods=["GET", "POST", "PUT"])
def flag_action(function=None, flag_id=None, flag_name=None):
    if function is None:
        #route to flag home page
        return redirect(flag_home_page)

    else:
        if function == "get_all_flags":
            flags = get_all_flags(flagging_mongo)
            flags = [str(x) for x in flags]
            return jsonify({'flags': flags})

        if function == "get_all_flag_ids":
            flag_ids = get_all_flag_ids(flagging_mongo)
            flag_ids = [str(x) for x in flag_ids]
            return jsonify({"_ids": flag_ids})

        if function == "get_specific_flag":
            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = get_specific_flag(flag_id_object, existing_flag_ids, flagging_mongo)
            return jsonify(({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)}))

        if function == "get_specific_flag_logic":
            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = get_specific_flag_logic(flag_id_object, existing_flag_ids, flagging_mongo)
            return jsonify(({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid),
                             "data": flag_schema_object.data}))


        if function == "create_flag":
            #TODO
            # need to pull flag logic,
            # need method and function to return flag logic without direct reference
            # to mongo db in function

            flag_info = pull_flag_logic_information(dummy_flag=True)
            flag_schema_object = create_flag(flag_name, flag_info, flagging_mongo)
            return jsonify({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)})


        if function == "update_flag_name":
            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = update_flag_name(flag_id_object, flag_name, existing_flag_ids, flagging_mongo)
            return jsonify({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)})

        if function == "update_flag_logic":
            #TODO
            # need to pull flag logic,
            # need method and function to return flag logic without direct reference
            # to mongo db in function

            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_info = pull_flag_logic_information(dummy_flag_2=True)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = update_flag_logic(flag_id_object, flag_info, existing_flag_ids, flagging_mongo)
            return jsonify({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)})

        if function == "delete_flag":
            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = delete_flag(flag_id_object, existing_flag_ids, flagging_mongo)
            return jsonify({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)})

        if function == "duplicate_flag":
            existing_flag_ids = get_all_flag_ids(flagging_mongo)
            flag_id_object = ObjectId(flag_id)
            flag_schema_object = duplicate_flag(flag_id_object, existing_flag_ids, flagging_mongo)
            return jsonify({"valid": flag_schema_object.valid,
                             "message": flag_schema_object.message,
                             "uuid": str(flag_schema_object.uuid)})
        else:
             return redirect("/flag")

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