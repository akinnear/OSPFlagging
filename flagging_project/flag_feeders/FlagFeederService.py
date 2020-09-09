#import

#function/method declartion

#pull flag feeders via GET api call to endpoint or local storage location query
def pull_flag_feeders(*args, **kwargs):
    #TODO
    # valid data pull
    api_endpoint = kwargs.get("api_endpoint")
    flag_feeders = dict()

    dummy_flag_feeders = kwargs.get("dummy_flag_feeders", None)
    if dummy_flag_feeders:
        return dummy_flag_feeders

    return flag_feeders


