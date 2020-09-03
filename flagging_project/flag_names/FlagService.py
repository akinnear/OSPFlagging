


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