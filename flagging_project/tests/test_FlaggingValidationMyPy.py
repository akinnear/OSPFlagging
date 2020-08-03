from flagging.FlaggingNodeVisitor import determine_variables, CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.FlaggingValidation import validate_returns_boolean
from flagging.ModuleInformation import ModuleInformation


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
    flag_feeders = {"cat": bool}
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


def test_mypy_if_statement_explicit():
    logic = """
x = (ff1 or ff2)
y = (ff3 + ff4)
if y > 100:
    return ff5 != x
else:
    return ff5 == x"""
    flag_feeders = {"ff1": bool, "ff2": bool, "ff3": float, "ff4": int, "ff5": bool}
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
    assert test_output.other_errors == {"no-any-return": {CodeLocation(4, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


#TODO
# why no-any-return??
def test_mypy_normal_expression_explicit():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    flag_feeders = {"ff1": float}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {'no-any-return': {CodeLocation(4, 0)}}
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


#TODO
# why no-any-return??
def test_mypy_add_operation():
    logic = """
test_1 = ff1 + ff2
return ff3 == test_1"""
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


def test_mypy_add_operation_3():
    logic = """
test_1 = ff1 + ff2
return ff3 < test_1"""
    flag_feeders = {"ff1": int, "ff2": int, "ff3": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
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


def test_mypy_embedded_if_2():
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
    flag_feeders = {"ff1": int, "ff2": bool, "ff3": int, "ff4": int, "ff5": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
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


def test_mypy_reduce_lambda_fail():
    logic = """
from functools import reduce                                  
f = lambda a,b: a if (a > b) else b              
if reduce(f, [47,11,42,102,13]) > 100:           
    return ff1 > reduce(f, [47,11,42,102,13])    
else:                                            
    return ff2 < reduce(f, [47,11,42,102,13])"""
    flag_feeders = {"ff1": bool, "ff2": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(7, 0)},
                                        "operator": {CodeLocation(7, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


#TODO
# why no-any-return??
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
    assert test_output.other_errors == {'assignment': {CodeLocation(3, 0)}, 'operator': {CodeLocation(4, 0)}}
    #top will pass, below will fail
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


def test_mypy_object():
    logic = """
a.b.c.d.e > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


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
    assert test_output.other_errors == {"name-defined": {CodeLocation(2, 0)},
                                        "no-any-return": {CodeLocation(3, 0)}}
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


def test_list_comprehension_CodeLocation():
    logic = """
names = set([name.id 
    for target in three_up_stack_node.targets if isinstance(target, ast.Tuple) 
    for name in target.elts if isinstance(name, ast.Name)])
return ff1 in names"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
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


def test_mypy_simple_function_dont_use_complex_2():
    logic = """
def my_function():
    a.b.k()
    return 1
return ff1 > 1"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


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
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_try_except_finally_in_defined_function():
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
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_unused_class():
    logic = """
class MyClass:
    pass
return ff1"""
    flag_feeders = {"ff1": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_used_class():
    logic = """
class MyClass():
    def __init__(self, val=None):
        self.val = val
my_val = MyClass(ff1)
return my_val.val"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# TODO
# update test
# no any return error
def test_mypy_dictionary():
    logic = """
dict[ff] > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(2,0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_list_slice_CodeLocation():
    logic = """
len(list[ff:]) > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# TODO
# update test
# no any return error
def test_mypy_simple_flag_CodeLocation():
    logic = """
f["MY_FLAG"]"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(2, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


# TODO
# update test
# no any return error
def test_mypy_simple_flag_get():
    logic = """
f.get("MY_FLAG")"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(2, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_function_with_vars_CodeLocation():
    logic = """my_func(a.b.c, x.y.z)"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_function_with_vars_using_import_function_CodeLocation():
    logic = """
import math
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_function_with_vars_using_import_function_2_CodeLocation():
    logic = """
import pandas as pd, math
import numpy as np
import datetime
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_function_with_vars_using_import_value_CodeLocation():
    logic = """
import math
my_func(math.PI, math.E)"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"syntax": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_import_from_CodeLocation():
    logic = """
from sqlalchemy import create_engine
from flask import render_template
engine = create_engine('oracle+cx_oracle://' + username + ':' + password + '@' + dsn_tns)"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"return": {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_import_with_as_CodeLocation():
    logic = """
import math as m
x = m.sqrt(10)
y = m.sqrt(x)
return y > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_import_with_as_2_CodeLocation():
    logic = """
from math import sqrt as sq
return sq(ff1) > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_import_with_as_3_CodeLocation():
    logic = """
from math import cos as c, sin as s
x = c(10)
y = s(10)
return x > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_import_with_as_4_CodeLocation():
    logic = """
from math import (cos as c, sin as s)
x = c(10)
y = s(10)
return y > 10"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_import_with_as_5_CodeLocation():
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



def test_mypy_special_lambda_CodeLocation():
    logic = """
high_ord_func = lambda x, func: x + func(x)
return high_ord_func(ff1, lambda x: x * x) > ff2"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {'no-any-return': {CodeLocation(3, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_invalid():
    logic = """
improper 
x = =  f
x = 12
y = = =  q2@"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {'return': {CodeLocation(0, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_odd_text():
    logic = "improper"
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {'no-any-return': {CodeLocation(1, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_empty_space_clean_up():
    logic = """    

x = 10


return ff1 > x"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_empty_space_clean_up_single_line():
    logic = """    

ff1 > 10


"""
    flag_feeders = {"ff1": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_empty_space_clean_up_single_multi_line_return():
    logic = """    

ff1 > 10 and \
    ff1 < 20 and \
    ff2 > 100


"""
    flag_feeders = {"ff1": int, "ff2": float}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_non_boolean_flag_feeder_only():
    logic = "ff1"
    flag_feeders = {"ff1": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {"return-value": {CodeLocation(1, 0)}}
    assert test_output.warnings == {}


def test_mypy_boolean_flag_feeder_only():
    logic = "ff1"
    flag_feeders = {"ff1": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_boolean_flag_feeder_only_2():
    logic = """

ff1

"""
    flag_feeders = {"ff1": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_determine_invalid_return():
    logic = """return 10 + 20"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {"return-value": {CodeLocation(1, 0)}}
    assert test_output.warnings == {}


def test_mypy_hardcoded_boolean():
    logic = """return True"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_determine_invalid_return_2():
    logic = """return cat + dog"""
    flag_feeders = {"cat": bool, "dog": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {"return-value": {CodeLocation(1, 0)}}
    assert test_output.warnings == {}


def test_mypy_determine_dynamic_flag_feeders():
    logic = """return cat or dog"""
    flag_feeders = {}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"no-any-return": {CodeLocation(1, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_determine_one_dynamic_flag_feeders():
    logic = """return cat < 10 or dog"""
    flag_feeders = {"cat": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_determine_known_flag_feeders_wrong_type():
    logic = """return cat or dog"""
    flag_feeders = {"cat": str, "dog": int}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"str, int": {CodeLocation(1, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_unreachable():
    logic = """\
if True or cat:
    return True

return dog"""
    flag_feeders = {"cat": bool, "dog": bool}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {"unreachable": {CodeLocation(1, 0), CodeLocation(4, 0)}}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}


def test_mypy_equality():
    logic = """return dog == 'dog'"""
    flag_feeders = {"dog": str}
    test_output = validate_returns_boolean(determine_variables(logic), flag_feeders)
    assert test_output.other_errors == {}
    assert test_output.validation_errors == {}
    assert test_output.warnings == {}






