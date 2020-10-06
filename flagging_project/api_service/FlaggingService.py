from api_service.App import app
from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specif_flag_dependnecy, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag
from flag_data.FlaggingMongo import flagging_mongo


@app.route("/get_all_flags/")
def get_all_flags_service(flagging_mongo):
        get_all_flags
        flags = get_all_flags(flagging_mongo)
        return flags

@app.route("/get_specific_flag/<string: flag_id>/")
def get_specfic_flag_service(flagging_mongo, flag_id):
    existing_flags = get_all_flags(flagging_mongo)
    flag_schema_object = get_specific_flag(flag_id, existing_flags, flagging_mongo)
    return flag_schema_object