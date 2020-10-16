from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.VariableInformation import VariableInformation

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
            used_variables={VariableInformation('x'): {CodeLocation(1, 1)}},
            assigned_variables={VariableInformation("x"): {CodeLocation(3, 3)}},
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


