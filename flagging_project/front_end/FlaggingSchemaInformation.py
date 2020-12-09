class FlaggingSchemaInformation:


    def __init__(self, valid=False, simple_message="", message="", name=None, uuid=None, logic=None):
        self.valid = valid
        self.simple_message = simple_message
        self.message = message
        self.name = name
        self.uuid = uuid
        self.logic = logic



    # object representation
    def __repr__(self):
        return f"FlaggingSchemaInformation({self.valid}, {self.simple_message}, {self.message}, {self.name}, " \
               f"{self.uuid}, {self.logic})"

    def __str__(self):
        return f"{self.valid}, {self.simple_message}, {self.message}, " \
               f"{self.name}, {self.uuid}", {self.logic}

    # object equality
    def __eq__(self, other):
        return self.valid == other.valid \
               and self.simple_message == other.simple_message \
               and self.message == other.message \
               and self.name == other.name \
               and self.uuid == other.uuid \
               and self.logic == other.logic

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.valid, self.simple_message, self.message,
                     self.name, self.uuid, self.logic))