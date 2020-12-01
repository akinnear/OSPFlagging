import pytest
from flask import Flask
from handlers.FlaggingAPI import make_routes
from app import _create_flagging_mongo
import re
from random_object_id import generate
from flag_names.FlagService import pull_flag_logic_information
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.ErrorInformation import ErrorInformation
from unittest import mock
from flagging.FlaggingNodeVisitor import determine_variables
from front_end.TransferFlagLogicInformation import _convert_FLI_to_TFLI
import requests
import json
from bson.objectid import ObjectId
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation



@pytest.fixture
def client():
    app = Flask(__name__)
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


#tets get flag ids
ids = [ObjectId(x) for x in ["1"*24, "2"*24, "1a"*12]]
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=(ids, 200), autospec=True)
def test_get_flag_ids(mock_call_return, client):
    url = '/flag/get_flag_ids'
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == {"_ids": ["1"*24, "2"*24, "1a"*12]}
    assert response.status == "200 OK"


#get specific flag, id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([], 200), autospec=True)
def test_get_specific_flag_does_not_exist(mock_get_flag_ids, client):
    flag_id = "1a" * 12
    url = '/flag/get_specific_flag/' + flag_id
    response = client.get(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag: " + flag_id + " does not exist"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag does not exist"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#get specific flag, no id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([], 200), autospec=True)
def test_get_specific_flag_missing_id(mock_get_flag_ids, client):
    url = "/flag/get_specific_flag"
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag id not specified"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag id not specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#get specifif flag, id not valid
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1a"*12)], 200), autospec=True)
def test_get_specific_flag_invalid_id(mock_get_flag_ids, client):
    url = "flag/get_specific_flag/123"
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "error converting flag id to Object ID type"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "error converting flag id to Object ID type"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#get specific flag, valid id
flag_uuid = ObjectId("1a"*12)
flag_name = "FlagName1a"
flag_logic = _convert_FLI_to_TFLI(FlagLogicInformation())
flag_schema_object = FlaggingSchemaInformation(valid=True,
                                               message='found flag id',
                                               simple_message="found flag id",
                                               uuid=str(flag_uuid),
                                               name=flag_name,
                                               logic=flag_logic)
response_code = 200
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1a"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_specific_flag", return_value=flag_uuid, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_name", return_value=flag_name, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_logic_information", return_value=flag_logic, autospec=True)
def test_get_specific_flag_id_valid(mock_get_flag_logic_information, mock_get_flag_name, mock_get_specific_flag, mock_get_flag_ids, client):
    flag_id = "1a"*12
    url = "/flag/get_specific_flag/" + flag_id
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == _convert_FLI_to_TFLI(FlagLogicInformation())
    assert response.json["message"] == "found flag id"
    assert response.json["flag_name"] == "FlagName1a"
    assert response.json["simple_message"] == "found flag id"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == True

#create flag, missing flag name
def test_create_flag_missing_payload(client):
    url = "flag/create_flag"
    response = client.post(url)
    assert response.status_code == 500
    assert response.json["message"] == "error reading flag data to create flag"
    assert response.json["simple_message"] == "error flag data to create flag"
    assert response.json["valid"] == False

#TODO
@mock.patch("handlers.FlaggingAPI._convert_TFLI_to_FLI", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("handlers.FlaggingAPI.request.get_json", _create_flagging_mongo=_convert_FLI_to_TFLI(FlagLogicInformation()))
def test_create_flag_missing_name(mock_request, mock_payload, client):
    url = "flag/create_flag"
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag name not specified"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag name not specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#TODO
# create flag, valid
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
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1a"*12)], 200), autospec=True)
def test_duplicate_flag_missing_flag_id(mock_get_flag_ids, client):
    url = "flag/duplicate_flag"
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag id must be specified"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag id must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False



#duplicate flag, flag id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_duplicate_flag_id_does_not_exist(mock_get_flag_ids, client):
    flag_id = "1a"*12
    url = "flag/duplicate_flag/" + flag_id
    response = client.post(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag " + flag_id + " does not exist"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag does not exist"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#duplicate flag, invalid flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_duplicate_flag_invalid_flag_id(mock_get_flag_ids, client):
    flag_id = "1b"*10
    url = "flag/duplicate_flag/" + flag_id
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "error in duplicating flag: " + flag_id
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "error in duplicating flag"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False



#dupplicate flag, valid
flag_uuid = ObjectId("1a"*12)
flag_name = "FlagName1a"
flag_logic = _convert_FLI_to_TFLI(FlagLogicInformation())
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.duplicate_flag", return_value=flag_uuid, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_logic_information", return_value=flag_logic, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_name", return_value=flag_name, autospec=True)
def test_duplicate_flag_id_valid(mock_flag_name, mock_flag_logic, mock_duplicated_id, mock_get_flag_ids, client):
    og_flag_id = "2b"*12
    dup_flag_id = "1a"*12
    flag_name = "FlagName1a"
    url = "flag/duplicate_flag/" + og_flag_id
    response = client.post(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == _convert_FLI_to_TFLI(FlagLogicInformation())
    assert response.json["message"] == og_flag_id + " has been duplicated"
    assert response.json["flag_name"] == flag_name
    assert response.json["simple_message"] == "flag has been duplicated"
    assert response.json["uuid"] == dup_flag_id
    assert response.json["valid"] == True


#update flag name, missing flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_update_flag_name_missing_flag_id(mock_get_flag_ids, client):
    url = "flag/update_flag_name"
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "user must specify id of original flag"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "missing flag id"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#update flag name, missing new flag name
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_update_flag_name_missing_name(mock_get_flag_ids, client):
    flag_id = "2b"*12
    url = "flag/update_flag_name/" + flag_id
    response = client.post(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "user must specify name of new flag"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "missing new flag name"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#update flag name, invalid flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_update_flag_name_invalid_id(mock_get_flag_ids, client):
    invalid_flag_id = "2b"*10
    new_flag_name = "FlagNameNew2b"
    url = "flag/update_flag_name/" + invalid_flag_id + "/" + new_flag_name
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "error converting: " + invalid_flag_id + " to object Id type"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "error updating flag name"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#update flag name, flag id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_update_flag_name_flag_id_not_exist(mock_get_flag_ids, client):
    flag_id = "1a"*12
    new_flag_name = "FlagNameNew1a"
    url = "flag/update_flag_name/" + flag_id + "/" + new_flag_name
    response = client.post(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "original flag id " + flag_id + " does not exist"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag id does not exist"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#update flag name, new name is same as old name
flag_name = "FlagName2b"
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_name", return_value=flag_name, autospec=True)
def test_update_flag_name_non_unique_name(mock_get_flag_name, mock_get_flag_ids, client):
    flag_name = "FlagName2b"
    flag_id = "2b"*12
    url = "flag/update_flag_name/" + flag_id + "/" + flag_name
    response = client.post(url)
    assert response.status_code == 405
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag id: " + flag_id + " with name: " + flag_name + " must be given a new unique name"
    assert response.json["flag_name"] == flag_name
    assert response.json["simple_message"] == "new flag name must be different than original flag name"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == False


#update flag name, valid
og_flag_name = "FlagName2b"
new_flag_name = "FlagName1a"
new_flag_id = ObjectId("1a"*12)
flag_logic = _convert_FLI_to_TFLI(FlagLogicInformation())
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_name", side_effect=[og_flag_name, new_flag_name], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.get_flag_logic_information", return_value=flag_logic, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingMongo.update_flag", return_value=new_flag_id, autospec=True)
def test_update_flag_name_valid(mock_update_flag, mock_get_flag_logic, mock_get_flag_name, mock_get_flag_ids, client):
    og_flag_id = "2b"*12
    new_flag_name = "FlagName1a"
    new_flag_id = "1a" * 12
    flag_logic = _convert_FLI_to_TFLI(FlagLogicInformation())
    url = "flag/update_flag_name/" + og_flag_id + "/" + new_flag_name
    response = client.post(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == flag_logic
    assert response.json["message"] == "original flag " + og_flag_id + " has been renamed " + new_flag_name
    assert response.json["flag_name"] == new_flag_name
    assert response.json["simple_message"] == "flag has been renamed"
    assert response.json["uuid"] == new_flag_id
    assert response.json["valid"] == True


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
unique_dummy_flag = FlagLogicInformation(
    used_variables={VariableInformation("ff1"): {CodeLocation(4, 11)},
                    VariableInformation("ff2"): {CodeLocation(6, 11)},
                    VariableInformation("a"): {CodeLocation(2, 16), CodeLocation(2, 22)},
                    VariableInformation("b"): {CodeLocation(2, 26), CodeLocation(2, 34)},
                    VariableInformation("f"): {CodeLocation(3, 10), CodeLocation(4, 24),
                                               CodeLocation(6, 24)}},
    assigned_variables={VariableInformation("f"): {CodeLocation(2, 0)},
                        VariableInformation("a"): {CodeLocation(2, 11)},
                        VariableInformation('b'): {CodeLocation(2, 13)}},
    referenced_functions={
        VariableInformation("reduce"): {CodeLocation(3, 3), CodeLocation(4, 17), CodeLocation(6, 17)}},
    defined_functions={VariableInformation("my_add"): {CodeLocation(2, 4)}},
    defined_classes={VariableInformation("my_class"): {CodeLocation(1, 1)}},
    referenced_modules={ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                        ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)}},
    referenced_flags={"Flag5": {CodeLocation(5, 10), CodeLocation(6, 10)},
                      "Flag6": {CodeLocation(7, 10)}},
    return_points={CodeLocation(4, 4), CodeLocation(6, 4)},
    used_lambdas={"LAMBDA": {CodeLocation(2, 4)}},
    errors=[ErrorInformation(cl=CodeLocation(3, 5),
                             msg="invalid syntax",
                             text="x = =  f\n"),
            ErrorInformation(cl=CodeLocation(5, 5),
                             msg="invalid syntax",
                             text="y = = =  q2@\n")],
    flag_logic="""
    f = lambda a,b: a if (a > b) else b
    if reduce(f, [47,11,42,102,13]) > 100:
    return ff1 > reduce(f, [47,11,42,102,13])
    else:
    return ff2 < reduce(f, [47,11,42,102,13])""",
    validation_results=TypeValidationResults())
error_flag = pull_flag_logic_information(unique_dummy_flag=unique_dummy_flag)
@mock.patch("handlers.FlaggingAPI.get_valid_dummy_flag", return_value=error_flag, autospec=True)
def test_move_flag_to_production_error_in_flag(mock_error_flag, client):
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

#move flag to production, valid
def test_move_flag_to_production_valid(client):
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

    # production flag
    flag_production_url = "flag/move_flag_to_production/" + id
    response = client.put(flag_production_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

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

#duplicate flag group, missing flag group id
def test_duplicate_flag_group_missing_flag_group_id(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

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

    #duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#duplicate flag group, flag group does not exist
def test_duplicate_flag_group_flag_group_no_exist(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

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

    #create new unique flag group id
    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    #duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + new_flag_group_id + "/FlagGroup2B"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 404

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#duplicate flag group, invalid flag group id
def test_duplicate_flag_group_invalid_flag_group_id(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

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

    #duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/1A1A/FlagGroup2B"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#duplicate flag group, missing new name
def test_duplicate_flag_group_missing_new_name(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

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

    #duplicate_flag_group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + flag_group_id
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#duplicate flag group, new name same as old name
def test_duplicate_flag_group_same_name(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    #duplicate_flag_group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + flag_group_id + "/" + flag_group_name
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 405

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#dupliacte flag group, valid
def test_duplicate_flag_group_valid(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # duplicate_flag_group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + flag_group_id + "/" + "FlagGroup2B"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 200

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#move flag group to production, missing flag group id
def test_move_flag_group_to_production_missing_flag_group_id(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])
    
    #move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production"
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200
    
#move flag group to production, flag group does not exist
def test_move_flag_group_to_production_flag_group_no_exist(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])
    
    #create new unique flag group id
    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    # move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production/" + new_flag_group_id
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200
    
#move flag group to production, invalid flag group id
def test_move_flag_group_to_production_invalid_flag_group_id(client):
    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

    # move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production/" + "1A1A"
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

#move flag group to production, error in flag group
unique_dummy_flag = FlagLogicInformation(
    used_variables={VariableInformation("ff1"): {CodeLocation(4, 11)},
                    VariableInformation("ff2"): {CodeLocation(6, 11)},
                    VariableInformation("a"): {CodeLocation(2, 16), CodeLocation(2, 22)},
                    VariableInformation("b"): {CodeLocation(2, 26), CodeLocation(2, 34)},
                    VariableInformation("f"): {CodeLocation(3, 10), CodeLocation(4, 24),
                                               CodeLocation(6, 24)}},
    assigned_variables={VariableInformation("f"): {CodeLocation(2, 0)},
                        VariableInformation("a"): {CodeLocation(2, 11)},
                        VariableInformation('b'): {CodeLocation(2, 13)}},
    referenced_functions={
        VariableInformation("reduce"): {CodeLocation(3, 3), CodeLocation(4, 17), CodeLocation(6, 17)}},
    defined_functions={VariableInformation("my_add"): {CodeLocation(2, 4)}},
    defined_classes={VariableInformation("my_class"): {CodeLocation(1, 1)}},
    referenced_modules={ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                        ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)}},
    referenced_flags={"Flag5": {CodeLocation(5, 10), CodeLocation(6, 10)},
                      "Flag6": {CodeLocation(7, 10)}},
    return_points={CodeLocation(4, 4), CodeLocation(6, 4)},
    used_lambdas={"LAMBDA": {CodeLocation(2, 4)}},
    errors=[ErrorInformation(cl=CodeLocation(3, 5),
                             msg="invalid syntax",
                             text="x = =  f\n"),
            ErrorInformation(cl=CodeLocation(5, 5),
                             msg="invalid syntax",
                             text="y = = =  q2@\n")],
    flag_logic="""
    f = lambda a,b: a if (a > b) else b
    if reduce(f, [47,11,42,102,13]) > 100:
    return ff1 > reduce(f, [47,11,42,102,13])
    else:
    return ff2 < reduce(f, [47,11,42,102,13])""",
    validation_results=TypeValidationResults())
error_flag = pull_flag_logic_information(unique_dummy_flag=unique_dummy_flag)
@mock.patch("handlers.FlaggingAPI.get_valid_dummy_flag", return_value=error_flag, autospec=True)
def test_move_flag_group_to_production_error_error_in_flag_group(mock_error_flag, client):
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

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

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
    
    #add flag to flag group, flag has error, thereby flag group will have error
    add_flag_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(add_flag_url)
    assert response.status_code == 200

    # move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production/" + flag_group_id
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 405

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

def test_move_flag_group_to_production_valid(client):
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

    # create flag group
    flag_group_name = "FlagGroup1A"
    flag_group_creation_url = "flag_group/create_flag_group/XX/" + flag_group_name
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group id
    flag_group_id_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_id_get_url)
    assert response.status_code == 200

    # unpack flag group id
    x = response.get_data().decode("utf-8")
    flag_group_id = re.sub("[^a-zA-Z0-9]+", "", x.split(":")[1])

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

    # add flag to flag group, flag has error, thereby flag group will have error
    add_flag_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(add_flag_url)
    assert response.status_code == 200

    # move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production/" + flag_group_id
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200




def test_simple_request_post(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    flag_logic ="""\
if FF1 > 10:
    return True
else:
    return False"""
    flag_logic_info = determine_variables(flag_logic)
    payload = _convert_FLI_to_TFLI(flag_logic_info)
    url = "http://localhost:5000/flag/create_flag/x/Flag1A"

    r = requests.post(url, data=json.dumps(payload))

    unpack = client.get("flag/get_flags")
    print("hello")




