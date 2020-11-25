from flask import Flask, jsonify, redirect, request, Response
from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specific_flag_dependency, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag, get_all_flag_ids, get_flag_group_ids, get_flag_group_names, \
    get_flag_group_flags, get_flag_names_in_flag_group, get_flag_dep_ids, move_flag_group_to_production, \
    move_flag_to_production, delete_all_flags, delete_all_flag_groups, delete_all_flag_dependencies
from flagging.FlagLogicInformation import FlagLogicInformation
from flag_names.FlagService import pull_flag_names_in_flag_group, pull_flag_names, \
    pull_flag_logic_information, get_valid_dummy_flag
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation
import json
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.ErrorInformation import ErrorInformation
from front_end.TransferFlagLogicInformation import _convert_TFLI_to_FLI


def make_routes(app, flagging_mongo):
    @app.route("/flag")
    def flag_home_page():
        return "flag home page to go here"

    @app.route("/flag_group")
    def flag_group_home_page():
        return "flag group home page to go here"

    @app.route("/flag_dependency")
    def flag_dependencies_home_page():
        return "flag dependency home page to go here"

    # flags
    @app.route("/flag", methods=["GET"])
    @app.route("/flag/<string:function>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag/<string:function>/<string:flag_id>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag/<string:function>/<string:flag_id>/<string:flag_name>", methods=["GET", "POST", "PUT"])
    def flag_action(function=None, flag_id=None, flag_name=None):
        # flagging_mongo = _create_flagging_mongo()
        if function is None:
            # route to flag home page
            return redirect(flag_home_page)

        else:
            if function == "get_flags":
                flags, response_code = get_all_flags(flagging_mongo)
                flags = [str(x) for x in flags]
                data = {'flags': flags}
                return data, response_code

            if function == "get_flag_ids":
                flag_ids, response_code = get_all_flag_ids(flagging_mongo)
                flag_ids = [str(x) for x in flag_ids]
                data = {"_ids": flag_ids}
                return data, response_code

            if function == "get_specific_flag":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = get_specific_flag(flag_id, existing_flag_ids, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "create_flag":
                try:
                    flag_info_transfer_object = request.get_json(force=True)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error reading flag data to create flag",
                            "simple_message": "error reading flag data to create flag"}
                    response_code = 500
                    return data, response_code
                try:
                    flag_info = _convert_TFLI_to_FLI(flag_info_transfer_object)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error converting flag data to proper form to create flag",
                            "simple_message": "error converting flag data to proper form to create flag"}
                    response_code = 500
                    return data, response_code
                flag_schema_object, response_code = create_flag(flag_name, flag_info, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "update_flag_name":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = update_flag_name(flag_id, flag_name, existing_flag_ids,
                                                                     flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "update_flag_logic":
                try:
                    flag_info_transfer_object = request.get_json(force=True)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error reading flag data to update flag logic",
                            "simple_message": "error reading flag data to update flag logic"}
                    response_code = 500
                    return data, response_code
                try:
                    flag_info = _convert_TFLI_to_FLI(flag_info_transfer_object)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error converting flag data to proper form to update flag logic",
                            "simple_message": "error converting flag data to proper form to update flag logic"}
                    response_code = 500
                    return data, response_code
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = update_flag_logic(flag_id, flag_info, existing_flag_ids,
                                                                      flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete_flag":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = delete_flag(flag_id, existing_flag_ids, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "duplicate_flag":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = duplicate_flag(flag_id, existing_flag_ids, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "move_flag_to_production":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = move_flag_to_production(flag_id, existing_flag_ids, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all_flags":
                flag_schema_object, response_code = delete_all_flags(flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "logic": flag_schema_object.logic}
                return data, response_code

            else:
                return redirect("/flag")

    # flag groups
    @app.route("/flag_group", methods=["GET"])
    @app.route("/flag_group/<string:function>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag_group/<string:function>/<string:flag_group_id>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag_group/<string:function>/<string:flag_group_id>/<string:flag_group_name>",
               methods=["GET", "POST", "PUT"])
    @app.route("/flag_group/<string:function>/<string:flag_group_id>/<string:flag_group_name>/<string:flag_id>",
               methods=["GET", "POST", "PUT"])
    def flag_group_action(function=None, flag_group_id=None, flag_group_name=None, flag_id=None):
        # flagging_mongo = _create_flagging_mongo()
        if function is None:
            # route to flag home pag
            return redirect(flag_group_home_page)

        else:
            if function == "get_flag_groups":
                flag_groups, response_code = get_flag_groups(flagging_mongo)
                flag_groups = [str(x) for x in flag_groups]
                data = {'flags_groups': flag_groups}
                return data, response_code

            if function == "get_flag_group_ids":
                flag_group_ids, response_code = get_flag_group_ids(flagging_mongo)
                flag_group_ids = [str(x) for x in flag_group_ids]
                data = {'flags_group_ids': flag_group_ids}
                return data, response_code

            if function == "get_flag_group_names":
                flag_group_names, response_code = get_flag_group_names(flagging_mongo)
                flag_group_names = [str(x) for x in flag_group_names]
                data = {'flag_group_names': flag_group_names}
                return data, response_code

            if function == "get_flag_group_flags":
                flag_group_ids, response_code_flag_group_ids = get_flag_group_ids(flagging_mongo)
                flag_schema_object, response_code = get_flag_group_flags(flag_group_id, flag_group_ids, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flags_in_flag_group": flag_schema_object.logic,
                        "flag_group_name": flag_schema_object.name}
                return data, response_code

            if function == "get_specific_flag_group":
                existing_flag_groups, response_code_id = get_flag_group_ids(flagging_mongo)
                flag_schema_object, response_code = get_specific_flag_group(flag_group_id, existing_flag_groups,
                                                                            flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flags_in_flag_group": flag_schema_object.logic,
                        "flag_group_name": flag_schema_object.name}
                return data, response_code

            if function == "create_flag_group":
                # TODO
                # need to pull flag logic,
                # need method and function to return flag logic without direct reference
                # to mongo db in function
                flag_groups_names, response_code_name = get_flag_group_names(flagging_mongo)
                flag_schema_object, response_code = create_flag_group(flag_group_name, flag_groups_names,
                                                                      flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete_flag_group":
                existing_flag_groups, response_code_ids = get_flag_group_ids(flagging_mongo)
                flag_schema_object, response_code = delete_flag_group(flag_group_id, existing_flag_groups,
                                                                      flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "fso_name": flag_schema_object.name,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "add_flag_to_flag_group":
                existing_flags, response_code_flag_ids = get_all_flag_ids(flagging_mongo)
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_mongo)
                flags_in_flag_group_schema, response_code_flags = get_flag_group_flags(flag_group_id,
                                                                                       existing_flag_groups,
                                                                                       flagging_mongo)
                flags_in_flag_group = flags_in_flag_group_schema.logic
                # if flags_in_flag_group_schema.valid:
                flag_schema_object, response_code = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                                                           new_flags=[flag_id],
                                                                           existing_flags=existing_flags,
                                                                           existing_flag_groups=existing_flag_groups,
                                                                           flags_in_flag_group=flags_in_flag_group,
                                                                           flagging_mongo=flagging_mongo)
                # else:
                #     flag_schema_object = FlaggingSchemaInformation(valid=False,
                #                                                    message="error in pulling flags for flag group" + str(
                #                                                        flag_group_id),
                #                                                    uuid=flag_group_id)
                #     response_code = 401
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "remove_flag_from_flag_group":
                del_flags = [flag_id]
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_mongo)
                flags_in_flag_group_schema, response_code_flags = get_flag_group_flags(flag_group_id,
                                                                                       existing_flag_groups,
                                                                                       flagging_mongo)
                flags_in_flag_group = flags_in_flag_group_schema.logic
                existing_flags, response_code_flag_ids = get_all_flag_ids(flagging_mongo)
                flag_schema_object, response_code = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                                                                del_flags=del_flags,
                                                                                existing_flags=existing_flags,
                                                                                existing_flag_groups=existing_flag_groups,
                                                                                flags_in_flag_group=flags_in_flag_group,
                                                                                flagging_mongo=flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "duplicate_flag_group":
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_mongo)
                flag_schema_object, response_code = duplicate_flag_group(flag_group_id, existing_flag_groups,
                                                                         flag_group_name, flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "move_flag_group_to_production":
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_mongo)
                flag_schema_object, response_code = move_flag_group_to_production(flag_group_id, existing_flag_groups,
                                                                                  flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all_flag_groups":
                flag_schema_object, response_code = delete_all_flag_groups(flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "name": flag_schema_object.name,
                        "fso_logic": flag_schema_object.logic}
                return data, response_code
            else:
                return redirect("/flag_group")

    # flag_dependency
    @app.route("/flag_dependency", methods=["GET"])
    @app.route("/flag_dependency/<string:function>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag_dependency/<string:function>/<string:flag_dep_id>", methods=["GET", "POST", "PUT"])
    def flag_dependency_action(function=None, flag_dep_id=None):
        # flagging_mongo = _create_flagging_mongo()
        if function is None:
            return redirect(flag_dependencies_home_page)
        else:
            if function == "get_flag_dependencies":
                flag_deps, response_code = get_flag_dependencies(flagging_mongo)
                flag_deps = [str(x) for x in flag_deps]
                data = {"flag_deps": flag_deps}
                return data, response_code

            if function == "get_specific_flag_dependency":
                existing_flag_dep_ids, response_code_ids = get_flag_dep_ids(flagging_mongo)
                flag_schema_object, response_code = get_specific_flag_dependency(flag_dep_id, existing_flag_dep_ids,
                                                                                 flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_name": flag_schema_object.name,
                        "flag_dep_flags": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all_flag_dependencies":
                flag_schema_object, response_code = delete_all_flag_dependencies(flagging_mongo)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_name": flag_schema_object.name,
                        "flag_dep_flags": flag_schema_object.logic}
                return data, response_code

            else:
                return redirect(flag_dependencies_home_page)