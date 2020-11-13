from front_end.ReferencedFlag import ReferencedFlag, _convert_RF_to_TRF
from bson.objectid import ObjectId

def test_object_equality():
    flag_name = "Flag5"
    flag_group_id = ObjectId("111111111111111111111111")
    rf_1 = ReferencedFlag(flag_name=flag_name, flag_group_id=flag_group_id)
    rf_2 = ReferencedFlag(flag_name=flag_name, flag_group_id=flag_group_id)
    assert rf_1 == rf_2
