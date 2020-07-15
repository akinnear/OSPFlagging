from flagging.FlaggingValidationMyPy import _validate_returns_boolean
from flagging.ErrorInformation import ErrorInformation
from flagging.FlaggingNodeVisitor import FlagFeederNodeVisitor
from flagging.FlagLogicInformation import FlagLogicInformation
import ast


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
