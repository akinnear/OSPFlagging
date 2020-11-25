from flagging.FlagLogicInformation import FlagLogicInformation
from flagging.FlaggingNodeVisitor import CodeLocation
from flagging.FlagErrorInformation import FlagErrorInformation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
import json

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
                elif key == "referenced_modules":
                    dictionary_data["name"] = name.name
                    dictionary_data["as_name"] = name.asname
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

def _convert_TFLI_to_FLI(tfli_dict, og_FLI):

    def iterate_transfer_data(tfli_dict, param_name):
        '''

        :param tfli_dict: transfer flag logc dictionary
        :param param_name: parameter name, e.g. "used_variables", "referenced_functions", etc.
        :return:
        '''
        if param_name in ["used_variables", "assigned_variables", "referenced_functions",
                          "referenced_modules", "defined_functions", "defined_classes",
                          "referenced_flags", "used_lambdas"]:
            fli_param = {}
            for my_dict in tfli_dict[param_name]:
                # variable information key
                name_key = my_dict["name"]
                if param_name == "referenced_modules":
                    as_name_key = my_dict["as_name"]
                    fli_key = ModuleInformation(name=name_key, asname=as_name_key)
                elif param_name == "referenced_flags":
                    fli_key = name_key
                elif param_name == "used_lambdas":
                    fli_key = "LAMBDA"
                else:
                    fli_key = VariableInformation(name=name_key)
                fli_param[fli_key] = set()
                # set of code location value
                for code_loc in my_dict["locations"]:
                    cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
                    fli_param[fli_key].add(cl)
        elif param_name == "flag_logic":
            fli_param = tfli_dict[param_name][0]["logic"]
        elif param_name == "return_points":
            for my_dict in tfli_dict[param_name]:
                fli_param = set()
                for code_loc in my_dict["locations"]:
                    cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
                    fli_param.add(cl)
        return fli_param

    used_variables = iterate_transfer_data(tfli_dict, "used_variables")
    assigned_variables = iterate_transfer_data(tfli_dict, "assigned_variables")
    referenced_functions = iterate_transfer_data(tfli_dict, "referenced_functions")
    defined_functions = iterate_transfer_data(tfli_dict, "defined_functions")
    defined_classes = iterate_transfer_data(tfli_dict, "defined_classes")
    referenced_modules = iterate_transfer_data(tfli_dict, "referenced_modules")
    referenced_flags = iterate_transfer_data(tfli_dict, "referenced_flags")
    flag_logic = iterate_transfer_data(tfli_dict, "flag_logic")
    return_points = iterate_transfer_data(tfli_dict, "return_points")
    used_lambdas = iterate_transfer_data(tfli_dict, "used_lambdas")
    #errors


    flag_logic_info = FlagLogicInformation(used_variables=used_variables,
                                           assigned_variables=assigned_variables,
                                           referenced_functions=referenced_functions,
                                           defined_functions=defined_functions,
                                           defined_classes=defined_classes,
                                           referenced_modules=referenced_modules,
                                           referenced_flags=referenced_flags,
                                           return_points=return_points,
                                           flag_logic=flag_logic,
                                           used_lambdas=used_lambdas)

    return flag_logic_info


    # for dict in TFLI["used_variables"]:
    #     #variable information key
    #     fli_key = dict["name"]
    #     FLI.used_variables.set_default(fli_key, set())
    #     #set of code location value
    #     for code_loc in dict["locations"]:
    #         cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
    #         FLI.used_variables[fli_key].add(cl)

    # for dict in TFLI["assigned_variables"]:
    #     #variable information key
    #     fli_key = dict["name"]
    #     FLI.used_variables.set_default(fli_key, set())
    #     #set of code location value
    #     for code_loc in dict["locations"]:
    #         cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
    #         FLI.used_variables[fli_key].add(cl)
    #
    # for dict in TFLI["referenced_functions"]:
    #     #variable information key
    #     fli_key = dict["name"]
    #     FLI.used_variables.set_default(fli_key, set())
    #     #set of code location value
    #     for code_loc in dict["locations"]:
    #         cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
    #         FLI.used_variables[fli_key].add(cl)
    #
    # for dict in TFLI["defined_functions"]:
    #     # variable information key
    #     fli_key = dict["name"]
    #     FLI.used_variables.set_default(fli_key, set())
    #     # set of code location value
    #     for code_loc in dict["locations"]:
    #         cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
    #         FLI.used_variables[fli_key].add(cl)
    #
    # for dict in TFLI["defined_classes"]:
    #     # variable information key
    #     fli_key = dict["name"]
    #     FLI.used_variables.set_default(fli_key, set())
    #     # set of code location value
    #     for code_loc in dict["locations"]:
    #         cl = CodeLocation(line_number=code_loc["line_number"], column_offset=code_loc["column_offset"])
    #         FLI.used_variables[fli_key].add(cl)


    print("hello")

















