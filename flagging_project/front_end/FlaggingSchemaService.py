#imports
import pandas as pd

from flagging.FlaggingNodeVisitor import determine_variables
from flag_feeders.FlagFeederService import pull_flag_feeders
from flagging.FlaggingValidation import validate_flag_logic_information
from front_end.FlaggingSchemaInformation import FlaggingSchemaInformation

#TODO
# interface design, html5 + bootstrap4

#A call to validate logic, this will return only warning and errors
# with enough information to understand the problem and location.
# TO perform validation please use the interface created in #67 for flag feeders.

def validate_logic(flag_name:str, user_logic: str):
    #get flag feeders
    flag_feeders = pull_flag_feeders("dummy_text_endpoint")

    #perform full validation on user_logic via nodevisitor, mypy, and validation

    #nodeivisitor on user_logic
    #determine variables form FlaggingNodeVisitor
    flag_logic_information = determine_variables(user_logic)

    #mypy validation is part of full validation method, do not need explicit mypy validation call


    #need flag_dependiceis from api call or direct query
    flag_dependencies = get_flag_dependencies()

    #validation
    validation_result = validate_flag_logic_information(flag_name, flag_feeders, flag_dependencies, flag_logic_information)

    #return errors and warning information
    return validation_result


#A call to get flag dependencies
def get_flag_dependencies():
    #api endpoint of db endpoint
    #hard code dependencies for now
    flag_dependencies = {"Flag1": {"Flag8"},
     "Flag2": {"Flag3"},
     "Flag3": {"Flag4"},
     "Flag4": {"Flag5"},
     "Flag5": {"Flag6"},
     "Flag6": {"Flag7"},
     "Flag7": {"Flag8"},
     "Flag8": {}}
    return flag_dependencies

#A call to create a flag given a name and logic, this will return a UUID,
# name cannot be empty if so error

def create_flag(flag_name: str, flag_logic: str):
    #store flag name and flag logic in db

    if flag_name is None:
        # return error message, no flag name specified
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag name not specified")

    else:

        # write query, with new primary key
        # cursor.execute("""INSERT into TABLE FLAG_NAME_COL= :flag_name, FLAG_LOGIC_COL= :flag_logic""",
        # flag_name=flag_name,
        # flag_logic=flag_logic)

        # cursor.execute("""SELECT PRIMARY_KEY_COL FROM TABLE
        # WHERE FLAG_NAME_COL = :flag_name
        # AND FLAG_LOGIC_COL = :flag_logic""",
        # flag_name=flag_name,
        # flag_logic=flag_logic)

        # df_new_flag = df_from_cursor.cursor()
        # return df_new_flag['PRIMARY_KEY_COL'].values[0]

        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="new flag created",
                                                       name=flag_name,
                                                       uuid=flag_name + "_primary_key_id")
    return flag_schema_object



#A call to save changes to a flag, this will take in the change and a UUID
#One call for flag name
def update_flag_name(original_flag_name: str, new_flag_name: str):

    #query to get existing flag names

    existing_flag_names = pd.DataFrame()

    if original_flag_name in existing_flag_names and original_flag_name is not None and new_flag_name is not None:
        # query to update existing flag_name with new flag_name

        # cursor.execute("""UPDATE TABLE SET FLAG_NAME_COL = :new_flag_name
        # WHERE FLAG_NAME_COL = :original_flag_name""",
        # new_flag_name=new_flag_name,
        # orginal_flag_name=original_flag_name)

        # cursor.execute("""SELECT PRIMARY_KEY_COL FROM TALBE WHERE FLAG_NAME_COL = :new_flag_name""",
        # new_flag_name=new_flag_name)

        # df_primary_key = df_from_cursor.cursor()

        # return df_primary_key['PRIMARY_KEY_COL'].values[0]
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="original flag name " + original_flag_name + " updated to " + new_flag_name,
                                                       name=new_flag_name,
                                                       uuid=new_flag_name + "_primary_key_id")
    else:
        if original_flag_name not in existing_flag_names:
            #return error to user that original_flag_name does not exist
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="original flag name: " + original_flag_name + " does not exist")


        if original_flag_name is None:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify name of original flag")


        if new_flag_name is None:
            #return error to user that original_flag_name and new_flag_name have to be specified
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="user must specify new flag name")
    return flag_schema_object

#Another call for flag logic
def update_flag_logic(primary_key, new_flag_logic: str):

    #check if primary_key is contained in existing flags
    #query to get existing flags or existing UUID, whichever is passed by user
    existing_flags = []

    if primary_key not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="could not identify existing flag: " + primary_key)

    if primary_key in existing_flags:

        #run validation on new_flag_logic
        validation_results = validate_logic(primary_key, new_flag_logic)

        if validation_results.errors() is None and validation_results.mypy_errors is None:

            #query to update existing flag logic

            flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                           message="logic for flag has been updated",
                                                           name=primary_key,
                                                           uuid=primary_key + "primary_key_id")
        else:
            flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                           message="error in flag logic")


    return flag_schema_object



#A call to delete a flag provided a UUID, return true/false
def delete_flag(primary_key):
    #check if primary_key exists in db

    existing_flags = []
    if primary_key not in existing_flags:
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="flag name specified does not exist")
    else:
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

        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="flag " + primary_key + " has been deleted",
                                                       name=primary_key,
                                                       uuid=primary_key + "_primary_key_id")
    return flag_schema_object


#A call to create a named flag group, returns a UUID, name cannot be empty if so error
def create_flag_group(flag_group_name: str):
    if flag_group_name is None or flag_group_name.replace(" ", "") == "":
        flag_schema_object = FlaggingSchemaInformation(valid=False,
                                                       message="unique flag group name must be created")
    else:


        #create flag group with unique Primary_key
        #insert statment here
        flag_schema_object = FlaggingSchemaInformation(valid=True,
                                                       message="Unique flag group " + flag_group_name + " created",
                                                       name=flag_group_name,
                                                       uuid=flag_group_name + "_primary_key_id")
    return flag_schema_object


#A call to delete a flag group provided a UUID, return true/false
def delete_flag_group(flag_group_name: str):
    #check that flag group exists in db
    #query to get flag group UUID via flag_group_name passed
    #if flag_group_name exists in db, get UUID
        #delete row via delete statement using UUID in WHERE condition
        #return true
    #else
        #flag_group_name does not exist, can not delete
        #return false

    return True


#Flag Groups Updating, within these calls cyclic and existing flag name checks need to occur.
# They should both return validation information such describing possible errors
# in the group such as missing and cyclic flags

#A call to add flags to a group provided a UUID for the group and UUIDs for the flags to add
def add_flag_to_flag_group(flag_group_name: str, new_flags: []):
    #for each new_flag in new_flags, check to see if flag exists already
    #if flag does not exist, call add method

    missing_flags = []
    #create default flag_logic_dictionary
    new_flag_logic = {}
    flag_errors = []

    #check that flag_group_name exists
    #query db for flag group name
    #if flag group name does not exist, return message to user

    for new_flag in new_flags:
        #query to get UUID for each new_flag
        #if UUID does NOT exist:
            #missing_flags.append(new_flag)
        if len(missing_flags) != 0:
            #return error message that flag must be created first before added to flag group
            pass
        else:
            #run validation checks on flag and flag_logic
            #query db to get flag logic for each flag_name
            # query to get flag logic
            flag_logic = "flag_logic"
            new_flag_logic.setdefault(new_flag, flag_logic)

            #run validation on flag_logic
            flag_validation_result = validate_logic(new_flag, flag_logic)

            #if there are any errors, do not update flag_group
            if flag_validation_result.errors():
                flag_errors.append(flag_validation_result.errors())
            if flag_validation_result.mypy_errors():
                flag_errors.append(flag_validation_result.mypy_errors())

            if len(flag_errors) != 0:
                #errors in flags, do not update existing flag group
                pass
            else:
                #update existing flag group with UUID for each flag
                pass
                #return new flag_group UUID
                return None






#A call to remove flags from a group provided a UUID for the group and UUIDs for the flags to remove
def remove_flag_from_flag_group(flag_group_name: str, del_flags: []):
    #check that flag_group_name exists
    #query db for flag_group_name
    #if flag_group_name does not exist
    #return error message to user

    #flag group name does exist
    #for ech flag in del_flags, make sure flag exists in passed flag_group_name

    #only attempt to delete flags that exist in flag_group_name
    for del_flag in del_flags:
        #cursor.execute("""SELECT PRIMARY_KEY_ID, FLAG_GROUP_NAME, FLAGS
        #FROM TABLE WHERE :del_flag IN FLAGS""",
        #del_flag=del_flag)

        #df_del_flag = df_from_cursor.cursor()

        #if df_del_flag['PRIMARY_KEY_ID'].values[0]
            #run query to remove del flag from FLAG
            #query depends on database structure

        #return UUID of flag_group, along with UUID of flags current in flag group
        #pass information to front end to user
        pass
    return None





#A call to duplicate a flag provided a new name and UUID
def duplicate_flag(og_flag_name:str, new_flag_name: str):
    #query to identify entry in db via og_flag_name
    #make sure original flag already exists, otherwise return error message to user
    #cursor.execute("""SELECT * FROM TABLE WHERE FLAG_NAME = :og_flag_name""",
    #og_flag_name=og_flag_name)

    #df_og_flag = df_from_cursor.cursor()

    #if df_og_flag:
        #query to insert copy with new name
        #cursor.execute("""INSERT INTO TABLE(PRIMARY_KEY, :new_flag_name, TABLE.EVERYTHING_ELSE)
        #SELECT (TABLE.EVERYTHING_ELSE FROM TABLE WHERE FLAG_NAME = :og_flag_name""",
        #og_flag_name=og_flag_name, new_flag_name=new_flag_name)

        #return new primary key to user for duplicated flag

    #else:
        #return error message to user that og_flag_name does not already exist

    return None


#A call to duplicate a flag group provided a new name and UUID
def duplicate_flag_group(og_flag_group_name: str, new_flag_group_name:str):
    #query to identify entry in db via og_flag_group_name

    #make sure og_flag_group_name already exists as flag_group
    #cursor.execute(""""SELECT * FROM TABLE WHERE FLAG_GROUP_NAME = :og_flag_group_name""",
    #og_flag_group_name=og_flag_group_name)

    #df_og_flag_group = df_from_cursor.cursor()

    #if df_of_flag_group:
        #query to insert copy with new name
        #cursor.execute("""INSERT INTO TABLE(PRIMARY_KEY, :new_flag_group_name, TABLE.EVERYTING_ELSE)
        #SELECT (TABLE.EVERYTHING_ELSE FROM TABLE WHERE FLAG_GROUP_NAME = :og_flag_group_name""",
        #og_flag_group_name=og_flag_group_name, new_flag_group_name=new_flag_group_name)

        #return new primary key to user for duplicated flag group

    #else:
        #return error message to user that og_flag_group does not exist


    return None

#TODO,
# write new tests in tests module