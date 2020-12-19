from flask import Flask, jsonify, redirect, request, Response
from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specific_flag_dependency, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag, get_all_flag_ids, get_flag_group_ids, get_flag_group_names, \
    get_flag_group_flags, get_flag_names_in_flag_group, get_flag_dep_ids, move_flag_group_to_production, \
    move_flag_to_production, delete_all_flags, delete_all_flag_groups, delete_all_flag_dependencies
from flagging.FlaggingNodeVisitor import determine_variables


def make_routes(app, flagging_dao):
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
        if function is None:
            # route to flag home page
            return redirect(flag_home_page)

        else:
            if function == "get":
                flags, response_code = get_all_flags(flagging_dao)
                # flags = [str(x) for x in flags]
                for flag in flags:
                    flag["_id"] = str(flag["_id"])
                data = {'flags': flags}
                return data, response_code

            if function == "get_ids":
                flag_ids, response_code = get_all_flag_ids(flagging_dao)
                flag_ids = [str(x) for x in flag_ids]
                data = {"_ids": flag_ids}
                return data, response_code

            if function == "get_specific":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = get_specific_flag(flag_id, existing_flag_ids, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "create":
                try:
                    flag_payload = request.get_json(force=True)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error reading flag data to create flag",
                            "simple_message": "error reading flag data to create flag"}
                    response_code = 500
                    return data, response_code
                try:
                    flag_info = determine_variables(flag_payload["FLAG_LOGIC"])
                except Exception as e:
                    data = {"valid": False,
                            "message": "error converting flag data to proper form to create flag",
                            "simple_message": "error converting flag data to proper form to create flag"}
                    response_code = 500
                    return data, response_code
                flag_schema_object, response_code = create_flag(flag_name, flag_info, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "update_name":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = update_flag_name(flag_id, flag_name, existing_flag_ids,
                                                                     flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "update_logic":
                try:
                    flag_payload = request.get_json(force=True)
                except Exception as e:
                    data = {"valid": False,
                            "message": "error reading flag data to update flag logic",
                            "simple_message": "error reading flag data to update flag logic"}
                    response_code = 400
                    return data, response_code
                try:
                    flag_info = determine_variables(flag_payload["FLAG_LOGIC"])
                except Exception as e:
                    data = {"valid": False,
                            "message": "error converting flag data to proper form to update flag logic",
                            "simple_message": "error converting flag data to proper form to update flag logic"}
                    response_code = 400
                    return data, response_code
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = update_flag_logic(flag_id, flag_info, existing_flag_ids,
                                                                      flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = delete_flag(flag_id, existing_flag_ids, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "duplicate":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = duplicate_flag(flag_id, existing_flag_ids, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "move_to_production":
                existing_flag_ids, response_code_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = move_flag_to_production(flag_id, existing_flag_ids, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all":
                flag_schema_object, response_code = delete_all_flags(flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_name": flag_schema_object.name,
                        "flag_logic": flag_schema_object.logic}
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
        if function is None:
            # route to flag home pag
            return redirect(flag_group_home_page)

        else:
            if function == "get":
                flag_groups, response_code = get_flag_groups(flagging_dao)
                for flag_group in flag_groups:
                    flag_group["_id"] = str(flag_group["_id"])
                    if len(flag_group["FLAGS_IN_GROUP"]) > 0:
                        flag_group["FLAGS_IN_GROUP"] = [str(x) for x in flag_group["FLAGS_IN_GROUP"]]
                data = {"flag_groups": flag_groups}
                return data, response_code

            if function == "get_ids":
                flag_group_ids, response_code = get_flag_group_ids(flagging_dao)
                flag_group_ids = [str(x) for x in flag_group_ids]
                data = {'_ids': flag_group_ids}
                return data, response_code

            if function == "get_names":
                flag_group_names, response_code = get_flag_group_names(flagging_dao)
                flag_group_names = [str(x) for x in flag_group_names]
                data = {'flag_group_names': flag_group_names}
                return data, response_code

            if function == "get_flags":
                flag_group_ids, response_code_flag_group_ids = get_flag_group_ids(flagging_dao)
                flag_schema_object, response_code = get_flag_group_flags(flag_group_id, flag_group_ids, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flags_in_flag_group": flag_schema_object.logic,
                        "flag_group_name": flag_schema_object.name}
                return data, response_code

            if function == "get_specific":
                existing_flag_groups, response_code_id = get_flag_group_ids(flagging_dao)
                flag_schema_object, response_code = get_specific_flag_group(flag_group_id, existing_flag_groups,
                                                                            flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flags_in_flag_group": flag_schema_object.logic,
                        "flag_group_name": flag_schema_object.name}
                return data, response_code

            if function == "create":
                flag_groups_names, response_code_name = get_flag_group_names(flagging_dao)
                flag_schema_object, response_code = create_flag_group(flag_group_name, flag_groups_names,
                                                                      flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "delete":
                existing_flag_groups, response_code_ids = get_flag_group_ids(flagging_dao)
                flag_schema_object, response_code = delete_flag_group(flag_group_id, existing_flag_groups,
                                                                      flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "flag_group_name": flag_schema_object.name,
                        "uuid": str(flag_schema_object.uuid),
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "add_flag":
                existing_flags, response_code_flag_ids = get_all_flag_ids(flagging_dao)
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_dao)
                flags_in_flag_group_schema, response_code_flags = get_flag_group_flags(flag_group_id,
                                                                                       existing_flag_groups,
                                                                                       flagging_dao)
                flags_in_flag_group = flags_in_flag_group_schema.logic
                # if flags_in_flag_group_schema.valid:
                flag_schema_object, response_code = add_flag_to_flag_group(flag_group_id=flag_group_id,
                                                                           new_flags=[flag_id],
                                                                           existing_flags=existing_flags,
                                                                           existing_flag_groups=existing_flag_groups,
                                                                           flags_in_flag_group=flags_in_flag_group,
                                                                           flagging_dao=flagging_dao)
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
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "remove_flag":
                del_flags = [flag_id]
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_dao)
                flags_in_flag_group_schema, response_code_flags = get_flag_group_flags(flag_group_id,
                                                                                       existing_flag_groups,
                                                                                       flagging_dao)
                flags_in_flag_group = flags_in_flag_group_schema.logic
                existing_flags, response_code_flag_ids = get_all_flag_ids(flagging_dao)
                flag_schema_object, response_code = remove_flag_from_flag_group(flag_group_id=flag_group_id,
                                                                                del_flags=del_flags,
                                                                                existing_flags=existing_flags,
                                                                                existing_flag_groups=existing_flag_groups,
                                                                                flags_in_flag_group=flags_in_flag_group,
                                                                                flagging_dao=flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "duplicate":
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_dao)
                flag_schema_object, response_code = duplicate_flag_group(flag_group_id, existing_flag_groups,
                                                                         flag_group_name, flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "move_to_production":
                existing_flag_groups, response_code_flag_group_ids = get_flag_group_ids(flagging_dao)
                flag_schema_object, response_code = move_flag_group_to_production(flag_group_id, existing_flag_groups,
                                                                                  flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all":
                flag_schema_object, response_code = delete_all_flag_groups(flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "flag_group_name": flag_schema_object.name,
                        "flags_in_flag_group": flag_schema_object.logic}
                return data, response_code
            else:
                return redirect("/flag_group")

    # flag_dependency
    @app.route("/flag_dependency", methods=["GET"])
    @app.route("/flag_dependency/<string:function>", methods=["GET", "POST", "PUT", "DELETE"])
    @app.route("/flag_dependency/<string:function>/<string:flag_dep_id>", methods=["GET", "POST", "PUT"])
    def flag_dependency_action(function=None, flag_dep_id=None):
        if function is None:
            return redirect(flag_dependencies_home_page)
        else:
            if function == "get":
                flag_deps, response_code = get_flag_dependencies(flagging_dao)
                for flag_dep in flag_deps:
                    flag_dep["_id"] = str(flag_dep["_id"])
                    flag_dep["FLAG_ID"] = str(flag_dep["_FLAG_ID"])
                    flag_dep["FLAG_GROUP_ID"] = str(flag_dep["FLAG_GROUP_ID"])
                data = {"flag_deps": flag_deps}
                return data, response_code

            if function == "get_specific":
                existing_flag_dep_ids, response_code_ids = get_flag_dep_ids(flagging_dao)
                flag_schema_object, response_code = get_specific_flag_dependency(flag_dep_id, existing_flag_dep_ids,
                                                                                 flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_name": flag_schema_object.name,
                        "flag_dep_flags": flag_schema_object.logic}
                return data, response_code

            if function == "delete_all":
                flag_schema_object, response_code = delete_all_flag_dependencies(flagging_dao)
                data = {"valid": flag_schema_object.valid,
                        "message": flag_schema_object.message,
                        "simple_message": flag_schema_object.simple_message,
                        "uuid": str(flag_schema_object.uuid),
                        "fso_name": flag_schema_object.name,
                        "flag_dep_flags": flag_schema_object.logic}
                return data, response_code

            else:
                return redirect(flag_dependencies_home_page)