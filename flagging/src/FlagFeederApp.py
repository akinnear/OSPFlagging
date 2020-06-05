import ast
import contextlib
from ast import NodeVisitor
from flagging.src.VariableInformation import VariableInformation



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

def code_location_helper(var_dict, key, cl):
    if key in var_dict.keys():
        var_dict[key].add(cl)
        print(key + ": " + str(cl))
        print(var_dict)
    else:
        #creat new key
        var_dict.setdefault(key, set())
        var_dict[key].add(cl)
        print(key + ": " + str(cl))
        print(var_dict)
    return var_dict

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
        self._stack = []
        self._attribute_stack = []

    @contextlib.contextmanager
    def handle_node_stack(self, node):
        print("NODE:"+f"{_print_helper(node)} Stack[{', '.join(map(lambda x: _print_helper(x), self._stack))}]")

        self._stack.append(node)
        print("-PUSH->")
        try:
            yield node
            self._stack.pop()
            print("**POP**")
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
            self.defined_functions = code_location_helper(self.defined_functions, node.name,
                                                          CodeLocation(line_number=node.lineno,
                                                                       column_offset=node.col_offset))
            # self.defined_functions.add(node.name)
            for arg in node.args.args:
                self.assigned_variables = code_location_helper(self.assigned_variables, arg.arg,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                # self.assigned_variables.add(arg.arg)
            for body_line in node.body:
                ast.NodeVisitor.generic_visit(self, body_line)
            ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        with self.handle_node_stack(node):
            for name in node.names:
                self.referenced_moduels = code_location_helper(self.referenced_modules, name.name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                # self.referenced_modules.add(name.name)
            ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        with self.handle_node_stack(node):
            for name in node.names:
                self.referenced_modules = code_location_helper(self.referenced_modules, name.name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                # self.referenced_modules.add(name.name)
            ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self, node):
        with self.handle_node_stack(node):
            name = node.id
            parent = self._stack[-2]
            if isinstance(parent, ast.Assign):
                self.assigned_variables = code_location_helper(self.assigned_variables, name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                # self.assigned_variables.add(name)
            elif isinstance(parent, ast.FunctionDef):
                self.assigned_variables = code_location_helper(self.assigned_variables, name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                # self.assigned_variables.add(name)
            elif isinstance(parent, ast.Attribute):
                before_attributes = self._stack[-1*(len(self._attribute_stack) + 2)]
                attributes = self._attribute_stack.copy()
                attributes.reverse()
                if isinstance(before_attributes, ast.Call) or isinstance(before_attributes, ast.FunctionDef):
                    function_name = attributes[-1].attr
                    post_variable_name = ".".join(map(lambda attr_node: attr_node.attr, attributes[:-1]))
                    variable_name = name
                    if post_variable_name:
                        variable_name += f".{post_variable_name}"
                    full_name = f"{variable_name}.{function_name}"

                    if variable_name not in self.referenced_moduels:
                        code_location_helper(self.used_variables, variable_name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))

                    possible_args = self._call_args_to_names(before_attributes.args)
                    if full_name in possible_args:
                        self.used_variables = code_location_helper(self.used_variables, full_name,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                        # self.used_variables.add(full_name)

                    else:
                        post_attr_name = ".".join(map(lambda attr_node: attr_node.attr, attributes))
                        full_name = f"{name}.{post_attr_name}"
                        self.referenced_functions = code_location_helper(self.referenced_functions, full_name,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                        # self.referenced_functions.add(full_name)
                else:
                    #TODO
                    # bug fix for full_name declaration
                    self.used_variables = code_location_helper(self.used_variables, full_name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                    # self.used_variables.add(full_name)
            elif isinstance(parent, ast.Call):
                args = map(lambda x: x.id, filter(lambda y: isinstance(y, ast.Name), parent.args))
                if name in args:
                    self.used_variables = code_location_helper(self.used_variables, name,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                    # self.used_variables.add(name)
                else:
                    self.referenced_functions = code_location_helper(self.referenced_functions, name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                    # self.referenced_functions.add(name)
            elif isinstance(parent, ast.Tuple):
                three_up_stack_node = self._stack[-3]
                if isinstance(three_up_stack_node, ast.Assign):
                    names = set([name.id
                                 for target in three_up_stack_node.targets if isinstance(target, ast.Tuple)
                                 for name in target.elts if isinstance(name, ast.Name)])
                    if name in names:
                        self.assigned_variables = code_location_helper(self.assigned_variables, name,
                                                                         CodeLocation(line_number=node.lineno,
                                                                                      column_offset=node.col_offset))
                        # self.assigned_variables.add(name)
                    else:
                        self.used_variables = code_location_helper(self.used_variables, name,
                                                                       CodeLocation(line_number=node.lineno,
                                                                                    column_offset=node.col_offset))
                        # self.used_variables.add(name)
                else:
                    raise ValueError(f"Have no idea how to handle this node from a tuple {type(three_up_stack_node)}")
            elif isinstance(parent, ast.withitem):
                if parent.optional_vars is node:
                    self.assigned_variables = code_location_helper(self.assigned_variables, name,
                                                               CodeLocation(line_number=node.lineno,
                                                                            column_offset=node.col_offset))
                    # self.assigned_variables.add(name)
            elif isinstance(parent, ast.comprehension):
                if parent.target is node:
                    self.assigned_variables = code_location_helper(self.assigned_variables, name,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                    # self.assigned_variables.add(name)
            elif isinstance(parent, ast.ExceptHandler):
                # not sure what to do with exceptions right now
                pass
            elif isinstance(parent, ast.Subscript):
                if name == "f":
                    self.referenced_flags = code_location_helper(self.referenced_flags, parent.slice.value.s,
                                                                   CodeLocation(line_number=node.lineno,
                                                                                column_offset=node.col_offset))
                    # self.referenced_flags.add(parent.slice.value.s)
                self.used_variables = code_location_helper(self.used_variables, name,
                                                             CodeLocation(line_number=node.lineno,
                                                                          column_offset=node.col_offset))
                # self.used_variables.add(name)
            else:
                self.used_variables = code_location_helper(self.used_variables, name,
                                                           CodeLocation(line_number=node.lineno,
                                                                        column_offset=node.col_offset))
                # self.used_variables.add(name)

            ast.NodeVisitor.generic_visit(self, node)

    def visit_Attribute(self, node):
        with self.handle_node_stack(node):
            self._attribute_stack.append(node)
            ast.NodeVisitor.generic_visit(self, node)
            self._attribute_stack.pop()

    def visit_ClassDef(self, node):
        with self.handle_node_stack(node):
            self.defined_classes = code_location_helper(self.defined_classes, node.name,
                                                       CodeLocation(line_number=node.lineno,
                                                                    column_offset=node.col_offset))
            # self.defined_classes.add(node.name)

    def generic_visit(self, node):
        with self.handle_node_stack(node):
            ast.NodeVisitor.generic_visit(self, node)





class FlagLogicInformation:
    def __init__(self, used_variables=None, assigned_variables=None, referenced_functions=None,
                 defined_functions=None, defined_classes=None, referenced_modules=None,
                 referenced_flags=None):
        self.used_variables = used_variables
        self.assigned_variables = assigned_variables
        self.referenced_functions = referenced_functions
        self.defined_functions = defined_functions
        self.defined_classes = defined_classes
        self.referenced_modules = referenced_modules
        self.referenced_flags = referenced_flags


def determine_variables(logic):
    root = ast.parse(logic)
    nv = FlagFeederNodeVisitor()
    nv.visit(root)

    #TODO
    # parse used_variabeles, assigned_varaibles,
    # referenced_fucntiosn, defined_functions
    # to create VaribleInformation Objects as keys
    return FlagLogicInformation(used_variables=nv.used_variables,
                                assigned_variables=nv.assigned_variables,
                                referenced_functions=nv.referenced_functions,
                                defined_functions=nv.defined_functions,
                                defined_classes=nv.defined_classes,
                                referenced_modules=nv.referenced_modules,
                                referenced_flags=nv.referenced_flags)