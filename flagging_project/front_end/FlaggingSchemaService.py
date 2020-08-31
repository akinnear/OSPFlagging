#imports
from flagging.FlaggingNodeVisitor import determine_variables
from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information

#TODO
# interface design, html5 + bootstrap4

#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.

def validate_logic(user_logic):
    #get flag feeders
    flag_feeders = pull_flag_feeders("dummy_text_endpoint")

    #perform full validation on user_logic via nodevisitor, mypy, and validation

    #nodeivisitor on user_logic
    #determine variables form FlaggingNodeVisitor
    flag_logic_information = determine_variables(user_logic)

    #mypy validation is part of full validation method, do not need explicit mypy validation call

    #need flag name from user
    flag_name = create_flag("Mock_Default_Flag_Name", user_logic)

    #need flag_dependiceis from api call or direct query

    #validation
    validation_result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_logic_information)

    #return errors and warning information
    return validation_result


#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error

def create_flag(flag_name, flag_logic):
    #store flag name and flag logic in db
    #write query, with new primary key
    #cursor.execute("""INSERT into TABLE FLAG_NAME_COL= :flag_name, FLAG_LOGIC_COL= :flag_logic""",
    # flag_name=flag_name,
    # flag_logic=flag_logic)

    #cursor.execute("""SELECT PRIMARY_KEY_COL FROM TABLE
    # WHERE FLAG_NAME_COL = :flag_name
    # AND FLAG_LOGIC_COL = :flag_logic""",
    #flag_name=flag_name,
    #flag_logic=flag_logic)

    #df_new_flag = df_from_cursor.cursor()
    #return df_new_flag['PRIMARY_KEY_COL'].values[0]
    

    return flag_name





#A call to save changes to a flag, this will take in the change and a UUID
#One call for flag name
def update_flag_name(original_flag_name, new_flag_name):
    #query to update existing flag_name with new flag_name

    #cursor.execute("""UPDATE TABLE SET FLAG_NAME_COL = :new_flag_name
    #WHERE FLAG_NAME_COL = :original_flag_name""",
    #new_flag_name=new_flag_name,
    #orginal_flag_name=original_flag_name)

    #cursor.execute("""SELECT PRIMARY_KEY_COL FROM TALBE WHERE FLAG_NAME_COL = :new_flag_name""",
    #new_flag_name=new_flag_name)

    #df_primary_key = df_from_cursor.cursor()

    #return df_primary_key['PRIMARY_KEY_COL'].values[0]

    return None

#Another call for flag logic
def update_flag_logic(primary_key, new_flag_logic):

    #cursor.execute("""UPDATE TABLE SET FLAG_LOGIC_COL = :new_flag_logic
    #WHERE FLAG_PRIMARY_ID = :primary_key""",
    #primary_key=primary_key,
    #new_flag_logic=new_flag_logic)
    return None



#A call to delete a flag provided a UUID, return true/false
def delete_flag(primary_key):
    #check if primary_key exists in db
    #cursor.execute("""SELECT COL_PRIMARY_KEY, COL_FLAG_NAME
    #FROM TABLE WHERE COL_PRIMARY_KEY = :primary_key""",
    #primary_key=primary_key)

    #df_pimrary_key = df_from_cursor.cursor()

    #if df_primary_key.empty:
        #return False
    #else
        #cursor.execute("""DELETE * FROM TABLE WHERE COL_PRIMARY_KEY = :col_primary_key""",
        #col_primary_key=primary_key)
        #return True

    return True


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