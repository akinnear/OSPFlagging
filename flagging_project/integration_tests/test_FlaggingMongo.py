from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flag_data.FlaggingMongo import FlaggingMongo, FLAGGING_DATABASE, FLAGGING_COLLECTION
from integration_tests import MONGO_DOCKER_IMAGE


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
