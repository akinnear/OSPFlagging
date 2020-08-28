class FlagErrorInformation:

    def __init__(self, flag, err_info, cl):
        self.flag = flag
        self.err_info = err_info
        self.cl = cl



    # object representation
    def __repr__(self):
        return f"FlagErrorInformation({self.flag}, {self.err_info}, {self.cl})"


    def __str__(self):
        return f"{self.flag}, {self.err_info}, {self.cl}"

    # object equality
    def __eq__(self, other):
        return self.flag == other.flag \
               and self.err_info == other.err_info \
               and self.cl == other.cl

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.flag, self.err_info, self.cl))
