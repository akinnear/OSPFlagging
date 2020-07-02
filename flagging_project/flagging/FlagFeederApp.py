from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation
from flagging.ErrorInformation import ErrorInformation
from mypy import api
import ast
import contextlib
from ast import NodeVisitor
import os




def _print_helper(node):
    if isinstance(node, ast.Name):
        return f"Name({node.id})"
    elif isinstance(node, ast.Attribute):
        return f"Attribute({node.attr})"
    elif isinstance(node, ast.ExceptHandler):
        return f"ExceptHandler({node.type.id})"
    elif isinstance(node, ast.ClassDef):
        return f"ClassDef({node.name})"
    elif isinstance(node, ast.FunctionDef):
        return f"FunctionDef({node.name})"
    return type(node).__name__

def code_location_helper(var_data, key, cl):
    if isinstance(var_data, dict):
        if key in var_data.keys():
            var_data[key].add(cl)
            print(str(key) + ": " + str(cl))
            print(var_data)
        else:
            #creat new key
            var_data.setdefault(key, set())
            var_data[key].add(cl)
            print(str(key) + ": " + str(cl))
            print(var_data)
    elif isinstance(var_data, set) and key == "return point":
        var_data.add(cl)


class CodeLocation:
    ## constructor
    def __init__(self, line_number=None, column_offset=None):
        self.line_number = line_number
        self.column_offset = column_offset

    ## object representation
    def __repr__(self):
        return f"CodeLocation({self.line_number}, {self.column_offset})"

    ## object equality
    def __eq__(self, other):
        return self.line_number == other.line_number and self.column_offset == other.column_offset

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.line_number, self.column_offset))


class FlagFeederNodeVisitor(NodeVisitor):
    def __init__(self):
        self.used_variables = dict()
        self.assigned_variables = dict()
        self.referenced_functions = dict()
        self.defined_functions = dict()
        self.referenced_modules = dict()
        self.defined_classes = dict()
        self.referenced_flags = dict()
        self.return_points = set()
        self.errors = []
        self._stack = []
        self._attribute_stack = []
        self.validation_results = None

    @contextlib.contextmanager
    def handle_node_stack(self, node):
        print("NODE:"+f"{_print_helper(node)} Stack[{', '.join(map(lambda x: _print_helper(x), self._stack))}]")

        self._stack.append(node)
        # print("-PUSH->")
        try:
            yield node
            self._stack.pop()
            # print("**POP**")
        except:
            raise

    def _create_full_name(self, node):
        if isinstance(node, ast.Attribute):
            return f"{self._create_full_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.arg):
            return node.arg
        else:
            raise ValueError(f"Do not know how to handle a node of type {type(node)}")

    def _call_args_to_names(self, args):
        if isinstance(args, ast.arguments):
            args = args.args
        return set(list(map(lambda node: self._create_full_name(node),
                            filter(
                                lambda y: isinstance(y, ast.Name) or
                                          isinstance(y, ast.Attribute) or
                                          isinstance(y, ast.arg),
                                args))))

    def visit_FunctionDef(self, node):
        with self.handle_node_stack(node):
            code_location_helper(self.defined_functions, VariableInformation(node.name),
                                                          CodeLocation(line_number=node.lineno,
                                                                       column_offset=node.col_offset+4))
            for arg in node.args.args:
                code_location_helper(self.assigned_variables, VariableInformation(arg.arg),
                                                               CodeLocation(line_number=arg.lineno,
                                                                            column_offset=arg.col_offset))
            for body_line in node.body:
                ast.NodeVisitor.generic_visit(self, body_line)
            ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        with self.handle_node_stack(node):
            offset = len("import ")
            for name in node.names:
                code_location_helper(self.referenced_modules, ModuleInformation(name.name, name.asname),
                                     CodeLocation(line_number=node.lineno,
                                                  column_offset=node.col_offset+offset))

                if name.asname:
                    offset = offset + len(name.asname) + len (" as ")
                offset = offset + len(name.name) + len(", ")

            ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        with self.handle_node_stack(node):
            for name in node.names:
                code_location_helper(self.referenced_modules, ModuleInformation(node.module),
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset + len("from ")))
            ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self, node):
        with self.handle_node_stack(node):
            name = node.id
            parent = self._stack[-2]
            if isinstance(parent, ast.Assign):
                code_location_helper(self.assigned_variables, VariableInformation(name),
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
            elif isinstance(parent, ast.FunctionDef):
                code_location_helper(self.assigned_variables, VariableInformation(name),
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
            elif isinstance(parent, ast.Attribute):
                before_attributes = self._stack[-1*(len(self._attribute_stack) + 2)]
                attributes = self._attribute_stack.copy()
                attributes.reverse()


                defined_functions_str = []
                for item in self.defined_functions:
                    defined_functions_str.append(item.name)
                if isinstance(before_attributes, ast.FunctionDef) and before_attributes.name in defined_functions_str:
                    before_attributes = before_attributes.body[0]

                if isinstance(before_attributes, ast.Call) or isinstance(before_attributes, ast.FunctionDef):
                    function_name = attributes[-1].attr
                    post_variable_name = ".".join(map(lambda attr_node: attr_node.attr, attributes[:-1]))
                    variable_name = name
                    if post_variable_name:
                        variable_name += f".{post_variable_name}"
                    full_name = f"{variable_name}.{function_name}"


                    variable_names = [attribute.attr for attribute in attributes]
                    variable_names.insert(0, name)
                    variable_information = VariableInformation.create_var(variable_names)

                    pre_variable_name = ".".join(variable_names[:-1])

                    possible_args = self._call_args_to_names(before_attributes.args)

                    if full_name == "f.get":
                        flag_name = self._stack[-4].value.args[0].s
                        code_location_helper(self.referenced_flags, flag_name,
                                             CodeLocation(line_number=node.lineno,
                                                          column_offset=self._stack[-4].value.args[0].col_offset + 1))

                    if full_name in possible_args:
                        code_location_helper(self.used_variables, variable_information,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))

                    else:
                        referenced_modules_str = []
                        for item in self.referenced_modules.keys():
                            referenced_modules_str.append(item.name)
                            referenced_modules_str.append(item.asname)
                        referenced_modules_set = set(referenced_modules_str)
                        if len(variable_names) > 1 and pre_variable_name not in (referenced_modules_set):
                            code_location_helper(self.used_variables, VariableInformation.create_var(variable_names[0:-1]),
                                                                       CodeLocation(line_number=node.lineno,
                                                                                    column_offset=node.col_offset))

                        code_location_helper(self.referenced_functions, variable_information,
                                                                   CodeLocation(line_number=node.lineno,
                                                                          column_offset=node.col_offset))
                else:
                    variable_names = [attribute.attr for attribute in attributes]
                    variable_names.insert(0, name)
                    variable_information = VariableInformation.create_var(variable_names)
                    if isinstance(before_attributes, ast.Assign):
                        code_location_helper(self.assigned_variables, variable_information,
                                             CodeLocation(line_number=node.lineno,
                                                          column_offset=node.col_offset))
                    else:
                        code_location_helper(self.used_variables, variable_information,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
            elif isinstance(parent, ast.Call):
                args = map(lambda x: x.id, filter(lambda y: isinstance(y, ast.Name), parent.args))
                if name in args:
                    code_location_helper(self.used_variables, VariableInformation(name),
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                else:
                    code_location_helper(self.referenced_functions, VariableInformation(name),
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
            elif isinstance(parent, ast.Tuple):
                three_up_stack_node = self._stack[-3]
                if isinstance(three_up_stack_node, ast.Assign):
                    names = set([name.id
                                 for target in three_up_stack_node.targets if isinstance(target, ast.Tuple)
                                 for name in target.elts if isinstance(name, ast.Name)])
                    if name in names:
                        code_location_helper(self.assigned_variables, VariableInformation(name),
                                                                         CodeLocation(line_number=node.lineno,
                                                                                      column_offset=node.col_offset))
                    else:
                        code_location_helper(self.used_variables, VariableInformation(name),
                                                                       CodeLocation(line_number=node.lineno,
                                                                                    column_offset=node.col_offset))
                else:
                    raise ValueError(f"Have no idea how to handle this node from a tuple {type(three_up_stack_node)}")
            elif isinstance(parent, ast.withitem):
                if parent.optional_vars is node:
                    code_location_helper(self.assigned_variables, VariableInformation(name),
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
            elif isinstance(parent, ast.comprehension):
                if parent.target is node:
                    code_location_helper(self.assigned_variables, VariableInformation(name),
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
            elif isinstance(parent, ast.ExceptHandler):
                # not sure what to do with exceptions right now
                pass
            elif isinstance(parent, ast.Subscript):
                if name == "f":
                    code_location_helper(self.referenced_flags, parent.slice.value.s,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=parent.slice.value.col_offset + 1))
                code_location_helper(self.used_variables, VariableInformation(name),
                                                             CodeLocation(line_number=node.lineno,
                                                                          column_offset=node.col_offset))
            else:
                code_location_helper(self.used_variables, VariableInformation(name),
                                                           CodeLocation(line_number=node.lineno,
                                                                        column_offset=node.col_offset))

            ast.NodeVisitor.generic_visit(self, node)

    def visit_Attribute(self, node):
        with self.handle_node_stack(node):
            self._attribute_stack.append(node)
            ast.NodeVisitor.generic_visit(self, node)
            self._attribute_stack.pop()

    def visit_ClassDef(self, node):
        with self.handle_node_stack(node):
            code_location_helper(self.defined_classes, node.name,
                                                       CodeLocation(line_number=node.lineno,
                                                                    column_offset=node.col_offset + 6))

    def visit_Return(self, node):
        with self.handle_node_stack(node):
            code_location_helper(self.return_points, "return point",
                                 CodeLocation(line_number=node.lineno,
                                              column_offset=node.col_offset))
            ast.NodeVisitor.generic_visit(self, node)

    def generic_visit(self, node):
        with self.handle_node_stack(node):
            ast.NodeVisitor.generic_visit(self, node)





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


class TypeValidationResults:
    def __init__(self, validation_errors=None, other_errors=None, warnings=None):
        self.validation_errors = validation_errors if validation_errors else []
        self.other_errors = other_errors if other_errors else []
        self.warnings = warnings if warnings else []

    def add_validation_error(self, error):
        self.validation_errors.append(error)

    def add_other_error(self, error):
        self.other_errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)

def _validate_returns_boolean(flag_logic, is_single_line, return_points, nv: FlagFeederNodeVisitor,
                              flag_feeders):
    """
    This function will attempt to run mypy and get the results out.
    A resulting warning is something like this:
    "Expected type 'bool', got 'int' instead"

    If nothing is returned from mypy then the result is valid else we return
    an error.

    :param flag_logic: The logic to test
    :return: An error object that shows possible typing errors
    """

    spaced_flag_logic = os.linesep.join(
        [_process_line(is_single_line, line, return_points) for line in flag_logic.splitlines()])

    used_var_names = {str(var) for var in nv.used_variables}
    assigned_var_names = {str(var) for var in nv.assigned_variables}

    must_define_flag_feeders = used_var_names - assigned_var_names

    function_params = [f"{flag_feeder_name}: {flag_feeder_type.__name__}"
                       for (flag_feeder_name, flag_feeder_type) in flag_feeders.items()
                       if flag_feeder_name in must_define_flag_feeders]

    flag_feeder_names = {name for name in flag_feeders}
    must_define_flag_feeders = must_define_flag_feeders - flag_feeder_names

    function_params.extend([name for name in must_define_flag_feeders])

    func_variables = ", ".join(function_params)

    typed_flag_logic_function = f"""\
def flag_function({func_variables}) -> bool:
{spaced_flag_logic}"""
    flag_function_lines = spaced_flag_logic.split('\n')


    #NOTE
    # --always-True-NAME could be used to hard code flagFeeders to True
    result = api.run(["--show-error-codes", "--ignore-missing-imports", "--no-error-summary", "--strict-equality", "--show-column-numbers", "--warn-return-any", "--warn-unreachable", "-c", typed_flag_logic_function])

    # see if we have an error
    type_validation = TypeValidationResults()
# Update tests to check for proper return checking


    if result[2] != 0:
        errors = [line.replace("<string>:", "") for line in result[0].split("\n") if line]
        for error in errors:
            error_code = error[error.find("[")+1:error.find("]")]
            error_code_full = error_code + ", " + error[error.find("error: ") + len("error: ")
                                                       : error.find(" [") - 1]
            orig_code_location = error[:error.find("error")-2]
            error_code_location_line = int(orig_code_location[:orig_code_location.find(":")]) - 1
            if error_code == "return-value":
                error_code_location_col_offset = flag_function_lines[error_code_location_line-1].lower().find("return") - 4
                type_validation.add_validation_error({error_code_full: CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=error_code_location_col_offset)})
            elif error_code == 'return':
                error_code_location_col_offset = 1
                type_validation.add_other_error({error_code_full: CodeLocation(line_number=error_code_location_line,
                                                              column_offset=error_code_location_col_offset)})
            else:
                error_code_location_col_offset = 1
                type_validation.add_other_error({error_code_full: CodeLocation(line_number=error_code_location_line,
                                                                               column_offset=error_code_location_col_offset)})

    return type_validation


def _process_line(is_single_line, line, return_points):
    new_line = line
    if is_single_line and line and len(return_points) == 0:
        new_line = f"return {line}"
    return f"    {new_line}"
