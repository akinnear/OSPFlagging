import pytest
from flask import Flask
from handlers.FlaggingAPI import make_routes
from flag_data.FlaggingMongo import FlaggingMongo
from testcontainers.mongodb import MongoDbContainer
from integration_tests import MONGO_DOCKER_IMAGE
from app import _create_flagging_mongo
import json
import re
from random_object_id import generate

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

#test flag home page
def test_flag_home(client):
    url = '/flag'
    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8")
    assert str_data == 'flag home page to go here'
    assert response.status_code == 200

#test get flags no flags
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

#test get flag ids no ids
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

#get specific flag, id does not exist
def test_get_specific_flag_does_not_exist(client):
    url = '/flag/get_specific_flag/111111111111111111111111'

    response = client.get(url)
    assert response.status_code == 404

#get specific flag, no id
def test_get_specific_flag_missing_id(client):
    url = "/flag/get_specific_flag"

    response = client.get(url)
    assert response.status_code == 400

#get specifif flag, id not valid
def test_get_specific_flag_invalid_id(client):
    url = "flag/get_specific_flag/123"

    response = client.get(url)
    assert response.status_code == 400

#get specific flag, valid id, have to create flag first
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
def test_create_flag_missing_flag_name_1(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    #create flag, no name
    flag_creation_url = "flag/create_flag"
    response = client.post(flag_creation_url)
    assert response.status_code == 400

def test_create_flag_missing_flag_name_2(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag, no name
    flag_creation_url = "flag/create_flag/XX/"
    response = client.post(flag_creation_url)
    assert response.status_code >= 400

#create flag, valid
def test_create_flag_valid(client):
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

#duplicate flag, missing flag id
def test_duplicate_flag_missing_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    flag_duplicate_missing_id_url = "flag/duplicate_flag"
    response = client.post(flag_duplicate_missing_id_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#duplicate flag, flag id does not exist
def test_duplicate_flag_id_does_not_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200


    # get new flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])
    new_id = str(generate())
    while new_id == id:
        new_id = str(generate())

    url_duplicate_flag_does_not_exist = "flag/duplicate_flag/" + new_id
    response = client.post(url_duplicate_flag_does_not_exist)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#duplicate flag, invalid flag id
def test_duplicate_flag_invalid_flag_id(client):
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    url_invalid_duplicate_flag = "flag/duplicate_flag/1A"
    response = client.post(url_invalid_duplicate_flag)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#dupplicate flag, valid
def test_duplicate_flag_id_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #get new flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])


    url_duplicate_flag_valid = "flag/duplicate_flag/" + id
    response = client.post(url_duplicate_flag_valid)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, missing flag id
def test_update_flag_name_missing_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #missing_id
    flag_update_name_url = "flag/update_flag_name"
    response = client.put(flag_update_name_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, missing new flag name
def test_update_flag_name_missing_name(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get new flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #missing name
    flag_update_name_url = "flag/update_flag_name/" + id
    response = client.put(flag_update_name_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, invalid flag id
def test_update_flag_name_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #missing_id
    flag_update_name_url = "flag/update_flag_name/1A/name"
    response = client.put(flag_update_name_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, flag id does not exist
def test_update_flag_name_flag_id_not_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #generate distinct new id
    new_id = str(generate())
    while new_id == id:
        new_id = str(generate())

    #missing_id
    flag_update_name_url = "flag/update_flag_name/" + new_id + "/name"
    response = client.put(flag_update_name_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, flag in more than one flag group
def test_update_flag_name_flag_in_multi_groups(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    #delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    #delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create 2nd flag group
    flag_group_creation_url_2 = "flag_group/create_flag_group/XX/FlagGroup2B"
    response = client.post(flag_group_creation_url_2)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])


    #add flag to flag group 1
    add_flag_url = "flag_group/add_flag_to_flag_group/"
    response = client.put(add_flag_url + flag_group_id_1 + "/name/" + flag_id)
    assert response.status_code == 200

    #add flag to flag group 2
    response = client.put(add_flag_url + flag_group_id_2 + "/name/" + flag_id)
    assert response.status_code == 200

    #attempt to update flag name
    update_flag_name_2_url = "flag/update_flag_name/" + flag_id + "/Flag_New_Name_1A"
    response = client.post(update_flag_name_2_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#update flag name, new name is same as old name
def test_update_flag_name_non_unique_name(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])


    #missing_id
    flag_update_name_url = "flag/update_flag_name/" + id + "/Flag1A"
    response = client.put(flag_update_name_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag name, valid
def test_update_flag_name_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # missing_id
    flag_update_name_url = "flag/update_flag_name/" + id + "/Flag2B"
    response = client.put(flag_update_name_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag logic, missing flag id
def test_update_flag_logic_missing_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #put missing id
    update_logic_url = "flag/update_flag_logic"
    response = client.put(update_logic_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag logic, flag id does not exist
def test_update_flag_logic_id_does_not_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create unique new id
    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    #call incorrect id
    url_incorrect_id = "flag/update_flag_logic/" + new_id
    response = client.put(url_incorrect_id)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag logic, invalid flag id
def test_update_flag_logic_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #invalid id
    url_invalid_id = "flag/update_flag_logic/1A1A"
    response = client.put(url_invalid_id)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#update flag logic, flag in more than one flag group
def test_update_flag_logic_multi_group(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create 2nd flag group
    flag_group_creation_url_2 = "flag_group/create_flag_group/XX/FlagGroup2B"
    response = client.post(flag_group_creation_url_2)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])

    # add flag to flag group 1
    add_flag_url = "flag_group/add_flag_to_flag_group/"
    response = client.put(add_flag_url + flag_group_id_1 + "/name/" + flag_id)
    assert response.status_code == 200

    # add flag to flag group 2
    response = client.put(add_flag_url + flag_group_id_2 + "/name/" + flag_id)
    assert response.status_code == 200

    # attempt to update flag logic
    update_flag_logic_2_url = "flag/update_flag_logic/" + flag_id + "/Flag_New_Name_1A"
    response = client.post(update_flag_logic_2_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#update flag logic, valid
def test_update_flag_logic_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #update logic default update
    url_update_logic = "flag/update_flag_logic/" + id
    response = client.put(url_update_logic)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#delete flag, missing flag id
def test_delete_flag_missing_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #url missing id
    flag_delete_url = "flag/delete_flag"
    response = client.delete(flag_delete_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#delete flag, flag id does not exist
def test_delete_flag_id_does_not_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create unique new id
    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    #delete missing id
    url_missing_id = "flag/delete_flag/" + new_id
    response = client.delete(url_missing_id)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#delete flag, invalid flag id
def test_delete_flag_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #invaid id url
    url_invalid_id = "flag/delete_flag/1A1A"
    response = client.delete(url_invalid_id)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#delete flag, flag in more than one flag group
def test_delete_flag_mulit_group(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get flag id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create 2nd flag group
    flag_group_creation_url_2 = "flag_group/create_flag_group/XX/FlagGroup2B"
    response = client.post(flag_group_creation_url_2)
    assert response.status_code == 200

    # get flag group ids
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_group_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])

    # add flag to flag group 1
    add_flag_url = "flag_group/add_flag_to_flag_group/"
    response = client.put(add_flag_url + flag_group_id_1 + "/name/" + flag_id)
    assert response.status_code == 200

    # add flag to flag group 2
    response = client.put(add_flag_url + flag_group_id_2 + "/name/" + flag_id)
    assert response.status_code == 200

    # attempt to delete flag
    delete_flag_url = "flag/delete_flag/" + flag_id
    response = client.delete(delete_flag_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#delete flag, valid
def test_delete_flag_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #delete flag
    delete_flag_url = "flag/delete_flag/" + id
    response = client.delete(delete_flag_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#move flag to production, missing id
def test_move_flag_to_production_missing_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #move to production
    flag_production_url = "flag/move_flag_to_production"
    response = client.put(flag_production_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#move flag to production, id does not exist
def test_move_flag_to_production_id_no_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #generate new id
    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    #move to production
    flag_production_url = "flag/move_flag_to_production/" + new_id
    response = client.put(flag_production_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#move flag to production, invalid id
def test_move_flag_to_production_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    #flag production
    flag_production_url = "flag/move_flag_to_production/2A1A"
    response = client.put(flag_production_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#move flag to production, error in flag
def test_move_flag_to_production_error_in_flag(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #production flag
    flag_production_url = "flag/move_flag_to_production/" + id
    response = client.put(flag_production_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

#TODO
# move flag to production, valid

#get flag groups
def test_get_flag_groups(client):
    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    #create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get flag group
    flag_group_get_url = "flag_group/get_flag_groups"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag group ids
def test_get_flag_group_ids(client):
    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    #create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get flag group
    flag_group_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag group names
def test_get_flag_group_names(client):
    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    #create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get flag group
    flag_group_get_url = "flag_group/get_flag_group_names"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    #delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag ids in flag group, missing id
def test_get_flags_in_flag_group_missing_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get_flag_group_flags_missing_id
    url_get_flag_group = "flag_group/get_flag_group_flags"
    response = client.get(url_get_flag_group)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag ids in flag group, flag group does not exist
def test_flags_in_flag_group_id_does_not_exist(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    #get flag group flags
    url_get_flag_group_flags = "flag_group/get_flag_group_flags/" + new_id
    response = client.get(url_get_flag_group_flags)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag ids in flag group, invalid flag group id
def test_get_flags_in_flag_group_invalid_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get flags
    flag_group_flags_get_url = "flag_group/get_flag_group_flags/1A1A"
    response = client.get(flag_group_flags_get_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get flag ids in flag group, valid
def test_get_flags_in_flag_group_valid(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #get flags in flag group
    flag_in_flag_group_url = "flag_group/get_flag_group_flags/" + id
    response = client.get(flag_in_flag_group_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get specific flag group, missing id
def test_get_specific_flag_group_missing_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #get flag group
    flag_group_get_url = "flag_group/get_specific_flag_group"
    response = client.get(flag_group_get_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get specific flag group, id does not exist
def test_get_specific_flag_group_id_does_not_exist(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    new_id = str(generate())
    while new_id == id:
        new_id = str(generate())

    #get specific flag group
    flag_group_get_url = "flag_group/get_specific_flag_group/" + new_id
    response = client.get(flag_group_get_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get specific flag group, invalid id
def test_get_specific_flag_group_invalid_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get specific flag group
    new_id = "1A1A"
    flag_group_get_url = "flag_group/get_specific_flag_group/" + new_id
    response = client.get(flag_group_get_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#get specific flag group, valid
def test_get_specific_flag_group_valid(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # get specific flag group
    flag_group_get_url = "flag_group/get_specific_flag_group/" + id
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#create flag group, missing name
def test_create_flag_group_missing_name(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#create flag group, non unique name
def test_create_flag_group_non_unique_name(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    #2nd flag group create
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#create flag group, valid
def test_create_flag_group_valid(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#delete flag group, no id
def test_delete_flag_group_no_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    #delete flag group
    flag_group_delete_url = "flag_group/delete_flag_group"
    response = client.delete(flag_group_delete_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#delete flag group, id does not exist
def test_delete_flag_group_id_does_not_exist(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete flag group
    id = str(generate())
    flag_group_delete_url = "flag_group/delete_flag_group/" + id
    response = client.delete(flag_group_delete_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#delete flag group, invalid id
def test_delete_flag_group_invalid_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete flag group
    id = "1A1A"
    flag_group_delete_url = "flag_group/delete_flag_group/" + id
    response = client.delete(flag_group_delete_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#delete flag group, valid
def test_delete_flag_group_valid(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # delete flag group
    flag_group_delete_url = "flag_group/delete_flag_group/" + id
    response = client.delete(flag_group_delete_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#add flag to flag group, missing flag group id
def test_add_flag_to_flag_group_missing_flag_group_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag to flag group
    flag_group_add_flag_url = "flag_group/add_flag_to_flag_group"
    response = client.put(flag_group_add_flag_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, flag group id does not exist
def test_add_flag_to_flag_group_flag_group_id_no_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    #add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + new_flag_group_id + "/x/" + flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, invalid flag group id
def test_add_flag_to_flag_group_invalid_flag_group_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + "1A1A" + "/x/" + flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, missing flag id
def test_add_flag_to_flag_group_missing_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x"
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, flag id does not exist
def test_add_flag_to_flag_group_flag_id_no_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create new unique flag id
    new_flag_id = str(generate())
    while flag_id == new_flag_id:
        new_flag_id = str(generate())

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + new_flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, invalid flag id
def test_add_flag_to_flag_group_invalid_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + "1A1A"
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create new unique flag id
    new_flag_id = str(generate())
    while flag_id == new_flag_id:
        new_flag_id = str(generate())

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + new_flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, flag id already exists in flag group
def test_add_flag_to_flag_group_flag_id_already_exists_in_flag_group(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 200

    # attempt to add same id to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, flag name already exists in flag group
def test_add_flag_to_flag_group_flag_name_already_in_flag(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create second flag with same name
    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_1
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 200

    # attempt to add new flag id for flag with same name
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_2
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#add flag to flag group, valid
def test_add_flag_to_flag_group_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create second flag with same name
    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag2B"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # add flag to flag group
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_1
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 200

    # attempt to add new flag id for flag with same name
    flag_add_flag_group_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_2
    response = client.put(flag_add_flag_group_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, missing flag group id
def test_remove_flag_from_flag_group_missing_flag_group_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #remove flag from flag group
    flag_remove_flag_group_url = "flag_group/remove_flag_from_flag_group"
    response = client.put(flag_remove_flag_group_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, flag group id does not exist
def test_remove_flag_from_flag_group_flag_group_does_not_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create new unique id
    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    #remove flag from flag group
    flag_remove_flag_group_url = "flag_group/remove_flag_from_flag_group/" + new_flag_group_id + "/x/" + flag_id
    response = client.put(flag_remove_flag_group_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, flag group id is not valid
def test_remove_flag_from_flag_group_invalid_flag_group_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #remove flag
    flag_remove_url = "flag_group/remove_flag_from_flag_group/1A1A/X/" + flag_id
    response = client.put(flag_remove_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200


#remove flag from flag group, missing flag to remove
def test_remove_flag_from_flag_group_missing_flag(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #remove flag
    flag_remove_url = "flag_group/remove_flag_from_flag_group/1A1A/X"
    response = client.put(flag_remove_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, flag to remove does not exist
def test_remove_flag_from_flag_group_flag_no_exist(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #create unique flag id
    new_flag_id = str(generate())
    while flag_id == new_flag_id:
        new_flag_id = str(generate())

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #remove flag
    flag_remove_url = "flag_group/remove_flag_from_flag_group/" + flag_group_id + "/x/" + new_flag_id
    response = client.put(flag_remove_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, flag does not exist in flag group
def test_remove_flag_from_flag_group_flag_not_in_flag_group(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_1 = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create second flag with same name
    flag_creation_url = "flag/create_flag/XX/Flag2B"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id_2 = re.sub("[^a-zA-Z0-9]+", "", x.split(",")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag 1 to flag group
    flag_add_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_1
    response = client.put(flag_add_url)
    assert response.status_code == 200

    #remove flag 2
    flag_remove_url = "flag_group/remove_flag_from_flag_group/" + flag_group_id + "/x/" + flag_id_2
    response = client.put(flag_remove_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, invalid flag id
def test_remove_flag_from_flag_group_invalid_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #remove flag invalid
    flag_remove_url = "flag_group/remove_flag_from_flag_group/" + flag_group_id + "/x/1A1A"
    response = client.put(flag_remove_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

#remove flag from flag group, valid
def test_remove_flag_from_flag_group_valid(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # get id
    flag_id_get_url = "flag/get_flag_ids"
    response = client.get(flag_id_get_url)
    assert response.status_code == 200

    # unpack flag id
    x = response.get_data().decode("utf-8")
    flag_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #add flag
    add_flag_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(add_flag_url)
    assert response.status_code == 200

    #remove flag
    flag_remove_url = "flag_group/remove_flag_from_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(flag_remove_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete all dependency entries
    flag_dep_deletion_url = "flag_dependency/delete_all_flag_dependencies"
    response = client.delete(flag_dep_deletion_url)
    assert response.status_code == 200











