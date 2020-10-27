from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.TypeValidationResults import TypeValidationResults
from flagging.VariableInformation import VariableInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.ErrorInformation import ErrorInformation
from flagging.ModuleInformation import ModuleInformation
from front_end.TransferFlagLogicInformation import TransferFlagLogicInformation, _convert_FLI_to_TFLI

def test_flag_logic_information_transfer_object_creation():
    #create FLI
    flag_logic_information = FlagLogicInformation(
        used_variables={VariableInformation("ff1"): {CodeLocation(4, 11)},
                        VariableInformation("ff2"): {CodeLocation(6, 11)},
                        VariableInformation("a"): {CodeLocation(2, 16), CodeLocation(2, 22)},
                        VariableInformation("b"): {CodeLocation(2, 26), CodeLocation(2, 34)},
                        VariableInformation("f"): {CodeLocation(3, 10), CodeLocation(4, 24), CodeLocation(6, 24)}},
        assigned_variables={VariableInformation("f"): {CodeLocation(2, 0)},
                            VariableInformation("a"): {CodeLocation(2, 11)},
                            VariableInformation('b'): {CodeLocation(2, 13)}},
        referenced_functions={
            VariableInformation("reduce"): {CodeLocation(3, 3), CodeLocation(4, 17), CodeLocation(6, 17)}},
        defined_functions={VariableInformation("my_add"): {CodeLocation(2, 4)}},
        defined_classes={VariableInformation("my_class"): {CodeLocation(1, 1)}},
        referenced_modules={ModuleInformation("wtforms"): {CodeLocation(2, 5)},
                            ModuleInformation("functools", "my_funky_tools"): {CodeLocation(1, 7)}},
        referenced_flags={"Flag5": {CodeLocation(5, 10), CodeLocation(6, 10)}},
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
    #convert to transfer object form
    transfer_flag_logic_information = _convert_FLI_to_TFLI(flag_logic_information)
    assert len(transfer_flag_logic_information['used_variables']) == 5
    assert transfer_flag_logic_information["used_variables"][0]["name"] == "ff1"
    assert transfer_flag_logic_information["used_variables"][0]["locations"][0]["line_number"] == 4
    assert transfer_flag_logic_information["used_variables"][0]["locations"][0]["column_offset"] == 11
    assert transfer_flag_logic_information["used_variables"][1]["name"] == "ff2"
    assert transfer_flag_logic_information["used_variables"][1]["locations"][0]["line_number"] == 6
    assert transfer_flag_logic_information["used_variables"][1]["locations"][0]["column_offset"] == 11
    assert transfer_flag_logic_information["used_variables"][2]["name"] == "a"
    assert transfer_flag_logic_information["used_variables"][2]["locations"][0]["line_number"] == 2
    assert transfer_flag_logic_information["used_variables"][2]["locations"][0]["column_offset"] == 16
    assert transfer_flag_logic_information["used_variables"][2]["locations"][1]["line_number"] == 2
    assert transfer_flag_logic_information["used_variables"][2]["locations"][1]["column_offset"] == 22

    print("hello")

