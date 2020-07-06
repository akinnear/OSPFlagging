from flagging.FlaggingValidationMyPy import _validate_returns_boolean
from flagging.ErrorInformation import ErrorInformation
from flagging.FlaggingNodeVisitor import FlagFeederNodeVisitor
import ast


class FlagLogicInformation:
    def __init__(self, used_variables=None, assigned_variables=None, referenced_functions=None,
                 defined_functions=None, defined_classes=None, referenced_modules=None,
                 referenced_flags=None, return_points=None, errors=None, validation_results=None):
        self.used_variables = used_variables if used_variables else {}
        self.assigned_variables = assigned_variables if assigned_variables else {}
        self.referenced_functions = referenced_functions if referenced_functions else {}
        self.defined_functions = defined_functions if defined_functions else {}
        self.defined_classes = defined_classes if defined_classes else {}
        self.referenced_modules = referenced_modules if referenced_modules else {}
        self.referenced_flags = referenced_flags if referenced_flags else {}
        self.return_points = return_points if return_points else set()
        self.errors = errors if errors else []
        self.validation_results = validation_results


def determine_variables(logic, flag_feeders=None):
    nv = FlagFeederNodeVisitor()

    # Determine if we have a single line
    single_line_statement = len(logic.strip().splitlines()) == 1

    logic_copy = logic

    invalid_check = True
    while(invalid_check):
        try:
            root = ast.parse(logic_copy)
            nv.visit(root)
            invalid_check = False
        except SyntaxError as se:
            nv.errors.append(ErrorInformation(se.msg, se.text, se.lineno, se.offset))
            logic_copy = logic_copy.replace(se.text.strip(), "##ErRoR##")

    type_return_results = _validate_returns_boolean(logic_copy, single_line_statement, nv.return_points,
                                                    nv, flag_feeders if flag_feeders else {})
    print(type_return_results)
    return FlagLogicInformation(used_variables=nv.used_variables,
                                assigned_variables=nv.assigned_variables,
                                referenced_functions=nv.referenced_functions,
                                defined_functions=nv.defined_functions,
                                defined_classes=nv.defined_classes,
                                referenced_modules=nv.referenced_modules,
                                referenced_flags=nv.referenced_flags,
                                return_points=nv.return_points,
                                errors=nv.errors,
                                validation_results=type_return_results)
