from pymongo import MongoClient


def add_flag():
    with MongoClient('localhost', 27017) as client:
        db = client.flagging_test
        flagging = db.flagging
        flag_id = flagging.insert_one({'name': 'Flag Name', 'Type': 123}).inserted_id

        flag = flagging.find_one({"_id": flag_id})
        print(flag)


add_flag()
