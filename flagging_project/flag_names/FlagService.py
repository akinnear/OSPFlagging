from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation
from bson.objectid import ObjectId
from flagging.FlaggingNodeVisitor import determine_variables

def pull_flag_ids(*args, **kwargs):
    dummy_flag_ids = kwargs.get("dummy_flag_ids", None)
    if dummy_flag_ids:
        pass
    else:
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
        dummy_flag_ids = [flag_1a_object_id, flag_2b_object_id, flag_3c_object_id,
                          flag_4d_object_id, flag_5e_object_id, flag_6f_object_id,
                          flag_7g_object_id, flag_8h_object_id, flag_9i_object_id,
                          flag_10j_object_id, flag_11k_object_id, flag_12l_object_id]
        return dummy_flag_ids

def pull_flag_names(*args, **kwargs):
    #method to pull flag names from api endpiont or internal db query

    api_endpoint = kwargs.get("api_endpoint")

    dummy_flag_names = kwargs.get("dummy_flag_names", None)

    if dummy_flag_names:
        return dummy_flag_names


def pull_flag_names_in_flag_group(*args, **kwargs):
    #method to pull falg names form api endpoint or intenal db query
    #flags exists inside of flag_group

    api_endpoint = kwargs.get("api_endpoint")

    dummy_flag_names = kwargs.get("dummy_flag_names", None)

    if dummy_flag_names:
        return dummy_flag_names


def pull_flag_logic_information(*args, **kwargs):
    dummy_flag = kwargs.get("dummy_flag", False)
    dummy_flag_2 = kwargs.get("dummy_flag_2", False)
    unique_dummy_flag = kwargs.get("unique_dummy_flag", False)
    if dummy_flag:
        flag_info = FlagLogicInformation(
            used_variables={VariableInformation('x'): {CodeLocation(1, 1), CodeLocation(1, 5)},
                            VariableInformation("y"): {CodeLocation(1, 10)}},
            assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)},
                                VariableInformation("y"): {CodeLocation(2, 2)}},
            referenced_flags={}
        )
    elif dummy_flag_2:
        flag_info = FlagLogicInformation(
            used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
            assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
            referenced_flags={"Flag1A": {CodeLocation(0, 0)}},
            flag_logic="Flag1A > x + 10"
        )
    elif unique_dummy_flag:
        flag_info = unique_dummy_flag
    else:
        flag_info = FlagLogicInformation()
    return flag_info

def get_valid_dummy_flag():
    logic = """\
if FF1 > 10:
    return True
else:
    return False"""
    flag_info = determine_variables(logic)
    return flag_info



def get_flag_service(flag_logic):
    flag_node_visitor = determine_variables(flag_logic)
    return flag_node_visitor
