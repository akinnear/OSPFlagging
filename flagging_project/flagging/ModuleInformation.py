class ModuleInformation:

    def __init__(self, name, asname=None):
        self.name = name
        if asname:
            self.asname = asname
        else:
            self.asname = name

    # object representation
    def __repr__(self):
        return f"ModuleInformation({self.name}, {self.asname})"

    def __str__(self):
        return f"{self.name}, {self.asname}"

    # object equality
    def __eq__(self, other):
        return self.name == other.name and self.asname == other.asname

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.asname))