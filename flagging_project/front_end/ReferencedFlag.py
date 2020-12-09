class ReferencedFlag:
    def __init__(self, flag_name, flag_group_id):
        self.flag_name = flag_name
        self.flag_group_id = flag_group_id

    # object representation
    def __repr__(self):
        return f"ReferencedFlag({self.flag_name}, {self.flag_group_id})"

    def __str__(self):
        return f"{self.flag_name}, {self.flag_group_id}"

    # object equality
    def __eq__(self, other):
        return self.flag_name == other.flag_name \
               and self.flag_group_id == other.flag_group_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.flag_name, self.flag_group_id))

def _convert_RF_to_TRF(RF_list):
    rf_list = []
    for x in RF_list:
        rf_list.append({"FLAG_NAME": x.flag_name,
                        "FLAG_GROUP_ID": x.flag_group_id})
    return rf_list
