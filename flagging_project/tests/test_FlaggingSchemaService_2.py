from unittest import mock
from mock import patch
from unittest.mock import Mock
import mongomock
from flag_data.FlaggingMongo import FlaggingMongo
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from front_end.FlaggingSchemaService import create_flag, create_flag, \
    update_flag_name, update_flag_logic, \
    delete_flag, create_flag_group, delete_flag_group, add_flag_to_flag_group, \
    remove_flag_from_flag_group, duplicate_flag, duplicate_flag_group
from front_end.FlaggingValidateLogic import validate_logic
from flagging.FlaggingValidation import FlaggingValidationResults





# #test interface, simple mock pull
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo", return_value=FlaggingMongo("mock_url"), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo.get_flags", return_value="FlagID", autospec=True)
# def test_pull_flag_interface(mfm, mgf):
#     flag_mongo = FlaggingMongo(connection_url="mock_url")
#     flags = flag_mongo.get_flags()
#     assert "FlagID" in flags
#
# #utilize mongomock as Mongo DB client
# def test_mongomock():
#     flagging_mongo = FlaggingMongo(connection_url="mongodb://test:test@localhost:27017")
#     flagging_mongo.client = mongomock.MongoClient()
#     add_id = flagging_mongo.add_flag({"_id": "FlagID1"})
#     flags = flagging_mongo.get_flags()
#     assert len(flags) == 1
#     assert flags[0]['_id'] == "FlagID1"
#
#
# #test create flag, valid flag
# #mock add
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# def test_create_flag(mvrb):
#     flag_name = "Flag1"
#     flag_logic_information = FlagLogicInformation(
#     used_variables={VariableInformation("FF1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
#                                                  CodeLocation(9, 5), CodeLocation(17, 15)},
#                     VariableInformation("FF2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
#                     VariableInformation("FF3"): {CodeLocation(7, 9)},
#                     VariableInformation("FF4"): {CodeLocation(2, 3), CodeLocation(8, 15)}},
#     assigned_variables={VariableInformation("a"): {CodeLocation(12, 4), CodeLocation(16, 8)},
#                         VariableInformation("b"): {CodeLocation(13, 4)},
#                         VariableInformation("c"): {CodeLocation(14, 4)}},
#     referenced_functions=dict(),
#     defined_functions=dict(),
#     defined_classes=dict(),
#     referenced_modules=dict(),
#     referenced_flags={"MY_FLAG": {CodeLocation(9, 9)}},
#     return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
#                    CodeLocation(10, 4), CodeLocation(17, 8)},
#     used_lambdas=dict(),
#     errors=[],
#     flag_logic="""does not matter""",
#     validation_results=TypeValidationResults())
#     flagging_mongo = FlaggingMongo(connection_url="mongodb://test:test@localhost:27017")
#     flagging_mongo.client = mongomock.MongoClient()
#     result = create_flag(flag_name, flag_logic_information, flagging_mongo)
#     assert result.valid == True
#     assert result.message == "new flag created"
#     assert result.uuid == "Flag1_primary_key_id"
#
#     #add flag to MongoDb
#     add_flag_id = flagging_mongo.add_flag({'_id': result.uuid,
#                                           "flag_logic": flag_logic_information.flag_logic,
#                                           "flag_name": flag_name,
#                                           "referenced_flags": [referenced_flags for referenced_flags in flag_logic_information.referenced_flags.keys()]})
#     flags = flagging_mongo.get_flags()
#     assert len(flags) == 1
#     assert flags[0]["_id"] == add_flag_id
#     assert flags[0]["flag_logic"] == flag_logic_information.flag_logic
#     assert flags[0]["flag_name"] == "Flag1"
#     assert flags[0]["referenced_flags"] == ["MY_FLAG"]


#mock add_flag() and mock valdate_logic
#add_flag should return 1 as and ide
#validate_logic should return a FlaggingValidationResults() object

#creae a mock instance of flagging_data
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_simple(flagging_mongo):
    print("hello")




@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_mock_simple_class(flagging_mongo):
    flagging_mongo.return_value.add_flag.return_value = 1
    mock_flagging_mongo = flagging_mongo()
    result = mock_flagging_mongo.add_flag()
    print(result)
    assert result == 1



@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_mock_simple_add(flagging_mongo):
    flagging_mongo.return_value.add_flag.return_value = 1
    mock_flagging_mongo = flagging_mongo()
    add_id = mock_flagging_mongo.add_flag({"flag_name": "Flag1",
                                      "flag_logic_information": "flag_logic_information"})
    print(add_id)
    assert add_id == 1

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag(flagging_mongo, mvrb, mvl):
    print("hello")
    flagging_mongo.return_value.add_flag.return_value = 1
    mock_flagging_mongo = flagging_mongo()
    flag_name = "Flag1"
    flag_logic_information = FlagLogicInformation(
    used_variables={VariableInformation("FF1"): {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15),
                                                 CodeLocation(9, 5), CodeLocation(17, 15)},
                    VariableInformation("FF2"): {CodeLocation(4, 15), CodeLocation(5, 9)},
                    VariableInformation("FF3"): {CodeLocation(7, 9)},
                    VariableInformation("FF4"): {CodeLocation(2, 3), CodeLocation(8, 15)}},
    assigned_variables={VariableInformation("a"): {CodeLocation(12, 4), CodeLocation(16, 8)},
                        VariableInformation("b"): {CodeLocation(13, 4)},
                        VariableInformation("c"): {CodeLocation(14, 4)}},
    referenced_functions=dict(),
    defined_functions=dict(),
    defined_classes=dict(),
    referenced_modules=dict(),
    referenced_flags=dict(),
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag created"
    assert result.uuid == "Flag1_primary_key_id"