class ErrorInformation:

    def __init__(self, cl, msg, text):
        self.cl = cl
        self.msg = msg
        self.text = text



    # object representation
    def __repr__(self):
        return f"ErrorInformation({self.cl}, {self.msg}, {self.text})"

    def __str__(self):
        return f"{self.cl}, {self.msg}, {self.text}"

    # object equality
    def __eq__(self, other):
        return self.cl == other.cl \
               and self.msg == other.msg \
               and self.text == other.text

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.cl, self.msg, self.text))