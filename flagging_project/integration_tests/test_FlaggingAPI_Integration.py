import pytest
from app import app as flask_app
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flag_data.FlaggingMongo import FlaggingMongo, FLAGGING_DATABASE, FLAGGING_COLLECTION, FLAG_DEPENDENCIES, FLAG_GROUPS
from integration_tests import MONGO_DOCKER_IMAGE
from unittest import mock



def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)

def _create_flagging_mongo(container):
    return FlaggingMongo(_get_connection_string(container))

def _create_mongo_client(container):
    return MongoClient(_get_connection_string(container))



def _make_mongo():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_mongo(container) as flagging_mongo:
        return flagging_mongo


def _make_client():
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container,\
            _create_mongo_client(container) as client:
        return client



@pytest.fixture
def client():
    return flask_app.test_client()

@mock.patch("app._create_flagging_mongo", return_value=_make_mongo(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.get_db", return_value=_make_mongo().client["flagging_test"], autospec=True)
def test_get_flags(mock_client, mock_mongo, client):
    res = client.get("flag/get_flags")
    print('hello')


@mock.patch("app._create_flagging_mongo", return_value=_make_mongo(), autospec=True)
def test_get_flags_1(mock_mongo, client):
    res = client.get("flag/get_flags")
    print('hello')



def test_get_flags_2(client):
    res = client.get("flag/get_flags")
    print('hello')