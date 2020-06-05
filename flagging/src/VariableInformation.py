class VariableInformation:

    def __init__(self, name, parent=None):
        self.name = name
        if parent:
            self.parent = parent
            self.parent.child = self
        else:
            self.parent = None
        self.child = None

    # object representation
    def __repr__(self):
        return f"VariableInformation({self.name}, {self.parent})"

    def __str__(self):
        pre = ""
        post = ""
        if self.parent:
            pre = ""
            a_parent = self.parent
            while a_parent:
                pre = f"{a_parent.name}.{pre}"
                a_parent = a_parent.parent
            pre = f"[{pre}]"
        if self.child:
            a_child = self.child
            while a_child:
                post += f".{a_child.name}"
                a_child = a_child.child
        return f"{pre}{self.name}{post}"

    # object equality
    def __eq__(self, other):
        return self.name == other.name and \
               self.parent is other.parent and \
               self.child is other.child

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.child))
