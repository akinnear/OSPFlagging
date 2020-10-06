from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlagLogicInformation import FlagLogicInformation
from front_end.FlaggingDependencies import get_flag_dependencies
from flagging.FlaggingValidation import validate_flag_logic_information


#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.


def validate_logic(flag_id:str, flag_logic_information:FlagLogicInformation()):
    #TODO
    # get flag feeders
    flag_feeders = pull_flag_feeders(dummy_flag_feeders={"FF1": int, "FF2": bool, "FF3": str, "FF4": int})

    #TODO
    # need flag_dependiceis from api call or direct query
    flag_dependencies = get_flag_dependencies()


    #TODO
    # perform full validation on user_logic via nodevisitor, mypy, and validation
    # mypy validation is part of full validation method, do not need explicit mypy validation call



    #validation
    validation_result = validate_flag_logic_information(flag_id, flag_feeders, flag_dependencies, flag_logic_information)

    #return errors and warning information
    return validation_result
