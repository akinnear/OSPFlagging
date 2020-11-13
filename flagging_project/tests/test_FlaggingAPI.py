import pytest
from flask import Flask
from handlers.routes import make_routes
from flag_data.FlaggingMongo import FlaggingMongo
from testcontainers.mongodb import MongoDbContainer
from integration_tests import MONGO_DOCKER_IMAGE
from app import _create_flagging_mongo
import json
import re

# def make_flag_data_pretty(payload):
#     data = payload.split("\\")
#     my_dict = {}
#     keys = ["valid", "message", "simple_message", "uuid", "flag_name", "flag_logic"]
#     for i in range(0, len(data)):
#         if data[i] in keys:
#             my_dict[data[i]] = ""
#             j = i
#         else:
#             my_dict[data[j]] = data[i]


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
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    url = '/flag/get_flags'
    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8").replace("\n","")
    assert str_data == '{"flags":[]}'
    assert response.status_code == 200

def test_get_flag_ids_no_flag_ids(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

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
    #delete all flags first
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

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
    #call valid get specific flag
    specific_flag_url = "flag/get_specific_flag/" + id
    response = client.get(specific_flag_url)
    assert response.status_code == 200

    #delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200



#create flag, missing flag name
def create_flag_missing_flag_name_1(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    #create flag, no name
    flag_creation_url = "flag/create_flag"
    response = client.post(flag_creation_url)
    assert response.status_code == 401


def create_flag_missing_flag_name_2(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag, no name
    flag_creation_url = "flag/create_flag/XX"
    response = client.post(flag_creation_url)
    assert response.status_code == 401


#create flag, valid
def create_flag_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

