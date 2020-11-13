import pytest
from flask import Flask
from handlers.routes import make_routes
from flag_data.FlaggingMongo import FlaggingMongo
from testcontainers.mongodb import MongoDbContainer
from integration_tests import MONGO_DOCKER_IMAGE
from app import _create_flagging_mongo
import json
import re

def make_flag_data_pretty(payload):
    data = payload.split("\\")
    my_dict = {}
    keys = ["valid", "message", "simple_message", "uuid", "flag_name", "flag_logic"]
    for i in range(0, len(data)):
        if data[i] in keys:
            my_dict[data[i]] = ""
            j = i
        else:
            my_dict[data[j]] = data[i]


@pytest.fixture
def client():
    app = Flask(__name__)
    # app.config["DEBUG"] = True
    app.config["TESTING"] = True
    flagging_mongo = _create_flagging_mongo()
    make_routes(app, flagging_mongo)
    client = app.test_client()
    return client

def test_flag_home(client):
    url = '/flag'
    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8")
    assert str_data == 'flag home page to go here'
    assert response.status_code == 200

def test_get_flags_no_flags(client):
    url = '/flag/get_flags'

    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8").replace("\n","")
    assert str_data == '{"flags":[]}'
    assert response.status_code == 200

def test_get_flag_ids_no_flag_ids(client):
    url = '/flag/get_flag_ids'

    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8").replace("\n", "")
    assert str_data == '{"_ids":[]}'
    assert response.status_code == 200

#get specific flag

#id does not exist
def test_get_specific_flag_does_not_exist(client):
    url = '/flag/get_specific_flag/111111111111111111111111'

    response = client.get(url)
    assert response.status_code == 404

#no id
def test_get_specific_flag_missing_id(client):
    url = "/flag/get_specific_flag"

    response = client.get(url)
    assert response.status_code == 401

#id not valid
def test_get_specific_flag_invalid_id(client):
    url = "flag/get_specific_flag/123"

    response = client.get(url)
    assert response.status_code == 406

#valid id, have to create flag first
def test_get_specific_flag_id_valid(client):
    #create valid flag first
    flag_creation_url = "flag/create_flag/XX/Flag1A"

    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #get new flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    #unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])
    print("hello")



#
# def test_flag_home(client):
#     res = client.get('/flag')
#     assert res.status_code == 200
#     assert str(res.get_data()) == """b'flag home page to go here'"""
#
# def test_flag_group_home(client):
#     res = client.get("/flag_group")
#     assert res.status_code == 200
#     assert str(res.get_data()) == """b'flag group home page to go here'"""
#
# def test_flag_dependencies_home(client):
#     res = client.get("/flag_dependency")
#     assert res.status_code == 200
#     assert str(res.get_data()) == """b'flag dependency home page to go here'"""