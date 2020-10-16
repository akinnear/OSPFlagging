class FlaggingSchemaInformation:


    def __init__(self, valid, message, name=None, uuid=None, data=None):
        self.valid = valid
        self.message = message
        self.name = name
        self.uuid = uuid
        self.data = data



    # object representation
    def __repr__(self):
        return f"FlaggingSchemaInformation({self.valid}, {self.message}, {self.name}, {self.uuid}, {self.data})"

    def __str__(self):
        return f"{self.valid}, {self.message}, {self.name}, {self.uuid}", {self.data}

    # object equality
    def __eq__(self, other):
        return self.valid == other.valid \
               and self.message == other.message \
               and self.name == other.name \
               and self.uuid == other.uuid \
               and self.data == other.data

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.valid, self.message, self.name, self.uuid, self.data))