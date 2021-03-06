from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flag_data.FlaggingDAO import FlaggingDAO, FLAGGING_DATABASE, FLAGGING_COLLECTION, FLAG_DEPENDENCIES, FLAG_GROUPS
from integration_tests import MONGO_DOCKER_IMAGE
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
from flagging.ErrorInformation import ErrorInformation
import datetime
import pandas as pd



def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)


def _create_flagging_dao(container):
    return FlaggingDAO(_get_connection_string(container))


def _create_mongo_client(container):
    return MongoClient(_get_connection_string(container))


def test_empty_db():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        assert flagging_dao.get_flags() == []


def test_flag_in_db():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flags() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            #db = client[FLAGGING_DATABASE]
            added_id = flagging_dao.add_flag({'name': 'Test Flag'})

        flags = flagging_dao.get_flags()
        # Only 1
        assert len(flags) == 1
        # The whole object
        assert flags[0]['_id'] == added_id

def test_get_flag_data_by_name():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults()
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2



def test_remove_flag_based_on_name():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults()
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})
            flags = flagging_dao.get_flags()
            assert len(flags) == 2
            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

            #remove flag
            deleted_id = flagging_dao.remove_flag(id_1)
            flags = flagging_dao.get_flags()
            assert len(flags) == 1
            assert flags[0]["_id"] == id_2
            assert flags[0]["FLAG_NAME"] == flag_name_2
            assert pulled_flag_1["_id"] == deleted_id



# def test_update_flag_old():
#     with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
#             _create_flagging_dao(container) as flagging_dao:
#         assert flagging_dao.get_flags() == []
#
#         with _create_mongo_client(container) as client:
#             flag_name_1 = "Flag1A1A"
#             flag_status = "Development"
#             referenced_flags = "Flag3"
#             flag_validation_results = FlaggingValidationResults()
#             db = client[FLAGGING_DATABASE]
#             id_1 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_1,
#                                                        "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
#                                                        "REFERENCED_FLAGS": referenced_flags,
#                                                        "FLAG_STATUS": flag_status,
#                                                        "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id
#
#             # get flags
#             flags = flagging_dao.get_flags()
#             # Only 1
#             assert len(flags) == 1
#             # The whole object
#             assert flags[0]['_id'] == id_1
#
#             flag_name_2 = "FLAG2B2B"
#             id_2 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_2,
#                                                        "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
#                                                        "REFERENCED_FLAGS": referenced_flags,
#                                                        "FLAG_STATUS": flag_status,
#                                                        "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id
#
#             pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
#             pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})
#             flags = flagging_dao.get_flags()
#             assert len(flags) == 2
#             assert pulled_flag_1["_id"] == id_1
#             assert pulled_flag_2["_id"] == id_2
#
#             #update flag
#             flagging_dao.update_flag_old({"FLAG_NAME": flag_name_2}, {"FLAG_STATUS": "PRODUCTION"})
#             updated_flag = db[FLAGGING_COLLECTION].find_one({"FLAG_STATUS": "PRODUCTION"})
#             assert updated_flag["_id"] == id_2


def test_update_flag():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults()
            db = client[FLAGGING_DATABASE]
            id_1 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_1,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id

            # get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})
            flags = flagging_dao.get_flags()
            assert len(flags) == 2
            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

            #update flag
            updated_flag = flagging_dao.update_flag(flag=id_2, update_value="PRODUCTION", update_column="FLAG_STATUS")
            production_flag = db[FLAGGING_COLLECTION].find_one({"FLAG_STATUS": "PRODUCTION"})["_id"]
            assert updated_flag == id_2
            assert updated_flag == production_flag




def test_duplicate_flag():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults()
            db = client[FLAGGING_DATABASE]
            id_1 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_1,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id

            # get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = db[FLAGGING_COLLECTION].insert_one({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": vars(flag_validation_results),
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()}).inserted_id

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})
            flags = flagging_dao.get_flags()
            assert len(flags) == 2
            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

            #duplicate flag, new id
            duplicate_flag_1_id = flagging_dao.duplicate_flag(id_1)
            flags = flagging_dao.get_flags()
            assert len(flags) == 3
            assert duplicate_flag_1_id != id_1
            flag_1s = db[FLAGGING_COLLECTION].find({"FLAG_NAME": flag_name_1})
            flag_1_id = db[FLAGGING_COLLECTION].find({"_id": id_1})
            assert len(list(flag_1s)) == 2
            assert len(list(flag_1_id)) == 1

def test_flag_w_errors_1():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults(errors={"my_add": {CodeLocation(2, 2)}},
                                                                mypy_errors={"mypy_error": {CodeLocation(3, 4)}})
            flag_validation_information = [error for error in flag_validation_results.errors.keys()] + [mypy_error for mypy_error in flag_validation_results.mypy_errors.keys()]
            flag_validation_information = [error.__str__() for error in flag_validation_information if isinstance(error, object)]
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

def test_flag_w_errors_2():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults(errors={VariableInformation("x"): {CodeLocation(2, 2)}},
                                                                mypy_errors={"mypy_error": {CodeLocation(3, 4)}})
            flag_validation_information = [error for error in flag_validation_results.errors.keys()] + [mypy_error for mypy_error in flag_validation_results.mypy_errors.keys()]
            flag_validation_information = [error.__str__() for error in flag_validation_information if isinstance(error, object)]
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

def test_flag_w_errors_3():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults(errors={VariableInformation("x"): {CodeLocation(2, 2)},
                                                                        "FlagLogicInformationError invalid syntax":
                                                                            {ErrorInformation(CodeLocation(3, 5),
                                                                                       "invalid syntax",
                                                                                       "x = == = 5")}                                                        },
                                                                mypy_errors={"mypy_error": {CodeLocation(3, 4)}})
            flag_validation_information = [error for error in flag_validation_results.errors.keys()] + [mypy_error for mypy_error in flag_validation_results.mypy_errors.keys()]
            flag_validation_information = [error.__str__() for error in flag_validation_information if isinstance(error, object)]
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

def test_flag_w_errors_4():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults(errors={VariableInformation.create_var(["matplotlib", "plot"]): {CodeLocation(1, 1)}},
                                                                mypy_errors={"mypy_error": {CodeLocation(3, 4)}})
            flag_validation_information = [error for error in flag_validation_results.errors.keys()] + [mypy_error for mypy_error in flag_validation_results.mypy_errors.keys()]
            flag_validation_information = [error.__str__() for error in flag_validation_information if isinstance(error, object)]
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2

def test_flag_w_errors_5():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:
            flag_name_1 = "Flag1A1A"
            flag_status = "Development"
            referenced_flags = "Flag3"
            flag_validation_results = FlaggingValidationResults(errors={ModuleInformation("matplotlib", "plot"): {CodeLocation(1, 1)}},
                                                                mypy_errors={"mypy_error": {CodeLocation(3, 4)}})
            flag_validation_information = [error for error in flag_validation_results.errors.keys()] + [mypy_error for mypy_error in flag_validation_results.mypy_errors.keys()]
            flag_validation_information = [error.__str__() for error in flag_validation_information if isinstance(error, object)]
            db = client[FLAGGING_DATABASE]
            id_1 = flagging_dao.add_flag({"FLAG_NAME": flag_name_1,
                                                         "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                         "REFERENCED_FLAGS": referenced_flags,
                                                         "FLAG_STATUS":  flag_status,
                                                         "FLAG_TIMESTAMP": datetime.datetime.now()})

            #get flags
            flags = flagging_dao.get_flags()
            # Only 1
            assert len(flags) == 1
            # The whole object
            assert flags[0]['_id'] == id_1

            flag_name_2 = "FLAG2B2B"
            id_2 = flagging_dao.add_flag({"FLAG_NAME": flag_name_2,
                                                       "FLAG_VALIDATION_RESULTS": flag_validation_information,
                                                       "REFERENCED_FLAGS": referenced_flags,
                                                       "FLAG_STATUS": flag_status,
                                                       "FLAG_TIMESTAMP": datetime.datetime.now()})

            pulled_flag_1 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_1})
            pulled_flag_2 = db[FLAGGING_COLLECTION].find_one({"FLAG_NAME": flag_name_2})

            assert pulled_flag_1["_id"] == id_1
            assert pulled_flag_2["_id"] == id_2


#test get flag groups
def test_get_flag_groups():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            #db = client[FLAGGING_DATABASE]
            added_id = flagging_dao.add_flag_group({'name': 'Test Flag Group'})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == added_id


def test_add_flag_groups():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            #db = client[FLAGGING_DATABASE]
            flag_group_name_1 = "FLAG_GROUP_NAME_1"
            added_id = flagging_dao.add_flag_group({'NAME': flag_group_name_1})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == added_id

            #add another
            flag_group_name_2 = "FLAG_GROUP_NAME_2"
            added_id_2 = flagging_dao.add_flag_group({"NAME": flag_group_name_2 })
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 2
            assert flag_groups[1]["_id"] == added_id_2

#test get flag group by name
def test_pull_flag_group_by_name():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            db = client[FLAGGING_DATABASE]
            flag_group_name_1 = "FLAG_GROUP_NAME_1"
            id_1 = flagging_dao.add_flag_group({'FLAG_GROUP_NAME': flag_group_name_1})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == id_1

            #add another
            flag_group_name_2 = "FLAG_GROUP_NAME_2"
            id_2 = flagging_dao.add_flag_group({"FLAG_GROUP_NAME": flag_group_name_2})
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 2
            assert flag_groups[1]["_id"] == id_2

            #pull flag group based on name
            pulled_flag_group_1 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_1})
            pulled_flag_group_2 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_2})

            assert pulled_flag_group_1["_id"] == id_1
            assert pulled_flag_group_2["_id"] == id_2


def test_remove_flag_group_based_on_id():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            db = client[FLAGGING_DATABASE]
            flag_group_name_1 = "FLAG_GROUP_NAME_1"
            id_1 = flagging_dao.add_flag_group({'FLAG_GROUP_NAME': flag_group_name_1})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == id_1

            #add another
            flag_group_name_2 = "FLAG_GROUP_NAME_2"
            id_2 = flagging_dao.add_flag_group({"FLAG_GROUP_NAME": flag_group_name_2})
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 2
            assert flag_groups[1]["_id"] == id_2

            #pull flag group based on name
            pulled_flag_group_1 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_1})
            pulled_flag_group_2 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_2})

            assert pulled_flag_group_1["_id"] == id_1
            assert pulled_flag_group_2["_id"] == id_2

            #remove flag_group
            removed_flag_group_id = flagging_dao.remove_flag_group(id_1)
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 1
            assert removed_flag_group_id == id_1
            assert flag_groups[0]["_id"] == id_2
            assert flag_groups[0]["FLAG_GROUP_NAME"] == flag_group_name_2


def test_update_flag_group_based_on_id():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            db = client[FLAGGING_DATABASE]
            flag_group_name_1 = "FLAG_GROUP_NAME_1"
            id_1 = flagging_dao.add_flag_group({'FLAG_GROUP_NAME': flag_group_name_1,
                                                  "FLAGS": ["FLAG5", "FLAG6", "FLAG7"]})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == id_1

            #add another
            flag_group_name_2 = "FLAG_GROUP_NAME_2"
            id_2 = flagging_dao.add_flag_group({"FLAG_GROUP_NAME": flag_group_name_2,
                                                  "FLAGS": ["FLAG2", "FLAG3"]})
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 2
            assert flag_groups[1]["_id"] == id_2

            #pull flag group based on name
            pulled_flag_group_1 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_1})
            pulled_flag_group_2 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_2})

            assert pulled_flag_group_1["_id"] == id_1
            assert pulled_flag_group_2["_id"] == id_2

            # update flag group
            updated_flag_group_id = flagging_dao.update_flag_group(flag_group=id_2, update_value=["FLAG1", "FLAG2", "FLAG4"], update_column="FLAGS")
            assert updated_flag_group_id == id_2
            assert "FLAG1" in db[FLAG_GROUPS].find_one({"_id": updated_flag_group_id})["FLAGS"]
            assert "FLAG2" in db[FLAG_GROUPS].find_one({"_id": updated_flag_group_id})["FLAGS"]
            assert "FLAG4" in db[FLAG_GROUPS].find_one({"_id": updated_flag_group_id})["FLAGS"]
            assert "FLAG3" not in db[FLAG_GROUPS].find_one({"_id": updated_flag_group_id})["FLAGS"]

def test_duplicate_flag_group_based_on_id():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        # No data is in the database
        assert flagging_dao.get_flag_groups() == []

        # Add a flag to the database
        with _create_mongo_client(container) as client:
            db = client[FLAGGING_DATABASE]
            flag_group_name_1 = "FLAG_GROUP_NAME_1"
            id_1 = flagging_dao.add_flag_group({'FLAG_GROUP_NAME': flag_group_name_1,
                                                  "FLAGS": ["FLAG5", "FLAG6", "FLAG7"]})

            flag_groups = flagging_dao.get_flag_groups()
            # Only 1
            assert len(flag_groups) == 1
            # The whole object
            assert flag_groups[0]['_id'] == id_1

            #add another
            flag_group_name_2 = "FLAG_GROUP_NAME_2"
            id_2 = flagging_dao.add_flag_group({"FLAG_GROUP_NAME": flag_group_name_2,
                                                  "FLAGS": ["FLAG2", "FLAG3"]})
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 2
            assert flag_groups[1]["_id"] == id_2

            #pull flag group based on name
            pulled_flag_group_1 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_1})
            pulled_flag_group_2 = db[FLAG_GROUPS].find_one({"FLAG_GROUP_NAME": flag_group_name_2})

            assert pulled_flag_group_1["_id"] == id_1
            assert pulled_flag_group_2["_id"] == id_2

            flag_group_dup_id = flagging_dao.duplicate_flag_group(id_1)
            assert flag_group_dup_id != id_1
            flag_groups = flagging_dao.get_flag_groups()
            assert len(flag_groups) == 3

            df_flag_groups = pd.DataFrame(flag_groups)
            assert df_flag_groups[df_flag_groups["_id"] == flag_group_dup_id]["FLAG_GROUP_NAME"].item() == df_flag_groups[df_flag_groups["_id"] == id_1]["FLAG_GROUP_NAME"].item()





def test_add_flag_dependencies():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:

            flag_deps = flagging_dao.get_flag_dependencies()
            assert flag_deps == []

            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 1
            assert flag_deps[0]["_id"] == flag_deps_id_1
            assert flag_deps[0]["FLAG_NAME"] == flag_name
            assert flag_deps[0]["DEPENDENT_FLAGS"] == flag_dependencies

            flag_deps_id_2 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": "FLAG9",
                                                              "DEPENDENT_FLAGS": ["FLAG3"]}).inserted_id

            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 2




#get flag deps collection
def test_get_flag_deps():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:

            flag_deps = flagging_dao.get_flag_dependencies()
            assert flag_deps == []

            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 1
            assert flag_deps[0]["_id"] == flag_deps_id_1
            assert flag_deps[0]["FLAG_NAME"] == flag_name
            assert flag_deps[0]["DEPENDENT_FLAGS"] == flag_dependencies

            flag_deps_id_2 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": "FLAG9",
                                                              "DEPENDENT_FLAGS": ["FLAG3"]}).inserted_id

            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 2

def test_add_dependencies_to_flag():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:

            flag_deps = flagging_dao.get_flag_dependencies()
            assert flag_deps == []

            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 1
            assert flag_deps[0]["_id"] == flag_deps_id_1
            assert flag_deps[0]["FLAG_NAME"] == flag_name
            assert flag_deps[0]["DEPENDENT_FLAGS"] == flag_dependencies

            flag_deps_id_2 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": "FLAG9",
                                                              "DEPENDENT_FLAGS": ["FLAG3"]}).inserted_id

            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 2

            #add FLAG9 dependent on FLAG4
            id_flag_9 = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG9"})["_id"]
            flag_deps_id_add = flagging_dao.add_specific_flag_dependencies(flag=id_flag_9, new_deps=["FLAG4"], dependent_flag_column="DEPENDENT_FLAGS")
            assert flag_deps_id_add == flag_deps_id_2

            #get len of deps for FLAG9
            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_add})["DEPENDENT_FLAGS"]) == 2
            assert "FLAG4" in db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_2})["DEPENDENT_FLAGS"]
            assert id_flag_9 == db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG9"})["_id"]

def test_add_dependencies_to_flag_2():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        assert flagging_dao.get_flags() == []

        with _create_mongo_client(container) as client:

            flag_deps = flagging_dao.get_flag_dependencies()
            assert flag_deps == []

            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 1
            assert flag_deps[0]["_id"] == flag_deps_id_1
            assert flag_deps[0]["FLAG_NAME"] == flag_name
            assert flag_deps[0]["DEPENDENT_FLAGS"] == flag_dependencies

            flag_deps_id_2 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": "FLAG9",
                                                              "DEPENDENT_FLAGS": ["FLAG3"]}).inserted_id

            flag_deps = flagging_dao.get_flag_dependencies()
            assert len(flag_deps) == 2

            #add FLAG9 dependent on FLAG4
            id_flag_9 = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG9"})["_id"]
            flag_deps_id_add = flagging_dao.add_specific_flag_dependencies(flag=id_flag_9, new_deps=["FLAG4"], dependent_flag_column="DEPENDENT_FLAGS")
            assert flag_deps_id_add == flag_deps_id_2

            #get len of deps for FLAG9
            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_add})["DEPENDENT_FLAGS"]) == 2
            assert "FLAG4" in db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_2})["DEPENDENT_FLAGS"]

            #check id on flag 9
            id_flag_9_check = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG9"})["_id"]
            assert id_flag_9 == id_flag_9_check


            #add FLAG9 dependent on FLAG6, FLAG7
            flag_deps_id_add_2 = flagging_dao.add_specific_flag_dependencies(flag=id_flag_9, new_deps=["FLAG6", "FLAG7"], dependent_flag_column="DEPENDENT_FLAGS")
            assert flag_deps_id_add_2 == flag_deps_id_2

            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_add_2})["DEPENDENT_FLAGS"]) == 4
            assert "FLAG7" in db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_2})["DEPENDENT_FLAGS"]
            assert "FLAG4" in db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_2})["DEPENDENT_FLAGS"]


#remove deps from flag
def test_remove_deps_from_flag():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
        _create_flagging_dao(container) as flagging_dao:

        with _create_mongo_client(container) as client:
            #add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                              "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            flag_deps_id_2 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": "FLAG9",
                                                              "DEPENDENT_FLAGS": ["FLAG3"]}).inserted_id
            id_flag_9 = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG9"})["_id"]
            flag_deps_id_add = flagging_dao.add_specific_flag_dependencies(flag=id_flag_9, new_deps=["FLAG4", "FLAG6", "FLAG7"], dependent_flag_column="DEPENDENT_FLAGS")

            #remove FLAG4 dependency from FLAG9
            flag_deps_id_rm = flagging_dao.remove_specific_flag_dependencies(flag=id_flag_9, rm_deps=["FLAG4"], dependent_flag_column="DEPENDENT_FLAGS")
            assert id_flag_9 == flag_deps_id_rm
            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]) == 3
            assert "FLAG4" not in db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]
            assert "FLAG7" in db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]

            #romve FLAG5, FLAG6, FLAG7 dependency from FLAG9, FLAG5 not in set, no action
            flag_deps_id_rm_2 = flagging_dao.remove_specific_flag_dependencies(flag=id_flag_9, rm_deps=["FLAG5", "FLAG6", "FLAG7"], dependent_flag_column="DEPENDENT_FLAGS")
            assert id_flag_9 == flag_deps_id_rm_2
            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]) == 1
            assert "FLAG6" not in db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]
            assert "FLAG7" not in db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]
            assert "FLAG3" in db[FLAG_DEPENDENCIES].find_one({"_id": id_flag_9})["DEPENDENT_FLAGS"]



#add new flag key
def test_add_new_flag_deps_key():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        with _create_mongo_client(container) as client:
            # add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                               "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            new_flag_deps_key = flagging_dao.add_flag_dependencies({"FLAG_NAME": "FLAG3",
                                                                      "DEPENDENT_FLAGS": ["FLAG1", "FLAG2", "FLAG4"]})
            flag_3_id = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG3"})["_id"]
            assert flag_3_id == new_flag_deps_key
            assert len(db[FLAG_DEPENDENCIES].find_one({"_id": new_flag_deps_key})["DEPENDENT_FLAGS"]) == 3
            assert len(flagging_dao.get_flag_dependencies()) == 2
            assert "FLAG1" in db[FLAG_DEPENDENCIES].find_one({"_id": flag_3_id})["DEPENDENT_FLAGS"]

#remove flag dep key
def test_remove_flag_deps_key():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        with _create_mongo_client(container) as client:
            # add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                               "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            new_flag_deps_key = flagging_dao.add_flag_dependencies({"FLAG_NAME": "FLAG3",
                                                                      "DEPENDENT_FLAGS": ["FLAG1", "FLAG2", "FLAG4"]})

            #remove flag_key for FLAG1
            flag_1_id = db[FLAG_DEPENDENCIES].find_one({"FLAG_NAME": "FLAG1"})["_id"]
            flagging_dao.remove_flag_dependencies(flag_dep_id=flag_1_id)
            assert len(flagging_dao.get_flag_dependencies()) == 1
            assert db[FLAG_DEPENDENCIES].find_one({"_id": flag_deps_id_1}) == None
            assert db[FLAG_DEPENDENCIES].find_one({"_id": new_flag_deps_key})["FLAG_NAME"] == "FLAG3"
            assert flagging_dao.get_flag_dependencies()[0]["FLAG_NAME"] == "FLAG3"

def test_update_flag_dependencies():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        with _create_mongo_client(container) as client:
            # add flag_deps
            db = client[FLAGGING_DATABASE]
            flag_name = "FLAG1"
            flag_dependencies = ["FLAG9", "FLAG3"]
            flag_deps_id_1 = db[FLAG_DEPENDENCIES].insert_one({"FLAG_NAME": flag_name,
                                                               "DEPENDENT_FLAGS": flag_dependencies}).inserted_id
            #update flag1 deps
            updated_flag_1_deps = flagging_dao.update_flag_dependencies(flag=flag_deps_id_1, dependent_flag_value=["FLAG2", "FLAG8"], dependent_flag_column="DEPENDENT_FLAGS")
            assert "FLAG8" in db[FLAG_DEPENDENCIES].find_one({"_id": updated_flag_1_deps})["DEPENDENT_FLAGS"]
            assert "FLAG2" in db[FLAG_DEPENDENCIES].find_one({"_id": updated_flag_1_deps})["DEPENDENT_FLAGS"]
            assert "FLAG9" not in db[FLAG_DEPENDENCIES].find_one({"_id": updated_flag_1_deps})["DEPENDENT_FLAGS"]
            assert "FLAG3" not in db[FLAG_DEPENDENCIES].find_one({"_id": updated_flag_1_deps})["DEPENDENT_FLAGS"]

