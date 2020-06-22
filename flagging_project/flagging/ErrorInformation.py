class ErrorInformation:

    def __init__(self, msg, text, lineno, offset):
        self.msg = msg
        self.text = text
        self.lineno = lineno
        self.offset = offset


    # object representation
    def __repr__(self):
        return f"ErrorInformation({self.msg}, {self.text}, {self.lineno}, {self.offset})"

    def __str__(self):
        return f"{self.msg}, {self.text}, {self.lineno}, {self.offset}"

    # object equality
    def __eq__(self, other):
        return self.msg == other.msg \
               and self.text == other.text \
               and self.lineno == other.lineno \
               and self.offset == other.offset

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.msg, self.text, self.lineno, self.offset))