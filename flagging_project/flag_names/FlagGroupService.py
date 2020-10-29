from bson.objectid import ObjectId

def pull_flag_group_ids(*args, **kwargs):
    # method to pull flag names from api endpiont or internal db query

    api_endpoint = kwargs.get("api_endpoint")

    dummy_flag_group_ids = kwargs.get("dummy_flag_group_ids", None)

    if dummy_flag_group_ids:
       pass
    else:
        flag_group_1a_object_id = ObjectId("B11111111111111111111101")
        flag_group_2b_object_id = ObjectId("B11111111111111111111102")
        flag_group_3c_object_id = ObjectId("B11111111111111111111103")
        flag_group_4d_object_id = ObjectId("B11111111111111111111104")
        flag_group_5e_object_id = ObjectId("B11111111111111111111105")
        flag_group_6f_object_id = ObjectId("B11111111111111111111106")
        flag_group_7g_object_id = ObjectId("B11111111111111111111107")
        flag_group_8h_object_id = ObjectId("B11111111111111111111108")
        flag_group_9i_object_id = ObjectId("B11111111111111111111109")
        flag_group_10j_object_id = ObjectId("B11111111111111111111110")
        flag_group_11k_object_id = ObjectId("B11111111111111111111111")
        flag_group_12l_object_id = ObjectId("B11111111111111111111112")

        dummy_flag_group_ids = [flag_group_1a_object_id, flag_group_2b_object_id, flag_group_3c_object_id,
                                flag_group_4d_object_id, flag_group_5e_object_id, flag_group_6f_object_id,
                                flag_group_7g_object_id, flag_group_8h_object_id, flag_group_9i_object_id,
                                flag_group_10j_object_id, flag_group_11k_object_id, flag_group_12l_object_id]
        return dummy_flag_group_ids


def pull_flag_group_names(*args, **kwargs):
    # method to pull flag names from api endpiont or internal db query

    api_endpoint = kwargs.get("api_endpoint")

    dummy_flag_group_names = kwargs.get("dummy_flag_group_names", None)

    if dummy_flag_group_names:
        return dummy_flag_group_names