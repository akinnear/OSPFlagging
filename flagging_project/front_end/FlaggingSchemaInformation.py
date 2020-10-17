class FlaggingSchemaInformation:


    def __init__(self, valid, message, name=None, uuid=None, flag_logic_information=None):
        self.valid = valid
        self.message = message
        self.name = name
        self.uuid = uuid
        self.flag_logic_information = flag_logic_information



    # object representation
    def __repr__(self):
        return f"FlaggingSchemaInformation({self.valid}, {self.message}, {self.name}, {self.uuid}, {self.flag_logic_information})"

    def __str__(self):
        return f"{self.valid}, {self.message}, {self.name}, {self.uuid}", {self.flag_logic_information}

    # object equality
    def __eq__(self, other):
        return self.valid == other.valid \
               and self.message == other.message \
               and self.name == other.name \
               and self.uuid == other.uuid \
               and self.flag_logic_information == other.flag_logic_information

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.valid, self.message, self.name, self.uuid, self.flag_logic_information))