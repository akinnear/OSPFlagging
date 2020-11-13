import pytest
from flask import Flask
from handlers.routes import make_routes
from flag_data.FlaggingMongo import FlaggingMongo
from testcontainers.mongodb import MongoDbContainer
from integration_tests import MONGO_DOCKER_IMAGE
from app import _create_flagging_mongo




def test_flag_home():
    app = Flask(__name__)
    flagging_mongo_test = _create_flagging_mongo()
    make_routes(app, flagging_mongo_test)
    client = app.test_client()
    url = '/flag'

    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8")
    assert str_data == 'flag home page to go here'
    assert response.status_code == 200

def test_get_flags_no_flags():
    app = Flask(__name__)
    flagging_mongo_test = _create_flagging_mongo()
    make_routes(app, flagging_mongo_test)
    client = app.test_client()
    url = '/flag/get_flags'

    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8")
    assert str_data == '{"flags":[]}\n'
    assert response.status_code == 200

def test_get_flag_ids_no_flag_ids():
    app = Flask(__name__)
    flagging_mongo_test = _create_flagging_mongo()
    make_routes(app, flagging_mongo_test)
    client = app.test_client()
    url = '/flag/get_flag_ids'

    response = client.get(url)
    data = response.get_data()
    str_data = data.decode("utf-8")
    assert str_data == '{"_ids":[]}\n'
    assert response.status_code == 200



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