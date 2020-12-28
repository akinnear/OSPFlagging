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

#duplicate flag, valid
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
        flag_group_name_1 = "FlagGroupName1"
        flag_group_name_2 = "FlagGroupName2"

        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        url_2 = "flag_group/create/x/" + flag_group_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_group_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_group_name_2 + " created"
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
        assert r_add_1.json["flag_group_name"] == flag_group_name_1
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
        assert r_add_2.json["flag_group_name"] == flag_group_name_2
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

        #attempt to update flag logic
        flag_logic = """\
if FF1 > 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGIC": flag_logic}
        r = client.put("flag/update_logic", data=json.dumps(payload_2), content_type="application/json")
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "user must specify flag id"
        assert r.json["simple_message"] == "user must specify flag id"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

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
def test_update_flag_logic_id_does_not_exist():
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

        # attempt to update flag logic
        flag_logic = """\
if FF1 > 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGIC": flag_logic}
        new_id = "1a" * 12
        if new_id == response.json["uuid"]:
            new_id = "1b" * 12
        r = client.put("flag/update_logic/" + new_id, data=json.dumps(payload_2), content_type="application/json")
        assert r.status_code == 404
        assert r.json["flag_name"] == None
        assert r.json["message"] == "flag id " + new_id + " does not exist"
        assert r.json["simple_message"] == "flag id does not exist"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag still exists
        # confirm only one flag
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert len(r2.json["_ids"]) == 1
        assert response.json["uuid"] in r2.json["_ids"]

        # confirm flag logic is still the same
        r3 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r3.status_code == 200
        assert r3.json["flag_logic"] == response.json["flag_logic"]

# update flag logic, invalid flag id
def test_update_flag_logic_invalid_id():
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

        # attempt to update flag logic
        flag_logic = """\
if FF1 > 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGIC": flag_logic}
        new_id = "1a"
        r = client.put("flag/update_logic/" + new_id, data=json.dumps(payload_2), content_type="application/json")
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "error converting: " + new_id + " to object Id type"
        assert r.json["simple_message"] == "error in updating flag logic"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag still exists
        # confirm only one flag
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert len(r2.json["_ids"]) == 1
        assert response.json["uuid"] in r2.json["_ids"]

        # confirm flag logic is still the same
        r3 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r3.status_code == 200
        assert r3.json["flag_logic"] == response.json["flag_logic"]

# update flag logic, flag in more than one flag group
def test_update_flag_logic_multi_group():
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

        # create two valid flag groups
        flag_group_name_1 = "FlagGroupName1"
        flag_group_name_2 = "FlagGroupName2"

        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        url_2 = "flag_group/create/x/" + flag_group_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_group_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_group_name_2 + " created"
        assert response_group_2.json["simple_message"] == "new flag group created"
        assert response_group_2.json["valid"] == True
        assert response_group_2.json["flags_in_flag_group"] == None

        # confirm two flag groups
        r_ids = client.get("flag_group/get_ids")
        assert len(r_ids.json["_ids"]) == 2
        assert response_group_1.json["uuid"] in r_ids.json["_ids"]
        assert response_group_2.json["uuid"] in r_ids.json["_ids"]

        # add flag to flag group 1
        url = "flag_group/add_flag/" + response_group_1.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_1 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_1.status_code == 200
        assert r_add_1.json["flag_group_name"] == flag_group_name_1
        assert r_add_1.json["message"] == "flag group " + response_group_1.json[
            "uuid"] + " has been updated with flag(s) " + (
                   ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_1.json["simple_message"] == "flags added to flag group"
        assert r_add_1.json["uuid"] == response_group_1.json["uuid"]
        assert r_add_1.json["valid"] == True
        assert r_add_1.json["flags_in_flag_group"] == [response.json["uuid"]]

        # add flag to flag group 2
        url = "flag_group/add_flag/" + response_group_2.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_2 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_2.status_code == 200
        assert r_add_2.json["flag_group_name"] == flag_group_name_2
        assert r_add_2.json["message"] == "flag group " + response_group_2.json[
            "uuid"] + " has been updated with flag(s) " + (
                   ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_2.json["simple_message"] == "flags added to flag group"
        assert r_add_2.json["uuid"] == response_group_2.json["uuid"]
        assert r_add_2.json["valid"] == True
        assert r_add_2.json["flags_in_flag_group"] == [response.json["uuid"]]

        # attempt to update flag logic
        flag_logic = """\
if FF1 > 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGIC": flag_logic}
        r = client.put("flag/update_logic/" + response.json["uuid"], data=json.dumps(payload_2), content_type="application/json")
        assert r.status_code == 405
        assert r.json["flag_name"] == None
        assert r.json["message"] == "flag id: " + response.json["uuid"] + " can not be modified because it is contained in the following flag groups: " + ", ".join(
                                                           [response_group_1.json["uuid"], response_group_2.json["uuid"]])
        assert r.json["simple_message"] == "flag logic can not be modified"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # still just one flag
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag logic still the same
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_logic"] == response.json["flag_logic"]

#update flag logic, missing new logic payload
def test_update_flag_logic_missing_new_logic_payload():
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
        response = client.put(url, data=json.dumps(payload), content_type='application/json')
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

        #attempt to update flag logic
        r = client.put("flag/update_logic/" + response.json["uuid"])
        assert r.status_code == 400
        assert r.json["message"] == "error reading flag data to update flag logic"
        assert r.json["simple_message"] == "error reading flag data to update flag logic"
        assert r.json["valid"] == False

        # still just one flag
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag logic still the same
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_logic"] == response.json["flag_logic"]

#update flag logic, error unpacking new logic
def test_update_flag_logic_error_unpacking_new_logic():
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

        #attempt to update flag logic
        new_logic = """\
 if FF1 > 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGICX": new_logic}
        r = client.put("flag/update_logic/"+response.json["uuid"], data=json.dumps(payload_2), content_type='application/json')
        assert r.status_code == 400
        assert r.json["message"] == "error converting flag data to proper form to update flag logic"
        assert r.json["simple_message"] == "error converting flag data to proper form to update flag logic"
        assert r.json["valid"] == False

        # still just one flag
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag logic still the same
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_logic"] == response.json["flag_logic"]

#update flag lgoic, syntax error in new logic payload
def test_update_flag_logic_errors_in_flag_logic():
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

        #attempt to update flag logic
        new_logic = """wackity smackity doo, 23casae\b\b\v\b\n\nds\b\vasdfa"""
        payload_2 = {"FLAG_LOGIC": new_logic}
        r = client.put("flag/update_logic/"+response.json["uuid"], data=json.dumps(payload_2), content_type='application/json')
        assert r.status_code == 200
        assert r.json["flag_name"] == response.json["flag_name"]
        assert r.json["message"] == "error in flag logic"
        assert r.json["simple_message"] == "new logic updated but has errors"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))

        # still just one flag
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag logic has been updated, errors put flag in draft status
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_logic"] == r.json["flag_logic"]
        r3 = client.get("flag/get")
        assert r3.status_code == 200
        assert r3.json["flags"][0]["FLAG_ERRORS"] == "ERROR"
        assert r3.json["flags"][0]["FLAG_STATUS"] == "DRAFT"

#update flag logic, create cyclical flag
def test_update_flag_logic_create_cyclical_flag():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag, no flag references
        flag_name_1 = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_1 = response.json["uuid"]

        # create flags that reference original flag
        flag_name_2 = "FlagName2B"
        flag_logic = f"""\
if f["{flag_name_1}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_2, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_2 = response.json["uuid"]

        flag_name_3 = "FlagName3C"
        flag_logic = f"""\
if f["{flag_name_2}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_3, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_3 = response.json["uuid"]

        flag_name_4 = "FlagName4D"
        flag_logic = f"""\
if f["{flag_name_3}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_4, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_4 = response.json["uuid"]

        #create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #add flag 1 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_1)
        assert r.status_code == 200

        #confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][0]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][0]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][0]["FLAG_NAME"] == flag_name_1

        # add flag 2 to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_2)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][1]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][1]["FLAG_ID"] == flag_id_2
        assert r.json["flag_deps"][1]["FLAG_NAME"] == flag_name_2
        assert r.json["flag_deps"][1]["DEPENDENT_FLAGS"] == [flag_name_1]

        #add flag 3 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_3)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][2]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][2]["FLAG_ID"] == flag_id_3
        assert r.json["flag_deps"][2]["FLAG_NAME"] == flag_name_3
        assert r.json["flag_deps"][2]["DEPENDENT_FLAGS"] == [flag_name_2]

        #add flag 4 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_4)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][3]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][3]["FLAG_ID"] == flag_id_4
        assert r.json["flag_deps"][3]["FLAG_NAME"] == flag_name_4
        assert r.json["flag_deps"][3]["DEPENDENT_FLAGS"] == [flag_name_3]


        #update flag 1 to reference flag 4, confirm cyclical flag behavior
        flag_name_1 = "FlagName1A"
        flag_logic = f"""\
if f["{flag_name_4}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/update_logic/"+flag_id_1
        r = client.put(url, data=json.dumps(payload), content_type='application/json')

        assert r.status_code == 200
        assert r.json["flag_name"] == flag_name_1
        assert r.json["message"] == "error in flag logic"
        assert r.json["simple_message"] == "new logic updated but has errors"
        assert r.json["uuid"] == flag_id_1
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        #pull flag dep entries
        response = client.get("flag_dependency/get")
        assert response.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][3]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][3]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][3]["FLAG_NAME"] == flag_name_1
        assert r.json["flag_deps"][3]["DEPENDENT_FLAGS"] == [flag_name_4]

        #confirm that both flag 1 and flag group are no longer production ready due to cyclical flags
        r = client.get("flag/get")
        assert r.json["flags"][0]["FLAG_ERRORS"] == "ERROR"
        assert r.json["flags"][0]["FLAG_STATUS"] == "DRAFT"
        assert r.json["flags"][0]["_id"] == flag_id_1

        r = client.get("flag_group/get")
        assert set(r.json["flag_groups"][0]["FLAGS_IN_GROUP"]) == set([flag_id_1, flag_id_2, flag_id_3, flag_id_4])
        assert r.json["flag_groups"][0]["FLAG_GROUP_ERRORS"] == "CYCLICAL ERROR"
        assert r.json["flag_groups"][0]["FLAG_GROUP_STATUS"] == "DRAFT"
        assert r.json["flag_groups"][0]["_id"] == flag_group_id
        print("hello")

def test_update_flag_logic_create_cyclical_flag_2():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag, no flag references
        flag_name_1 = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_1 = response.json["uuid"]

        # create flags that reference original flag
        flag_name_2 = "FlagName2B"
        flag_logic = f"""\
if f["{flag_name_1}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_2, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_2 = response.json["uuid"]

        #create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #add flag 1 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_1)
        assert r.status_code == 200

        #confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][0]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][0]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][0]["FLAG_NAME"] == flag_name_1

        # add flag 2 to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_2)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][1]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][1]["FLAG_ID"] == flag_id_2
        assert r.json["flag_deps"][1]["FLAG_NAME"] == flag_name_2
        assert r.json["flag_deps"][1]["DEPENDENT_FLAGS"] == [flag_name_1]




        #update flag 1 to reference flag 4, confirm cyclical flag behavior
        flag_name_1 = "FlagName1A"
        flag_logic = f"""\
if f["{flag_name_2}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/update_logic/"+flag_id_1
        r = client.put(url, data=json.dumps(payload), content_type='application/json')

        assert r.status_code == 200
        assert r.json["flag_name"] == flag_name_1
        assert r.json["message"] == "error in flag logic"
        assert r.json["simple_message"] == "new logic updated but has errors"
        assert r.json["uuid"] == flag_id_1
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        #pull flag dep entries
        response = client.get("flag_dependency/get")
        assert response.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][1]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][1]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][1]["FLAG_NAME"] == flag_name_1
        assert r.json["flag_deps"][1]["DEPENDENT_FLAGS"] == [flag_name_2]

        #confirm that both flag 1 and flag group are no longer production ready due to cyclical flags





# update flag logic, valid
def test_update_flag_logic_valid():
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

        # attempt to update flag logic
        new_logic = """\
if FF2 < 5:
    return False
else:
    return True"""
        payload_2 = {"FLAG_LOGIC": new_logic}
        r = client.put("flag/update_logic/" + response.json["uuid"], data=json.dumps(payload_2),
                       content_type='application/json')
        assert r.status_code == 200
        assert r.json["flag_name"] == response.json["flag_name"]
        assert r.json["message"] == "logic for flag " + response.json["uuid"] + " has been updated"
        assert r.json["simple_message"] == "flag logic has been updated"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == True
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))

        # still just one flag
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # confirm flag logic has been updated, errors put flag in draft status
        r2 = client.get("flag/get_specific/" + response.json["uuid"])
        assert r2.status_code == 200
        assert r2.json["flag_logic"] == r.json["flag_logic"]
        r3 = client.get("flag/get")
        assert r3.status_code == 200
        assert r3.json["flags"][0]["FLAG_ERRORS"] == ""
        assert r3.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION READY"

# delete flag, missing flag id
def test_delete_flag_missing_flag_id():
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

        #attempt to delete flag
        r = client.delete("flag/delete")
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "user must specify flag id"
        assert r.json["simple_message"] == "missing flag id"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        #confirm flag still exists
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

# delete flag, flag id does not exist
def test_delete_flag_id_does_not_exist():
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

        # attempt to delete flag
        new_id = "1a"*12
        if new_id == response.json["uuid"]:
            new_id = "1b"*12
        r = client.delete("flag/delete/" + new_id)
        assert r.status_code == 404
        assert r.json["flag_name"] == None
        assert r.json["message"] == "flag id " + new_id + " does not exist"
        assert r.json["simple_message"] == "flag id does not exist"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag still exists
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

# delete flag, invalid flag id
def test_delete_flag_invalid_id():
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

        # attempt to delete flag
        new_id = "1a"
        r = client.delete("flag/delete/" + new_id)
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "error converting: " + new_id + " to object Id type"
        assert r.json["simple_message"] == "error in deleting flag"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag still exists
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

# delete flag, flag in more than one flag group
def test_delete_flag_multi_group():
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

        # create two valid flag groups
        flag_group_name_1 = "FlagGroupName1"
        flag_group_name_2 = "FlagGroupName2"

        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        url_2 = "flag_group/create/x/" + flag_group_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_group_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_group_name_2 + " created"
        assert response_group_2.json["simple_message"] == "new flag group created"
        assert response_group_2.json["valid"] == True
        assert response_group_2.json["flags_in_flag_group"] == None

        # confirm two flag groups
        r_ids = client.get("flag_group/get_ids")
        assert len(r_ids.json["_ids"]) == 2
        assert response_group_1.json["uuid"] in r_ids.json["_ids"]
        assert response_group_2.json["uuid"] in r_ids.json["_ids"]

        # add flag to flag group 1
        url = "flag_group/add_flag/" + response_group_1.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_1 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_1.status_code == 200
        assert r_add_1.json["flag_group_name"] == flag_group_name_1
        assert r_add_1.json["message"] == "flag group " + response_group_1.json[
            "uuid"] + " has been updated with flag(s) " + (
                   ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_1.json["simple_message"] == "flags added to flag group"
        assert r_add_1.json["uuid"] == response_group_1.json["uuid"]
        assert r_add_1.json["valid"] == True
        assert r_add_1.json["flags_in_flag_group"] == [response.json["uuid"]]

        # add flag to flag group 2
        url = "flag_group/add_flag/" + response_group_2.json["uuid"] + "/x/" + response.json["uuid"]
        r_add_2 = client.put(url)
        flagging_message = ""
        new_flags = [response.json["uuid"]]
        assert r_add_2.status_code == 200
        assert r_add_2.json["flag_group_name"] == flag_group_name_2
        assert r_add_2.json["message"] == "flag group " + response_group_2.json[
            "uuid"] + " has been updated with flag(s) " + (
                   ", ".join(map(str, new_flags))) + "\n" + flagging_message
        assert r_add_2.json["simple_message"] == "flags added to flag group"
        assert r_add_2.json["uuid"] == response_group_2.json["uuid"]
        assert r_add_2.json["valid"] == True
        assert r_add_2.json["flags_in_flag_group"] == [response.json["uuid"]]

       #attempt to delete flag
        r = client.delete("flag/delete/"+response.json["uuid"])
        assert r.status_code == 405
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == "flag id: " + response.json["uuid"] + " can not be modified because " \
                                                                                 "it is contained in the following flag groups: " + ", ".join(str(x) for x in [response_group_1.json["uuid"], response_group_2.json["uuid"]])
        assert r.json["simple_message"] == "flag can not be deleted"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm flag still exists
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert len(response_unpack.json["_ids"]) == 1
        assert response.json["uuid"] in response_unpack.json["_ids"]

# delete flag, valid
def test_delete_flag_valid():
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

        #attempt to delete flag
        url = "flag/delete/" + response.json["uuid"]
        r = client.delete(url)
        assert r.status_code == 200
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == response.json["uuid"] + " has been deleted"
        assert r.json["simple_message"] == "flag has been deleted"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == True
        assert r.json["flag_logic"] == None

        #confirm flag deletion
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert r2.json["_ids"] == []

def test_delete_flag_valid_2():
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

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 > 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response_2 = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response_2.status_code == 200
        assert response_2.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response_2.json["message"] == "flag id: " + response_2.json["uuid"] + " has been created"
        assert response_2.json["simple_message"] == "new flag created"
        assert response_2.json["valid"] == True
        assert response_2.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))

        #confirm second flag creation
        r_id = client.get("flag/get_ids")
        assert r_id.status_code == 200
        assert r_id.json["_ids"] == [response.json["uuid"], response_2.json["uuid"]]

        # attempt to delete flag
        url = "flag/delete/" + response.json["uuid"]
        r = client.delete(url)
        assert r.status_code == 200
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == response.json["uuid"] + " has been deleted"
        assert r.json["simple_message"] == "flag has been deleted"
        assert r.json["uuid"] == response.json["uuid"]
        assert r.json["valid"] == True
        assert r.json["flag_logic"] == None

        # confirm flag deletion
        r2 = client.get("flag/get_ids")
        assert r2.status_code == 200
        assert r2.json["_ids"] == [response_2.json["uuid"]]

        r3 = client.get("flag/get_specific/"+response.json["uuid"])
        assert r3.status_code == 404
        assert r3.json["flag_name"] == None
        assert r3.json["message"] == "flag: " + response.json["uuid"] + " does not exist"
        assert r3.json["simple_message"] == "flag does not exist"
        assert r3.json["uuid"] == "None"
        assert r3.json["valid"] == False
        assert r3.json["flag_logic"] == None

# move flag to production, missing id
def test_move_flag_to_production_missing_id():
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

        #get flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

        #attempt to move flag to production
        r = client.put("flag/move_to_production")
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "user must specify flag id"
        assert r.json["simple_message"] == "user must specify flag id"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm same flag status as before
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

# move flag to production, id does not exist
def test_move_flag_to_production_id_no_exist():
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

        # get flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

        # attempt to move flag to production
        flag_id = "1a"*12
        if flag_id == response.json["uuid"]:
            flag_id = "1b"*12
        r = client.put("flag/move_to_production/"+flag_id)
        assert r.status_code == 404
        assert r.json["flag_name"] == None
        assert r.json["message"] == "flag id: " + flag_id + " does not exist"
        assert r.json["simple_message"] == "flag id does not exist"
        assert r.json["uuid"] == flag_id
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm same flag status as before
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

# move flag to production, invalid id
def test_move_flag_to_production_invalid_id():
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

        # get flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

        # attempt to move flag to production
        flag_id = "1a"
        r = client.put("flag/move_to_production/" + flag_id)
        assert r.status_code == 400
        assert r.json["flag_name"] == None
        assert r.json["message"] == "error converting: " + flag_id + " to object Id type"
        assert r.json["simple_message"] == "error moving flag to production"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm same flag status as before
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

# move flag to production, error in flag
def test_move_flag_to_production_error_in_flag():
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
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " was created but has error in flag logic"
        assert response.json["simple_message"] == "flag created with errors"
        assert response.json["valid"] == False
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        # get flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "DRAFT"

        # attempt to move flag to production
        flag_id = response.json["uuid"]
        r = client.put("flag/move_to_production/" + flag_id)
        assert r.status_code == 405
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == "flag id: " + flag_id + " can not be moved to production due to flag errors"
        assert r.json["simple_message"] == "flag can not be moved to production due to flag errors"
        assert r.json["uuid"] == flag_id
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == None

        # confirm same flag status as before
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "DRAFT"

# move flag to production, valid
def test_move_flag_to_production_valid():
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

        # get flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION_READY"

        # attempt to move flag to production
        flag_id = response.json["uuid"]
        r = client.put("flag/move_to_production/" + flag_id)
        assert r.status_code == 200
        assert r.json["flag_name"] == payload["FLAG_NAME"]
        assert r.json["message"] == "flag id: " + flag_id + " has been moved to production"
        assert r.json["simple_message"] == "flag has been moved to production"
        assert r.json["uuid"] == flag_id
        assert r.json["valid"] == True
        assert r.json["flag_logic"] == None

        # confirm change in flag status
        r2 = client.get("flag/get")
        assert r2.status_code == 200
        assert r2.json["flags"][0]["FLAG_STATUS"] == "PRODUCTION"

# get flag groups
def test_get_flag_groups():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        response = client.get("flag_group/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        #create flag
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

        #create flag group
        flag_group_name = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        #flag group get
        r = client.get("flag_group/get")
        assert r.status_code == 200
        assert r.json["flag_groups"][0]["FLAGS_IN_GROUP"] == {}
        assert r.json["flag_groups"][0]["FLAG_GROUP_ERRORS"] == ""
        assert r.json["flag_groups"][0]["FLAG_GROUP_NAME"] == flag_group_name
        assert r.json["flag_groups"][0]["FLAG_GROUP_STATUS"] == "PRODUCTION_READY"
        assert r.json["flag_groups"][0]["_id"] == response_group_1.json["uuid"]

        #add flag to flag group
        r = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id)
        assert r.status_code == 200

        #flag group get with new flag in group
        r2 = client.get("flag_group/get")
        assert r2.status_code == 200
        assert r2.json["flag_groups"][0]["FLAGS_IN_GROUP"] == [flag_id]
        assert r2.json["flag_groups"][0]["FLAG_GROUP_ERRORS"] == ""
        assert r2.json["flag_groups"][0]["FLAG_GROUP_NAME"] == flag_group_name
        assert r2.json["flag_groups"][0]["FLAG_GROUP_STATUS"] == "PRODUCTION_READY"
        assert r2.json["flag_groups"][0]["_id"] == response_group_1.json["uuid"]



# get flag group ids
def test_get_flag_group_ids():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        response = client.get("flag_group/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        # create flag group
        flag_group_name_2 = "FlagGroupName2"
        url_2 = "flag_group/create/x/" + flag_group_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_group_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_group_name_2 + " created"
        assert response_group_2.json["simple_message"] == "new flag group created"
        assert response_group_2.json["valid"] == True
        assert response_group_2.json["flags_in_flag_group"] == None

        response = client.get("flag_group/get_ids")
        assert response.status_code == 200
        assert len(response.json["_ids"]) == 2
        assert response.json["_ids"] == [response_group_1.json["uuid"], response_group_2.json["uuid"]]




# get flag group names
def test_get_flag_group_names():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        response = client.get("flag/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        response = client.get("flag_group/get_ids")
        assert response.status_code == 200
        assert response.json["_ids"] == []

        response = client.get("flag_group/get_names")
        assert response.status_code == 200
        assert response.json["flag_group_names"] == []

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        # create flag group
        flag_group_name_2 = "FlagGroupName2"
        url_2 = "flag_group/create/x/" + flag_group_name_2
        response_group_2 = client.post(url_2)
        assert response_group_2.status_code == 200
        assert response_group_2.json["flag_group_name"] == flag_group_name_2
        assert response_group_2.json["message"] == "unique flag group: " + flag_group_name_2 + " created"
        assert response_group_2.json["simple_message"] == "new flag group created"
        assert response_group_2.json["valid"] == True
        assert response_group_2.json["flags_in_flag_group"] == None

        response = client.get("flag_group/get_ids")
        assert response.status_code == 200
        assert len(response.json["_ids"]) == 2
        assert response.json["_ids"] == [response_group_1.json["uuid"], response_group_2.json["uuid"]]

        response = client.get("flag_group/get_names")
        assert response.status_code == 200
        assert len(response.json["flag_group_names"]) == 2
        assert response.json["flag_group_names"] == [flag_group_name_1, flag_group_name_2]


# get flag ids in flag group, missing id
def test_get_flags_in_flag_group_missing_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        #create 2 flags
        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload_1 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_1["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_1), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_1["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_1["FLAG_LOGIC"]))
        flag_id_1 = response.json["uuid"]

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 < 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))
        flag_id_2 = response.json["uuid"]

        #add flag to flag group, x2
        response = client.put("flag_group/add_flag/"+response_group_1.json["uuid"] + "/xx/" + flag_id_1)
        assert response.status_code == 200
        response = client.put("flag_group/add_flag/"+response_group_1.json["uuid"] + "/xx/" + flag_id_2)
        assert response.status_code == 200

        #attempt to get flags in flag group
        r = client.get("flag_group/get_flags")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group id must be specified"
        assert r.json["simple_message"] == "flag group id must be specified"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None



# get flag ids in flag group, flag group does not exist
def test_flags_in_flag_group_id_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        # create 2 flags
        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload_1 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_1["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_1), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_1["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_1["FLAG_LOGIC"]))
        flag_id_1 = response.json["uuid"]

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 < 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))
        flag_id_2 = response.json["uuid"]

        # add flag to flag group, x2
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_1)
        assert response.status_code == 200
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_2)
        assert response.status_code == 200

        # attempt to get flags in flag group
        flag_group_id = "1a"*12
        if flag_group_id == response_group_1.json["uuid"]:
            flag_group_id = "1b"*12
        r = client.get("flag_group/get_flags/"+flag_group_id)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group: " + flag_group_id + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# get flag ids in flag group, invalid flag group id
def test_get_flags_in_flag_group_invalid_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        # create 2 flags
        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload_1 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_1["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_1), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_1["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_1["FLAG_LOGIC"]))
        flag_id_1 = response.json["uuid"]

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 < 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))
        flag_id_2 = response.json["uuid"]

        # add flag to flag group, x2
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_1)
        assert response.status_code == 200
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_2)
        assert response.status_code == 200

        # attempt to get flags in flag group
        flag_group_id = "1a"
        r = client.get("flag_group/get_flags/" + flag_group_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "error converting flag group id: " + flag_group_id + " to proper Object Id type"
        assert r.json["simple_message"] == "error pulling flags for flag group"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# get flag ids in flag group, valid
def test_get_flags_in_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        # create 2 flags
        flag_name = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload_1 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_1["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_1), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_1["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_1["FLAG_LOGIC"]))
        flag_id_1 = response.json["uuid"]

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 < 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response.status_code == 200
        assert response.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response.json["message"] == "flag id: " + response.json["uuid"] + " has been created"
        assert response.json["simple_message"] == "new flag created"
        assert response.json["valid"] == True
        assert response.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))
        flag_id_2 = response.json["uuid"]

        # add flag to flag group, x2
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_1)
        assert response.status_code == 200
        response = client.put("flag_group/add_flag/" + response_group_1.json["uuid"] + "/xx/" + flag_id_2)
        assert response.status_code == 200

        # attempt to get flags in flag group
        r = client.get("flag_group/get_flags/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name_1
        assert r.json["message"] == "return flags for flag group: " + flag_group_id
        assert r.json["simple_message"] == "return flags for flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True
        assert set(r.json["flags_in_flag_group"]) == set([flag_id_1, flag_id_2])


# get specific flag group, missing id
def test_get_specific_flag_group_missing_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        r = client.get("flag_group/get_specific")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group id must be specified"
        assert r.json["simple_message"] == "flag group id must be specified"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None



# get specific flag group, id does not exist
def test_get_specific_flag_group_id_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id_valid = response_group_1.json["uuid"]

        #attempt to get flag group
        flag_group_id = "1a"*12
        if flag_group_id == flag_group_id_valid:
            flag_group_id = "1b"*12
        r = client.get("flag_group/get_specific/"+flag_group_id)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group: " + flag_group_id + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None




# get specific flag group, invalid id
def test_get_specific_flag_group_invalid_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None

        #attempt to get flag group
        flag_group_id = "1a"
        r = client.get("flag_group/get_specific/"+flag_group_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "error converting flag group: " + flag_group_id + " to proper Object Id type"
        assert r.json["simple_message"] == "invalid flag group id type"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# get specific flag group, valid
def test_get_specific_flag_group_valid():
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
        flag_id_1 = response.json["uuid"]

        # confirm created flag id is in get_ids call
        response_unpack = client.get("flag/get_ids")
        assert response_unpack.status_code == 200
        assert response.json["uuid"] in response_unpack.json["_ids"]

        flag_name = "FlagName2B"
        flag_logic = """\
if FF2 > 5:
    return True
else:
    return False"""
        payload_2 = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload_2["FLAG_NAME"]
        response_2 = client.post(url, data=json.dumps(payload_2), content_type='application/json')
        assert response_2.status_code == 200
        assert response_2.json["flag_name"] == payload_2["FLAG_NAME"]
        assert response_2.json["message"] == "flag id: " + response_2.json["uuid"] + " has been created"
        assert response_2.json["simple_message"] == "new flag created"
        assert response_2.json["valid"] == True
        assert response_2.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload_2["FLAG_LOGIC"]))
        flag_id_2 = response_2.json["uuid"]

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #add flag to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/xx/"+flag_id_1)
        assert r.status_code == 200
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_2)
        assert r.status_code == 200

        #attempt to get flag group
        r = client.get('flag_group/get_specific/'+flag_group_id)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name_1
        assert r.json["message"] == "found flag group id: " + flag_group_id
        assert r.json["simple_message"] == "found flag group id"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True
        assert set(r.json["flags_in_flag_group"]) == set([flag_id_1, flag_id_2])


# create flag group, missing name
def test_create_flag_group_missing_name_1():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x"
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 400
        assert response_group_1.json["flag_group_name"] == None
        assert response_group_1.json["message"] == "unique flag group name must be specified"
        assert response_group_1.json["simple_message"] == "missing flag group name"
        assert response_group_1.json["valid"] == False
        assert response_group_1.json["flags_in_flag_group"] == None

def test_create_flag_group_missing_name_2():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create"
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 400
        assert response_group_1.json["flag_group_name"] == None
        assert response_group_1.json["message"] == "unique flag group name must be specified"
        assert response_group_1.json["simple_message"] == "missing flag group name"
        assert response_group_1.json["valid"] == False
        assert response_group_1.json["flags_in_flag_group"] == None

# create flag group, non unique name
def test_create_flag_group_non_unique_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #attempt to create flag group with same name
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_2 = client.post(url_1)
        assert response_group_2.status_code == 405
        assert response_group_2.json["flag_group_name"] == flag_group_name_1
        assert response_group_2.json["message"] =="new flag group name: " + flag_group_name_1 + " must be unique"
        assert response_group_2.json["simple_message"] == "new flag group name must be unique"
        assert response_group_2.json["valid"] == False
        assert response_group_2.json["flags_in_flag_group"] == None



# create flag group, valid
def test_create_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        r = client.get("flag_group/get")
        assert r.status_code == 200
        assert r.json["flag_groups"][0]["_id"] == flag_group_id
        assert r.json["flag_groups"][0]["FLAG_GROUP_NAME"] == flag_group_name_1
        assert r.json["flag_groups"][0]["FLAGS_IN_GROUP"] == {}
        assert r.json["flag_groups"][0]["FLAG_GROUP_STATUS"] == "PRODUCTION_READY"


# delete flag group, no id
def test_delete_flag_group_no_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #attempt to delete flag group
        r = client.delete("flag_group/delete")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group id must be specified"
        assert r.json["simple_message"] == "flag group id must be specified"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None

        #confirm flag still exists
        r = client.get("flag_group/get_ids")
        assert r.json["_ids"] == [flag_group_id]



# delete flag group, id does not exist
def test_delete_flag_group_id_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #attempt to delete flag group
        flag_group_id_2 = "1a"*12
        if flag_group_id_2 == flag_group_id:
            flag_group_id_2 = "1b"*12
        r = client.delete("flag_group/delete/"+flag_group_id_2)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "could not identify flag group: " + flag_group_id_2 + " in database"
        assert r.json["simple_message"] == "could not identify flag group in database"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None

        #confirm flag still exists
        r = client.get("flag_group/get_ids")
        assert r.json["_ids"] == [flag_group_id]


# delete flag group, invalid id
def test_delete_flag_group_invalid_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        # attempt to delete flag group
        flag_group_id_2 = "1a"
        r = client.delete("flag_group/delete/" + flag_group_id_2)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "error deleting flag group: " + flag_group_id_2 + ", error converting to proper Object Id type"
        assert r.json["simple_message"] == "error deleting flag group, invalid id type"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None

        # confirm flag still exists
        r = client.get("flag_group/get_ids")
        assert r.json["_ids"] == [flag_group_id]


# delete flag group, valid
def test_delete_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        # attempt to delete flag group
        r = client.delete("flag_group/delete/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name_1
        assert r.json["message"] == "flag group: " + flag_group_id + " deleted from database"
        assert r.json["simple_message"] == "flag group has been deleted"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True
        assert r.json["flags_in_flag_group"] == None

        # confirm flag still exists
        r = client.get("flag_group/get_ids")
        assert len(r.json["_ids"]) == 0


# add flag to flag group, missing flag group id
def test_add_flag_to_flag_group_missing_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        r = client.get("flag_group/add_flag")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag group must be specified"
        assert r.json["simple_message"] == "flag group must be specified"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None



# add flag to flag group, flag group id does not exist
def test_add_flag_to_flag_group_flag_group_id_no_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_id = "1a"*12
        flag_id = "2b"*12
        r = client.put("flag_group/add_flag/"+flag_group_id+"/xx/"+flag_id)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "flag_group: " + flag_group_id + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# add flag to flag group, invalid flag group id
def test_add_flag_to_flag_group_invalid_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_id = "1a"
        flag_id = "2b"*12
        r = client.put("flag_group/add_flag/"+flag_group_id+"/xx/"+flag_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "error adding flag to flag group: " + flag_group_id + ", error converting to Object Id type"
        assert r.json["simple_message"] == "error converting flag group id to Object Id type"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None




# add flag to flag group, missing flag id
def test_add_flag_to_flag_group_missing_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        #create flag group
        flag_group_name = "FlagGroupName1a"
        r = client.post("flag_group/create/x/"+flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        flag_id = "2b"*12
        r = client.put("flag_group/add_flag/"+flag_group_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["message"] == "no new flags were specified"
        assert r.json["simple_message"] == "missing flags to add to flag group"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None



# add flag to flag group, flag id does not exist
def test_add_flag_to_flag_group_flag_id_no_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        #create flag group
        flag_group_name = "FlagGroupName1a"
        r = client.post("flag_group/create/x/"+flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        flag_id = "2b"*12
        r = client.put("flag_group/add_flag/"+flag_group_id+"/xx/"+flag_id)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["message"] == "Flag(s) " + ", ".join(map(str, [flag_id])) + " do not exist"
        assert r.json["simple_message"] == "flag does not exist"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# add flag to flag group, invalid flag id
def test_add_flag_to_flag_group_invalid_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        #create flag group
        flag_group_name = "FlagGroupName1a"
        r = client.post("flag_group/create/x/"+flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        flag_id = "2b"
        r = client.put("flag_group/add_flag/"+flag_group_id+"/xx/"+flag_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["message"] == "error adding flag to flag group: " + flag_group_id + ", error converting flag id to ObjectId type"
        assert r.json["simple_message"] == "error adding flag to flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None


# add flag to flag group, flag id already exists in flag group
def test_add_flag_to_flag_group_flag_id_already_exists_in_flag_group():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        #create flag
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
        flag_id = response.json["uuid"]


        #create flag group
        flag_group_name = "FlagGroupName1a"
        r = client.post("flag_group/create/x/"+flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        #add flag to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id)
        assert r.status_code == 200
        #confrim flag in flag group
        r = client.get("flag_group/get_specific/"+flag_group_id)
        assert r.status_code == 200
        assert r.json["flags_in_flag_group"] == [flag_id]

        #attempt to add same flag to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["message"] == "Flag(s) " + ", ".join(map(str, [flag_id])) + " already exist in flag group"
        assert r.json["simple_message"] == 'flag already in flag group'
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False
        assert r.json["flags_in_flag_group"] == None




# add flag to flag group, flag name already exists in flag group
def test_add_flag_to_flag_group_flag_name_already_in_flag():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag 2 separate flags with same name
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
        flag_id_1 = response.json["uuid"]

        flag_name = "FlagName1A"
        flag_logic = """\
if FF2 < 5:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_2 = response.json["uuid"]

        # create flag group
        flag_group_name = "FlagGroupName1a"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # add first flag to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_1)
        assert r.status_code == 200
        # confirm flag in flag group
        r = client.get("flag_group/get_specific/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flags_in_flag_group"] == [flag_id_1]

        # attempt to add second flag to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_2)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["message"] =="flag: " + flag_id_2 + " with name: " + paylaod["FLAG_NAME"] + " already exists in flag group: " + flag_group_id
        assert r.json["simple_message"] == 'flag already exists in flag group'
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False

        #confrim first flag is still in flag group
        # confirm flag in flag group
        r = client.get("flag_group/get_specific/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flags_in_flag_group"] == [flag_id_1]


#update flag logic, create cyclical flag
def test_update_flag_logic_create_cyclical_flag_3():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag, no flag references
        flag_name_1 = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_1 = response.json["uuid"]

        # create flags that reference original flag
        flag_name_2 = "FlagName2B"
        flag_logic = f"""\
if f["{flag_name_1}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_2, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_2 = response.json["uuid"]

        flag_name_3 = "FlagName3C"
        flag_logic = f"""\
if f["{flag_name_2}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_3, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_3 = response.json["uuid"]

        flag_name_4 = "FlagName4D"
        flag_logic = f"""\
if f["{flag_name_3}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_4, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_4 = response.json["uuid"]

        #create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        #add flag 1 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_1)
        assert r.status_code == 200

        #confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][0]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][0]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][0]["FLAG_NAME"] == flag_name_1

        # add flag 2 to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_2)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][1]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][1]["FLAG_ID"] == flag_id_2
        assert r.json["flag_deps"][1]["FLAG_NAME"] == flag_name_2
        assert r.json["flag_deps"][1]["DEPENDENT_FLAGS"] == [flag_name_1]

        #add flag 3 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_3)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][2]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][2]["FLAG_ID"] == flag_id_3
        assert r.json["flag_deps"][2]["FLAG_NAME"] == flag_name_3
        assert r.json["flag_deps"][2]["DEPENDENT_FLAGS"] == [flag_name_2]

        #add flag 4 to flag group
        r = client.put("flag_group/add_flag/"+flag_group_id+"/x/"+flag_id_4)
        assert r.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][3]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][3]["FLAG_ID"] == flag_id_4
        assert r.json["flag_deps"][3]["FLAG_NAME"] == flag_name_4
        assert r.json["flag_deps"][3]["DEPENDENT_FLAGS"] == [flag_name_3]


        #update flag 1 to reference flag 4, confirm cyclical flag behavior
        flag_name_1 = "FlagName1A"
        flag_logic = f"""\
if f["{flag_name_4}"] == True:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/update_logic/"+flag_id_1
        r = client.put(url, data=json.dumps(payload), content_type='application/json')

        assert r.status_code == 200
        assert r.json["flag_name"] == flag_name_1
        assert r.json["message"] == "error in flag logic"
        assert r.json["simple_message"] == "new logic updated but has errors"
        assert r.json["uuid"] == flag_id_1
        assert r.json["valid"] == False
        assert r.json["flag_logic"] == _convert_FLI_to_TFLI(determine_variables(payload["FLAG_LOGIC"]))

        #pull flag dep entries
        response = client.get("flag_dependency/get")
        assert response.status_code == 200

        # confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][3]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][3]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][3]["FLAG_NAME"] == flag_name_1
        assert r.json["flag_deps"][3]["DEPENDENT_FLAGS"] == [flag_name_4]

        #confirm that both flag 1 and flag group are no longer production ready due to cyclical flags
        r = client.get("flag/get")
        assert r.json["flags"][0]["FLAG_ERRORS"] == "ERROR"
        assert r.json["flags"][0]["FLAG_STATUS"] == "DRAFT"
        assert r.json["flags"][0]["_id"] == flag_id_1

        r = client.get("flag_group/get")
        assert set(r.json["flag_groups"][0]["FLAGS_IN_GROUP"]) == set([flag_id_1, flag_id_2, flag_id_3, flag_id_4])
        assert r.json["flag_groups"][0]["FLAG_GROUP_ERRORS"] == "CYCLICAL ERROR"
        assert r.json["flag_groups"][0]["FLAG_GROUP_STATUS"] == "DRAFT"
        assert r.json["flag_groups"][0]["_id"] == flag_group_id
        print("hello")


#add flag to flag group, flag has error
def test_add_flag_to_flag_group_flag_has_error():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag, no flag references
        flag_name_1 = "FlagName1A"
        flag_name_4 = "FlagName4D"
        flag_logic = f"""\
        if f["{flag_name_4}"] > 10:
            return True
        else:
            return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_1 = response.json["uuid"]

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        assert response_group_1.json["flag_group_name"] == flag_group_name_1
        assert response_group_1.json["message"] == "unique flag group: " + flag_group_name_1 + " created"
        assert response_group_1.json["simple_message"] == "new flag group created"
        assert response_group_1.json["valid"] == True
        assert response_group_1.json["flags_in_flag_group"] == None
        flag_group_id = response_group_1.json["uuid"]

        # add flag 1 to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_1)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name_1
        assert r.json["flags_in_flag_group"] == [flag_id_1]
        assert r.json["message"] == "flag: " + flag_id_1 + " is in DRAFT status but was added to flag group: " + flag_group_id + "\n"
        assert r.json["simple_message"] == "flag added to flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True

        #confirm no dependency create because flag and flag group are in DRAFT status
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"] == []

# add flag to flag group, valid
def test_add_flag_to_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200
        flag_dep_delete_url = "flag_dependency/delete_all"
        response = client.delete(flag_dep_delete_url)
        assert response.status_code == 200

        # create flag, no flag references
        flag_name_1 = "FlagName1A"
        flag_logic = """\
if FF1 > 10:
    return True
else:
    return False"""
        payload = {"FLAG_NAME": flag_name_1, "FLAG_LOGIC": flag_logic}
        url = "flag/create/x/" + payload["FLAG_NAME"]
        response = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 200
        flag_id_1 = response.json["uuid"]

        # create flag group
        flag_group_name_1 = "FlagGroupName1"
        url_1 = "flag_group/create/x/" + flag_group_name_1
        response_group_1 = client.post(url_1)
        assert response_group_1.status_code == 200
        flag_group_id = response_group_1.json["uuid"]

        #add flag to flag group
        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id_1)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name_1
        assert r.json["flags_in_flag_group"] == [flag_id_1]
        assert r.json["message"] == "flag group " + flag_group_id + " has been updated with flag(s) " + flag_id_1 + "\n"
        assert r.json["simple_message"] == "flags added to flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True

        #confirm flag dep entry created
        r = client.get("flag_dependency/get")
        assert r.status_code == 200
        assert r.json["flag_deps"][0]["DEPENDENT_FLAGS"] == []
        assert r.json["flag_deps"][0]["FLAG_GROUP_ID"] == flag_group_id
        assert r.json["flag_deps"][0]["FLAG_ID"] == flag_id_1
        assert r.json["flag_deps"][0]["FLAG_NAME"] == flag_name_1


# remove flag from flag group, missing flag group id
def test_remove_flag_from_flag_group_missing_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        r = client.put("flag_group/remove_flag")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "flag group not specified"
        assert r.json["simple_message"] == "flag group not specified"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False

# remove flag from flag group, flag group id does not exist
def test_remove_flag_from_flag_group_flag_group_does_not_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        #make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/"+flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        #confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        flag_group_id_2 = "1a"*12
        if flag_group_id == flag_group_id_2:
            flag_group_id_2 = "2b"*12


        r = client.put("flag_group/remove_flag/"+flag_group_id_2)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "flag group: " + flag_group_id_2 + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["uuid"] == flag_group_id_2
        assert r.json["valid"] == False


# remove flag from flag group, flag group id is not valid
def test_remove_flag_from_flag_group_invalid_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_id_2 = "1a"

        r = client.put("flag_group/remove_flag/" + flag_group_id_2)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "error removing flag from flag group, error converting flag group id: " + flag_group_id_2 + " to ObjectId type"
        assert r.json["simple_message"] == "error removing flag from flag group"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False


# remove flag from flag group, missing flag to remove
def test_remove_flag_from_flag_group_missing_flag():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        r = client.put("flag_group/remove_flag/" + flag_group_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "no flags to remove were specified"
        assert r.json["simple_message"] == "missing flags to remove from flag group"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False


# remove flag from flag group, flag to remove does not exist
def test_remove_flag_from_flag_group_flag_no_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        flag_id = "2b"*12

        r = client.put("flag_group/remove_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "the following flag does not exist: " + flag_id
        assert r.json["simple_message"] == "error removing flags from flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False

# remove flag from flag group, flag does not exist in flag group
def test_remove_flag_from_flag_group_flag_not_in_flag_group():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        # create flag
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
        flag_id = response.json["uuid"]

        r = client.put("flag_group/remove_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "the following flag is not part of flag group " + flag_group_id + ": " + flag_id
        assert r.json["simple_message"] == "flag specified for removal is not part of flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False

# remove flag from flag group, invalid flag id
def test_remove_flag_from_flag_group_invalid_flag_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        # create flag
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
        flag_id = response.json["uuid"]
        flag_id_2 = "2b"

        r = client.put("flag_group/remove_flag/" + flag_group_id + "/x/" + flag_id_2)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "error removing flag: " + flag_id_2 + " from flag group " + flag_group_id + ", error converting flag id to proper ObjectId type"
        assert r.json["simple_message"] == "invalid flag id type"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False


# remove flag from flag group, valid
def test_remove_flag_from_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        # make flag group
        flag_group_name = "FlagGroupName1"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # confirm flag group_created
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

        # create flag
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
        flag_id = response.json["uuid"]

        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 200

        r = client.get("flag_group/get_specific/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flags_in_flag_group"] == [flag_id]

        r = client.put("flag_group/remove_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 200
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["flags_in_flag_group"] == []
        assert r.json["message"] == "Flag(s) " + flag_id + " removed from " + flag_group_id
        assert r.json["simple_message"] == "flags removed from flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == True

        r = client.get("flag_group/get_specific/" + flag_group_id)
        assert r.status_code == 200
        assert r.json["flags_in_flag_group"] == []


# duplicate flag group, missing flag group id
def test_duplicate_flag_group_missing_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        r = client.post("flag_group/duplicate")
        assert r.status_code == 400
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "user must specify flag group id"
        assert r.json["simple_message"] == "user must specify flag group id"
        assert r.json["uuid"] == "None"
        assert r.json["valid"] == False


# duplicate flag group, flag group does not exist
def test_duplicate_flag_group_flag_group_no_exist():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]


        flag_group_id_2 = "1a"*12
        if flag_group_id == flag_group_id_2:
            flag_group_id_2 = "2b"*12

        r = client.post("flag_group/duplicate/" + flag_group_id_2)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "flag group: " + flag_group_id_2 + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["uuid"] == flag_group_id_2
        assert r.json["valid"] == False

        #confirm only one flag group exists
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

# duplicate flag group, invalid flag group id
def test_duplicate_flag_group_invalid_flag_group_id():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        flag_group_id_2 = "1a" * 12
        if flag_group_id == flag_group_id_2:
            flag_group_id_2 = "2b" * 12

        r = client.post("flag_group/duplicate/" + flag_group_id_2)
        assert r.status_code == 404
        assert r.json["flag_group_name"] == None
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "flag group: " + flag_group_id_2 + " does not exist"
        assert r.json["simple_message"] == "flag group does not exist"
        assert r.json["uuid"] == flag_group_id_2
        assert r.json["valid"] == False

        # confirm only one flag group exists
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]


# duplicate flag group, missing new name
def test_duplicate_flag_group_missing_new_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        r = client.post("flag_group/duplicate/" + flag_group_id)
        assert r.status_code == 400
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "error duplicating flag group: " + flag_group_id + ", missing new flag group name"
        assert r.json["simple_message"] == "error duplicating flag group"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False

        # confirm only one flag group exists
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]

# duplicate flag group, new name same as old name
def test_duplicate_flag_group_same_name():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        r = client.post("flag_group/duplicate/" + flag_group_id +"/" + flag_group_name)
        assert r.status_code == 405
        assert r.json["flag_group_name"] == flag_group_name
        assert r.json["flags_in_flag_group"] == None
        assert r.json["message"] == "can not duplicate flag group " + flag_group_id + " must be given a unique name"
        assert r.json["simple_message"] == "new name for flag group must be unique"
        assert r.json["uuid"] == flag_group_id
        assert r.json["valid"] == False

        # confirm only one flag group exists
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert r.json["_ids"] == [flag_group_id]


# duplicate flag group, valid
def test_duplicate_flag_group_valid():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        new_flag_group_name = "FlagGroupName1ANewName"

        r = client.post("flag_group/duplicate/" + flag_group_id +"/" + new_flag_group_name)
        assert r.status_code == 200
        new_flag_group_id = r.json["uuid"]
        assert r.json["flag_group_name"] == new_flag_group_name
        assert r.json["flags_in_flag_group"] == []
        assert r.json["message"] == "new flag group " + new_flag_group_id + " created off of " + flag_group_id
        assert r.json["simple_message"] == "new flag group created"
        assert r.json["valid"] == True

        # confirm two flag group creates
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert set(r.json["_ids"]) == set([flag_group_id, new_flag_group_id])

# duplicate flag group, valid
def test_duplicate_flag_group_valid_2():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with MongoDbContainer(MONGO_DOCKER_IMAGE) as container, \
            _create_flagging_dao(container) as flagging_dao:
        make_routes(app, flagging_dao)
        client = app.test_client()
        flag_deletion_url = "flag/delete_all"
        response = client.delete(flag_deletion_url)
        assert response.status_code == 200
        flag_group_delete_url = "flag_group/delete_all"
        response = client.delete(flag_group_delete_url)
        assert response.status_code == 200

        flag_group_name = "FlagGroupName1A"
        r = client.post("flag_group/create/x/" + flag_group_name)
        assert r.status_code == 200
        flag_group_id = r.json["uuid"]

        # create flag
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
        flag_id = response.json["uuid"]

        r = client.put("flag_group/add_flag/" + flag_group_id + "/x/" + flag_id)
        assert r.status_code == 200

        new_flag_group_name = "FlagGroupName1ANewName"

        r = client.post("flag_group/duplicate/" + flag_group_id +"/" + new_flag_group_name)
        assert r.status_code == 200
        new_flag_group_id = r.json["uuid"]
        assert r.json["flag_group_name"] == new_flag_group_name
        assert r.json["flags_in_flag_group"] == [flag_id]
        assert r.json["message"] == "new flag group " + new_flag_group_id + " created off of " + flag_group_id
        assert r.json["simple_message"] == "new flag group created"
        assert r.json["valid"] == True

        # confirm two flag group creates
        r = client.get("flag_group/get_ids")
        assert r.status_code == 200
        assert set(r.json["_ids"]) == set([flag_group_id, new_flag_group_id])


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













