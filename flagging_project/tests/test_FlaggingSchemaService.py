from unittest import mock
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from front_end.FlaggingSchemaService import create_flag, \
    update_flag_name, update_flag_logic, \
    delete_flag, create_flag_group, delete_flag_group, add_flag_to_flag_group, \
    remove_flag_from_flag_group, duplicate_flag, duplicate_flag_group, get_all_flags, \
    create_flag_dependency, delete_flag_dependency, add_dependencies_to_flag, \
    remove_dependencies_from_flag
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlagErrorInformation import FlagErrorInformation
from flag_names.FlagService import pull_flag_names, \
    pull_flag_names_in_flag_group, pull_flag_ids
from flag_names.FlagGroupService import pull_flag_group_names, pull_flag_group_ids
# from front_end.FlaggingDependencies import add_flag_dependencies, remove_flag_dependencies
from flag_data.FlaggingMongo import FlaggingMongo
from random_object_id import generate as generate_object_id
from bson.objectid import ObjectId
from front_end.ReferencedFlag import ReferencedFlag








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
    assert result == 1



@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_mock_simple_add(flagging_mongo):
    flagging_mongo.return_value.add_flag.return_value = 1
    mock_flagging_mongo = flagging_mongo()
    add_id = mock_flagging_mongo.add_flag({"flag_name": "Flag1",
                                      "flag_logic_information": "flag_logic_information"})
    assert add_id == 1

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag(flagging_mongo, mvrb, mvl):
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
    result, response_code = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag created"
    assert result.uuid == 1
    assert response_code == 200


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_missing_name(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.add_flag.return_value = 1
    mock_flagging_mongo = flagging_mongo()
    flag_name = None
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
    result, response_code = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag name not specified"
    assert response_code >= 400


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(errors={"Flag1": FlagErrorInformation(flag="Flag1",
                                                           err_info="cyclical_flag",
                                                           cl={CodeLocation(1, 10)})}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_error(flagging_mongo, mvrb, mvl):
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
    result, response_code = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert response_code == 200


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(mypy_errors={"mypyerror": "does not matter"}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_myerror(flagging_mongo, mvrb, mvl):
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
    result, response_code = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert response_code == 200


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = ObjectId(generate_object_id())
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=[og_flag_id, ObjectId(generate_object_id())])
    result, response_code = update_flag_name(original_flag_id=str(og_flag_id), new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "original flag " + str(og_flag_id) + " has been renamed " + nw_flag_name
    assert result.uuid == 2
    assert response_code == 200

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_missing_og_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = None
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    result, response_code = update_flag_name(original_flag_id=og_flag_id, new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify id of original flag"
    assert response_code >= 400

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_missing_new_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    og_flag_id = "FlagID1"
    nw_flag_name = None
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    result, response_code = update_flag_name(original_flag_id=str(og_flag_id), new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify name of new flag"
    assert response_code >= 400


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_og_flag_not_found(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = ObjectId(generate_object_id())
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    result, response_code = update_flag_name(original_flag_id=str(og_flag_id), new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "original flag id " + str(og_flag_id) + " does not exist"
    assert response_code >= 400

#test update flag logic informatio
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = ObjectId(generate_object_id())
    existing_flags = pull_flag_names(dummy_flag_names=[og_flag_id, ObjectId(generate_object_id())])
    nw_flag_logic_information = FlagLogicInformation(
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
    referenced_flags={"MY_FLAG2B2B": {CodeLocation(9, 9)}},
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result, response_code = update_flag_logic(flag_id=str(og_flag_id), new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "logic for flag " + str(3) + " has been updated"
    assert result.uuid == 3
    assert response_code == 200


#update flag logic, flag id not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_missing_flag_1(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    og_flag_id = None
    nw_flag_logic_information = FlagLogicInformation(
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
        referenced_flags={"MY_FLAG2B2B": {CodeLocation(9, 9)}},
        return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                       CodeLocation(10, 4), CodeLocation(17, 8)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""does not matter""",
        validation_results=TypeValidationResults())
    result, response_code = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information,
                               existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag id"
    assert response_code >= 400

#update flag logic, flag id does not exists
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_missing_flag_2(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    og_flag_id = ObjectId(generate_object_id())
    while og_flag_id in existing_flags:
        og_flag_id = ObjectId(generate_object_id())
    nw_flag_logic_information = FlagLogicInformation(
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
        referenced_flags={"MY_FLAG2B2B": {CodeLocation(9, 9)}},
        return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                       CodeLocation(10, 4), CodeLocation(17, 8)},
        used_lambdas=dict(),
        errors=[],
        flag_logic="""does not matter""",
        validation_results=TypeValidationResults())
    result, response_code = update_flag_logic(flag_id=str(og_flag_id), new_flag_logic_information=nw_flag_logic_information,
                               existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "could not identify existing flag " + str(og_flag_id)
    assert response_code >= 400



#update flag logic, error in result
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(errors={"some_error": {"some_code_location"}}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_errors(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = ObjectId(generate_object_id())
    existing_flags = pull_flag_names(dummy_flag_names=[og_flag_id, ObjectId(generate_object_id())])
    nw_flag_logic_information = FlagLogicInformation(
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
    referenced_flags={"MY_FLAG2B2B": {CodeLocation(9, 9)}},
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result, response_code = update_flag_logic(flag_id=str(og_flag_id), new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == 3
    response_code == 200


#update flag lgoic, mypy_error in result
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(mypy_errors={"some_mypy_error": {"some_code_location"}}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_mypy_errors(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = ObjectId(generate_object_id())
    existing_flags = pull_flag_names(dummy_flag_names=[og_flag_id, ObjectId(generate_object_id())])
    nw_flag_logic_information = FlagLogicInformation(
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
    referenced_flags={"MY_FLAG2B2B": {CodeLocation(9, 9)}},
    return_points={CodeLocation(4, 8), CodeLocation(6, 8), CodeLocation(8, 8),
                   CodeLocation(10, 4), CodeLocation(17, 8)},
    used_lambdas=dict(),
    errors=[],
    flag_logic="""does not matter""",
    validation_results=TypeValidationResults())
    result, response_code = update_flag_logic(flag_id=str(og_flag_id), new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert response_code == 200



#test to delete flag, valid
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    rfrv = ObjectId(generate_object_id())
    flagging_mongo.return_value.remove_flag.return_value = rfrv
    og_flag_id = ObjectId(generate_object_id())
    existing_flags = pull_flag_names(dummy_flag_names=[og_flag_id, ObjectId(generate_object_id())])
    result, response_code = delete_flag(flag_id=str(og_flag_id), existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == str(og_flag_id) + " has been deleted"
    assert result.uuid == rfrv
    assert response_code == 200

#test to delete flag, missign flag id
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag_missing_flag_id(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = None
    result, response_code = delete_flag(flag_id=og_flag_id, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag id"
    assert result.uuid == og_flag_id
    assert response_code >= 400

#test to delete flag, flag does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag_flag_does_not_exist(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    og_flag_id = ObjectId(generate_object_id())
    while og_flag_id in existing_flags:
        og_flag_id = ObjectId(generate_object_id())
    result, response_code = delete_flag(flag_id=str(og_flag_id), existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag id specified does not exist"
    assert response_code >= 400

#test, duplicate flag
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.duplicate_flag.return_value = 4
    flag_id = ObjectId(generate_object_id())
    existing_flag_ids = pull_flag_names(dummy_flag_names=[flag_id, ObjectId(generate_object_id())])
    result, response_code = duplicate_flag(original_flag_id=str(flag_id), existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == str(flag_id) + " has be duplicated"
    assert result.uuid == 4
    assert response_code == 200

#test, duplicate flag, flag name not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_missing_flag_id(flagging_mongo, mvrb, mvl):
    flagging_mongo.duplicate_flag.return_value = 4
    mock_flagging_mongo = flagging_mongo
    flag_id = None
    existing_flag_ids = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B"])
    result, response_code = duplicate_flag(original_flag_id=flag_id, existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag id must be specified"
    assert response_code >= 400

#test, duplicate flag, flag name does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_flag_does_not_exist(flagging_mongo, mvrb, mvl):
    flagging_mongo.duplicate_flag.return_value = 4
    mock_flagging_mongo = flagging_mongo
    existing_flag_ids = pull_flag_names(dummy_flag_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    flag_id = ObjectId(generate_object_id())
    while flag_id in existing_flag_ids:
        flag_id = ObjectId(generate_object_id())
    result, response_code = duplicate_flag(original_flag_id=str(flag_id), existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag " + str(flag_id) + " does not exist"
    assert response_code >= 400


#test, create new flag group
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.add_flag_group.return_value = 5
    mock_flagging_mongo = flagging_mongo()
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    new_flag_group = "FlagGroup3"
    result = create_flag_group(flag_group_name=new_flag_group, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "unique flag group " + new_flag_group + " created"
    assert result.uuid == 5

#test, create new flag group, flag group name not specifed
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group_name_not_specified(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.add_flag_group.return_value = 5
    mock_flagging_mongo = flagging_mongo()
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    new_flag_group = None
    result, response_code = create_flag_group(flag_group_name=new_flag_group, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "unique flag group name must be specified"
    assert response_code >= 400

#test, create new flag group, flag group name is not unique
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group_name_not_unique(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.add_flag_group.return_value = 5
    mock_flagging_mongo = flagging_mongo()
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    new_flag_group = "FlagGroup1"
    result, response_code = create_flag_group(flag_group_name=new_flag_group, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "new flag group name must be unique"
    assert response_code >= 400


#test remove flag group
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    flagging_mongo.return_value.remove_flag_group.return_value = 6
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    flag_group_2_remove = "FlagGroup1"
    result = delete_flag_group(flag_group_name=flag_group_2_remove, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "flag group " + flag_group_2_remove + " deleted from database"
    assert result.uuid == 6

#test remove flag group, name not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group_missing_flag_group_name(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    flagging_mongo.return_value.remove_flag_group.return_value = 6
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    flag_group_2_remove = None
    result, response_code = delete_flag_group(flag_group_id=flag_group_2_remove, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group name must be specified"
    assert response_code >= 400

#test remove flag group, flag group name does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group_flag_group_name_does_not_exist(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    flagging_mongo.return_value.remove_flag_group.return_value = 6
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    flag_group_2_remove = ObjectId(generate_object_id())
    while flag_group_2_remove in existing_flag_group_names:
        flag_group_2_remove = ObjectId(generate_object_id())
    result, response_code = delete_flag_group(flag_group_id=str(flag_group_2_remove), existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "could not identify flag group " + str(flag_group_2_remove) + " in database"
    assert response_code >= 400


#test, duplicate flag_group
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.get_flag_group_name.return_value = "FlagName1A"
    flagging_mongo.return_value.duplicate_flag_group.return_value = ObjectId(generate_object_id())
    mock_return_value = flagging_mongo.return_value.duplicate_flag_group.return_value
    flagging_mongo.return_value.update_flag_group.return_value = mock_return_value
    mock_flagging_mongo = flagging_mongo()
    flag_group_id = ObjectId(generate_object_id())
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=[flag_group_id, ObjectId(generate_object_id())])
    result, response_code = duplicate_flag_group(original_flag_group_id=str(flag_group_id), existing_flag_groups=existing_flag_groups,
                                                 new_flag_group_name="FlagGroup3C", flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag group " + str(mock_return_value) + " created off of " + str(flag_group_id)
    assert result.uuid == mock_return_value
    assert response_code == 200

#test, duplicate flag_group, flag_group_id not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group_missing_flag_group(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.duplicate_flag_group.return_value = "Flag_Group_7G"
    mock_flagging_mongo = flagging_mongo()
    flag_group_id = None
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B"])
    result, response_code = duplicate_flag_group(original_flag_group_id=flag_group_id, existing_flag_groups=existing_flag_groups, new_flag_group_name="NEW_NAME", flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag group id"
    assert response_code >= 400

#test, duplicate flag_group, flag_group_id does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.get_flag_group_name.return_value = "FlagName1A"
    flagging_mongo.return_value.duplicate_flag_group.return_value = ObjectId(generate_object_id())
    mock_return_value = flagging_mongo.return_value.duplicate_flag_group.return_value
    flagging_mongo.return_value.update_flag_group.return_value = mock_return_value
    mock_flagging_mongo = flagging_mongo()
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    flag_group_id = ObjectId(generate_object_id())
    while flag_group_id in existing_flag_groups:
        flag_group_id = ObjectId(generate_object_id())
    result, response_code = duplicate_flag_group(original_flag_group_id=str(flag_group_id), existing_flag_groups=existing_flag_groups, new_flag_group_name="new_name", flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group " + str(flag_group_id) + " does not exist"

# #test, add new dependency to flag
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG6F"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.return_value.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12J": set()}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == True
#     assert result.message == "the following flag has been updated with new dependencies: " + flag_id
#     assert result.uuid == "FLAG13M"

# #test, add new dependency to flag, missing flag_name/id (flag being modified)
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_missing_flag(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG6F"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.return_value.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = None
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12J": set()}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag name not specified"

# #test, add new depdendnecy to flag, flag_name/id does not exist (flag being modified)
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_flag_does_not_exist(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG6F"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.return_value.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG14N"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12J": set()}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag " + flag_id + " does not exist"

# #test, add new dependency to flag, missing flag_name/id (flag dependency being added)
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_missing_new_deps(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = []
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.return_value.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12J": set()}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "no new flag dependencies were identified"

# #test, add new dependeny to flag, flag_name/id does not exist (flag dependency being added)
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_new_dep_does_not_exist(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG16P"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.return_value.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12J": set()}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "the following flag attempting to be added as new dependencies do not exist: " + "FLAG16P"

# #test, add new dependeny to flag, flag is already dependent on flag dependency being added
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_flag_already_contains_dep(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG2B"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12L": {"FLAG3C"}}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "the following flag attempting to be added as a new dependency already exists as a dependency (duplicate dependency): " + "FLAG2B"

# #test, add new dependency to flag, new depdendency being added results in cyclical flag
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_new_flag_dependency_results_in_cyclical_flag_dep(flagging_mongo, mvrb):
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     new_deps = ["FLAG5E", "FLAG12L"]
#     flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     mock_flagging_mongo = flagging_mongo
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                           "FLAG2B": {"FLAG3C"},
#                           "FLAG3C": set(),
#                           "FLAG4D": {"FLAG5E"},
#                           "FLAG5E": set(),
#                           "FLAG6F": set(),
#                           "FLAG7G": {"FLAG8G"},
#                           "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                           "FLAG9I": set(),
#                           "FLAG10J": {"FLAG9I"},
#                           "FLAG11K": set(),
#                           "FLAG12L": {"FLAG1A"}}
#     result = add_flag_dependencies(flag=flag_id, new_deps=new_deps, existing_flags=existing_flags, all_flag_dependencies=flag_dependencies, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "the following flag dependency resulted in cyclical dependencies: " + "FLAG12L"

# #test, remove flag deps
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = ["FLAG2B", "FLAG3C"]
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = "FLAG1A"
#     flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
#                          "FLAG2B": {"FLAG3C"},
#                          "FLAG3C": set(),
#                          "FLAG4D": {"FLAG5E"},
#                          "FLAG5E": set(),
#                          "FLAG6F": set(),
#                          "FLAG7G": {"FLAG8G"},
#                          "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
#                          "FLAG9I": set(),
#                          "FLAG10J": {"FLAG9I"},
#                          "FLAG11K": set(),
#                          "FLAG12L": {"FLAG3C"}}
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == True
#     assert result.message == "the following dependencies were removed from flag " + flag_id + ": " + (", ".join(deps_2_remove))
#     assert result.uuid == "FLAG13M"

#test, remove flag deps, missing original flag
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_missing_original_flag(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = ["FLAG2B", "FLAG3C"]
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = None
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag name not specified"

# #test, remove flag deps, original flag does not exist
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_orginal_flag_does_not_exist(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = ["FLAG2B", "FLAG3C"]
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = "FLAG14N"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag " + flag_id + " does not exist"

# #test, remove flag deps, missing deps 2 remove
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_missing_dependencies_to_remove(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = []
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "no dependencies to remove were identified"

# #test, remove flag deps, deps 2 remove do not exist
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_deps_to_remove_do_not_exist(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = ["FLAG2B", "FLAG3C", "FLAG14N"]
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "the following flag is not part of the flag dependency set: " + "FLAG14N"

# #test, remove flag deps, deps 2 remove do not exist as current deps
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_deps_to_remove_do_not_exist_as_current_dependencies(flagging_mongo, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     current_flag_deps = ["FLAG2B", "FLAG3C", "FLAG4D"]
#     deps_2_remove = ["FLAG2B", "FLAG3C", "FLAG5E", "FLAG6F"]
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG13M"
#     flagging_mongo.get_specific_flag_dependencies.return_value = current_flag_deps
#     flag_id = "FLAG1A"
#     existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
#                                                        "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
#     result = remove_flag_dependencies(flag=flag_id, deps_2_remove=deps_2_remove, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
#     print("hello")
#     assert result.valid == False
#     assert result.message == "the following flags are not part of the flag dependency set: FLAG5E, FLAG6F"


#test, create flag group
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.add_flag_group.return_value = "FLAG_GROUP_13M_id"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C"])
    flag_group = "FLAG_GROUP_4D"
    result, response_code = create_flag_group(flag_group_name=flag_group, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "unique flag group " + flag_group + " created"
    assert result.uuid == "FLAG_GROUP_13M_id"
    assert response_code == 200


#test, create flag group, missing flag group name
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group_missing_flag_group_new(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.add_flag_group.return_value = "FLAG_GROUP_13M_id"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C"])
    flag_group = None
    result, response_code = create_flag_group(flag_group_name=flag_group, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "unique flag group name must be specified"
    assert response_code >= 400

#test, create flag group, flag group name already exists
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group_non_unique_flag_group_name(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId(generate_object_id())
    flagging_mongo.add_flag_group.return_value = mock_return_value
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C"])
    flag_group = "FLAG_GROUP_1A"
    result, response_code = create_flag_group(flag_group_name=flag_group, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "new flag group name must be unique"
    assert response_code >= 400

#test, remove flag group
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId(generate_object_id())
    flagging_mongo.remove_flag_group.return_value = mock_return_value
    flag_group_id = ObjectId(generate_object_id())
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=[flag_group_id, ObjectId(generate_object_id())])
    result, response_code = delete_flag_group(flag_group_id=str(flag_group_id), existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "flag group " + str(flag_group_id) + " deleted from database"
    assert result.uuid == mock_return_value
    assert response_code == 200

#test, remove flag group, flag group name is not specified
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group_flag_group_not_specified(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.remove_flag_group.return_value = "FLAG_GROUP_13M_id"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP3C"])
    flag_group = None
    result, response_code = delete_flag_group(flag_group_id=flag_group, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group name must be specified"
    assert response_code >= 400

#tst, remove flag group, flag group does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId(generate_object_id())
    flagging_mongo.remove_flag_group.return_value = mock_return_value
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=[ObjectId(generate_object_id()), ObjectId(generate_object_id())])
    flag_group_id = ObjectId(generate_object_id())
    while flag_group_id in existing_flag_groups:
        flag_group_id
    result, response_code = delete_flag_group(flag_group_id=str(flag_group_id), existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "could not identify flag group " + str(flag_group_id) + " in database"
    assert response_code >= 400

#test, add flag to flag_group
mock_flag_dependencies = {"FLAG1A": {"FLAG2B", "FLAG3C"},
                     "FLAG2B": {"FLAG3C"},
                     "FLAG3C": set(),
                     "FLAG4D": {"FLAG5E"},
                     "FLAG5E": set(),
                     "FLAG6F": set(),
                     "FLAG7G": {"FLAG8G"},
                     "FLAG8G": {"FLAG9I", "FLAG10J", "FLAG11K"},
                     "FLAG9I": set(),
                     "FLAG10J": {"FLAG9I"},
                     "FLAG11K": set(),
                     "FLAG12L": {"FLAG3C"}}
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111101")
    new_flags = [ObjectId("A11111111111111111111103")]
    flags_in_flag_group = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102")]
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "flag group " + str(flag_group_id) + " has been updated with flag(s) " + (", ".join([str(x) for x in new_flags]) + "\n")
    assert result.uuid == mock_return_value
    assert response_code == 200


@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_2(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111101")
    new_flags = [ObjectId("A11111111111111111111103"), ObjectId("A11111111111111111111104")]
    flags_in_flag_group = []
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "flag group " + str(flag_group_id) + " has been updated with flag(s) " + (", ".join([str(x) for x in new_flags])) + "\n"
    assert result.uuid == mock_return_value
    assert response_code == 200

#test, add flag to flag_group, flag group_name/id not passed
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_missing_flag_group_name(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    new_flags = [ObjectId("A11111111111111111111103"), ObjectId("A11111111111111111111104")]
    flags_in_flag_group = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102")]
    result, response_code = add_flag_to_flag_group(flag_group_id=None, new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group must be specified"
    assert response_code >= 400

#test, add flag to flag_gropu, flag_group_name/id does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_flag_group_does_not_exist(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("C11111111111111111111113")
    new_flags = [ObjectId("A11111111111111111111103"), ObjectId("A11111111111111111111104")]
    flags_in_flag_group = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102")]
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag_group " + str(flag_group_id) + " does not exist"
    assert response_code >= 400


#test, add flag to flag_group, flag is not specified
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_missing_flag(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111112")
    new_flags = []
    flags_in_flag_group = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102")]
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=new_flags, existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "no new flags were specified"
    assert response_code >= 400

#test, add flag to flag_group, flag does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_flag_does_not_exist(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
                                                       "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C", "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
                                                       "FLAG_GROUP_7G", "FLAG_GORUP_8H", "FLAG_GROUP_9I", "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    flag_group_name = "FLAG_GROUP_2B"
    new_flags = ["FLAG1A", "FLAG2B", "FLAG_DOES_NOT_EXIST", "FLAG4D", "FLAG_DOES_NOT_EXIST_2"]
    flags_in_flag_group = []
    result = add_flag_to_flag_group(flag_group_name=flag_group_name, new_flags=new_flags, existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "Flag(s) " + (", ".join(["FLAG_DOES_NOT_EXIST", "FLAG_DOES_NOT_EXIST_2"])) + " do not exist"

#test, add flag to flag_group, flag already exists in flag group
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_flag_does_not_exist(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111112")
    new_flags = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102"),
                 ObjectId("A11111111111111111111103"), ObjectId("A11111111111111111111104")]
    flags_in_flag_group = [ObjectId("A11111111111111111111101"), ObjectId("A11111111111111111111102")]
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "Flag(s) " + (", ".join([str(x) for x in flags_in_flag_group])) + " already exist in flag group"
    assert response_code >= 400


    # mock_flagging_mongo = flagging_mongo
    # flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    # existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
    #                                                    "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    # existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C", "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
    #                                                    "FLAG_GROUP_7G", "FLAG_GORUP_8H", "FLAG_GROUP_9I", "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    # flag_group_name = "FLAG_GROUP_2B"
    # new_flags = ["FLAG1A", "FLAG2B", "FLAG4D", "FLAG5E"]
    # flags_in_flag_group = ["FLAG2B", "FLAG4D"]
    # result = add_flag_to_flag_group(flag_group_id=flag_group_name, new_flags=new_flags, existing_flags=existing_flags,
    #                                 existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
    #                                 flagging_mongo=mock_flagging_mongo)
    # assert result.valid == False
    # assert result.message == "Flag(s) " + (", ".join(["FLAG2B", "FLAG4D"])) + " already exist in flag group"

#test, add flag to flag_group, new flag in flag group results in cyclical flagging

flag_1a_object_id = ObjectId("A11111111111111111111101")
flag_2b_object_id = ObjectId("A11111111111111111111102")
flag_3c_object_id = ObjectId("A11111111111111111111103")
flag_4d_object_id = ObjectId("A11111111111111111111104")
flag_5e_object_id = ObjectId("A11111111111111111111105")
flag_6f_object_id = ObjectId("A11111111111111111111106")
flag_7g_object_id = ObjectId("A11111111111111111111107")
flag_8h_object_id = ObjectId("A11111111111111111111108")
flag_9i_object_id = ObjectId("A11111111111111111111109")
flag_10j_object_id = ObjectId("A11111111111111111111110")
flag_11k_object_id = ObjectId("A11111111111111111111111")
flag_12l_object_id = ObjectId("A11111111111111111111112")

flag_group_1a_object_id = ObjectId("B11111111111111111111101")
flag_group_2b_object_id = ObjectId("B11111111111111111111102")
flag_group_3c_object_id = ObjectId("B11111111111111111111103")
flag_group_4d_object_id = ObjectId("B11111111111111111111104")
flag_group_5e_object_id = ObjectId("B11111111111111111111105")
flag_group_6f_object_id = ObjectId("B11111111111111111111106")
flag_group_7g_object_id = ObjectId("B11111111111111111111107")
flag_group_8h_object_id = ObjectId("B11111111111111111111108")
flag_group_9i_object_id = ObjectId("B11111111111111111111109")
flag_group_10j_object_id = ObjectId("B11111111111111111111110")
flag_group_11k_object_id = ObjectId("B11111111111111111111111")
flag_group_12l_object_id = ObjectId("B11111111111111111111112")


mock_flag_dependencies = {flag_1a_object_id: {flag_2b_object_id, flag_3c_object_id},
                     flag_2b_object_id: {flag_3c_object_id},
                     flag_3c_object_id: {flag_4d_object_id},
                     flag_4d_object_id: {flag_2b_object_id},
                     flag_5e_object_id: set(),
                     flag_6f_object_id: set(),
                     flag_7g_object_id: {flag_8h_object_id},
                     flag_8h_object_id: {flag_9i_object_id, flag_10j_object_id, flag_11k_object_id},
                     flag_9i_object_id: set(),
                     flag_10j_object_id: {flag_9i_object_id},
                     flag_11k_object_id: set(),
                     flag_12l_object_id: {flag_3c_object_id}}
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flags_to_flag_group_cyclical_flag_not_refereced(flagging_mongo, mgfd, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111102")
    new_flags = [ObjectId("A11111111111111111111105"), ObjectId("A11111111111111111111106")]
    flags_in_flag_group = [ObjectId("A11111111111111111111111")]
    result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "flag group " + str(flag_group_id) + " has been updated with flag(s) " + (", ".join([str(x) for x in new_flags])) + "\n"
    assert result.uuid == mock_return_value
    assert response_code == 200



# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("front_end.FlaggingValidateLogic.get_flag_dependencies", return_value=mock_flag_dependencies, autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_add_flags_to_flag_group_cyclical_flag_referenced(flagging_mongo, mgfd, mvrb):
#     mock_flagging_mongo = flagging_mongo
#     mock_return_value = ObjectId("B11111111111111111111113")
#     flagging_mongo.update_flag_group.return_value = mock_return_value
#     existing_flags = pull_flag_ids()
#     existing_flag_groups = pull_flag_group_ids()
#     flag_group_id = ObjectId("B11111111111111111111102")
#     new_flags = [ObjectId("A11111111111111111111105"), ObjectId("A11111111111111111111112")]
#     flags_in_flag_group = [ObjectId("A11111111111111111111107")]
#     result, response_code = add_flag_to_flag_group(flag_group_id=str(flag_group_id), new_flags=[str(x) for x in new_flags], existing_flags=existing_flags,
#                                     existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
#                                     flagging_mongo=mock_flagging_mongo)
#     assert result.valid == False
#     assert result.message == "the following flag dependency resulted in cyclical dependencies: " + str(ObjectId("A11111111111111111111112"))
#     assert result.uuid == mock_return_value
#     assert response_code >= 400

#test, remove flag from flag group
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111104")
    flags_2_remove = [ObjectId("A11111111111111111111108"), ObjectId("A11111111111111111111109")]
    flags_in_flag_group = existing_flags
    result, response_code = remove_flag_from_flag_group(flag_group_id=str(flag_group_id), del_flags=[str(x) for x in flags_2_remove], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "Flag(s) " + ", ".join(str(x) for x in flags_2_remove) + " removed from " + str(flag_group_id)
    assert result.uuid == mock_return_value
    assert response_code == 200



#test, remove flag from flag group, missing flag group name
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group_missing_flag_group(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111104")
    flags_2_remove = [ObjectId("A11111111111111111111108"), ObjectId("A11111111111111111111109")]
    flags_in_flag_group = existing_flags
    result, response_code = remove_flag_from_flag_group(flag_group_id=None, del_flags=[str(x) for x in flags_2_remove], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group not specified"
    assert result.uuid == None
    assert response_code >= 400


#test, remove flag from flag group, flag group does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
                                                       "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C",
                                                                         "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
                                                                         "FLAG_GROUP_7G", "FLAG_GROUP_8H", "FLAG_GROUP_9I",
                                                                         "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    flag_group_name = "not_a_real_flag_group"
    flags_in_flag_group = existing_flags
    flags_2_remove = ["FLAG8H", "FLAG9I"]
    result = remove_flag_from_flag_group(flag_group_name=flag_group_name, del_flags=flags_2_remove, existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                         flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group does not exist"

#test, remove flag from flag group, missing flags to remove
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb):
    flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
                                                       "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C",
                                                                         "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
                                                                         "FLAG_GROUP_7G", "FLAG_GROUP_8H", "FLAG_GROUP_9I",
                                                                         "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    flag_group_name = "FLAG_GROUP_7G"
    flags_in_flag_group = existing_flags
    flags_2_remove = []
    result = remove_flag_from_flag_group(flag_group_name=flag_group_name, del_flags=flags_2_remove, existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                         flagging_mongo=flagging_mongo)
    assert result.valid == False
    assert result.message == "no flags to remove were specified"

#test, remove flag from flag group, flag to remove does not exist
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb):
    flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
                                                       "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C",
                                                                         "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
                                                                         "FLAG_GROUP_7G", "FLAG_GROUP_8H", "FLAG_GROUP_9I",
                                                                         "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    flag_group_name = "FLAG_GROUP_7G"
    flags_in_flag_group = existing_flags
    flags_2_remove = ["FLAG9I", "FLAG14N"]
    result = remove_flag_from_flag_group(flag_group_name=flag_group_name, del_flags=flags_2_remove, existing_flags=existing_flags,
                                         existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                         flagging_mongo=flagging_mongo)
    assert result.valid == False
    assert result.message == "no flags to remove were specified"

#test, remove flag from flag group, flag to remove is not associted with flag group
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_from_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb):
    mock_flagging_mongo = flagging_mongo
    mock_return_value = ObjectId("B11111111111111111111113")
    flagging_mongo.update_flag_group.return_value = mock_return_value
    existing_flags = pull_flag_ids()
    existing_flag_groups = pull_flag_group_ids()
    flag_group_id = ObjectId("B11111111111111111111104")
    flags_2_remove = [ObjectId("A11111111111111111111109")]
    flags_in_flag_group = existing_flags.copy()
    flags_in_flag_group.remove(ObjectId("A11111111111111111111109"))
    result, response_code = remove_flag_from_flag_group(flag_group_id=str(flag_group_id), del_flags=[str(x) for x in flags_2_remove], existing_flags=existing_flags,
                                    existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
                                    flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "the following flags are not part of flag group " + str(flag_group_id) + ": " + ("").join([str(x) for x in flags_2_remove])
    assert response_code >= 400


    # flagging_mongo.update_flag_group.return_value = "FLAG_GROUP_13M_ID"
    # existing_flags = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B", "FLAG3C", "FLAG4D", "FLAG5E", "FLAG6F",
    #                                                    "FLAG7G", "FLAG8H", "FLAG9I", "FLAG10J", "FLAG11K", "FLAG12L"])
    # existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B", "FLAG_GROUP_3C",
    #                                                                      "FLAG_GROUP_4D", "FLAG_GROUP_5E", "FLAG_GROUP_6F",
    #                                                                      "FLAG_GROUP_7G", "FLAG_GROUP_8H", "FLAG_GROUP_9I",
    #                                                                      "FLAG_GROUP_10J", "FLAG_GROUP_11K", "FLAG_GROUP_12L"])
    # flag_group_name = "FLAG_GROUP_7G"
    # flags_in_flag_group = existing_flags.copy()
    # flags_in_flag_group.remove("FLAG9I")
    # flags_2_remove = ["FLAG9I"]
    # result = remove_flag_from_flag_group(flag_group_id=flag_group_name, del_flags=flags_2_remove, existing_flags=existing_flags,
    #                                      existing_flag_groups=existing_flag_groups, flags_in_flag_group=flags_in_flag_group,
    #                                      flagging_mongo=flagging_mongo)
    # assert result.valid == False
    # assert result.message == "the following flags are not part of flag group " + flag_group_name + ": " + ("").join(flags_2_remove)

# #test, create flag dependency
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_create_flag_dependency(flagging_mongo, mvrb):
#     flagging_mongo.add_flag_dependencies.return_value = "flag_dep_key_1A"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_name = "FLAG4D"
#     new_flag_deps = ["FLAG2B", "FLAG5E"],
#     result = create_flag_dependency(flag_name=flag_name, existing_flag_dep_keys=existing_flag_dep_keys, flag_dependencies=new_flag_deps, flagging_mongo=flagging_mongo)
#     assert result.valid == True
#     assert result.message == "flag dependency data for flag " + flag_name + " has been created"
#     assert result.uuid == "flag_dep_key_1A"

# #test, create flag dependency, flag name not passed
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_create_flag_dependency_no_flag_name(flagging_mongo, mvrb):
#     flagging_mongo.add_flag_dependencies.return_value = "flag_dep_key_1A"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_name = None
#     new_flag_deps = ["FLAG2B", "FLAG5E"],
#     result = create_flag_dependency(flag_name=flag_name, existing_flag_dep_keys=existing_flag_dep_keys,
#                                     flag_dependencies=new_flag_deps, flagging_mongo=flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag name not specified"
#     assert result.uuid == None

# #test, create flag dependency, flag name already in existing flag set
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_create_flag_dependency_flag_already_exists(flagging_mongo, mvrb):
#     flagging_mongo.add_flag_dependencies.return_value = "flag_dep_key_1A"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_name = "FLAG3C"
#     new_flag_deps = ["FLAG2B", "FLAG5E"],
#     result = create_flag_dependency(flag_name=flag_name, existing_flag_dep_keys=existing_flag_dep_keys,
#                                     flag_dependencies=new_flag_deps, flagging_mongo=flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag dependencies for flag " + flag_name + " already exist"
#     assert result.uuid == None

# #test, delete flag dependnecy
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_delete_flag_dependency(flagging_mongo, mvrb):
#     flagging_mongo.remove_flag_dependencies.return_value = "Flag_ID_XX_RM"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_id = "FLAG1A"
#     result = delete_flag_dependency(flag_id, existing_flag_dep_keys, flagging_mongo)
#     assert result.valid == True
#     assert result.message == "flag " + flag_id + "has been removed from flag dependency database"
#     assert result.uuid == "Flag_ID_XX_RM"

# #test, delete flag dependency, flag id not passed
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_delete_flag_dependency_flag_id_not_passed(flagging_mongo, mvrb):
#     flagging_mongo.remove_flag_dependencies.return_value = "Flag_ID_XX_RM"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_id = None
#     result = delete_flag_dependency(flag_id, existing_flag_dep_keys, flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag id not specified"
#     assert result.uuid == None

# #test, delete flag dependnecy, flag id not in existing flag dependency database
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_delete_flag_dependency_flag_id_does_not_exist(flagging_mongo, mvrb):
#     flagging_mongo.remove_flag_dependencies.return_value = "Flag_ID_XX_RM"
#     existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
#     flag_id = "FLAG4D"
#     result = delete_flag_dependency(flag_id, existing_flag_dep_keys, flagging_mongo)
#     assert result.valid == False
#     assert result.message == "flag dependencies for flag " + flag_id + " do not exist"
#     assert result.uuid == None

#test, add_dependencies_to_flag
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flag_dependencies_to_flag(flagging_mongo, mvrb):
    flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG_ID_DEPS_ADDED_1A"
    existing_flag_dep_keys = [ObjectId("1"*21 + "1AD"), ObjectId("1"*21 + "2BD"), ObjectId("1"*21 + "3CD")]
    flag_dep_id = "1" * 21 + "1AD"
    new_deps_2_add = [ReferencedFlag(flag_name="FlagName1", flag_group_id="1"*21 + "1GA")]
    result, response_code = add_dependencies_to_flag(flag_dep_id, existing_flag_dep_keys, new_deps_2_add, flagging_mongo)
    assert result.valid == True
    assert result.message == "dependencies have been updated"
    assert result.uuid == "FLAG_ID_DEPS_ADDED_1A"
    assert response_code == 200

#test, add_dependencies_to_flag, flag id not passed
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flag_dependencies_to_flag_missing_flag_id(flagging_mongo, mvrb):
    flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG_ID_DEPS_ADDED_1A"
    existing_flag_dep_keys = ["FLAG1A", "FLAG2B", "FLAG3C"]
    flag_dep_id = None
    new_deps_2_add = ["FLAG2B"]
    result, response_code = add_dependencies_to_flag(flag_dep_id, existing_flag_dep_keys, new_deps_2_add, flagging_mongo)
    assert result.valid == False
    assert result.message == "flag dep id not specified"
    assert result.uuid == None
    assert response_code >= 400

#tests, add deps to flag, flag_id does not exist as an existing flag dep key
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_add_flag_dependencies_to_flag_flag_id_does_not_exist(flagging_mongo, mvrb):
    flagging_mongo.add_specific_flag_dependencies.return_value = "FLAG_ID_DEPS_ADDED_1A"
    existing_flag_dep_keys = [ObjectId("1"*21 + "1AD"), ObjectId("1"*21 + "2BD"), ObjectId("1"*21 + "3CD")]
    flag_dep_id = "1" * 21 + "4DD"
    new_deps_2_add = [ReferencedFlag(flag_name="FlagName1", flag_group_id="1"*21 + "1GA")]
    result, response_code = add_dependencies_to_flag(flag_dep_id, existing_flag_dep_keys, new_deps_2_add, flagging_mongo)
    assert result.valid == False
    assert result.message == "flag dep does not exist in flag dependency database"
    assert result.uuid == None
    assert response_code >= 400

# #test, remove deps from flag
# @mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
# @mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
# def test_remove_flag_dependencies_from_flag(flagging_mongo, mvrb):
#     flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG_ID_DEP_RM_1A"
#     existing_flag_dep_keys = [ObjectId("1"*21 + "1AD"), ObjectId("1"*21 + "2BD"), ObjectId("1"*21 + "3CD")]
#     flag_dep_id = "1" * 21 + "4DD"
#     deps_2_remove = [ReferencedFlag(flag_name="FlagName1", flag_group_id="1"*21 + "1GA")]
#     result, response_code = remove_dependencies_from_flag(flag_dep_id, existing_flag_dep_keys, deps_2_remove, flagging_mongo)
#     assert result.valid == True
#     assert result.message == "dependencies have been updated"
#     assert result.uuid == "FLAG_ID_DEP_RM_1A"
#     assert response_code == 200

#test, remove deps from flag, flag id not passed
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_dependencies_from_flag_missing_flag_id(flagging_mongo, mvrb):
    flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG_ID_DEP_RM_1A"
    flag_id = None
    existing_flag_dep_keys = ['FLAG1A', "FLAG2B", "FLAG3C"]
    deps_2_remove = ["FLAG1A"]
    result, response_code = remove_dependencies_from_flag(flag_id, existing_flag_dep_keys, deps_2_remove, flagging_mongo)
    assert result.valid == False
    assert result.message == "flag dep id not specified"
    assert result.uuid == None
    assert response_code >= 400

#test, remove deps from flag, flag_id does not exist as an existing flag dep key
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_dependencies_from_flag_flag_id_does_not_exist(flagging_mongo, mvrb):
    flagging_mongo.remove_specific_flag_dependencies.return_value = "FLAG_ID_DEP_RM_1A"
    flag_id = "1"*22 + "4D"
    existing_flag_dep_keys = ["1"*21 + "1AD", "1"*21 + "2BD"]
    deps_2_remove = ["1"*22 + "1A"]
    result, response_code = remove_dependencies_from_flag(flag_id, existing_flag_dep_keys, deps_2_remove, flagging_mongo)
    assert result.valid == False
    assert result.message == "flag dep does not exist in flag dependency database"
    assert result.uuid == None
    assert response_code >= 400

