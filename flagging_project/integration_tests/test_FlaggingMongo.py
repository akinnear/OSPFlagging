from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flag_data.FlaggingMongo import FlaggingMongo, FLAGGING_DATABASE, FLAGGING_COLLECTION, FLAG_DEPENDENCIES
from integration_tests import MONGO_DOCKER_IMAGE
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
from flagging.ErrorInformation import ErrorInformation
import datetime
import json

def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)


def _create_flagging_mongo(container):
    return FlaggingMongo(_get_connection_string(container))


def _create_mongo_client(container):
    return MongoClient(_get_connection_string(container))


def test_empty_db():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_mongo(container) as flagging_mongo:
        assert flagging_mongo.get_flags() == []


def test_flag_in_db():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_mongo(container) as flagging_mongo:
        # No data is in the database
        assert flagging_mongo.get_flags() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            db = client[FLAGGING_DATABASE]
            added_id = db[FLAGGING_COLLECTION].insert_one({'name': 'Test Flag'}).inserted_id

        flags = flagging_mongo.get_flags()
        # Only 1
        assert len(flags) == 1
        # The whole object
        assert flags[0]['_id'] == added_id

def test_get_flag_data_by_name():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_mongo(container) as flagging_mongo:

        assert flagging_mongo.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults()
            db = client[FLAGGING_DATABASE]
            id_1 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "UPDATE_TIMESTAMP": datetime.datetime.now()}).inserted_id

            #get flags
            flags = flagging_mongo.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "UPDATE_TIMESTAMP": datetime.datetime.now()}).inserted_id

            pulled_flag_1 = db[FLAGGING_COLLECTION].find({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find({"FLAG_NAME": flag_name_2})
            assert pulled_flag_1.get_flags()[0]["_id"] == id_1
            assert pulled_flag_2.get_flags()[0]["_id"] == id_2








def test_add_flag_dependencies():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_mongo(container) as flagging_mongo:

        assert flagging_mongo.get_flags() == []

        with _create_mongo_client(container) as client:

            flag_deps = flagging_mongo.get_flag_dependencies()
            assert flag_deps == []

            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "FLAG_DEPENDENCIES": flag_dependencies}).inserted_id
            flag_deps = flagging_mongo.get_flag_dependencies()
            assert len(flag_deps) == 1
            assert flag_deps[0]["_id"] == flag_deps_id_1
            assert flag_deps[0]["FLAG_NAME"] == flag_name
            assert flag_deps[0]["FLAG_DEPENDENCIES"] == flag_dependencies

# flag_validation_results = FlaggingValidationResults(errors={"my_add": {CodeLocation(2, 2)},
#                                                             VariableInformation("y"): {CodeLocation(2, 2)},
#                                                             "FlagLogicInformationError invalid syntax":
#                                                                 {ErrorInformation(CodeLocation(3, 5),
#                                                                                   "invalid syntax",
#                                                                                   "x = == = 5")},
#                                                             VariableInformation.create_var(
#                                                                 ["matplotlib", "plot"]): {
#                                                                 CodeLocation(2, 5)},
#                                                             },
#                                                     ModuleInformation("seaborn", "sns"): {
#     CodeLocation(1, 5)}
#                                                     mypy_errors={"mock_validation_error": {CodeLocation(1, 1)}})
#
