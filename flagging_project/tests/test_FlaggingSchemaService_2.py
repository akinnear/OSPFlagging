from unittest import mock
from flagging.TypeValidationResults import TypeValidationResults
from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from front_end.FlaggingSchemaService import create_flag, create_flag, \
    update_flag_name, update_flag_logic, \
    delete_flag, create_flag_group, delete_flag_group, add_flag_to_flag_group, \
    remove_flag_from_flag_group, duplicate_flag, duplicate_flag_group
from flagging.FlaggingValidation import FlaggingValidationResults
from flagging.FlagErrorInformation import FlagErrorInformation
from flag_names.FlagService import pull_flag_names, \
    pull_flag_names_in_flag_group
from flag_names.FlagGroupService import pull_flag_group_names








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
    result = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag created"
    assert result.uuid == 1


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
    result = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag name not specified"


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
    result = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == 1

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
    result = create_flag(flag_name, flag_logic_information, mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == 1

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = "FlagID1"
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["FlagID1", "FlagID3"])
    result = update_flag_name(original_flag_id=og_flag_id, new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "original flag " + og_flag_id + " has been renamed " + nw_flag_name
    assert result.uuid == 2

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_missing_og_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = None
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["FlagID1", "FlagID3"])
    result = update_flag_name(original_flag_id=og_flag_id, new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify id of original flag"

@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_missing_new_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = "FlagID1"
    nw_flag_name = None
    existing_flags = pull_flag_names(dummy_flag_names=["FlagID1", "FlagID3"])
    result = update_flag_name(original_flag_id=og_flag_id, new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify name of new flag"


@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_name_og_flag_not_found(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 2
    mock_flagging_mongo = flagging_mongo()
    og_flag_id = "FlagID1"
    nw_flag_name = "Flag2"
    existing_flags = pull_flag_names(dummy_flag_names=["FlagID2", "FlagID3"])
    result = update_flag_name(original_flag_id=og_flag_id, new_flag_name=nw_flag_name, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "original flag id " + og_flag_id + " does not exist"

#test update flag logic informatio
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID1"
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
    result = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "logic for flag " + str(3) + " has been updated"
    assert result.uuid == 3


#update flag logic, flag id not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_missing_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
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
    result = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information,
                               existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag id"

#update flag logic, flag id does not exists
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_missing_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID3"
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
    result = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information,
                               existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "could not identify existing flag " + og_flag_id
    assert result.uuid == og_flag_id

#update flag logic, error in result
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(errors={"some_error": {"some_code_location"}}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_errors(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID1"
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
    result = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == og_flag_id

#update flag lgoic, mypy_error in result
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(mypy_errors={"some_mypy_error": {"some_code_location"}}), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_flag_logic_mypy_errors(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.update_flag.return_value = 3
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID1"
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
    result = update_flag_logic(flag_id=og_flag_id, new_flag_logic_information=nw_flag_logic_information, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "error in flag logic"
    assert result.uuid == og_flag_id


#test to delete flag, valid
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID1"
    result = delete_flag(flag_id=og_flag_id, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == og_flag_id + " has been deleted"
    assert result.uuid == og_flag_id

#test to delete flag, missign flag id
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag_missing_flag_id(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = None
    result = delete_flag(flag_id=og_flag_id, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag id"
    assert result.uuid == og_flag_id

#test to delete flag, flag does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_update_delete_flag_flag_does_not_exist(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    existing_flags = pull_flag_names(dummy_flag_names=["FLAGID1", "FLAGID2"])
    og_flag_id = "FLAGID3"
    result = delete_flag(flag_id=og_flag_id, existing_flags=existing_flags, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag id specified does not exist"
    assert result.uuid == og_flag_id

#test, duplicate flag
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag(flagging_mongo, mvrb, mvl):
    flagging_mongo.duplicate_flag.return_value = 4
    mock_flagging_mongo = flagging_mongo
    flag_id = "FLAG1A"
    existing_flag_ids = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B"])
    result = duplicate_flag(original_flag_id=flag_id, existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == flag_id + " has be duplicated"
    assert result.uuid == 4

#test, duplicate flag, flag name not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_missing_flag_id(flagging_mongo, mvrb, mvl):
    flagging_mongo.duplicate_flag.return_value = 4
    mock_flagging_mongo = flagging_mongo
    flag_id = None
    existing_flag_ids = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B"])
    result = duplicate_flag(original_flag_id=flag_id, existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag id must be specified"

#test, duplicate flag, flag name does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_flag_does_not_exist(flagging_mongo, mvrb, mvl):
    flagging_mongo.duplicate_flag.return_value = 4
    mock_flagging_mongo = flagging_mongo
    flag_id = "FLAG3C"
    existing_flag_ids = pull_flag_names(dummy_flag_names=["FLAG1A", "FLAG2B"])
    result = duplicate_flag(original_flag_id=flag_id, existing_flags=existing_flag_ids, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag " + flag_id + " does not exist"


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
    result = create_flag_group(flag_group_name=new_flag_group, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "unique flag group name must be specified"

#test, create new flag group, flag group name is not unique
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_create_flag_group_name_not_unique(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.add_flag_group.return_value = 5
    mock_flagging_mongo = flagging_mongo()
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    new_flag_group = "FlagGroup1"
    result = create_flag_group(flag_group_name=new_flag_group, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "new flag group name must be unique"


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
    result = delete_flag_group(flag_group_name=flag_group_2_remove, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group name must be specified"

#test remove flag group, flag group name does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_remove_flag_group_flag_group_name_does_not_exist(flagging_mongo, mvrb, mvl):
    mock_flagging_mongo = flagging_mongo()
    flagging_mongo.return_value.remove_flag_group.return_value = 6
    existing_flag_group_names = pull_flag_group_names(dummy_flag_group_names=["FlagGroup1", "FlagGroup2"])
    flag_group_2_remove = "FlagGrup3"
    result = delete_flag_group(flag_group_name=flag_group_2_remove, existing_flag_groups=existing_flag_group_names, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "could not identify flag group " + flag_group_2_remove + " in database"


#test, duplicate flag_group
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.duplicate_flag_group.return_value = "Flag_Group_7G"
    mock_return_value = flagging_mongo.return_value.duplicate_flag_group.return_value
    mock_flagging_mongo = flagging_mongo()
    flag_group_id = "FLAG_GROUP_1A"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B"])
    result = duplicate_flag_group(original_flag_group_id=flag_group_id, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == True
    assert result.message == "new flag group " + mock_return_value + " created off of " + flag_group_id
    assert result.uuid == mock_return_value

#test, duplicate flag_group, flag_group_id not specified
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group_missing_flag_group(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.duplicate_flag_group.return_value = "Flag_Group_7G"
    mock_flagging_mongo = flagging_mongo()
    flag_group_id = None
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B"])
    result = duplicate_flag_group(original_flag_group_id=flag_group_id, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "user must specify flag group id"

#test, duplicate flag_group, flag_group_id does not exist
@mock.patch("front_end.FlaggingSchemaService.validate_logic", return_value=FlaggingValidationResults(), autospec=True)
@mock.patch("flagging.FlaggingValidation.validate_returns_boolean", return_value=TypeValidationResults(), autospec=True)
@mock.patch("flag_data.FlaggingMongo.FlaggingMongo")
def test_duplicate_flag_group_flag_group_does_not_exist(flagging_mongo, mvrb, mvl):
    flagging_mongo.return_value.duplicate_flag_group.return_value = "Flag_Group_7G"
    mock_flagging_mongo = flagging_mongo()
    flag_group_id = "FLAG_GROUP_3C"
    existing_flag_groups = pull_flag_group_names(dummy_flag_group_names=["FLAG_GROUP_1A", "FLAG_GROUP_2B"])
    result = duplicate_flag_group(original_flag_group_id=flag_group_id, existing_flag_groups=existing_flag_groups, flagging_mongo=mock_flagging_mongo)
    assert result.valid == False
    assert result.message == "flag group " + flag_group_id + " does not exist"


