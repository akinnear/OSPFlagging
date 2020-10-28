from flagging.FlaggingNodeVisitor import CodeLocation

class TransferFlagLogicInformation:
    def __init__(self, used_variables=None, assigned_variables=None, referenced_functions=None,
                 defined_functions=None, defined_classes=None, referenced_modules=None,
                 referenced_flags=None, return_points=None, used_lambdas=None, flag_logic=None,
                 errors=None):
        self.used_variables = used_variables if used_variables else []
        self.assigned_variables = assigned_variables if assigned_variables else []
        self.referenced_functions = referenced_functions if referenced_functions else []
        self.defined_functions = defined_functions if defined_functions else []
        self.defined_classes = defined_classes if defined_classes else []
        self.referenced_modules = referenced_modules if referenced_modules else []
        self.referenced_flags = referenced_flags if referenced_flags else []
        self.return_points = return_points if return_points else []
        self.used_lambdas = used_lambdas if used_lambdas else []
        self.flag_logic = flag_logic if flag_logic else []
        self.errors = errors if errors else []

def _convert_FLI_to_TFLI(FLI):
    TFLI = TransferFlagLogicInformation()

    def iterate_object_data(flag_logic, transfer_object, key):
        if key == "flag_logic":
            dictionary_data = dict()
            dictionary_data["name"] = key
            dictionary_data["logic"] = flag_logic
            transfer_object.append(dictionary_data)
        elif key == "return_points":
            dictionary_data = dict()
            dictionary_data["name"] = key
            dictionary_data["locations"] = []
            for cl in flag_logic:
                dictionary_data["locations"].append(
                    dict({"line_number": cl.line_number, "column_offset": cl.column_offset}))
            transfer_object.append(dictionary_data)
        elif key == "errors":
            for ei in flag_logic:
                dictionary_data = dict()
                dictionary_data["name"] = "errors"
                dictionary_data["locations"] = []
                dictionary_data["text"] = ei.text
                dictionary_data["msg"] = ei.msg
                dictionary_data["locations"].append(dict({"line_number": ei.cl.line_number,
                                                          "column_offset": ei.cl.column_offset}))
                transfer_object.append(dictionary_data)
        else:
            for name, cls in flag_logic.items():
                dictionary_data = dict()
                if key in ["referenced_flags", "used_lambdas"]:
                    dictionary_data["name"] = name
                else:
                    dictionary_data["name"] = name.name
                dictionary_data["locations"] = []
                for cl in cls:
                    dictionary_data["locations"].append(dict({"line_number": cl.line_number, "column_offset": cl.column_offset}))
                transfer_object.append(dictionary_data)

    def make_dict(TFLI):
        tfli_dict = dict()
        for k, v in TFLI.__dict__.items():
            tfli_dict[k] = v
        return tfli_dict


    iterate_object_data(FLI.used_variables, TFLI.used_variables, "used_variables")
    iterate_object_data(FLI.assigned_variables, TFLI.assigned_variables, "assigned_variables")
    iterate_object_data(FLI.referenced_functions, TFLI.referenced_functions, "referenced_functions")
    iterate_object_data(FLI.defined_functions, TFLI.defined_functions, "defined_functions")
    iterate_object_data(FLI.defined_classes, TFLI.defined_classes, "defined_classes")
    iterate_object_data(FLI.referenced_modules, TFLI.referenced_modules, "referenced_modules")
    iterate_object_data(FLI.referenced_flags, TFLI.referenced_flags, "referenced_flags")
    iterate_object_data(FLI.return_points, TFLI.return_points, "return_points")
    iterate_object_data(FLI.used_lambdas, TFLI.used_lambdas, "used_lambdas")
    iterate_object_data(FLI.flag_logic, TFLI.flag_logic, "flag_logic")
    iterate_object_data(FLI.errors, TFLI.errors, "errors")

    tfli_dict = make_dict(TFLI)

    return tfli_dict







