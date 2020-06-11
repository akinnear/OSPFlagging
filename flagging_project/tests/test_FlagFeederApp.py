from flagging.FlagFeederApp import determine_variables, CodeLocation
from flagging.VariableInformation import VariableInformation


def test_determine_flag_feeders_logic_and_CodeLocation():
    logic = """cat and dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None),
                                                 VariableInformation("dog", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {CodeLocation(line_number=1, column_offset=0)}
    assert test_output.used_variables[VariableInformation("dog", None)] == {CodeLocation(line_number=1, column_offset=8)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeders_logic_or_CodeLocation():
    logic = """
man or woman"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("man", None),
                                                 VariableInformation("woman", None)}
    assert test_output.used_variables[VariableInformation("man", None)] == {CodeLocation(line_number=2, column_offset=0)}
    assert test_output.used_variables[VariableInformation("woman", None)] == {CodeLocation(line_number=2, column_offset=7)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeder_conditional_CodeLocation():
    logic = """
cat = 100
return cat < 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {CodeLocation(line_number=3, column_offset=7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("cat", None)}
    assert test_output.assigned_variables[VariableInformation("cat", None)] == {CodeLocation(line_number=2, column_offset=0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeder_if_statement_CodeLocation():
    logic = """
x = (ff1 or ff2)
y = (ff3 + ff4)
if y > 100:
    return ff5 != x
else:
    return ff5 == x"""
    # note the difference in location for used variables and variable assignment
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("y", None), VariableInformation("x", None),
                                                 VariableInformation("ff1", None), VariableInformation('ff2', None),
                                                 VariableInformation("ff3", None), VariableInformation("ff4", None),
                                                 VariableInformation("ff5", None)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(line_number=4, column_offset=3)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(line_number=5, column_offset=18),
                                               CodeLocation(line_number=7, column_offset=18)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(2, 5)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(2, 12)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(3, 5)}
    assert test_output.used_variables[VariableInformation("ff4", None)] == {CodeLocation(3, 11)}
    assert test_output.used_variables[VariableInformation("ff5", None)] == {CodeLocation(line_number=5, column_offset=11),
                                                 CodeLocation(line_number=7, column_offset=11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("y", None), VariableInformation("x", None)}
    assert test_output.assigned_variables["y"] == {CodeLocation(line_number=3, column_offset=0)}
    assert test_output.assigned_variables["x"] == {CodeLocation(line_number=2, column_offset=0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_normal_expression_keys():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"x", "y", "ff1", "z"}
    assert test_output.assigned_variables.keys() == {"x", "y", "z"}
    assert test_output.referenced_functions.keys() == {"my_add"}
    assert test_output.defined_functions.keys() == {"my_add"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()

#TODO
# bug in assigned variable code location for variables passed as parameters to functions
# expected x to have code location line 3, col 11
# actual x has code location line 2, col offset 0
def test_normal_expression_CodeLocation():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("z", None),
                                                 VariableInformation("x", None), VariableInformation("y", None)}
    assert test_output.used_variables[VariableInformation('ff1', None)] == {CodeLocation(4, 7)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(4, 13)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(2, 25)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(2, 29)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x", None), VariableInformation("y", None),
                                                     VariableInformation("z", None)}
    assert test_output.assigned_variables[VariableInformation("x", None)] == {CodeLocation(3, 11)}
    assert test_output.referenced_functions.keys() == {"my_add"}
    assert test_output.defined_functions.keys() == {"my_add"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_equals_operation_CodeLocation():
    logic = """return ff1 == ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
                                          VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_less_than_operation_CodeLocation():
    logic = """return ff1 >= ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
                                          VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_greater_than_operation_CodeLocation():
    logic = """return ff1 <= ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
                                          VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_add_operation_CodeLocation():
    logic = """
test_1 = ff1 + ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None), VariableInformation("test_1", None)}
    assert test_output.used_variables == {VariableInformation("test_1", None): {CodeLocation(line_number=3, column_offset=13)},
                                          VariableInformation("ff1", None): {CodeLocation(line_number=2, column_offset=9)},
                                          VariableInformation("ff2", None): {CodeLocation(line_number=2, column_offset=15)},
                                          VariableInformation("ff3", None): {CodeLocation(line_number=3, column_offset=7)}}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {VariableInformation("test_1", None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_subtraction_operation_CodeLocation():
    logic = """
test_1 = ff1 - ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(line_number=2, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(line_number=2, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(line_number=3, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1",None)] == {CodeLocation(line_number=3, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {VariableInformation('test_1', None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_multiplication_operation_CodeLocation():
    logic = """
test_1 = ff1 * ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(line_number=2, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(line_number=2, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(line_number=3, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {CodeLocation(line_number=3, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {VariableInformation('test_1', None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_division_operation_CodeLocation():
    logic = """
test_1 = ff1 / ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(line_number=2, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(line_number=2, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(line_number=3, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {CodeLocation(line_number=3, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {VariableInformation('test_1', None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_modulo_operation_CodeLocation():
    logic = """
test_1 = ff1 % ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(line_number=2, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(line_number=2, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(line_number=3, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {CodeLocation(line_number=3, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {VariableInformation('test_1', None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeder_for_loop_CodeLocation():
    logic = """                                            
if ff4 >= 50:                                              
    if ff1 > 10:                                           
        return ff2 == True                                 
    elif ff2:                                              
        return ff1 < 10                                    
    elif ff3 > ff1:                                        
        return ff4 < 50                                    
elif ff1 < 10:                                             
    return ff5 == 'CAT'                                    
else:                                                      
    a = 10                                                 
    b = True                                               
    c = "CAR"                                              
    if ff5 == "DOG":                                       
        a = a + 10                                         
        return ff1 < a"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("ff4", None),
                                                 VariableInformation("ff5", None),
                                                 VariableInformation("a", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(3, 7), CodeLocation(6, 15), CodeLocation(7, 15), CodeLocation(9, 5), CodeLocation(17, 15)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(4, 15), CodeLocation(5, 9)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(7, 9)}
    assert test_output.used_variables[VariableInformation("ff4", None)] == {CodeLocation(2, 3), CodeLocation(8, 15)}
    assert test_output.used_variables[VariableInformation("ff5", None)] == {CodeLocation(10, 11), CodeLocation(15, 7)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(16, 12), CodeLocation(17, 21)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a", None),
                                                     VariableInformation("b", None),
                                                     VariableInformation("c", None)}
    assert test_output.assigned_variables[VariableInformation("a", None)] == {CodeLocation(12, 4), CodeLocation(16, 8)}
    assert test_output.assigned_variables[VariableInformation("b", None)] == {CodeLocation(13, 4)}
    assert test_output.assigned_variables[VariableInformation("c", None)] == {CodeLocation(14, 4)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_reduce_lambda_CodeLocation():
    logic = """                                  
f = lambda a,b: a if (a > b) else b              
if reduce(f, [47,11,42,102,13]) > 100:           
    return ff1 > reduce(f, [47,11,42,102,13])    
else:                                            
    return ff2 < reduce(f, [47,11,42,102,13])"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("a", None),
                                                 VariableInformation("b", None),
                                                 VariableInformation("f", None)}
    assert test_output.used_variables[VariableInformation("f", None)] == {CodeLocation(3, 10), CodeLocation(4, 24), CodeLocation(6, 24)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(2, 16), CodeLocation(2, 22)}
    assert test_output.used_variables[VariableInformation("b", None)] == {CodeLocation(2, 26), CodeLocation(2, 34)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(4, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(6, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("f", None)}
    assert test_output.assigned_variables == {VariableInformation("f", None): {CodeLocation(2, 0)}}
    assert test_output.referenced_functions.keys() == {VariableInformation("reduce", None)}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(3, 3),
                                                                                     CodeLocation(4, 17),
                                                                                     CodeLocation(6, 17)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_comprehension_CodeLocation():
    logic = """
sum = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
return sum > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("sum", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("cat", None)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(2, 26)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(2, 30)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {CodeLocation(2, 34), CodeLocation(2, 41)}
    assert test_output.used_variables[VariableInformation("sum", None)] == {CodeLocation(3, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("sum", None),
                                                     VariableInformation("cat", None)}
    assert test_output.assigned_variables[VariableInformation("sum", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("cat", None)] == {CodeLocation(2, 49)}
    assert test_output.referenced_functions.keys() == {VariableInformation("reduce", None),
                                                       VariableInformation("range", None)}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(2, 6)}
    assert test_output.referenced_functions[VariableInformation("range", None)] == {CodeLocation(2, 56)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_expression_CodeLocation():
    logic = """
numbers = (1, 2, 3, 4)
result = map(lambda x: x + x, numbers)
if ff1 in list(result):
    return ff2 > max(list(result))
else:
    return ff3 < min(list(result))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("numbers", None),
                                                 VariableInformation("result", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None)}
    assert test_output.used_variables[VariableInformation("numbers", None)] == {CodeLocation(3, 30)}
    assert test_output.used_variables[VariableInformation("result", None)] == {CodeLocation(4, 15), CodeLocation(5, 26), CodeLocation(7, 26)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(3, 23), CodeLocation(3, 27)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(4, 3)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(5, 11)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(7, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("numbers", None),
                                                     VariableInformation("result", None)}
    assert test_output.assigned_variables[VariableInformation("numbers", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("result", None)] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("map", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(3, 9)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(4, 10), CodeLocation(5, 21), CodeLocation(7, 21)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(5, 17)}
    assert test_output.referenced_functions[VariableInformation("min", None)] == {CodeLocation(7, 17)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_lambda_keys():
    logic = """
a = [1,2,3,4]
b = [17,12,11,10]
c = [-1,-4,5,9]
my_map_list = list(map(lambda x,y,z:x+y-z, a,b,c))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "x", "y", "z"}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "my_map_list"}
    assert test_output.referenced_functions.keys() == {"list", "map"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_lambda_CodeLocation():
    logic = """
a = [1,2,3,4]
b = [17,12,11,10]
c = [-1,-4,5,9]
my_map_list = list(map(lambda x,y,z:x+y-z, a,b,c))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "x", "y", "z"}
    assert test_output.used_variables["a"] == {CodeLocation(5, 43)}
    assert test_output.used_variables["b"] == {CodeLocation(5, 45)}
    assert test_output.used_variables["c"] == {CodeLocation(5, 47)}
    assert test_output.used_variables["x"] == {CodeLocation(5, 36)}
    assert test_output.used_variables["y"] == {CodeLocation(5, 38)}
    assert test_output.used_variables["z"] == {CodeLocation(5, 40)}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "my_map_list"}
    assert test_output.assigned_variables["a"] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables["b"] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables["c"] == {CodeLocation(4, 0)}
    assert test_output.assigned_variables["my_map_list"] == {CodeLocation(5, 0)}
    assert test_output.referenced_functions.keys() == {"list", "map"}
    assert test_output.referenced_functions["list"] == {CodeLocation(5, 14)}
    assert test_output.referenced_functions["map"] == {CodeLocation(5, 19)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_lambda_expression_keys():
    logic = """                               
add = (lambda x, y: x + y)(2, 3)              
return ff1 == add"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"add", "ff1", "x", "y"}
    assert test_output.assigned_variables.keys() == {"add"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_lambda_expression_CodeLocation():
    logic = """                               
add = (lambda x, y: x + y)(2, 3)              
return ff1 == add"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"add", "ff1", "x", "y"}
    assert test_output.used_variables["add"] == {CodeLocation(3, 14)}
    assert test_output.used_variables["ff1"] == {CodeLocation(3, 7)}
    assert test_output.used_variables["x"] == {CodeLocation(2, 20)}
    assert test_output.used_variables["y"] == {CodeLocation(2, 24)}
    assert test_output.assigned_variables.keys() == {"add"}
    assert test_output.assigned_variables["add"] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_math_expression_Keys():
    ''' changing ff1.isin(max(y_list))
    to ff2.ising(max(a_list))
    removes y_list from used_variable set
    despite y_list.add(math.sqrt(a))
    '''
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
for a in a_list:
    if math.sqrt(abs(a)) <= 4:
        y_list.append(math.sqrt(a))
if ff1 in (max(y_list)):
    return ff1
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("a_list", None),
                                                 VariableInformation("y_list", None),
                                                 VariableInformation("a", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("x", None)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a_list", None),
                                                 VariableInformation("y_list", None)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation("abs", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation.create_var(["y_list", "append"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {VariableInformation("math", None)}
    assert test_output.referenced_flags.keys() == set()


def test_math_expression_CodeLocation():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
for a in a_list:
    if math.sqrt(abs(a)) <= 4:
        y_list.add(math.sqrt(a))
if ff1.isin(max(y_list)):
    return ff1
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a_list", "y_list", "a", "ff1", "ff2", "x"}
    assert test_output.used_variables["a_list"] == {CodeLocation(5, 9), CodeLocation(11, 46)}
    assert test_output.used_variables["y_list"] == {CodeLocation(7, 8), CodeLocation(8, 16)}
    assert test_output.used_variables["a"] == {CodeLocation(5, 4), CodeLocation(6, 21), CodeLocation(7, 29)}
    assert test_output.used_variables["ff1"] == {CodeLocation(8, 3), CodeLocation(9, 11)}
    assert test_output.used_variables["ff2"] == {CodeLocation(11, 11)}
    assert test_output.used_variables["x"] == {CodeLocation(11, 40)}
    assert test_output.assigned_variables.keys() == {"a_list", "y_list"}
    assert test_output.assigned_variables == {"a_list": {CodeLocation(3, 0)}, "y_list": {CodeLocation(4, 0)}}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]), VariableInformation.create_var(["ff1", "isin"]),
     VariableInformation("abs", None), VariableInformation("max", None), VariableInformation("min", None),
     VariableInformation("list", None), VariableInformation("map", None), VariableInformation.create_var(["y_list", "add"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_modules == {"math": {CodeLocation(2, 0)}}
    assert test_output.referenced_flags.keys() == set()


def test_math_expression_2_keys():
    logic = """
import math
x = 10
y = math.sqrt(10)
return ff1 > x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"x", "ff1"}
    assert test_output.assigned_variables.keys() == {"x", "y"}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_flags.keys() == set()


def test_math_overwrite_module_CodeLocation():
    logic = """\
import math
math = math.sqrt(10)
return ff1 > math"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"math", "ff1"}
    assert test_output.used_variables["math"] == {CodeLocation(3, 13)}
    assert test_output.used_variables["ff1"] == {CodeLocation(3, 7)}
    assert test_output.assigned_variables.keys() == {"math"}
    assert test_output.assigned_variables["math"] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(2, 7)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_modules == {"math": {CodeLocation(1, 0)}}
    assert test_output.referenced_flags.keys() == set()


def test_math_expression_2_CodeLocation():
    logic = """
import math
x = 10
y = math.sqrt(10)
return ff1 > x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"x", "ff1"}
    assert test_output.used_variables["x"] == {CodeLocation(5, 13)}
    assert test_output.used_variables["ff1"] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {"x", "y"}
    assert test_output.assigned_variables["x"] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables["y"] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions["math.sqrt"] == {CodeLocation(4, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_modules == {"math": {CodeLocation(2, 0)}}
    assert test_output.referenced_flags.keys() == set()


def test_math_expression_3_Keys():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
for a in a_list:
    if math.sqrt(abs(a)) <= 4:
        y_list.append(math.sqrt(a))
if ff1 in (max(a_list)):
    return ff1
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("a_list", None), VariableInformation("y_list", None),
                                                 VariableInformation("a", None), VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None), VariableInformation("x", None)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a_list", None), VariableInformation("y_list", None)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]), VariableInformation("abs", None),
                                                       VariableInformation("max", None), VariableInformation("min", None),
                                                       VariableInformation("list", None), VariableInformation("map", None),
                                                       VariableInformation.create_var(["y_list", "append"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_flags.keys() == set()


def test_tuple_assignment_2_keys():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
(ff1, ff2, z) = ("potato", True, 12.8)
for a in a_list:
    if math.sqrt(abs(a)) <= 4 and z > 10:
        y_list.add(math.sqrt(a))
if ff1.isin(max(y_list)):
    return ff1
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a_list", "y_list", "a", "ff1", "ff2", "x", "z"}
    assert test_output.assigned_variables.keys() == {"a_list", "y_list", "ff1", "ff2", "z"}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation.create_var(["ff1", "isin"]),
                                                       "abs", "max", "min", "list", "map",
                                                        VariableInformation.create_var(["y_list", "add"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_flags.keys() == set()


def test_tuple_assignment_2_CodeLocation():
    logic = """
import math
a_list = [10, 13, 16, 19, 22, -212]
y_list = [1]
(ff1, ff2, z) = ("potato", True, 12.8)
for a in a_list:
    if math.sqrt(abs(a)) <= 4 and z > 10:
        y_list.add(math.sqrt(a))
if ff1.isin(max(y_list)):
    return ff1
else:
    return ff2 > min(list(map(lambda x: x**2, a_list)))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a_list", "y_list", "a", "ff1", "ff2", "x", "z"}
    assert test_output.assigned_variables.keys() == {"a_list", "y_list", "ff1", "ff2", "z"}
    assert test_output.assigned_variables["a_list"] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables["y_list"] == {CodeLocation(4, 0)}
    assert test_output.assigned_variables["ff1"] == {CodeLocation(5, 1)}
    assert test_output.assigned_variables["ff2"] == {CodeLocation(5, 6)}
    assert test_output.assigned_variables["z"] == {CodeLocation(5, 11)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation.create_var(["ff1", "isin"]), "abs", "max", "min", "list", "map",
                                                        VariableInformation.create_var(["y_list", "add"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(7, 7), CodeLocation(8, 19)}
    assert test_output.referenced_functions[VariableInformation.create_var(["ff1", "isin"])] == {CodeLocation(9, 3)}
    assert test_output.referenced_functions["abs"] == {CodeLocation(7, 17)}
    assert test_output.referenced_functions["max"] == {CodeLocation(9, 12)}
    assert test_output.referenced_functions["min"] == {CodeLocation(12, 17)}
    assert test_output.referenced_functions["list"] == {CodeLocation(12, 21)}
    assert test_output.referenced_functions["map"] == {CodeLocation(12, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["y_list", "add"])] == {CodeLocation(8, 8)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_modules == {"math": {CodeLocation(2, 0)}}
    assert test_output.referenced_flags.keys() == set()


def test_tuple_assignment_keys():
    logic = """
(x, y, z) = (-11, 2, 3)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {"x", "y", "z"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_tuple_assignment_CodeLocation():
    logic = """
(x, y, z) = (-11, 2, 3)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {"x", "y", "z"}
    assert test_output.assigned_variables == {"x": {CodeLocation(2, 1)}, "y": {CodeLocation(2, 4)}, "z": {CodeLocation(2, 7)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_object_keys():
    logic = """
a.b.c > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a.b.c"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_object_CodeLocation():
    logic = """
a.b.c.d.e > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a.b.c.d.e"}
    assert test_output.used_variables == {"a.b.c.d.e": {CodeLocation(2, 0)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_object_function_CodeLocation():
    logic = """
a.b.c() > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {VariableInformation.create_var(["a", "b"]): {CodeLocation(2, 0)}}
    assert test_output.assigned_variables == {}
    assert test_output.referenced_functions == {VariableInformation.create_var(["a", "b", "c"]): {CodeLocation(2, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_object_function_2_CodeLocation():
    logic = """
a.b.c > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"])}
    assert test_output.used_variables == {VariableInformation.create_var(["a", "b", "c"]): {CodeLocation(2, 0)}}
    assert test_output.assigned_variables == {}
    #assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["a", "b", "c"])}
    #assert test_output.referenced_functions == {VariableInformation.create_var(["a", "b", "c"]): {CodeLocation(2, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_feeder_function_function_CodeLocation():
    logic = """ff1.lower() == 'my value'"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {"ff1": {CodeLocation(1, 0)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions == {"ff1.lower": {CodeLocation(1, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeders_keys():
    logic = """
unused1, unused2 = fish, bird
return cat < 10 and fish > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"cat", "fish", "bird"}
    assert test_output.assigned_variables.keys() == {"unused1", "unused2"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_determine_flag_feeders_CodeLocation():
    logic = """
unused1, unused2 = fish, bird
return cat < 10 and fish > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"cat", "fish", "bird"}
    assert test_output.used_variables["cat"] == {CodeLocation(3, 7)}
    assert test_output.used_variables["fish"] == {CodeLocation(2, 19), CodeLocation(3, 20)}
    assert test_output.used_variables["bird"] == {CodeLocation(2, 25)}
    assert test_output.assigned_variables.keys() == {"unused1", "unused2"}
    assert test_output.assigned_variables["unused1"] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables["unused2"] == {CodeLocation(2, 9)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_filter_lambda_2_keys():
    logic = """    
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]
map_step = list(map(lambda x,y,z:x+y-z, a,b,c))
filter_step = list(filter(lambda x: x > 4, map_step))
reduce_step = list(reduce(lambda x, y: x if x>y else y, filter_step))
if max(a) in reduce_step:
    return ff2 > 10
elif max(b) in reduce_step:
    return ff1 < 10
else: 
    return ff1 + ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "map_step", "filter_step", "reduce_step", "x", "y", "z", "ff1",
                                          "ff2"}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "map_step", "filter_step", "reduce_step"}
    assert test_output.referenced_functions.keys() == {"list", "map", "filter", "reduce", "max"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_filter_lambda_2_CodeLocation():
    logic = """    
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]
map_step = list(map(lambda x,y,z:x+y-z, a,b,c))
filter_step = list(filter(lambda x: x > 4, map_step))
reduce_step = list(reduce(lambda x, y: x if x>y else y, filter_step))
if max(a) in reduce_step:
    return ff2 > 10
elif max(b) in reduce_step:
    return ff1 < 10
else: 
    return ff1 + ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "map_step", "filter_step", "reduce_step", "x", "y", "z",
                                                 "ff1", "ff2"}
    assert test_output.used_variables["a"] == {CodeLocation(5, 40), CodeLocation(8, 7)}
    assert test_output.used_variables["b"] == {CodeLocation(5, 42), CodeLocation(10, 9)}
    assert test_output.used_variables["c"] == {CodeLocation(5, 44)}
    assert test_output.used_variables["map_step"] == {CodeLocation(6, 43)}
    assert test_output.used_variables["filter_step"] == {CodeLocation(7, 56)}
    assert test_output.used_variables["reduce_step"] == {CodeLocation(8, 13), CodeLocation(10, 15)}
    assert test_output.used_variables["x"] == {CodeLocation(5, 33), CodeLocation(6, 36), CodeLocation(7, 39), CodeLocation(7, 44)}
    assert test_output.used_variables["y"] == {CodeLocation(5, 35), CodeLocation(7, 46), CodeLocation(7, 53)}
    assert test_output.used_variables["z"] == {CodeLocation(5, 37)}
    assert test_output.used_variables["ff1"] == {CodeLocation(11, 11), CodeLocation(13, 11)}
    assert test_output.used_variables["ff2"] == {CodeLocation(9, 11), CodeLocation(13, 17)}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "map_step", "filter_step", "reduce_step"}
    assert test_output.assigned_variables["a"] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables["b"] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables["c"] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {"list", "map", "filter", "reduce", "max"}
    assert test_output.referenced_functions["list"] == {CodeLocation(5, 11), CodeLocation(6, 14), CodeLocation(7, 14)}
    assert test_output.referenced_functions["map"] == {CodeLocation(5, 16)}
    assert test_output.referenced_functions["filter"] == {CodeLocation(6, 19)}
    assert test_output.referenced_functions["reduce"] == {CodeLocation(7, 19)}
    assert test_output.referenced_functions["max"] == {CodeLocation(8, 3), CodeLocation(10, 5)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_map_filter_lambda_keys():
    logic = """
import math
import pandas
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]    
d = reduce(lambda x, y: x if x>20 else y,(list(filter(lambda x: x > math.sqrt(10), list(map(lambda x,y,z:x+y-z, a,b,c))))))
if max(a) in d:
    return ff1 > min(a)
elif min(b) in d:
    return ff2 < max(b)
elif max(c) in d:
    return ff1 > min(c)
else:
    return ff3 == True"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "x", "y", "z", "ff1", "ff2", "ff3", "d"}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "d"}
    assert test_output.referenced_functions.keys() == {"reduce", "list", "filter", "map", "max", "min", VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == {"math", "pandas"}
    assert test_output.referenced_flags.keys() == set()


def test_map_filter_lambda_CodeLocation():
    logic = """
import math
import pandas
a = [1,2,3,4]
b = [17,12,11,10]        
c = [-1,-4,5,9]    
d = reduce(lambda x, y: x if x>20 else y,(list(filter(lambda x: x > math.sqrt(10), list(map(lambda x,y,z:x+y-z, a,b,c))))))
if max(a) in d:
    return ff1 > min(a)
elif min(b) in d:
    return ff2 < max(b)
elif max(c) in d:
    return ff1 > min(c)
else:
    return ff3 == True"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a", "b", "c", "x", "y", "z", "ff1", "ff2", "ff3", "d"}
    assert test_output.assigned_variables.keys() == {"a", "b", "c", "d"}
    assert test_output.referenced_functions.keys() == {"reduce", "list", "filter", "map", "max", "min", VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == {"math", "pandas"}
    assert test_output.referenced_flags.keys() == set()


def test_variables_in_list():
    logic = """
animals = [cat, dog, fish]
return cat in animals"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"animals", "cat", "dog", "fish"}
    assert test_output.assigned_variables.keys() == {"animals"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_with_no_as():
    logic = """
with method(item):
    return ff1 > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "item"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {'method'}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_with_using_as():
    logic = """
with method(ff1, ff2) as my_with:
    return my_with > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "ff2", "my_with"}
    assert test_output.assigned_variables.keys() == {"my_with"}
    assert test_output.referenced_functions.keys() == {'method'}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_func():
    logic = """
def myfunc(xyz):
    return xyz+10
myfunc(ff1) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "xyz"}
    assert test_output.assigned_variables.keys() == {"xyz"}
    assert test_output.referenced_functions.keys() == {"myfunc"}
    assert test_output.defined_functions.keys() == {"myfunc"}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_list_comprehension():
    logic = """
names = set([name.id 
    for target in three_up_stack_node.targets if isinstance(target, ast.Tuple) 
    for name in target.elts if isinstance(name, ast.Name)])
return ff1 in names"""
    test_output = determine_variables(logic)

    assert test_output.used_variables.keys() == {VariableInformation("names", None),
     VariableInformation.create_var(["name", "id"]),
     VariableInformation("target", None),
     VariableInformation.create_var(["three_up_stack_node", "targets"]),
     VariableInformation.create_var(["ast", "Tuple"]),
     VariableInformation("name", None),
     VariableInformation.create_var(["target", "elts"]),
     VariableInformation.create_var(["ast", "Name"]),
     VariableInformation("ff1", None)}

    assert test_output.assigned_variables.keys() == {VariableInformation("names", None),
                                                     VariableInformation("target", None),
                                                     VariableInformation("name", None)}
    assert test_output.referenced_functions.keys() == {VariableInformation("set", None),
                                                       VariableInformation("isinstance", None)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_class_reference():
    logic = """
isinstance(ff1, int)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "int"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"isinstance"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_complex_class_reference():
    logic = """
isinstance(a.b.Class, ff1)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", VariableInformation.create_var(["a", "b", "Class"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"isinstance"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_complex_object_reference():
    logic = """
my_function(a.b.c, c.d.e)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["c", "d", "e"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["my_function"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_complex_object_reference_complex_function():
    logic = """
a.b.c.my_function(a.b.c, c.d.e)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["c", "d", "e"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("a.b.c.my_function", None)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_complex_object_function_reference_complex_function():
    logic = """
a.b.c.my_function(a.b.c(), c.d.e())"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"a.b", "c.d", "a.b.c"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"a.b.c.my_function", "a.b.c", "c.d.e"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_generator():
    logic = """
eggs = (x*2 for x in [1, 2, 3, 4, 5])
return 10 in eggs"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"x", "eggs"}
    assert test_output.assigned_variables.keys() == {"x", "eggs"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_generator_with_yield():
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
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"n", "m", "ff1"}
    assert test_output.assigned_variables.keys() == {"n", "m", "k"}
    assert test_output.referenced_functions.keys() == {"my_gen", "print"}
    assert test_output.defined_functions.keys() == {"my_gen"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_comprehension_2():
    logic = """
eggs = [x*2 for x in [1, 2, 3, 4, 5]]
return 10 in eggs"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"x", "eggs"}
    assert test_output.assigned_variables.keys() == {"x", "eggs"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_fizzbuzz_comprehension():
    logic = """
fizzbuzz = [
    f'fizzbuzz {n}' if n % 3 == 0 and n % 5 == 0
    else f'fizz {n}' if n % 3 == 0
    else f'buzz {n}' if n % 5 == 0
    else n
    for n in range(100)
]
return 'not in' in fizzbuzz"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"n", "fizzbuzz"}
    assert test_output.assigned_variables.keys() == {"n", "fizzbuzz"}
    assert test_output.referenced_functions.keys() == {"range"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_simple_set_return_another():
    logic = """
k = 4
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1"}
    assert test_output.assigned_variables.keys() == {"k"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_simple_function_dont_use():
    logic = """
def my_function():
    k = 4
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1"}
    assert test_output.assigned_variables.keys() == {"k"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == {"my_function"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_simple_function_dont_use_complex():
    logic = """
def my_function():
    a.b.k = 4
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1"}
    assert test_output.assigned_variables.keys() == {"a.b.k"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == {"my_function"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_simple_function_dont_use_complex():
    logic = """
def my_function():
    a.b.k()
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "a.b"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"a.b.k"}
    assert test_output.defined_functions.keys() == {"my_function"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_unused_var():
    logic = """
k = 4
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1"}
    assert test_output.assigned_variables.keys() == {"k"}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_try_except_finally():
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
    assert test_output.used_variables.keys() == {VariableInformation("result", None), VariableInformation("x", None),
                                                 VariableInformation("y", None), VariableInformation("zde", None),
                                                 VariableInformation.create_var(["a", "b", "c"]), VariableInformation.create_var(["b", "c"]),
                                                 VariableInformation("ff1", None), VariableInformation("ezde", None),
                                                 VariableInformation.create_var(["c", "d", "e"]), VariableInformation.create_var(["d", "e"]),
                                                 VariableInformation("ff2", None), VariableInformation("fin", None),
                                                 VariableInformation.create_var(["e", "f", "g"]), VariableInformation.create_var(["f", "g"]),
                                                 VariableInformation("ff3", None)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None), VariableInformation("zde", None),
                                                     VariableInformation("ezde", None), VariableInformation("fin", None)}
    assert test_output.referenced_functions.keys() == {VariableInformation("fun_0", None), VariableInformation("zde_func", None),
                                                       VariableInformation("ezde_func", None), VariableInformation("fun_func", None),
                                                       VariableInformation.create_var(["b", "c", "d"]),
                                                       VariableInformation.create_var(["d", "e", "f"]),
                                                       VariableInformation.create_var(["f", "g", "h"]),
                                                       VariableInformation("fun_1", None), VariableInformation("fun_2", None), VariableInformation("fun_3", None)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_try_except_finally_in_defined_function():
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
    assert test_output.used_variables.keys() == {VariableInformation("result", None), VariableInformation("x", None),
                                                 VariableInformation("y", None), VariableInformation("zde", None),
                                                 VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["b", "c"]),
                                                 VariableInformation("ff1", None), VariableInformation("ezde", None),
                                                 VariableInformation.create_var(["c", "d", "e"]),
                                                 VariableInformation.create_var(["d", "e"]),
                                                 VariableInformation("ff2", None), VariableInformation("fin", None),
                                                 VariableInformation.create_var(["e", "f", "g"]),
                                                 VariableInformation.create_var(["f", "g"]),
                                                 VariableInformation("ff3", None)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None),
                                                     VariableInformation("zde", None),
                                                     VariableInformation("ezde", None),
                                                     VariableInformation("fin", None)}
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
    assert test_output.defined_functions.keys() == {VariableInformation("my_func", None)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_unused_class():
    logic = """
class MyClass:
    pass
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_used_class_CodeLocation():
    logic = """
class MyClass():
    def __init__(self, val=None):
        self.val = val
my_val = MyClass(ff1)
return my_val.val"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"ff1", "my_val.val"}
    assert test_output.used_variables["ff1"] == {CodeLocation(5, 17)}
    assert test_output.used_variables["my_val.val"] == {CodeLocation(6, 7)}
    assert test_output.assigned_variables.keys() == {"my_val"}
    assert test_output.referenced_functions.keys() == {"MyClass"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_dictionary_CodeLocation():
    logic = """
dict[ff] > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"dict", "ff"}
    assert test_output.used_variables == {"dict": {CodeLocation(2, 0)}, "ff": {CodeLocation(2, 5)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_list_slice_keys():
    logic = """
len(list[ff:]) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"list", "ff"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"len"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_list_slice_CodeLocation():
    logic = """
len(list[ff:]) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"list", "ff"}
    assert test_output.used_variables["ff"] == {CodeLocation(2, 9)}
    assert test_output.used_variables["list"] == {CodeLocation(2, 4)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"len"}
    assert test_output.referenced_functions == {"len": {CodeLocation(2, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_simple_flag():
    logic = """
f["MY_FLAG"]"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"f"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == {"MY_FLAG"}

#TODO
# Issue 3
def test_simple_flag_get():
    logic = """f.get("MY_FLAG")"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {"f"}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {"f.get"}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == {"MY_FLAG"}


def test_function_with_vars():
    logic = "my_func(a.b.c, x.y.z)"
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["my_func"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()


def test_function_with_vars_using_import_function():
    logic = """\
import math
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["my_func"]),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_flags.keys() == set()


def test_function_with_vars_using_import_value():
    logic = """\
import math
my_func(math.PI, math.E)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["math", "PI"]),
                                                 VariableInformation.create_var(["math", "E"])}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["my_func"])}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {"math"}
    assert test_output.referenced_flags.keys() == set()


def test_example():
    """Imagine code is:
    my_var = 1
    my_var = 2
    new_my_var = 3"""
    assigned_variables = dict()

    # First hit on name, imagine this code is in the visit_Name method or a helper function
    name_1 = "my_var"
    location_1 = CodeLocation(0, 0)  # First line
    assigned_variables_name_set = assigned_variables.setdefault(name_1,
                                                                set())  # Get first time if not there return empty set
    assigned_variables_name_set.add(location_1)

    # Second hit on name, imagine this code is in the visit_Name method or a helper function
    name_2 = "my_var"
    location_2 = CodeLocation(1, 0)  # Second line
    assigned_variables_name_set = assigned_variables.setdefault(name_2,
                                                                set())  # Get second time, will be there but this should be helper function
    assigned_variables_name_set.add(location_2)

    # First hit on new name, imagine this code is in the visit_Name method or a helper function
    name_3 = "new_my_var"
    location_3 = CodeLocation(2, 0)  # Second line
    assigned_variables_name_set = assigned_variables.setdefault(name_3,
                                                                set())  # Get second time, will be there but this should be helper function
    assigned_variables_name_set.add(location_3)

    # The parser comes along again and hits the same new_my_var variable
    name_4 = "new_my_var"
    location_4 = CodeLocation(2, 0)  # Second line
    assigned_variables_name_set = assigned_variables.setdefault(name_4,
                                                                set())  # Get second time, will be there but this should be helper function
    assigned_variables_name_set.add(location_4)

    print(assigned_variables)
    assert set(assigned_variables.keys()) == {"my_var", "new_my_var"}
    assert assigned_variables["my_var"] == {CodeLocation(0, 0), CodeLocation(1, 0)}
    assert assigned_variables["new_my_var"] == {CodeLocation(2, 0)}
