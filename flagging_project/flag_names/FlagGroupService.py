
def pull_flag_group_names(*args, **kwargs):
    # method to pull flag names from api endpiont or internal db query

    api_endpoint = kwargs.get("api_endpoint")

    dummy_flag_group_names = kwargs.get("dummy_flag_group_names", None)

    if dummy_flag_group_names:
        return dummy_flag_group_names