import pytest
from flask import Flask
from handlers.FlaggingAPI import make_routes
from app import _create_flagging_dao
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
import requests
from flagging.FlaggingNodeVisitor import determine_variables
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from flag_data.FlaggingDAO import FlaggingDAO
from integration_tests import MONGO_DOCKER_IMAGE
from front_end.TransferFlagLogicInformation import TransferFlagLogicInformation, _convert_FLI_to_TFLI, \
    _convert_TFLI_to_FLI
import json

def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)

def _create_flagging_dao(container):
    return FlaggingDAO(_get_connection_string(container))

def _create_mongo_client(container):
    return MongoClient(_get_connection_string(container))

#template
# 1) create app
# 2) create container and flagging_dao off of test container
# 3) make routes
# 4) intialize client
# 5) run test

# def test_simple_create():
#     app = Flask(__name__)
#     app.config["TESTING"] = True
#     with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
#             _create_flagging_dao(container) as flagging_dao:
#         make_routes(app, flagging_dao)
#         client = app.test_client()
#         flag_deletion_url = "flag/delete_all"
#         response = client.delete(flag_deletion_url)
#         assert response.status_code == 200
#         flag_name = "FlagName1A"
#         flag_logic = """\
#         if FF1 > 10:
#             return True
#         else:
#             return False"""
#         payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
#         url = "flag/create/x/" + payload["FLAG_NAME"]
#
#         response = client.post(url, data=json.dumps(payload),
#                                content_type='application/json')
#         unpack = client.get("flag/get")
#
#         print('hello')

def test_simple_create():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        #confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        #confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #confirm standard get
        response_2 = client.get("flag/get")
        assert response_2.status_code == 200
        assert response_2.json["flags"][0]["FLAG_ERRORS"] == ""
        assert response_2.json["flags"][0]["FLAG_LOGIC"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        assert response_2.json["flags"][0]["FLAG_NAME"] == payload["FLAG_NAME"]
        assert response_2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"
        assert response_2.json["flags"][0]["REFERENCED_FLAGS"] == []
        assert response_2.json["flags"][0]["_id"] == response.json["uuid"]



# test flag home page
def test_flag_home():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        response = client.get("flag")
        assert response.status_code == 200
        assert response.get_data().decode("utf-8") == "flag home page to go here"

# test get flags no flags
def test_get_flags_no_flags():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        response = client.get("flag/get")
        assert response.status_code == 200
        assert response.json["flags"] == []


# test get flag ids no ids
def test_get_flag_ids_no_flag_ids():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []


# get specific flag, id does not exist
def test_get_specific_flag_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_id = "1a"*12
        url = "flag/get_specific/" + flag_id
        response = client.get(url)
        assert response.status_code == 404
        assert response.status == "404 NOT FOUND"
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag: " + flag_id + " does not exist"
        assert response.json["simple_message"] == "flag does not exist"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False


def test_get_specific_flag_does_not_exist_2():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + ' has been created'
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        flag_id = "1a"*12
        if flag_id == response.json["uuid"]:
            flag_id = "1b"*12

        url = "flag/get_specific/" + flag_id
        response = client.get(url)
        assert response.status_code == 404
        assert response.status == "404 NOT FOUND"
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag: " + flag_id + " does not exist"
        assert response.json["simple_message"] == "flag does not exist"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False


# get specific flag, no id
def test_get_specific_flag_missing_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        response = client.get("flag/get_specific")
        assert response.status_code == 400
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag id not specified"
        assert response.json["simple_message"] == "flag id not specified"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False



# get specifif flag, id not valid
def test_get_specific_flag_invalid_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_id = "1a"*2
        url = "flag/get_specific/" + flag_id
        response = client.get(url)
        assert response.status_code == 400
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "error converting flag id to Object ID type"
        assert response.json["simple_message"] == "error converting flag id to Object ID type"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False


# get specific flag, valid id, have to create flag first
def test_get_specific_flag_id_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm standard get
        response_2 = client.get("flag/get")
        assert response_2.status_code == 200
        assert response_2.json["flags"][0]["FLAG_ERRORS"] == ""
        assert response_2.json["flags"][0]["FLAG_LOGIC"] == _convert_FLI_to_TFLI(
            determine_variables(payload["FLAG_LOGIC"]))
        assert response_2.json["flags"][0]["FLAG_NAME"] == payload["FLAG_NAME"]
        assert response_2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"
        assert response_2.json["flags"][0]["REFERENCED_FLAGS"] == []
        assert response_2.json["flags"][0]["_id"] == response.json["uuid"]


# create flag, missing flag name
def test_create_flag_missing_flag_name_1():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x"
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag name not specified"
        assert response.json["simple_message"] == "flag name not specified"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []


def test_create_flag_missing_flag_name_2():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = ""
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x" + flag_name
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag name not specified"
        assert response.json["simple_message"] == "flag name not specified"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []


def test_create_flag_missing_flag_name_3():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1a"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create"
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
        assert response.json["flag_logic"] == None
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag name not specified"
        assert response.json["simple_message"] == "flag name not specified"
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []


# create flag, valid, has errors
def test_create_flag_w_errors():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
    if FF1 > 10:
        return True
    else:
        return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " was created but has error in flag logic"
        assert response.json["simple_message"] == "flag created with errors"
        assert response.json["valid"] == False

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm standard get
        response_2 = client.get("flag/get")
        assert response_2.status_code == 200
        assert response_2.json["flags"][0]["FLAG_ERRORS"] == "ERROR"
        assert response_2.json["flags"][0]["FLAG_LOGIC"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        assert response_2.json["flags"][0]["FLAG_NAME"] == payload["FLAG_NAME"]
        assert response_2.json["flags"][0]["FLAG_STATUS"] == "DRAFT"
        assert response_2.json["flags"][0]["REFERENCED_FLAGS"] == []
        assert response_2.json["flags"][0]["_id"] == response.json["uuid"]

#create multiple flags, different names
def test_create_multiple_flags_w_unique_names():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm standard get
        response_2 = client.get("flag/get")
        assert response_2.status_code == 200
        assert response_2.json["flags"][0]["FLAG_ERRORS"] == ""
        assert response_2.json["flags"][0]["FLAG_LOGIC"] == _convert_FLI_to_TFLI(
            determine_variables(payload["FLAG_LOGIC"]))
        assert response_2.json["flags"][0]["FLAG_NAME"] == payload["FLAG_NAME"]
        assert response_2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"
        assert response_2.json["flags"][0]["REFERENCED_FLAGS"] == []
        assert response_2.json["flags"][0]["_id"] == response.json["uuid"]

        #create second flag
        flag_name_2 = "FlagName2AB"
        flag_logic = """\
        if FF1 > 10:
            return True
        else:
            return False"""
        payload = {"FLAG_NAME": flag_name_2, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " was created but has error in flag logic"
        assert response.json["simple_message"] == "flag created with errors"
        assert response.json["valid"] == False
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

#create multiple flags, same name
def test_create_multiple_flags_w_same_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm standard get
        response_2 = client.get("flag/get")
        assert response_2.status_code == 200
        assert response_2.json["flags"][0]["FLAG_ERRORS"] == ""
        assert response_2.json["flags"][0]["FLAG_LOGIC"] == _convert_FLI_to_TFLI(
            determine_variables(payload["FLAG_LOGIC"]))
        assert response_2.json["flags"][0]["FLAG_NAME"] == payload["FLAG_NAME"]
        assert response_2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"
        assert response_2.json["flags"][0]["REFERENCED_FLAGS"] == []
        assert response_2.json["flags"][0]["_id"] == response.json["uuid"]

        #create second flag
        flag_logic = """\
        if FF1 > 10:
            return True
        else:
            return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " was created but has error in flag logic"
        assert response.json["simple_message"] == "flag created with errors"
        assert response.json["valid"] == False
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

#create valid flag that references other imaginary flags
def test_create_valid_flag_w_img_ref_flags():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    if f["Flag_1A"] == True:
        return True
    else:
        return False
else:
    if f["Flag_2B"] == False:
        return True
    else:
        return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #confirm via get pull
        r = client.get("flag/get_specific/"+response.json["uuid"])
        assert r.status_code == 200
        assert r.json["flag_logic"] == response.json["flag_logic"]
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == "found flag id"
        assert r.json["simple_message"] == "found flag id"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == True
        print("hello")


# duplicate flag, missing flag id
def test_duplicate_flag_missing_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #duplicate flag, missing id
        url = "flag/duplicate"
        response = client.post(url)
        assert response.status_code == 400
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag id must be specified"
        assert response.json["simple_message"] == "flag id must be specified"
        assert response.json["valid"] == False
        assert response.json["uuid"] == "None"
        assert response.json["flag_logic"] == None

        #still ony one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1


# duplicate flag, flag id does not exist
def test_duplicate_flag_id_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # duplicate flag, missing id
        new_flag_id = "1a"*12
        if new_flag_id == response.json["uuid"]:
            new_flag_id = "1b"*12
        url = "flag/duplicate/" + new_flag_id
        response = client.post(url)
        assert response.status_code == 404
        assert response.json["flag_name"] == None
        assert response.json["message"] == "flag " + new_flag_id + " does not exist"
        assert response.json["simple_message"] == "flag does not exist"
        assert response.json["valid"] == False
        assert response.json["uuid"] == "None"
        assert response.json["flag_logic"] == None

        # still ony one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1

# duplicate flag, invalid flag id
def test_duplicate_flag_invalid_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # duplicate flag, missing id
        new_flag_id = "1a" * 2
        url = "flag/duplicate/" + new_flag_id
        response = client.post(url)
        assert response.status_code == 400
        assert response.json["flag_name"] == None
        assert response.json["message"] == "error in duplicating flag: " + new_flag_id + ", invalid object Id type"
        assert response.json["simple_message"] == "error in duplicating flag"
        assert response.json["valid"] == False
        assert response.json["uuid"] == "None"
        assert response.json["flag_logic"] == None

        # still ony one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1


def test_duplicate_flag_id_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))


        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # duplicate flag, missing id
        flag_id = response.json["uuid"]
        url = "flag/duplicate/" + flag_id
        r2 = client.post(url)
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]
        assert r2.json["message"] == response.json["uuid"] + " has been duplicated"
        assert r2.json["simple_message"] == "flag has been duplicated"
        assert r2.json["valid"] == True
        assert r2.json["uuid"] != response.json["uuid"]
        assert r2.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 2

        #get new flag id
        response_unpack.json["_ids"].remove(response.json["uuid"])
        new_uuid = response_unpack.json["_ids"][0]

        #get new flag
        url = "flag/get_specific/" + new_uuid
        r3 = client.get(url)
        assert r3.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]
        assert r2.json["message"] == response.json["uuid"] + " has been duplicated"
        assert r2.json["simple_message"] == "flag has been duplicated"
        assert r2.json["valid"] == True
        assert r2.json["uuid"] == new_uuid
        assert r2.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))


# update flag name, missing flag id
def test_update_flag_name_missing_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        flag_id = response.json["uuid"]

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        url = "flag/update_name"
        r = client.put(url)
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "user must specify id of original flag"
        assert r.json["simple_message"] == "missing flag id"
        assert r.json["valid"] == False
        assert r.json["uuid"] == "None"
        assert r.json["flag_logic"] == None

        #still just one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1

        #confirm flag name still the same
        r2 = client.get("flag/get_specific/"+flag_id)
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]

# update flag name, missing new flag name
def test_update_flag_name_missing_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        flag_id = response.json["uuid"]

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        url = "flag/update_name/" + response.json["uuid"]
        r = client.put(url)
        assert r.status_code == 404
        assert r.json["flag_name"] == None
        assert r.json["message"] == "user must specify name of new flag"
        assert r.json["simple_message"] == "missing new flag name"
        assert r.json["valid"] == False
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["flag_logic"] == None

        # still just one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag name still the same
        r2 = client.get("flag/get_specific/" + flag_id)
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]


# update flag name, invalid flag id
def test_update_flag_name_invalid_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        flag_id = response.json["uuid"]

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        invalid_flag_id = "1a"
        new_flag_name = "FlagName1aNew"
        url = "flag/update_name/" + invalid_flag_id + "/" + new_flag_name
        r = client.put(url)
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "error converting: " + invalid_flag_id + " to object Id type"
        assert r.json["simple_message"] == "error updating flag name"
        assert r.json["valid"] == False
        assert r.json["uuid"] == "None"
        assert r.json["flag_logic"] == None

        # still just one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag name still the same
        r2 = client.get("flag/get_specific/" + flag_id)
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]


# update flag name, flag id does not exist
def test_update_flag_name_flag_id_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))
        flag_id = response.json["uuid"]

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        invalid_flag_id = "1a"*12
        if invalid_flag_id == response.json["uuid"]:
            invalid_flag_id = "1b"*12
        new_flag_name = "FlagName1aNew"
        url = "flag/update_name/" + invalid_flag_id + "/" + new_flag_name
        r = client.put(url)
        assert r.status_code == 404
        assert r.json["flag_name"] == None
        assert r.json["message"] == "original flag id " + invalid_flag_id + " does not exist"
        assert r.json["simple_message"] == "flag id does not exist"
        assert r.json["valid"] == False
        assert r.json["uuid"] == "None"
        assert r.json["flag_logic"] == None

        # still just one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag name still the same
        r2 = client.get("flag/get_specific/" + flag_id)
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]

# update flag name, flag in more than one flag group
def test_update_flag_name_flag_id_in_multi_groups():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #create two valid flag groups
        flag_name_1 = "FlagName1"
        flag_name_2 = "FlagName2"

        url_1 = "flag_group/create/x/" + flag_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        url_2 = "flag_group/create/x/" + flag_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_name_2 + " created"
        assert response_group_2.json["simple_message"] == "new flag group created"
        assert response_group_2.json["valid"] == True
        assert response_group_2.json["flags_in_flag_group"] == None

        #confirm two flag groups
        r_ids = client.get("flag_group/get_ids")
        assert len(r_ids.json["_ids"]) == 2
        assert response_group_1.json["uuid"] in r_ids.json["_ids"]
        assert response_group_2.json["uuid"] in r_ids.json["_ids"]

        #add falg to flag group 1
        url = "flag_group/add_flag/" + response_group_1.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_1 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_1.status_code == 200
        assert r_add_1.json["flag_group_name"] == flag_name_1
        assert r_add_1.json["message"] == "flag group " + response_group_1.json["uuid"] + " has been updated with flag(s) " + (
                                                           ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_1.json["simple_message"] == "flags added to flag group"
        assert r_add_1.json["uuid"] == response_group_1.json["uuid"]
        assert r_add_1.json["valid"] == True
        assert r_add_1.json["flags_in_flag_group"] == [response.json["uuid"]]

        # add falg to flag group 2
        url = "flag_group/add_flag/" + response_group_2.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_2 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_2.status_code == 200
        assert r_add_2.json["flag_group_name"] == flag_name_2
        assert r_add_2.json["message"] == "flag group " + response_group_2.json[
            "uuid"] + " has been updated with flag(s) " + (
                   ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_2.json["simple_message"] == "flags added to flag group"
        assert r_add_2.json["uuid"] == response_group_2.json["uuid"]
        assert r_add_2.json["valid"] == True
        assert r_add_2.json["flags_in_flag_group"] == [response.json["uuid"]]

        #attempt to update flag name
        new_flag_name = "FlagName1aNew"
        url = "flag/update_name/" + response.json["uuid"] + "/" + new_flag_name
        r = client.put(url)
        assert r.status_code == 405
        assert r.json["flag_name"] == None
        assert r.json["message"] == "flag id: " + response.json["uuid"] + " can not be modified because it is contained in the following flag groups: " + ", ".join([response_group_1.json["uuid"], response_group_2.json["uuid"]])
        assert r.json["simple_message"] == "flag can not be modified"
        assert r.json["valid"] == False
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["flag_logic"] == None

        # still just one flag
        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag name still the same
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]


# update flag name, new name is same as old name
def test_update_flag_name_non_unique_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #attempt to update with same flag name
        url = "flag/update_name/" + response.json["uuid"] + "/" + payload["FLAG_NAME"]
        r = client.put(url)
        assert r.status_code == 405
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == "flag id: " + response.json["uuid"] + " with name: " + payload["FLAG_NAME"] + " must be given a new unique name"
        assert r.json["simple_message"] == "new flag name must be different than original flag name"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag name still the same
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_name"] == payload["FLAG_NAME"]



# update flag name, valid
def test_update_flag_name_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # attempt to update with same flag name
        new_flag_name = "NewFlagName1a"
        url = "flag/update_name/" + response.json["uuid"] + "/" + new_flag_name
        r = client.put(url)
        assert r.status_code == 200
        assert r.json["flag_name"] == new_flag_name
        assert r.json["message"] == "original flag " + response.json["uuid"] + " has been renamed " + new_flag_name
        assert r.json["simple_message"] == "flag has been renamed"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == True
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        #confirm only one flag
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert len(r2.json["_ids"]) == 1
        assert response.json["uuid"] in r2.json["_ids"]

        # confirm flag name has been updated
        r3 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r3.status_code == 200
        assert r3.json["flag_name"] == new_flag_name



# update flag logic, missing flag id
def test_update_flag_logic_missing_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200

        # confirm empty database
        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        #attempt to update flag logic without flag id
        url = "flag/update_logic"
        r = client.put(url)
        assert r.status_code == 400
        assert response.json["flag_name"] == None
        assert response.json["message"] == "user must specify flag id",
        assert response.json["simple_message"] == "user must specify flag id",
        assert response.json["uuid"] == "None"
        assert response.json["valid"] == False
        assert response.json["flag_logic"] == None

        #confirm flag still exists
        # confirm only one flag
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert len(r2.json["_ids"]) == 1
        assert response.json["uuid"] in r2.json["_ids"]

        # confirm flag logic is still the same
        r3 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r3.status_code == 200
        assert r3.json["flag_logic"] == response.json["flag_logic"]


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

    # create unique new id
    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    # call incorrect id
    url_incorrect_id = "flag/update_flag_logic/" + new_id
    response = client.put(url_incorrect_id)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


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

    # invalid id
    url_invalid_id = "flag/update_flag_logic/1A1A"
    response = client.put(url_invalid_id)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


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

    # update logic default update
    url_update_logic = "flag/update_flag_logic/" + id
    response = client.put(url_update_logic)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# delete flag, missing flag id
def test_delete_flag_missing_flag_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # url missing id
    flag_delete_url = "flag/delete_flag"
    response = client.delete(flag_delete_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# delete flag, flag id does not exist
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

    # delete missing id
    url_missing_id = "flag/delete_flag/" + new_id
    response = client.delete(url_missing_id)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# delete flag, invalid flag id
def test_delete_flag_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # invaid id url
    url_invalid_id = "flag/delete_flag/1A1A"
    response = client.delete(url_invalid_id)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# delete flag, flag in more than one flag group
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


# delete flag, valid
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

    # delete flag
    delete_flag_url = "flag/delete_flag/" + id
    response = client.delete(delete_flag_url)
    assert response.status_code == 200

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# move flag to production, missing id
def test_move_flag_to_production_missing_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # move to production
    flag_production_url = "flag/move_flag_to_production"
    response = client.put(flag_production_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# move flag to production, id does not exist
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

    # generate new id
    new_id = str(generate())
    while id == new_id:
        new_id = str(generate())

    # move to production
    flag_production_url = "flag/move_flag_to_production/" + new_id
    response = client.put(flag_production_url)
    assert response.status_code == 404

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# move flag to production, invalid id
def test_move_flag_to_production_invalid_id(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200

    # create flag
    flag_creation_url = "flag/create_flag/XX/Flag1A"
    response = client.post(flag_creation_url)
    assert response.status_code == 200

    # flag production
    flag_production_url = "flag/move_flag_to_production/2A1A"
    response = client.put(flag_production_url)
    assert response.status_code == 400

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# move flag to production, error in flag
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

    # production flag
    flag_production_url = "flag/move_flag_to_production/" + id
    response = client.put(flag_production_url)
    assert response.status_code == 405

    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200


# move flag to production, valid
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


# get flag groups
def test_get_flag_groups(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group
    flag_group_get_url = "flag_group/get_flag_groups"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag group ids
def test_get_flag_group_ids(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group
    flag_group_get_url = "flag_group/get_flag_group_ids"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag group names
def test_get_flag_group_names(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group
    flag_group_get_url = "flag_group/get_flag_group_names"
    response = client.get(flag_group_get_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag ids in flag group, missing id
def test_get_flags_in_flag_group_missing_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get_flag_group_flags_missing_id
    url_get_flag_group = "flag_group/get_flag_group_flags"
    response = client.get(url_get_flag_group)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag ids in flag group, flag group does not exist
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

    # get flag group flags
    url_get_flag_group_flags = "flag_group/get_flag_group_flags/" + new_id
    response = client.get(url_get_flag_group_flags)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag ids in flag group, invalid flag group id
def test_get_flags_in_flag_group_invalid_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flags
    flag_group_flags_get_url = "flag_group/get_flag_group_flags/1A1A"
    response = client.get(flag_group_flags_get_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get flag ids in flag group, valid
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

    # get flags in flag group
    flag_in_flag_group_url = "flag_group/get_flag_group_flags/" + id
    response = client.get(flag_in_flag_group_url)
    assert response.status_code == 200

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get specific flag group, missing id
def test_get_specific_flag_group_missing_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # get flag group
    flag_group_get_url = "flag_group/get_specific_flag_group"
    response = client.get(flag_group_get_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get specific flag group, id does not exist
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

    # get specific flag group
    flag_group_get_url = "flag_group/get_specific_flag_group/" + new_id
    response = client.get(flag_group_get_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# get specific flag group, invalid id
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


# get specific flag group, valid
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


# create flag group, missing name
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


# create flag group, non unique name
def test_create_flag_group_non_unique_name(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # create flag group
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 200

    # 2nd flag group create
    flag_group_creation_url = "flag_group/create_flag_group/XX/FlagGroup1A"
    response = client.post(flag_group_creation_url)
    assert response.status_code == 404

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# create flag group, valid
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


# delete flag group, no id
def test_delete_flag_group_no_id(client):
    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200

    # delete flag group
    flag_group_delete_url = "flag_group/delete_flag_group"
    response = client.delete(flag_group_delete_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# delete flag group, id does not exist
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


# delete flag group, invalid id
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


# delete flag group, valid
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


# add flag to flag group, missing flag group id
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

    # add flag to flag group
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


# add flag to flag group, flag group id does not exist
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

    # add flag to flag group
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


# add flag to flag group, invalid flag group id
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

    # add flag to flag group
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


# add flag to flag group, missing flag id
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


# add flag to flag group, flag id does not exist
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

    # create new unique flag id
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

    # add flag to flag group
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


# add flag to flag group, invalid flag id
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

    # add flag to flag group
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

    # create new unique flag id
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

    # add flag to flag group
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


# add flag to flag group, flag id already exists in flag group
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


# add flag to flag group, flag name already exists in flag group
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

    # create second flag with same name
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


# add flag to flag group, valid
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

    # create second flag with same name
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


# remove flag from flag group, missing flag group id
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

    # remove flag from flag group
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


# remove flag from flag group, flag group id does not exist
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

    # create new unique id
    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    # remove flag from flag group
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


# remove flag from flag group, flag group id is not valid
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

    # remove flag
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


# remove flag from flag group, missing flag to remove
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

    # remove flag
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


# remove flag from flag group, flag to remove does not exist
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

    # create unique flag id
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

    # remove flag
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


# remove flag from flag group, flag does not exist in flag group
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

    # add flag 1 to flag group
    flag_add_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id_1
    response = client.put(flag_add_url)
    assert response.status_code == 200

    # remove flag 2
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


# remove flag from flag group, invalid flag id
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

    # remove flag invalid
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


# remove flag from flag group, valid
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

    # add flag
    add_flag_url = "flag_group/add_flag_to_flag_group/" + flag_group_id + "/x/" + flag_id
    response = client.put(add_flag_url)
    assert response.status_code == 200

    # remove flag
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


# duplicate flag group, missing flag group id
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

    # duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# duplicate flag group, flag group does not exist
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

    # create new unique flag group id
    new_flag_group_id = str(generate())
    while flag_group_id == new_flag_group_id:
        new_flag_group_id = str(generate())

    # duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + new_flag_group_id + "/FlagGroup2B"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 404

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# duplicate flag group, invalid flag group id
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

    # duplicate flag group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/1A1A/FlagGroup2B"
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# duplicate flag group, missing new name
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

    # duplicate_flag_group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + flag_group_id
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 400

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# duplicate flag group, new name same as old name
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

    # duplicate_flag_group
    flag_group_duplicate_url = "flag_group/duplicate_flag_group/" + flag_group_id + "/" + flag_group_name
    response = client.post(flag_group_duplicate_url)
    assert response.status_code == 405

    # delete all flag group
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# dupliacte flag group, valid
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


# move flag group to production, missing flag group id
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

    # move flag group to production
    move_flag_group_to_production_url = "flag_group/move_flag_group_to_production"
    response = client.put(move_flag_group_to_production_url)
    assert response.status_code == 400

    # delete all flag groups
    flag_group_deletion_url = "flag_group/delete_all_flag_groups"
    response = client.delete(flag_group_deletion_url)
    assert response.status_code == 200


# move flag group to production, flag group does not exist
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

    # create new unique flag group id
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


# move flag group to production, invalid flag group id
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


# move flag group to production, error in flag group
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

    # add flag to flag group, flag has error, thereby flag group will have error
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

def test_create_flag_full_valid():
    flag_logic ="""\
if FF1 > 10:
    return True
else:
    return False"""
    flag_logic_information = determine_variables(flag_logic)
    flag_name = "Flag2B"
    url_prefix = "http://localhost:5000/"
    url = url_prefix + "flag/create_flag/x/" + flag_name
    r = requests.post(url=url, data={"flag_logic_information": flag_logic_information})

    #get date
    r = requests.get(url=url_prefix+"flag/get_flags")
    get_payload = r.json()
    print('hello')

    r = requests.get(url="flag/get_flags")
    print("hello")

def test_simple_get():
    flag_logic ="""\
if FF1 > 10:
    return True
else:
    return False"""
    flag_logic_information = determine_variables(flag_logic)
    flag_name = "Flag1A"
    url_prefix = "http://localhost:5000/"
    url = url_prefix + "flag/get_flag_ids"
    r = requests.get(url=url)
    payload = r.json()
    print('hello')

    r = requests.get(url="flag/get_flags")
    print("hello")

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

def test_simple_request_post(client):
    # delete all flags
    flag_deletion_url = "flag/delete_all_flags"
    response = client.delete(flag_deletion_url)
    assert response.status_code == 200
    flag_name = "FlagName1A"
    flag_logic ="""\
if FF1 > 10:
    return True
else:
    return False"""
    payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}

    #data needs to be {"Flag_Name": flag_name, "Flag_String": flag_string"}
    #do unpacking on api side

    response = client.post("flag/create_flag/x/Flag1A", data=json.dumps(payload),
                           content_type='application/json')
    # url = "http://localhost:5000/flag/create_flag/x/Flag1A"
    #
    # r = requests.post(url, data=json.dumps(payload))

    unpack = client.get("flag/get_flags")
    print("hello")

def _get_connection_string(container):
    return "mongodb://test:test@localhost:"+container.get_exposed_port(27017)













