#imports
from flagging.FlaggingNodeVisitor import determine_variables
from flagging.FlaggingValidation import validate_returns_boolean
from flag_feeders.

#TODO
# interface design, html5 + bootstrap4

#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.

def validate_logic(user_logic):
    #get flag feeders


    #perform full validation on user_logic via nodevisitor, mypy, and validation

    #nodeivisitor on user_logic
    #determine variables form FlaggingNodeVisitor
    flag_logic_information = determine_variables(user_logic)

    #mypy validation
    mypy_ouput =
    #call to get correct flag feeders
    #return errors and warning information


#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error


#A call to save changes to a flag, this will take in the change and a UUID
#One call for flag name
#Another call for flag logic


#A call to delete a flag provided a UUID, return true/false


#A call to create a named flag group, returns a UUID, name cannot be empty if so error


#A call to delete a flag group provided a UUID, return true/false


#Flag Groups Updating, within these calls cyclic and existing flag name checks need to occur.
# They should both return validation information such describing possible errors
# in the group such as missing and cyclic flags
#A call to add flags to a group provided a UUID for the group and UUIDs for the flags to add
#A call to remove flags from a group provided a UUID for the group and UUIDs for the flags to add


#A call to duplicate a flag provided a new name and UUID


#A call to duplicate a flag group provided a new name and UUID



#TODO,
# write new tests in tests module