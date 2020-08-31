#import

#function/method declartion

#pull flag feeders via GET api call to endpoint or local storage location query
def pull_flag_feeders (*args, **kwargs):
    #TODO
    # valid data pull
    api_endpoint = kwargs.get("api_endpoint", "mock_api_endpoint")

    flag_feeders = {"FF1": str, "FF2": int, "FF3": bool, "FF4": float}
    return flag_feeders


