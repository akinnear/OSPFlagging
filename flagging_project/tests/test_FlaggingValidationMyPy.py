from flagging.FlaggingNodeVisitor import determine_variables, CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.FlaggingValidation import validate_returns_boolean


def test_mypy_explicit_fail():
    logic = """cat and dog"""
    flag_feeders = {"cat": int, "dog": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {"return-value": {CodeLocation(1, 0)}}
    assert test_output.warnings == {}


def test_mypy_explicit_pass():
    logic = """
man or woman"""
    flag_feeders = {"man": bool, "woman": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_explicit_int():
    logic = """
cat = 100
return cat < 10"""
    flag_feeders = {"cat": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.validation_errors == {}
    assert test_output.other_errors == {}
    assert test_output.warnings == {}


def test_mypy_non_explicit_int():
    logic = """
cat = 100
return cat < 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

def test_mypy_if_statement_explicit():
    logic = """
x = (ff1 or ff2)
y = (ff3 + ff4)
if y > 100:
    return ff5 != x
else:
    return ff5 == x"""
    flag_feeders = {"ff5": bool, "ff1": bool, "ff2": bool, "ff3": int, "ff4": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

def test_mypy_if_statement_nonexplicit():
    logic = """
x = (ff1 or ff2)
y = (ff3 + ff4)
if y > 100:
    return ff5 != x
else:
    return ff5 == x"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(5, 0), CodeLocation(7, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_normal_expression_non_explicit():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"non-any-return": {CodeLocation(4, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_normal_expression_explicit():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    flag_feeders = {"ff1": float, "z": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_equals_operation():
    logic = """return ff1 == ff2"""
    flag_feeders = {"ff1": str, "ff2": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_less_than_operation():
    logic = """return ff1 >= ff2"""
    flag_feeders = {"ff1": float, "ff2": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_greater_than_operation():
    logic = """return ff1 <= ff2"""
    flag_feeders = {"ff1": bool, "ff2": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_add_operation():
    logic = """
test_1 = ff1 + ff2
return ff3 < test_1"""
    flag_feeders = {"ff1": bool, "ff3": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(3, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_add_operation_2():
    logic = """
test_1 = ff1 + ff2
return ff3 < test_1"""
    flag_feeders = {"ff1": bool, "ff2": str, "ff3": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"operator": {CodeLocation(2, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_embedded_if_statment():
    logic = """                                            
if ff4 >= 50:                                              
    if ff1 > 10:                                           
        return ff2 == True                                 
    elif ff2:                                              
        return ff1 < 10                                    
    elif ff3 > ff1:                                        
        return ff4 < 50      
    else:
        return ff2
elif ff1 < 10:                                             
    return ff5 == 'CAT'                                    
else:                                                      
    a = 10                                                 
    b = True                                               
    c = "CAR"                                              
    if ff5 == "DOG":                                       
        a = a + 10                                         
        return ff1 < a
    else:
        return ff2"""
    flag_feeders = {"ff1": int, "ff2": bool, "ff3": int, "ff4": int, "ff5":str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

def test_mypy_embedded_if_missing_return():
    logic = """
if ff4 >= 50:                                              
    if ff1 > 10:                                           
        return ff2 == True                                 
    elif ff2:                                              
        return ff1 < 10                                    
    elif ff3 > ff1:                                        
        return ff4 < 50      
    else:
        return ff2
elif ff1 < 10:                                             
    return ff5 == 'CAT'                                    
else:                                                      
    a = 10                                                 
    b = True                                               
    c = "CAR"                                              
    if ff5 == "DOG":                                       
        a = a + 10                                         
        return ff1 < a"""
    flag_feeders = {"ff1": int, "ff2": bool, "ff3": int, "ff4": int, "ff5": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"return": {CodeLocation(0,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

def test_mypy_reduce_lambda():
    logic = """
from functools import reduce                                  
f = lambda a,b: a if (a > b) else b              
if reduce(f, [47,11,42,102,13]) > 100:           
    return ff1 > reduce(f, [47,11,42,102,13])    
else:                                            
    return ff2 < reduce(f, [47,11,42,102,13])"""
    flag_feeders = {"ff1": float, "ff2": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_list_comprehension_var_not_defined():
    logic = """
from functools import reduce
sum = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
return sum > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(4,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_map_expression():
    logic = """
numbers = (1, 2, 3, 4)
result = map(lambda x: x + x, numbers)
if ff1 in list(result):
    return ff2 > max(list(result))
else:
    return ff3 < min(list(result))"""
    flag_feeders = {"ff2": float, "ff3": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_map_lambda():
    logic = """
a = [1,2,3,4]
b = [17,12,11,10]
c = [-1,-4,5,9]
my_map_list = list(map(lambda x,y,z:x+y-z, a,b,c))
return ff1 > max(my_map_list)"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_lambda_expression():
    logic = """                               
add = (lambda x, y: x + y)(2, 3)              
return ff1 == add"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_math_expression():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
for a in a_list:
    if math.sqrt(abs(a)) <= 4:
        y_list.append(int(math.sqrt(a)))
if ff1 == (max(y_list)):
    return ff1 > max(a_list)
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    flag_feeders = {"ff1": int, "ff2": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# TODO
# Issue #1
# don't allow user to overwrite module
# override module assignment error, no any return error
def test_math_overwrite_module_CodeLocation():
    logic = """
import math
math = math.sqrt(10)
return ff1 > math"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    # assert test_output.other_errors == {'assignment': {CodeLocation(3, 0)}, 'operator': {CodeLocation(4, 0)}}
    # top will pass, below will fail
    assert test_output == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_math_expression_2():
    logic = """
import math
x = 10
y = math.sqrt(10)
return ff1 > x"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}





# TODO
# update test
# name defined error, var.var
def test_mypy_math_expression_3():
    logic = """
import math
x.y = 10
a.b = math.sqrt(10)
return ff1 > x.y"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"name-defined": {CodeLocation(3, 0),
                                                         CodeLocation(4, 0),
                                                         CodeLocation(5, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# TODO
# update test,
# int, att-defined error
def test_mypy_tuple_assignment_2():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
(ff1, ff2, z) = (12, True, 12.8)
for a in a_list:
    if math.sqrt(abs(a)) <= 4 and z > 10:
        y_list.append(int(math.sqrt(a)))
if ff1 in y_list:
    return ff1 > 10
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    flag_feeders = {"ff1": int, "ff2": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

# syntax error
def test_mypy_object():
    logic = """
a.b.c.d.e > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# syntax error
def test_mypy_object_function():
    logic = """
a.b.c() > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_feeder_function_function():
    logic = """ff1.lower() == 'my value'"""
    flag_feeders = {"ff1": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_determine_flag_feeders():
    logic = """
unused1, unused2 = fish, bird
return cat < 10 and fish > 100"""
    flag_feeders = {"cat": int, "fish": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_map_filter_lambda_2():
    logic = """
from functools import reduce    
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]
map_step = list(map(lambda x,y,z:x+y-z, a,b,c))
filter_step = list(filter(lambda x: x > 4, map_step))
reduce_step = reduce(lambda x, y: x if x>y else y, filter_step)
if max(a) == reduce_step:
    return ff2 > 10
elif max(b) == reduce_step:
    return ff1 < 10
else: 
    return ff3 > ff1 + ff2"""
    flag_feeders = {"ff1": int, "ff2": int, "ff3": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_map_filter_lambda():
    logic = """
import math
from functools import reduce
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]    
d = reduce(lambda x, y: x if x>20 else y,(list(filter(lambda x: x > math.sqrt(10), list(map(lambda x,y,z:x+y-z, a,b,c))))))
if max(a) == d:
    return ff1 > min(a)
elif min(b) == d:
    return ff2 < max(b)
elif max(c) == d:
    return ff1 > min(c)
else:
    return ff3 == True"""
    flag_feeders = {"ff1": int, "ff2": int, "ff3": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_variables_in_list():
    logic = """
animals = [cat, dog, fish]
return cat in animals"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_with_no_as():
    logic = """
with method(item):
    return ff1 > 100"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"name-defined": {CodeLocation(2, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_with_using_as():
    logic = """
with method(ff1, ff2) as my_with:
    return my_with > 100"""
    flag_feeders = {"my_with": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"name-defined": {CodeLocation(2, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}



def test_mypy_func():
    logic = """
def myfunc(xyz):
    return xyz+10
return myfunc(ff1) > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(4, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

#TODO
# syntax error
def test_list_comprehension_CodeLocation():
    logic = """
names = set([name.id 
    for target in three_up_stack_node.targets if isinstance(target, ast.Tuple) 
    for name in target.elts if isinstance(name, ast.Name)])
return ff1 in names"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_generator_mypy():
    logic = """
eggs = (x*2 for x in [1, 2, 3, 4, 5])
return 10 in eggs"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_generator_with_yield():
    logic = """
# A simple generator function
def my_gen():
    n = 1
    print('This is printed first')
    # Generator function contains yield statements
    yield n
    m = n + 1
    print('This is printed second')
    yield m
    k = 4
    print('This is printed at last')
    yield ff1

return 1 in my_gen()"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_comprehension_2():
    logic = """
eggs = [x*2 for x in [1, 2, 3, 4, 5]]
return 10 in eggs"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}

def test_mypy_fizzbuzz_comprehension():
    logic = """
fizzbuzz = [
    f'fizzbuzz {n}' if n % 3 == 0 and n % 5 == 0
    else f'fizz {n}' if n % 3 == 0
    else f'buzz {n}' if n % 5 == 0
    else n
    for n in range(100)
]
return 'not in' in fizzbuzz"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_simple_set_return_another():
    logic = """
k = 4
return ff1"""
    flag_feeders = {"ff1": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_simple_function_dont_use():
    logic = """
def my_function():
    k = 4
    return 1
return ff1 > 0"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_simple_function_dont_use_complex():
    logic = """
def my_function():
    a.b.k = 4
    return 1
return ff1 > 0"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# syntax error
def test_mypy_complex_use():
    logic = """
x.y.z > 10"""
    flag_feeders = {"x.y.z": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_complex_in_function():
    logic = """
def my_function():
    x = 2
    a.b.k = 4
    return 1
return ff1 > 0"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# syntax error
def test_complex_assign():
    logic = """
x.y.z = 5"""
    test_output = determine_variables(logic)
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["x", "y", "z"])}


# syntax error
def test_simple_function_dont_use_complex_2_CodeLocation():
    logic = """
def my_function():
    a.b.k()
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation.create_var(["a", "b"])}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 7)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b"])] == {CodeLocation(3, 4)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["a", "b", "k"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["a", "b", "k"])] == {CodeLocation(3, 4)}
    assert test_output.defined_functions.keys() == {VariableInformation("my_function")}
    assert test_output.defined_functions[VariableInformation("my_function")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_unused_var_CodeLocation():
    logic = """
k = 4
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("k")}
    assert test_output.assigned_variables[VariableInformation("k")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_try_except_finally_CodeLocation():
    logic = """
try:
    result = x / y * fun_0()
    return result
except ZeroDivisionError:
    zde = zde_func(a.b.c, b.c.d(), ff1, fun_1())
    return zde
else:
    ezde = ezde_func(c.d.e, d.e.f(), ff2, fun_2())
    return ezde
finally:
    fin = fun_func(e.f.g, f.g.h(), ff3, fun_3())
    return fin"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("result", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("zde", None),
                                                 VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["b", "c"]),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ezde", None),
                                                 VariableInformation.create_var(["c", "d", "e"]),
                                                 VariableInformation.create_var(["d", "e"]),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("fin", None),
                                                 VariableInformation.create_var(["e", "f", "g"]),
                                                 VariableInformation.create_var(["f", "g"]),
                                                 VariableInformation("ff3", None)}
    assert test_output.used_variables[VariableInformation("result")] == {CodeLocation(4, 11)}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(3, 13)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(3, 17)}
    assert test_output.used_variables[VariableInformation("zde")] == {CodeLocation(7, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(6, 19)}
    assert test_output.used_variables[VariableInformation.create_var(["b", "c"])] == {CodeLocation(6, 26)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(6, 35)}
    assert test_output.used_variables[VariableInformation("ezde")] == {CodeLocation(10, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(9, 21)}
    assert test_output.used_variables[VariableInformation.create_var(["d", "e"])] == {CodeLocation(9, 28)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(9, 37)}
    assert test_output.used_variables[VariableInformation("fin")] == {CodeLocation(13, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["e", "f", "g"])] == {CodeLocation(12, 19)}
    assert test_output.used_variables[VariableInformation.create_var(["f", "g"])] == {CodeLocation(12, 26)}
    assert test_output.used_variables[VariableInformation("ff3")] == {CodeLocation(12, 35)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None),
                                                     VariableInformation("zde", None),
                                                     VariableInformation("ezde", None),
                                                     VariableInformation("fin", None)}
    assert test_output.assigned_variables[VariableInformation("result")] == {CodeLocation(3, 4)}
    assert test_output.assigned_variables[VariableInformation("zde")] == {CodeLocation(6, 4)}
    assert test_output.assigned_variables[VariableInformation("ezde")] == {CodeLocation(9, 4)}
    assert test_output.assigned_variables[VariableInformation("fin")] == {CodeLocation(12, 4)}
    assert test_output.referenced_functions.keys() == {VariableInformation("fun_0", None),
                                                       VariableInformation("zde_func", None),
                                                       VariableInformation("ezde_func", None),
                                                       VariableInformation("fun_func", None),
                                                       VariableInformation.create_var(["b", "c", "d"]),
                                                       VariableInformation.create_var(["d", "e", "f"]),
                                                       VariableInformation.create_var(["f", "g", "h"]),
                                                       VariableInformation("fun_1", None),
                                                       VariableInformation("fun_2", None),
                                                       VariableInformation("fun_3", None)}
    assert test_output.referenced_functions[VariableInformation("fun_0")] == {CodeLocation(3, 21)}
    assert test_output.referenced_functions[VariableInformation("zde_func")] == {CodeLocation(6, 10)}
    assert test_output.referenced_functions[VariableInformation("ezde_func")] == {CodeLocation(9, 11)}
    assert test_output.referenced_functions[VariableInformation("fun_func")] == {CodeLocation(12, 10)}
    assert test_output.referenced_functions[VariableInformation.create_var(["b", "c", "d"])] == {CodeLocation(6, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["d", "e", "f"])] == {CodeLocation(9, 28)}
    assert test_output.referenced_functions[VariableInformation.create_var(["f", "g", "h"])] == {CodeLocation(12, 26)}
    assert test_output.referenced_functions[VariableInformation("fun_1")] == {CodeLocation(6, 40)}
    assert test_output.referenced_functions[VariableInformation("fun_2")] == {CodeLocation(9, 42)}
    assert test_output.referenced_functions[VariableInformation("fun_3")] == {CodeLocation(12, 40)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_try_except_finally_in_defined_function_CodeLocation():
    logic = """
def my_func():
    try:
        result = x / y * fun_0()
        return result
    except ZeroDivisionError:
        zde = zde_func(a.b.c, b.c.d(), ff1, fun_1())
        return zde
    else:
        ezde = ezde_func(c.d.e, d.e.f(), ff2, fun_2())
        return ezde
    finally:
        fin = fun_func(e.f.g, f.g.h(), ff3, fun_3())
        return fin

return my_func()"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("result", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("zde", None),
                                                 VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["b", "c"]),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ezde", None),
                                                 VariableInformation.create_var(["c", "d", "e"]),
                                                 VariableInformation.create_var(["d", "e"]),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("fin", None),
                                                 VariableInformation.create_var(["e", "f", "g"]),
                                                 VariableInformation.create_var(["f", "g"]),
                                                 VariableInformation("ff3", None)}
    assert test_output.used_variables[VariableInformation("result")] == {CodeLocation(5, 15)}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(4, 17)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(4, 21)}
    assert test_output.used_variables[VariableInformation("zde")] == {CodeLocation(8, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(7, 23)}
    assert test_output.used_variables[VariableInformation.create_var(["b", "c"])] == {CodeLocation(7, 30)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(7, 39)}
    assert test_output.used_variables[VariableInformation("ezde")] == {CodeLocation(11, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(10, 25)}
    assert test_output.used_variables[VariableInformation.create_var(["d", "e"])] == {CodeLocation(10, 32)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(10, 41)}
    assert test_output.used_variables[VariableInformation("fin")] == {CodeLocation(14, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["e", "f", "g"])] == {CodeLocation(13, 23)}
    assert test_output.used_variables[VariableInformation.create_var(["f", "g"])] == {CodeLocation(13, 30)}
    assert test_output.used_variables[VariableInformation("ff3")] == {CodeLocation(13, 39)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None),
                                                     VariableInformation("zde", None),
                                                     VariableInformation("ezde", None),
                                                     VariableInformation("fin", None)}
    assert test_output.assigned_variables[VariableInformation("result")] == {CodeLocation(4, 8)}
    assert test_output.assigned_variables[VariableInformation("zde")] == {CodeLocation(7, 8)}
    assert test_output.assigned_variables[VariableInformation("ezde")] == {CodeLocation(10, 8)}
    assert test_output.assigned_variables[VariableInformation("fin")] == {CodeLocation(13, 8)}
    assert test_output.referenced_functions.keys() == {VariableInformation("fun_0", None),
                                                       VariableInformation("zde_func", None),
                                                       VariableInformation("ezde_func", None),
                                                       VariableInformation("fun_func", None),
                                                       VariableInformation.create_var(["b", "c", "d"]),
                                                       VariableInformation.create_var(["d", "e", "f"]),
                                                       VariableInformation.create_var(["f", "g", "h"]),
                                                       VariableInformation("fun_1", None),
                                                       VariableInformation("fun_2", None),
                                                       VariableInformation("fun_3", None),
                                                       VariableInformation("my_func", None)}
    assert test_output.referenced_functions[VariableInformation("fun_0")] == {CodeLocation(4, 25)}
    assert test_output.referenced_functions[VariableInformation("zde_func")] == {CodeLocation(7, 14)}
    assert test_output.referenced_functions[VariableInformation("ezde_func")] == {CodeLocation(10, 15)}
    assert test_output.referenced_functions[VariableInformation("fun_func")] == {CodeLocation(13, 14)}
    assert test_output.referenced_functions[VariableInformation.create_var(["b", "c", "d"])] == {CodeLocation(7, 30)}
    assert test_output.referenced_functions[VariableInformation.create_var(["d", "e", "f"])] == {CodeLocation(10, 32)}
    assert test_output.referenced_functions[VariableInformation.create_var(["f", "g", "h"])] == {CodeLocation(13, 30)}
    assert test_output.referenced_functions[VariableInformation("fun_1")] == {CodeLocation(7, 44)}
    assert test_output.referenced_functions[VariableInformation("fun_2")] == {CodeLocation(10, 46)}
    assert test_output.referenced_functions[VariableInformation("fun_3")] == {CodeLocation(13, 44)}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(16, 7)}
    assert test_output.defined_functions.keys() == {VariableInformation("my_func", None)}
    assert test_output.defined_functions[VariableInformation("my_func")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_unused_class_CodeLocation():
    logic = """
class MyClass:
    pass
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(4, 7)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.defined_classes["MyClass"] == {CodeLocation(2, 6)}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_used_class_CodeLocation():
    logic = """
class MyClass():
    def __init__(self, val=None):
        self.val = val
my_val = MyClass(ff1)
return my_val.val"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation.create_var(["my_val", "val"])}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 17)}
    assert test_output.used_variables[VariableInformation.create_var(["my_val", "val"])] == {CodeLocation(6, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("my_val")}
    assert test_output.assigned_variables[VariableInformation("my_val")] == {CodeLocation(5, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("MyClass")}
    assert test_output.referenced_functions[VariableInformation("MyClass")] == {CodeLocation(5, 9)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.defined_classes["MyClass"] == {CodeLocation(2, 6)}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# TODO
# update test
# no any return error
def test_dictionary_CodeLocation():
    logic = """
dict[ff] > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("dict"),
                                                 VariableInformation("ff")}
    assert test_output.used_variables == {VariableInformation("dict"): {CodeLocation(2, 0)},
                                          VariableInformation("ff"): {CodeLocation(2, 5)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_list_slice_CodeLocation():
    logic = """
len(list[ff:]) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("list"),
                                                 VariableInformation("ff")}
    assert test_output.used_variables[VariableInformation("list")] == {CodeLocation(2, 4)}
    assert test_output.used_variables[VariableInformation("ff")] == {CodeLocation(2, 9)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("len")}
    assert test_output.referenced_functions[VariableInformation("len")] == {CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# TODO
# update test
# no any return error
def test_simple_flag_CodeLocation():
    logic = """
f["MY_FLAG"]"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("f")}
    assert test_output.used_variables[VariableInformation("f")] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == {"MY_FLAG"}
    assert test_output.referenced_flags["MY_FLAG"] == {CodeLocation(2, 3)}
    assert test_output.errors == []


# TODO
# update test
# no any return error
def test_simple_flag_get():
    logic = """
f.get("MY_FLAG")"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"f"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"f.get"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == {"MY_FLAG"}
    assert test_output.referenced_flags["MY_FLAG"] == {CodeLocation(2, 7)}
    assert test_output.errors == []


# syntax error
def test_function_with_vars_CodeLocation():
    logic = """my_func(a.b.c, x.y.z)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(1, 8)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(1, 15)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func")}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(1, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_function_with_vars_using_import_function_CodeLocation():
    logic = """
import math
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(3, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(3, 36)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func"),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(3, 8),
                                                                                                  CodeLocation(3, 26)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_function_with_vars_using_import_function_2_CodeLocation():
    logic = """
import pandas as pd, math
import numpy as np
import datetime
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(5, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(5, 36)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func"),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(5, 0)}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(5, 8),
                                                                                                  CodeLocation(5, 26)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math"),
                                                     ModuleInformation("pandas", "pd"),
                                                     ModuleInformation("numpy", "np"),
                                                     ModuleInformation("datetime")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 21)}
    assert test_output.referenced_modules[ModuleInformation("pandas", "pd")] == {CodeLocation(2, 7)}
    assert test_output.referenced_modules[ModuleInformation("numpy", "np")] == {CodeLocation(3, 7)}
    assert test_output.referenced_modules[ModuleInformation("datetime")] == {CodeLocation(4, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# syntax error
def test_function_with_vars_using_import_value_CodeLocation():
    logic = """
import math
my_func(math.PI, math.E)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["math", "PI"]),
                                                 VariableInformation.create_var(["math", "E"])}
    assert test_output.used_variables[VariableInformation.create_var(["math", "PI"])] == {CodeLocation(3, 8)}
    assert test_output.used_variables[VariableInformation.create_var(["math", "E"])] == {CodeLocation(3, 17)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func")}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_from_CodeLocation():
    logic = """
from sqlalchemy import create_engine
from flask import render_template
engine = create_engine('oracle+cx_oracle://' + username + ':' + password + '@' + dsn_tns)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("username"),
                                                 VariableInformation("password"),
                                                 VariableInformation("dsn_tns")}
    assert test_output.used_variables[VariableInformation("username")] == {CodeLocation(4, 47)}
    assert test_output.used_variables[VariableInformation("password")] == {CodeLocation(4, 64)}
    assert test_output.used_variables[VariableInformation("dsn_tns")] == {CodeLocation(4, 81)}
    assert test_output.assigned_variables.keys() == {VariableInformation("engine")}
    assert test_output.assigned_variables["engine"] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("create_engine")}
    assert test_output.referenced_functions[VariableInformation("create_engine")] == {CodeLocation(4, 9)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("sqlalchemy"),
                                                     ModuleInformation("flask")}
    assert test_output.referenced_modules[ModuleInformation("sqlalchemy")] == {CodeLocation(2, 5)}
    assert test_output.referenced_modules[ModuleInformation("flask")] == {CodeLocation(3, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_CodeLocation():
    logic = """
import math as m
x = m.sqrt(10)
y = m.sqrt(x)
return y > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("y")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(4, 11)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["m", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["m", "sqrt"])] == {CodeLocation(3, 4),
                                                                                               CodeLocation(4, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math", "m")}
    assert test_output.referenced_modules[ModuleInformation("math", "m")] == {CodeLocation(2, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_2_CodeLocation():
    logic = """
from math import sqrt as sq
return sq(ff1) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 10)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("sq")}
    assert test_output.referenced_functions[VariableInformation("sq")] == {CodeLocation(3, 7)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_3_CodeLocation():
    logic = """
from math import cos as c, sin as s
x = c(10)
y = s(10)
return x > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("c"),
                                                       VariableInformation("s")}
    assert test_output.referenced_functions[VariableInformation("c")] == {CodeLocation(3, 4)}
    assert test_output.referenced_functions[VariableInformation("s")] == {CodeLocation(4, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_4_CodeLocation():
    logic = """
from math import (cos as c, sin as s)
x = c(10)
y = s(10)
return y > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("y")}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("c"),
                                                       VariableInformation("s")}
    assert test_output.referenced_functions[VariableInformation("c")] == {CodeLocation(3, 4)}
    assert test_output.referenced_functions[VariableInformation("s")] == {CodeLocation(4, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_5_CodeLocation():
    logic = """
import math as m
from m import sqrt as sq
x = m.sqrt(10)
y = m.sqrt(x)
return y > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("y")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(5, 11)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(6, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(4, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(5, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["m", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["m", "sqrt"])] == {CodeLocation(4, 4),
                                                                                               CodeLocation(5, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math", "m"),
                                                     ModuleInformation("m")}
    assert test_output.referenced_modules[ModuleInformation("math", "m")] == {CodeLocation(2, 7)}
    assert test_output.referenced_modules[ModuleInformation("m")] == {CodeLocation(3, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# TODO
# update test
# non any return error
def test_special_lambda_CodeLocation():
    logic = """
high_ord_func = lambda x, func: x + func(x)
return high_ord_func(ff1, lambda x: x * x) > ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("ff1"),
                                                 VariableInformation("ff2")}
    assert test_output.used_variables[VariableInformation('x')] == {CodeLocation(2, 32),
                                                                    CodeLocation(2, 41),
                                                                    CodeLocation(3, 36),
                                                                    CodeLocation(3, 40)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 21)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(3, 45)}
    assert test_output.assigned_variables.keys() == {VariableInformation("high_ord_func")}
    assert test_output.assigned_variables[VariableInformation("high_ord_func")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("func"),
                                                       VariableInformation("high_ord_func")}
    assert test_output.referenced_functions[VariableInformation("func")] == {CodeLocation(2, 36)}
    assert test_output.referenced_functions[VariableInformation("high_ord_func")] == {CodeLocation(3, 7)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_invalid():
    logic = """
improper 
x = =  f
x = 12
y = = =  q2@"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("improper")}
    assert test_output.used_variables[VariableInformation("improper")] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables.keys() == {VariableInformation('x')}
    assert test_output.assigned_variables[VariableInformation('x')] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert len(test_output.errors) == 2


def test_odd_text():
    logic = "improper"
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("improper")}
    assert test_output.used_variables[VariableInformation("improper")] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_empty_space_clean_up():
    logic = """    

x = 10


return ff1 > x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation('ff1')}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(6, 13)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(6, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_empty_space_clean_up_single_line():
    logic = """    

ff1 > 10


"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation('ff1')}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_empty_space_clean_up_single_multi_line_return():
    logic = """    

ff1 > 10 and \
    ff1 < 20 and \
    ff2 > 100


"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation('ff1'), VariableInformation('ff2')}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 0), CodeLocation(3, 17)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(3, 34)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_boolean_flag_feeder_only():
    logic = "ff1"
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation('ff1')}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_boolean_flag_feeder_only():
    logic = """

ff1

"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation('ff1')}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_invalid_return():
    logic = """return 10 + 20"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_hardcoded_boolean():
    logic = """return True"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_invalid_return_2():
    logic = """return cat + dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 13)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_dynamic_flag_feeders():
    logic = """return cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 14)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_one_dynamic_flag_feeders():
    logic = """return cat < 10 or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 19)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders():
    logic = """return cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 14)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders_wrong_type():
    logic = """return cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 14)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders_wrong_type_2():
    logic = """cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 0)},
        VariableInformation("dog"): {CodeLocation(1, 7)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders_wrong_type_3():
    logic = """cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 0)},
        VariableInformation("dog"): {CodeLocation(1, 7)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders_wrong_type_4():
    logic = """return cat or dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 14)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_known_flag_feeders_invalid_type_for_math():
    logic = """return cat + dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 7)},
        VariableInformation("dog"): {CodeLocation(1, 13)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


# TODO
# update test
# unreachable error
def test_unreachable():
    logic = """\
if True or cat:
    return True

return dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("cat"): {CodeLocation(1, 11)},
        VariableInformation("dog"): {CodeLocation(4, 7)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_equality():
    logic = """return dog == 'dog'"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("dog"): {CodeLocation(1, 7)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_equality_any_var():
    logic = """return dog == x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {
        VariableInformation("dog"): {CodeLocation(1, 7)},
        VariableInformation("x"): {CodeLocation(1, 14)},
    }
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []



