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
    assert result.message == "logic for flag " + og_flag_id + " has been updated"
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
