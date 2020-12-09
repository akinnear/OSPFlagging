import pytest
from flask import Flask
from handlers.FlaggingAPI import make_routes
from app import _create_flagging_doa
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
    flagging_doa = _create_flagging_doa()
    make_routes(app, flagging_doa)
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
    url = '/flag/get_ids'
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == {"_ids": ["1"*24, "2"*24, "1a"*12]}
    assert response.status == "200 OK"


#get specific flag, id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([], 200), autospec=True)
def test_get_specific_flag_does_not_exist(mock_get_flag_ids, client):
    flag_id = "1a" * 12
    url = '/flag/get_specific/' + flag_id
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
    url = "/flag/get_specific"
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
    url = "flag/get_specific/123"
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
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag", return_value=flag_uuid, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value=flag_name, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_logic_information", return_value=flag_logic, autospec=True)
def test_get_specific_flag_id_valid(mock_get_flag_logic_information, mock_get_flag_name, mock_get_specific_flag, mock_get_flag_ids, client):
    flag_id = "1a"*12
    url = "/flag/get_specific/" + flag_id
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
    url = "flag/create"
    response = client.post(url)
    assert response.status_code == 500
    assert response.json["message"] == "error reading flag data to create flag"
    assert response.json["simple_message"] == "error flag data to create flag"
    assert response.json["valid"] == False

#TODO
@mock.patch("handlers.FlaggingAPI._convert_TFLI_to_FLI", return_value=FlagLogicInformation(), autospec=True)
@mock.patch("handlers.FlaggingAPI.request.get_json", _create_flagging_doa=_convert_FLI_to_TFLI(FlagLogicInformation()))
def test_create_flag_missing_name(mock_request, mock_payload, client):
    url = "flag/create"
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
    flag_deletion_url = "flag/delete_all"
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
    url = "flag/duplicate"
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
    url = "flag/duplicate/" + flag_id
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
    url = "flag/duplicate/" + flag_id
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
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.duplicate_flag", return_value=flag_uuid, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_logic_information", return_value=flag_logic, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value=flag_name, autospec=True)
def test_duplicate_flag_id_valid(mock_flag_name, mock_flag_logic, mock_duplicated_id, mock_get_flag_ids, client):
    og_flag_id = "2b"*12
    dup_flag_id = "1a"*12
    flag_name = "FlagName1a"
    url = "flag/duplicate/" + og_flag_id
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
    url = "flag/update_name"
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
    url = "flag/update_name/" + flag_id
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
    url = "flag/update_name/" + invalid_flag_id + "/" + new_flag_name
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
    url = "flag/update_name/" + flag_id + "/" + new_flag_name
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
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value=flag_name, autospec=True)
def test_update_flag_name_non_unique_name(mock_get_flag_name, mock_get_flag_ids, client):
    flag_name = "FlagName2b"
    flag_id = "2b"*12
    url = "flag/update_name/" + flag_id + "/" + flag_name
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
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", side_effect=[og_flag_name, new_flag_name], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_logic_information", return_value=flag_logic, autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag", return_value=new_flag_id, autospec=True)
def test_update_flag_name_valid(mock_update_flag, mock_get_flag_logic, mock_get_flag_name, mock_get_flag_ids, client):
    og_flag_id = "2b"*12
    new_flag_name = "FlagName1a"
    new_flag_id = "1a" * 12
    flag_logic = _convert_FLI_to_TFLI(FlagLogicInformation())
    url = "flag/update_name/" + og_flag_id + "/" + new_flag_name
    response = client.post(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == flag_logic
    assert response.json["message"] == "original flag " + og_flag_id + " has been renamed " + new_flag_name
    assert response.json["flag_name"] == new_flag_name
    assert response.json["simple_message"] == "flag has been renamed"
    assert response.json["uuid"] == new_flag_id
    assert response.json["valid"] == True

#TODO
# update flag logic, missing flag id
def test_update_flag_logic_missing_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all"
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

#TODO
# update flag logic, flag id does not exist
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

#TODO
# update flag logic, invalid flag id
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

#TODO
# update flag logic, flag in more than one flag group
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

#TODO
# update flag logic, valid
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
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_delete_flag_missing_flag_id(mock_get_flag_ids, client):
    url = "flag/delete"
    response = client.delete(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "user must specify flag id"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "missing flag id"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#delete flag, flag id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_delete_flag_id_does_not_exist(mock_get_flag_ids, client):
    flag_id = "1a"*12
    url = "flag/delete/" + flag_id
    response = client.delete(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag id " + flag_id + " does not exist"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag id does not exist"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#delete flag, invalid flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_delete_flag_invalid_id(mock_get_flag_ids, client):
    flag_id = "1a"*10
    url = "flag/delete/" + flag_id
    response = client.delete(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "error converting: " + flag_id + " to object Id type"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "error in deleting flag"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#delete flag, valid
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.delete_flag_dependency", return_value=(ObjectId("3c"*12), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value="FlagName2b", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.remove_flag", return_value=ObjectId("2b"*12), autospec=True)
def test_delete_flag_valid(mock_remove_flag, mock_get_flag_name, mock_delete_flag_dependency, mock_get_flag_ids, client):
    flag_id = "2b"*12
    flag_name = "FlagName2b"
    url = "flag/delete/" + flag_id
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == None
    assert response.json["message"] == flag_id + " has been deleted"
    assert response.json["flag_name"] == flag_name
    assert response.json["simple_message"] == "flag has been deleted"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == True

#move flag to production, missing id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_move_flag_to_production_missing_id(mock_get_flag_ids, client):
    url = "flag/move_to_production"
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "user must specify flag id"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "user must specify flag id"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#move flag to production, id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_move_flag_to_production_id_no_exist(mock_get_flag_ids, client):
    flag_id = "1a"*12
    url = "flag/move_to_production/" + flag_id
    response = client.put(url)
    assert response.status_code == 404
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag id: " + flag_id + " does not exist"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "flag id does not exist"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == False

#move flag to production, invalid id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
def test_move_flag_to_production_invalid_id(mock_get_all_flag_ids, client):
    flag_id = "1a" * 10
    url = "flag/move_to_production/" + flag_id
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "error converting: " + flag_id + " to object Id type"
    assert response.json["flag_name"] == None
    assert response.json["simple_message"] == "error moving flag to production"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#move flag to production, error in flag
# unique_dummy_flag = FlagLogicInformation(
#     used_variables={VariableInformation("ff1"): {CodeLocation(4, 11)},
#                     VariableInformation("ff2"): {CodeLocation(6, 11)},
#                     VariableInformation("a"): {CodeLocation(2, 16), CodeLocation(2, 22)},
#                     VariableInformation("b"): {CodeLocation(2, 26), CodeLocation(2, 34)},
#                     VariableInformation("f"): {CodeLocation(3, 10), CodeLocation(4, 24),
#                                                CodeLocation(6, 24)}},
#     assigned_variables={VariableInformation("f"): {CodeLocation(2, 0)},
#                         VariableInformation("a"): {CodeLocation(2, 11)},
#                         VariableInformation('b'): {CodeLocation(2, 13)}},
#     referenced_functions={
#         VariableInformation("reduce"): {CodeLocation(3, 3), CodeLocation(4, 17), CodeLocation(6, 17)}},
#     defined_functions={VariableInformation("my_add"): {CodeLocation(2, 4)}},
#     defined_classes={VariableInformation("my_class"): {CodeLocation(1, 1)}},
#     referenced_modules={ModuleInformation("wtforms"): {CodeLocation(2, 5)},
#                         ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)}},
#     referenced_flags={"Flag5": {CodeLocation(5, 10), CodeLocation(6, 10)},
#                       "Flag6": {CodeLocation(7, 10)}},
#     return_points={CodeLocation(4, 4), CodeLocation(6, 4)},
#     used_lambdas={"LAMBDA": {CodeLocation(2, 4)}},
#     errors=[ErrorInformation(cl=CodeLocation(3, 5),
#                              msg="invalid syntax",
#                              text="x = =  f\n"),
#             ErrorInformation(cl=CodeLocation(5, 5),
#                              msg="invalid syntax",
#                              text="y = = =  q2@\n")],
#     flag_logic="""
#     f = lambda a,b: a if (a > b) else b
#     if reduce(f, [47,11,42,102,13]) > 100:
#     return ff1 > reduce(f, [47,11,42,102,13])
#     else:
#     return ff2 < reduce(f, [47,11,42,102,13])""",
#     validation_results=TypeValidationResults())
# error_flag = pull_flag_logic_information(unique_dummy_flag=unique_dummy_flag)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_error", return_value="ERROR", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value="FlagName2b", autospec=True)
def test_move_flag_to_production_error_in_flag(mock_flag_error, mock_get_all_flag_ids, mock_get_flag_name, client):
    flag_id = "2b"*12
    flag_name = "FlagName2b"
    url = "flag/move_to_production/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag can not be moved to production due to flag errors"
    assert response.json["flag_name"] == flag_name
    assert response.json["simple_message"] == "flag can not be moved to production due to flag errors"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == False


#move flag to production, valid
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_error", return_value="", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value="FlagName2b", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag", return_value=ObjectId("2b"*12), autospec=True)
def test_move_flag_to_production_valid(mock_update_flag, mock_get_flag_name, mock_get_flag_error, mock_get_flag_ids, client):
    flag_id = "2b" * 12
    flag_name = "FlagName2b"
    url = "flag/move_to_production/" + flag_id
    response = client.put(url)
    assert response.status_code == 200
    assert response.json["flag_logic"] == None
    assert response.json["message"] == "flag has been moved to production"
    assert response.json["flag_name"] == flag_name
    assert response.json["simple_message"] == "flag has been moved to production"
    assert response.json["uuid"] == flag_id
    assert response.json["valid"] == True


#get flag groups
flag_group_1 = {"_id": ObjectId("1a"*12),
                "FLAG_GROUP_NAME": "FlagGroupName1a",
                "FLAGS_IN_GROUP": [ObjectId("2a"*12), ObjectId("2b"*12)],
                "FLAG_GROUP_STATUS": "DRAFT"}
flag_group_2 = {"_id": ObjectId("3a"*12),
                "FLAG_GROUP_NAME": "FlagGroupName3a",
                "FLAGS_IN_GROUP": [ObjectId("4a"*12), ObjectId("4b"*12)],
                "FLAG_GROUP_STATUS": "PRODUCTION"}
@mock.patch("handlers.FlaggingAPI.get_flag_groups", return_value=([flag_group_1, flag_group_2], 200), autospec=True)
def test_get_flag_groups(mock_get_flag_groups, client):
    flag_group_1 = {"_id": ObjectId("1a" * 12),
                    "FLAG_GROUP_NAME": "FlagGroupName1a",
                    "FLAGS_IN_GROUP": [ObjectId("2a" * 12), ObjectId("2b" * 12)],
                    "FLAG_GROUP_STATUS": "DRAFT"}
    flag_group_2 = {"_id": ObjectId("3a" * 12),
                    "FLAG_GROUP_NAME": "FlagGroupName3a",
                    "FLAGS_IN_GROUP": [ObjectId("4a" * 12), ObjectId("4b" * 12)],
                    "FLAG_GROUP_STATUS": "PRODUCTION"}
    url = "flag_group/get"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_groups"] == [str(x) for x in [flag_group_1, flag_group_2]]


#get flag group ids
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_flag_group_ids(mock_get_flag_group_ids, client):
    url = "flag_group/get_ids"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_group_ids"] == [str(x) for x in [ObjectId("1a"*12), ObjectId("3a"*12)]]

#get flag group names
@mock.patch("handlers.FlaggingAPI.get_flag_group_names", return_value=(["FlagGroupName1a", "FlagGroupName3a"], 200), autospec=True)
def test_get_flag_group_names(mock_get_flag_group_names, client):
    url = "flag_group/get_names"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_group_names"] == ["FlagGroupName1a", "FlagGroupName3a"]

#get flag ids in flag group, missing id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_flags_in_flag_group_missing_id(mock_get_flag_group_ids, client):
    url = "flag_group/get_flags"
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group id must be specified"
    assert response.json["simple_message"] == "flag group id must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#get flag ids in flag group, flag group does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_flags_in_flag_group_id_does_not_exist(mock_get_flag_group_ids, client):
    flag_group_id = "2a"*12
    url = "flag_group/get_flags/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

#get flag ids in flag group, invalid flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_flags_in_flag_group_invalid_id(mock_get_flag_group_ids, client):
    flag_group_id = "2b"*10
    url = "flag_group/get_flags/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error converting flag group id: " + flag_group_id + " to proper Object Id type"
    assert response.json["simple_message"] == "error pulling flags for flag group"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#get flag ids in flag group, valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName3a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("2a"*12), ObjectId("2b"*12)], autospec=True)
def test_get_flags_in_flag_group_valid(mock_get_flag_group_flag, mock_get_flag_group_name, mock_get_flag_group_ids, client):
    flag_group_id = "3a" * 12
    flags_in_flag_group = [ObjectId("2a"*12), ObjectId("2b"*12)]
    url = "flag_group/get_flags/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == "FlagGroupName3a"
    assert response.json["flags_in_flag_group"] == [str(x) for x in flags_in_flag_group]
    assert response.json["message"] == "return flags for flag group: " + flag_group_id
    assert response.json["simple_message"] == "return flags for flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True


#get specific flag group, missing id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_specific_flag_group_missing_id(mock_get_flag_group_ids, client):
    url = "flag_group/get_specific"
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group id must be specified"
    assert response.json["simple_message"] == "flag group id must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#get specific flag group, id does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_specific_flag_group_id_does_not_exist(mock_get_flag_group_ids, client):
    flag_group_id = "2a" * 12
    url = "flag_group/get_specific/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False



#get specific flag group, invalid id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_get_specific_flag_group_invalid_id(mock_get_flag_group_id, client):
    flag_group_id = "2a" * 10
    url = "flag_group/get_specific/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error converting flag group: " + flag_group_id + " to proper Object Id type"
    assert response.json["simple_message"] == "invalid flag group id type"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#get specific flag group, valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_group", return_value=ObjectId("1a"*12), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("2a"*12), ObjectId("2b"*12)], autospec=True)
def test_get_specific_flag_group_valid(mock_get_flag_group_flags, mock_get_flag_group_name, mock_get_specific_fag,
                                       mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 12
    flags_in_flag_group = [ObjectId("2a"*12), ObjectId("2b"*12)]
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/get_specific/" + flag_group_id
    response = client.get(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == [str(x) for x in flags_in_flag_group]
    assert response.json["message"] == "found flag group id: " + flag_group_id
    assert response.json["simple_message"] == "found flag group id"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True

#create flag group, missing name
@mock.patch("handlers.FlaggingAPI.get_flag_group_names", return_value=(["FlagGroupName1a", "FlagGroupName2b"], 200), autospec=True)
def test_create_flag_group_missing_name(mock_get_flag_group_names, client):
    url = "flag_group/create/id_does_not_matter_here"
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "unique flag group name must be specified"
    assert response.json["simple_message"] == "missing flag group name"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#create flag group, non unique name
@mock.patch("handlers.FlaggingAPI.get_flag_group_names", return_value=(["FlagGroupName1a", "FlagGroupName2b"], 200), autospec=True)
def test_create_flag_group_non_unique_name(mock_get_flag_group_names, client):
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/create/id_does_not_matter_here/" + flag_group_name
    response = client.post(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "new flag group name must be unique"
    assert response.json["simple_message"] == "new flag group name must be unique"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#create flag group, valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_names", return_value=(["FlagGroupName1a", "FlagGroupName2b"], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.add_flag_group", return_value=ObjectId("2a"*12), autospec=True)
def test_create_flag_group_valid(mock_add_flag_group, mock_get_flag_group_names, client):
    flag_group_name = "FlagGroupName2a"
    url = "flag_group/create/id_does_not_matter_here/" + flag_group_name
    response = client.post(url)
    new_flag_group_id = "2a"*12
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "unique flag group: " + flag_group_name + " created"
    assert response.json["simple_message"] == "new flag group created"
    assert response.json["uuid"] == new_flag_group_id
    assert response.json["valid"] == True

#delete flag group, no id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_delete_flag_group_no_id(mock_get_flag_group_ids, client):
    url = "flag_group/delete"
    response = client.delete(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group id must be specified"
    assert response.json["simple_message"] == "flag group id must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#delete flag group, id does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_delete_flag_group_id_does_not_exist(mock_get_flag_group_ids, client):
    flag_group_id = "2a"*12
    url = "flag_group/delete/" + flag_group_id
    response = client.delete(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "could not identify flag group: " + flag_group_id + " in database"
    assert response.json["simple_message"] == "could not identify flag group in database"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False


#delete flag group, invalid id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
def test_delete_flag_group_invalid_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a"*10
    url = "flag_group/delete/" + flag_group_id
    response = client.delete(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error deleting flag group: " + flag_group_id + ", error converting to proper Object Id type"
    assert response.json["simple_message"] == "error deleting flag group, invalid id type"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#delete flag group, valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("3a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.delete_flag_dependency", return_value=(FlaggingSchemaInformation(), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.remove_flag_group", return_value=ObjectId("1a"*12), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_delete_flag_group_valid(mock_remove_flag_group, mock_delete_flag_dependency, mock_get_flag_group_ids,
                                 mock_get_flag_group_name, client):
    flag_group_id = "1a"*12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/delete/" + flag_group_id
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " deleted from database"
    assert response.json["simple_message"] == "flag group has been deleted"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True


#add flag to flag group, missing flag group id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
def test_add_flag_to_flag_group_missing_flag_group_id(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids, client):
    url = "flag_group/add_flag"
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group must be specified"
    assert response.json["simple_message"] == "flag group must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#add flag to flag group, flag group id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
def test_add_flag_to_flag_group_flag_group_id_no_exist(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids, client):
    flag_group_id = "3a"*12
    flag_id = "3f"*12
    flag_group_name = "FlagGroupName3a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag_group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

#add flag to flag group, invalid flag group id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
def test_add_flag_to_flag_group_invalid_flag_group_id(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids, client):
    flag_group_id = "3a"*10
    flag_id = "3f"*12
    flag_group_name = "FlagGroupName3a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error adding flag to flag group: " + flag_group_id + ", error converting to Object Id type"
    assert response.json["simple_message"] == "error converting flag group id to Object Id type"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#add flag to flag group, missing flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
def test_add_flag_to_flag_group_missing_flag_id(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids, client):
    flag_group_id = "1a"*12
    flag_id = "3f"*12
    flag_group_name = "FlagGroupName3a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "no new flags were specified"
    assert response.json["simple_message"] == "missing flags to add to flag group"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#add flag to flag group, flag id does not exist
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_add_flag_to_flag_group_flag_id_no_exist(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids,
                                                 mock_get_flag_group_name, client):
    flag_group_id = "1a"*12
    flag_id = "5f"*12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "Flag(s) " + ", ".join(map(str, [flag_id])) + " do not exist"
    assert response.json["simple_message"] == "flag does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False


#add flag to flag group, invalid flag id
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_add_flag_to_flag_group_invalid_flag_id(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids,
                                                mock_get_flag_group_name, client):
    flag_group_id = "1a"*12
    flag_id = "1f"*2
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error adding flag to flag group: " + flag_group_id + ", error converting flag id to ObjectId type"
    assert response.json["simple_message"] == "error adding flag to flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False


#add flag to flag group, flag id already exists in flag group
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_add_flag_to_flag_group_flag_id_already_exists_in_flag_group(mock_get_flag_group_flags, mock_get_flag_group_ids, mock_get_flag_ids,
                                                mock_get_flag_group_name, client):
    flag_group_id = "1a"*12
    flag_id = "1f"*12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "Flag(s) " + ", ".join(map(str, [flag_id])) + " already exist in flag group"
    assert response.json["simple_message"] == 'flag already in flag group'
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False


#add flag to flag group, flag name already exists in flag group
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_names_from_flag_group", return_value=["FlagName1f", "FlagName2f"], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value="FlagName1f", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_logic_information", return_value=_convert_FLI_to_TFLI(FlagLogicInformation()), autospec=True)
def test_add_flag_to_flag_group_flag_name_already_in_flag(mock_get_flag_ids, mock_get_flag_group_ids, mock_get_flag_group_flags,
                                                          mock_get_flag_group_name, mock_get_flag_names_in_flag_group,
                                                          mock_get_flag_name, mock_referenced_flags, client):
    flag_group_id = "1a"*12
    flag_id = "3f"*12
    flag_group_name = "FlagGroupName1a"
    flag_name = "FlagName1f"
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag: " + flag_id + " with name: " + flag_name + " already exists in flag group: " + flag_group_id
    assert response.json["simple_message"] == "flag already exists in flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False



#add flag to flag group, valid
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12), ObjectId("4f"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("2a"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags",
            return_value=(FlaggingSchemaInformation(logic=[ObjectId("1f"*12), ObjectId("2f"*12)]), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_names_from_flag_group", return_value=["FlagName1f", "FlagName2f"], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_name", return_value="FlagName3f", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_logic_information", return_value=_convert_FLI_to_TFLI(FlagLogicInformation()), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag_group", return_value=ObjectId("1a"*12), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_status", return_value="PRODUCTION", autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.validate_cyclical_logic", return_value=TypeValidationResults(), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_specific_flag", return_value=(FlagLogicInformation(), 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_dep_ids", return_value=([ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_dep_id_by_flag_id_and_flag_group_id", return_value=ObjectId("1b"*12), autospec=True)
@mock.patch("handlers.FlaggingAPI.add_dependencies_to_flag", return_value=(ObjectId("1b"*12), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12)], autospec=True)
def test_add_flag_to_flag_group_valid(mock_get_flag_ids, mock_get_flag_group_ids, mock_get_flag_group_flags,
                                      mock_get_flag_group_name, mock_get_flag_names_in_flag_group,
                                      mock_get_flag_name, mock_referenced_flags, mock_update_flag_group,
                                      mock_get_flag_status, mock_validate_cyclical_logic,
                                      mock_get_specific_flag, mock_flag_dep_ids,
                                      mock_get_specific_flag_deb_id_by_flag_id_and_flag_group_id,
                                      mock_add_dependencies_to_flag, mock_get_flag_group_flag_mongo, client):
    flag_group_id = "1a"*12
    flag_id = "3f"*12
    flag_group_name = "FlagGroupName1a"
    flag_name = "FlagName3f"
    flagging_message = ""
    flag_in_flag_group = ["1f"*12, "2f"*12, "3f"*12]
    url = "flag_group/add_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == flag_in_flag_group
    assert response.json["message"] == "flag group " + flag_group_id + " has been updated with flag(s) " + (
                                                       ", ".join(map(str, [flag_id]))) + "\n" + flagging_message
    assert response.json["simple_message"] == "flags added to flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True




#remove flag from flag group, missing flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_remove_flag_from_flag_group_missing_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 12
    flag_id = "3f" * 12
    flag_group_name = "FlagGroupName1a"
    flag_name = "FlagName3f"
    url = "flag_group/remove_flag"
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group not specified"
    assert response.json["simple_message"] == "flag group not specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False



#remove flag from flag group, flag group id does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_remove_flag_from_flag_group_flag_group_does_not_exist(mock_get_flag_group_ids, client):
    flag_group_id = "2a" * 12
    flag_id = "3f" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False



#remove flag from flag group, flag group id is not valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_remove_flag_from_flag_group_invalid_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "2a" * 2
    flag_id = "3f" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error removing flag from flag group, error converting flag group id: " + flag_group_id + " to ObjectId type"
    assert response.json["simple_message"] == "error removing flag from flag group"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False



#remove flag from flag group, missing flag to remove
get_all_flag_group_return_value = FlaggingSchemaInformation(valid=True,
                                                            logic=[ObjectId("2a"*12), ObjectId("2b"*12)],
                                                            message="return flags for flag group: " + "1a"*12,
                                                            simple_message="return flags for flag group",
                                                            uuid=ObjectId("1a"*12),
                                                            name="FlagGroupName1a")
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags", return_value=(get_all_flag_group_return_value, 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2a"*12), ObjectId("2b"*12), ObjectId("2c"*12), ObjectId("2d"*12)], 200), autospec=True)
def test_remove_flag_from_flag_group_missing_flag(mock_get_flag_ids, mock_get_flag_group_flags, mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 12
    flag_id = "2a" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "no flags to remove were specified"
    assert response.json["simple_message"] == "missing flags to remove from flag group"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False




#remove flag from flag group, flag to remove does not exist
get_all_flag_group_return_value = FlaggingSchemaInformation(valid=True,
                                                            logic=[ObjectId("2a"*12), ObjectId("2b"*12)],
                                                            message="return flags for flag group: " + "1a"*12,
                                                            simple_message="return flags for flag group",
                                                            uuid=ObjectId("1a"*12),
                                                            name="FlagGroupName1a")
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags", return_value=(get_all_flag_group_return_value, 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2a"*12), ObjectId("2b"*12), ObjectId("2c"*12), ObjectId("2d"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_remove_flag_from_flag_group_flag_no_exist(mock_get_flag_ids, mock_get_flag_group_flags, mock_get_flag_group_ids,
                                                   mock_get_flag_group_name, client):
    flag_group_id = "1a" * 12
    flag_id = "3a" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "the following flag does not exist: " + flag_id
    assert response.json["simple_message"] == "error removing flags from flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False



#remove flag from flag group, flag does not exist in flag group
get_all_flag_group_return_value = FlaggingSchemaInformation(valid=True,
                                                            logic=[ObjectId("2a"*12), ObjectId("2b"*12)],
                                                            message="return flags for flag group: " + "1a"*12,
                                                            simple_message="return flags for flag group",
                                                            uuid=ObjectId("1a"*12),
                                                            name="FlagGroupName1a")
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags", return_value=(get_all_flag_group_return_value, 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2a"*12), ObjectId("2b"*12), ObjectId("2c"*12), ObjectId("2d"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_remove_flag_from_flag_group_flag_not_in_flag_group(mock_get_flag_ids, mock_get_flag_group_flags, mock_get_flag_group_ids,
                                                            mock_get_flag_group_name, client):
    flag_group_id = "1a" * 12
    flag_id = "2c" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "the following flag is not part of flag group " + flag_group_id + ": " + flag_id
    assert response.json["simple_message"] =="flag specified for removal is not part of flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False


#remove flag from flag group, invalid flag id
get_all_flag_group_return_value = FlaggingSchemaInformation(valid=True,
                                                            logic=[ObjectId("2a"*12), ObjectId("2b"*12)],
                                                            message="return flags for flag group: " + "1a"*12,
                                                            simple_message="return flags for flag group",
                                                            uuid=ObjectId("1a"*12),
                                                            name="FlagGroupName1a")
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags", return_value=(get_all_flag_group_return_value, 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2a"*12), ObjectId("2b"*12), ObjectId("2c"*12), ObjectId("2d"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_remove_flag_from_flag_group_invalid_flag_id(mock_get_flag_ids, mock_get_flag_group_flags, mock_get_flag_group_ids,
                                                    mock_get_flag_group_name, client):
    flag_group_id = "1a" * 12
    flag_id = "2c" * 2
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error removing flag: " + flag_id + " from flag group " + flag_group_id + ", error converting flag id to proper ObjectId type"
    assert response.json["simple_message"] == "invalid flag id type"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#remove flag from flag group, valid
get_all_flag_group_return_value = FlaggingSchemaInformation(valid=True,
                                                            logic=[ObjectId("2a"*12), ObjectId("2b"*12)],
                                                            message="return flags for flag group: " + "1a"*12,
                                                            simple_message="return flags for flag group",
                                                            uuid=ObjectId("1a"*12),
                                                            name="FlagGroupName1a")
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_flag_group_flags", return_value=(get_all_flag_group_return_value, 200), autospec=True)
@mock.patch("handlers.FlaggingAPI.get_all_flag_ids", return_value=([ObjectId("2a"*12), ObjectId("2b"*12), ObjectId("2c"*12), ObjectId("2d"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("handlers.FlaggingAPI.delete_flag_dependency", return_value=(ObjectId("3a"*12), 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.remove_specific_flag_dependencies_via_flag_id_and_flag_group_id", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag_group", return_value=ObjectId("1a"*12), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.validate_cyclical_logic", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("2b"*12)], autospec=True)
def test_remove_flag_from_flag_group_valid(mock_get_flag_group_ids, mock_get_flag_group_flags_handler,
                                           mock_get_all_flag_ids, mock_get_flag_group_name, mock_delete_dep,
                                           mock_rm_flag_dep_via_flag_id_and_flag_group_id, mock_update_flag_group,
                                           mock_validate_cyclical_logic, mock_get_flag_group_flag_mongo, client):
    flag_group_id = "1a" * 12
    flag_id = "2a" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/remove_flag/" + flag_group_id + "/" + flag_group_name + "/" + flag_id
    response = client.put(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == ["2b"*12]
    assert response.json["message"] == "Flag(s) " + ", ".join(map(str, [flag_id])) + " removed from " + flag_group_id
    assert response.json["simple_message"] == "flags removed from flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True


#duplicate flag group, missing flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_duplicate_flag_group_missing_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/duplicate"
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "user must specify flag group id"
    assert response.json["simple_message"] == "user must specify flag group id"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#duplicate flag group, flag group does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_duplicate_flag_group_flag_group_no_exist(mock_get_flag_group_ids, client):
    flag_group_id = "1c" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/duplicate/" + flag_group_id + "/" + flag_group_name
    response = client.post(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False




#duplicate flag group, invalid flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_duplicate_flag_group_invalid_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 2
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/duplicate/" + flag_group_id
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error duplicating flag group " + flag_group_id + ", error converting flag group id to proper OjbectId type"
    assert response.json["simple_message"] == "error duplicating flag group"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#duplicate flag group, missing new name
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_duplicate_flag_group_missing_new_name(mock_get_flag_group_ids, mock_get_flag_group_name, client):
    flag_group_id = "1a" * 12
    flag_group_name = "NEWFlagGroupName1a"
    url = "flag_group/duplicate/" + flag_group_id
    response = client.post(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == "FlagGroupName1a"
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error duplicating flag group: " + flag_group_id + ", missing new flag group name"
    assert response.json["simple_message"] == "error duplicating flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

#duplicate flag group, new name same as old name
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
def test_duplicate_flag_group_same_name(mock_get_flag_group_ids, mock_get_flag_group_name, client):
    flag_group_id = "1a" * 12
    flag_group_name = "FlagGroupName1a"
    url = "flag_group/duplicate/" + flag_group_id + "/" + flag_group_name
    response = client.post(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "can not duplicate flag group " + flag_group_id + " must be given a unique name"
    assert response.json["simple_message"] == "new name for flag group must be unique"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

#dupliacte flag group, valid
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.duplicate_flag_group", return_value=ObjectId("2a"*12), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag_group", return_value=ObjectId("2a"*12), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("1f"*12), ObjectId("2f"*12)], autospec=True)
def test_duplicate_flag_group_valid(mock_get_flag_group_ids, mock_get_flag_group_name, mock_duplicate_flag_group,
                                    mock_update_flag_group, mock_get_flag_group_flag, client):
    flag_group_id = "1a" * 12
    flag_group_name = "NewFlagGroupName2a"
    url = "flag_group/duplicate/" + flag_group_id + "/" + flag_group_name
    response = client.post(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == flag_group_name
    assert response.json["flags_in_flag_group"] == ["1f"*12, "2f"*12]
    assert response.json["message"] == "new flag group " + "2a"*12 + " created off of " + "1a"*12
    assert response.json["simple_message"] == "new flag group created"
    assert response.json["uuid"] == "2a"*12
    assert response.json["valid"] == True

#move flag group to production, missing flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_move_flag_group_to_production_missing_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 12
    url = "flag_group/move_to_production"
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group id must be specified"
    assert response.json["simple_message"] == "flag group id must be specified"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False

#move flag group to production, flag group does not exist
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_move_flag_group_to_production_flag_group_no_exist(mocK_get_flag_group_ids, client):
    flag_group_id = "1c" * 12
    url = "flag_group/move_to_production/" + flag_group_id
    response = client.put(url)
    assert response.status_code == 404
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "flag group: " + flag_group_id + " does not exist"
    assert response.json["simple_message"] == "flag group does not exist"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

#move flag group to production, invalid flag group id
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
def test_move_flag_group_to_production_invalid_flag_group_id(mock_get_flag_group_ids, client):
    flag_group_id = "1a" * 2
    url = "flag_group/move_to_production/" + flag_group_id
    response = client.put(url)
    assert response.status_code == 400
    assert response.json["flag_group_name"] == None
    assert response.json["flags_in_flag_group"] == None
    assert response.json["message"] == "error moving flag group: " + flag_group_id + " to production, error converting flag group id to proper ObjectId type"
    assert response.json["simple_message"] == "error moving flag group to production"
    assert response.json["uuid"] == "None"
    assert response.json["valid"] == False


#move flag group to production, error in flag group
@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_errors", return_value="HAS ERROR HERE", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12)], autospec=True)
def test_move_flag_group_to_production_error_error_in_flag_group(mock_get_flag_group_ids, mock_get_flag_group_error,
                                                                 mock_get_flag_group_name, mock_get_flag_group_flags, client):
    flag_group_id = "1a" * 12
    url = "flag_group/move_to_production/" + flag_group_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == "FlagGroupName1a"
    assert response.json["flags_in_flag_group"] == ["1f"*12, "2f"*12, "3f"*12]
    assert response.json["message"] == "flag group: " + flag_group_id + " can not be moved to production due to errors in flag group"
    assert response.json["simple_message"] == "flag group can not be moved to production due to errors in flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_errors", return_value="", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12)], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_error", return_value="HAS FLAG ERROR HERE", autospec=True)
def test_move_flag_group_to_production_error_in_flag_in_flag_group(mock_get_flag_group_ids, mock_get_flag_group_errors, mock_get_flag_group_name,
                                                                   mock_get_flag_group_flags, mock_get_specific_flag_error, client):
    flag_group_id = "1a" * 12
    url = "flag_group/move_to_production/" + flag_group_id
    response = client.put(url)
    assert response.status_code == 405
    assert response.json["flag_group_name"] == "FlagGroupName1a"
    assert response.json["flags_in_flag_group"] == ["1f"*12, "2f"*12, "3f"*12]
    assert response.json["message"] == "flag group: " + flag_group_id + " can not be moved to production due to errors in flags found in flag group"
    assert response.json["simple_message"] == "flag group can not be moved to production due to error in flag in flag group"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == False

@mock.patch("handlers.FlaggingAPI.get_flag_group_ids", return_value=([ObjectId("1a"*12), ObjectId("1b"*12)], 200), autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_errors", return_value="", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_name", return_value="FlagGroupName1a", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_flag_group_flag", return_value=[ObjectId("1f"*12), ObjectId("2f"*12), ObjectId("3f"*12)], autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.get_specific_flag_error", return_value="", autospec=True)
@mock.patch("front_end.FlaggingSchemaService.FlaggingDOA.update_flag_group", return_value=ObjectId("1a"*12), autospec=True)
def test_move_flag_group_to_production_valid(mock_get_flag_group_ids, mock_get_flag_group_errors, mock_get_flag_group_name,
                                             mock_get_flag_group_flags, mock_get_specific_flag_error, mock_update_flag_group,
                                             client):
    flag_group_id = "1a" * 12
    url = "flag_group/move_to_production/" + flag_group_id
    response = client.put(url)
    assert response.status_code == 200
    assert response.json["flag_group_name"] == "FlagGroupName1a"
    assert response.json["flags_in_flag_group"] == ["1f"*12, "2f"*12, "3f"*12]
    assert response.json["message"] == "flag group: " + flag_group_id + " has been moved to production"
    assert response.json["simple_message"] == "flag group has been moved to production"
    assert response.json["uuid"] == flag_group_id
    assert response.json["valid"] == True







