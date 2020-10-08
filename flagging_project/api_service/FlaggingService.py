from front_end.FlaggingSchemaService import get_all_flags, get_specific_flag, \
    get_flag_groups, get_specific_flag_group, get_flag_dependencies, get_specif_flag_dependnecy, \
    create_flag, update_flag_name, update_flag_logic, delete_flag, create_flag_group, \
    delete_flag_group, add_flag_to_flag_group, remove_flag_from_flag_group, duplicate_flag, \
    duplicate_flag_group, create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag
from flask_pymongo import PyMongo
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging_project.api_service.App import app
from flask import jsonify
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flagging_project.flag_data.FlaggingMongo import FlaggingMongo, FLAGGING_DATABASE, FLAGGING_COLLECTION, FLAG_DEPENDENCIES, FLAG_GROUPS
from api_service import MONGO_DOCKER_IMAGE


#configure pymongo to integrate with flask
def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)

def _create_flagging_mongo(container):
    return FlaggingMongo(_get_connection_string(container))

container = MongoDbContainer(MONGO_DOCKER_IMAGE)
app.config["MONGO_URI"] = _create_flagging_mongo(container)
mongo = PyMongo(app)

#test simple add flag
@app.route("/create_flag/<string:flag_name>/", methods=["POST", "GET"])
def create_flag_service(flag_name):
    flag_schema_object_created = create_flag(flag_name, FlagLogicInformation(), mongo)
    return jsonify(
        valid=flag_schema_object_created.valid,
        message=flag_schema_object_created.message,
        uuid=flag_schema_object_created.uuid)

@app.route("/get_all_flags/", methods=["GET"])
def get_all_flags_service():
        flags = get_all_flags(mongo)
        return flags

@app.route("/get_specific_flag/<string:flag_id>/", methods=["GET"])
def get_specific_flag_service(flag_id):
    existing_flags = get_all_flags(mongo)
    flag_schema_object = get_specific_flag(flag_id, existing_flags, mongo)
    print("flag_schema_object.valid: " + flag_schema_object.valid)
    print("\n")
    print("flag_schema_objet.message: " + flag_schema_object.message)
    print("\n")
    print("flag_schema_object.uuid: " + flag_schema_object.uuid)
    return flag_schema_object

# @app.route("/create_flag/<string: flag_name>/", methods=["POST", "GET"])
# def create_flag_service(flag_name):
#     existing_flags = get_all_flags(mongo)
#     #TODO
#     # need actual flag logic information object based off of data from front end
#     flag_schema_object_created = create_flag(flag_name, FlagLogicInformation(), mongo)
#     print("flag_schema_object.valid: " + flag_schema_object_created.valid)
#     print("\n")
#     print("flag_schema_object.message: " + flag_schema_object_created.message)
#     print("\n")
#     print("flag_schema_object.uuid: " + flag_schema_object_created.uuid)
#
#     flag_schema_object_pulled = get_specific_flag(flag_schema_object_created.uuid, existing_flags, mongo)
#     print("flag_schema_object.valid: " + flag_schema_object_pulled.valid)
#     print("\n")
#     print("flag_schema_object.message: " + flag_schema_object_pulled.message)
#     print("\n")
#     print("flag_schema_object.uuid: " + flag_schema_object_pulled.uuid)
#     return flag_schema_object_pulled