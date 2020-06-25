from flagging.FlagFeederApp import determine_variables, CodeLocation
from flagging.VariableInformation import VariableInformation
from flagging.ModuleInformation import ModuleInformation


def test_determine_flag_feeders_logic_and_CodeLocation():
    logic = """cat and dog"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None),
                                                 VariableInformation("dog", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {
        CodeLocation(line_number=1, column_offset=0)}
    assert test_output.used_variables[VariableInformation("dog", None)] == {
        CodeLocation(line_number=1, column_offset=8)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_flag_feeders_logic_or_CodeLocation():
    logic = """man or woman"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("man", None),
                                                 VariableInformation("woman", None)}
    assert test_output.used_variables[VariableInformation("man", None)] == {
        CodeLocation(line_number=1, column_offset=0)}
    assert test_output.used_variables[VariableInformation("woman", None)] == {
        CodeLocation(line_number=1, column_offset=7)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_flag_feeder_conditional_CodeLocation():
    logic = """cat = 100
return cat < 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {
        CodeLocation(line_number=2, column_offset=7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("cat", None)}
    assert test_output.assigned_variables[VariableInformation("cat", None)] == {
        CodeLocation(line_number=1, column_offset=0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_flag_feeder_if_statement_CodeLocation():
    logic = """x = (ff1 or ff2)
y = (ff3 + ff4)
if y > 100:
    return ff5 != x
else:
    return ff5 == x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("y", None), VariableInformation("x", None),
                                                 VariableInformation("ff1", None), VariableInformation('ff2', None),
                                                 VariableInformation("ff3", None), VariableInformation("ff4", None),
                                                 VariableInformation("ff5", None)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(line_number=3, column_offset=3)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(line_number=4, column_offset=18),
                                                                          CodeLocation(line_number=6, column_offset=18)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(1, 5)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(1, 12)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(2, 5)}
    assert test_output.used_variables[VariableInformation("ff4", None)] == {CodeLocation(2, 11)}
    assert test_output.used_variables[VariableInformation("ff5", None)] == {
        CodeLocation(line_number=4, column_offset=11),
        CodeLocation(line_number=6, column_offset=11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("y", None), VariableInformation("x", None)}
    assert test_output.assigned_variables["y"] == {CodeLocation(line_number=2, column_offset=0)}
    assert test_output.assigned_variables["x"] == {CodeLocation(line_number=1, column_offset=0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.errors == []


def test_normal_expression_CodeLocation():
    logic = """
def my_add(x, y): return x + y
z = my_add(2, 3)
return ff1 > z"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("z", None),
                                                 VariableInformation("x", None), VariableInformation("y", None)}
    assert test_output.used_variables[VariableInformation('ff1', None)] == {CodeLocation(3, 7)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(3, 13)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(1, 25)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(1, 29)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x", None), VariableInformation("y", None),
                                                     VariableInformation("z", None)}
    assert test_output.assigned_variables[VariableInformation("x", None)] == {CodeLocation(1, 11)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(1, 14)}
    assert test_output.referenced_functions.keys() == {"my_add"}
    assert test_output.defined_functions.keys() == {"my_add"}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_equals_operation_CodeLocation():
    logic = """return ff1 == ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {
        VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
        VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_less_than_operation_CodeLocation():
    logic = """return ff1 >= ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {
        VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
        VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_greater_than_operation_CodeLocation():
    logic = """return ff1 <= ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None)}
    assert test_output.used_variables == {
        VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=7)},
        VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=14)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_add_operation_CodeLocation():
    logic = """
test_1 = ff1 + ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None), VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None), VariableInformation("test_1", None)}
    assert test_output.used_variables == {
        VariableInformation("test_1", None): {CodeLocation(line_number=2, column_offset=13)},
        VariableInformation("ff1", None): {CodeLocation(line_number=1, column_offset=9)},
        VariableInformation("ff2", None): {CodeLocation(line_number=1, column_offset=15)},
        VariableInformation("ff3", None): {CodeLocation(line_number=2, column_offset=7)}}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {
        VariableInformation("test_1", None): {CodeLocation(line_number=1, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_subtraction_operation_CodeLocation():
    logic = """
test_1 = ff1 - ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {
        CodeLocation(line_number=1, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {
        CodeLocation(line_number=1, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {
        CodeLocation(line_number=2, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {
        CodeLocation(line_number=2, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {
        VariableInformation('test_1', None): {CodeLocation(line_number=1, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_multiplication_operation_CodeLocation():
    logic = """
test_1 = ff1 * ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {
        CodeLocation(line_number=1, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {
        CodeLocation(line_number=1, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {
        CodeLocation(line_number=2, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {
        CodeLocation(line_number=2, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {
        VariableInformation('test_1', None): {CodeLocation(line_number=1, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_division_operation_CodeLocation():
    logic = """
test_1 = ff1 / ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {
        CodeLocation(line_number=1, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {
        CodeLocation(line_number=1, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {
        CodeLocation(line_number=2, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {
        CodeLocation(line_number=2, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {
        VariableInformation('test_1', None): {CodeLocation(line_number=1, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_modulo_operation_CodeLocation():
    logic = """
test_1 = ff1 % ff2
return ff3 < test_1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("test_1", None)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {
        CodeLocation(line_number=2, column_offset=9)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {
        CodeLocation(line_number=2, column_offset=15)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {
        CodeLocation(line_number=3, column_offset=7)}
    assert test_output.used_variables[VariableInformation("test_1", None)] == {
        CodeLocation(line_number=3, column_offset=13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("test_1", None)}
    assert test_output.assigned_variables == {
        VariableInformation('test_1', None): {CodeLocation(line_number=2, column_offset=0)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(3, 7), CodeLocation(6, 15),
                                                                            CodeLocation(7, 15), CodeLocation(9, 5),
                                                                            CodeLocation(17, 15)}
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
    assert test_output.errors == []


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
    assert test_output.used_variables[VariableInformation("f", None)] == {CodeLocation(2, 10), CodeLocation(3, 24),
                                                                          CodeLocation(5, 24)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(1, 16), CodeLocation(1, 22)}
    assert test_output.used_variables[VariableInformation("b", None)] == {CodeLocation(1, 26), CodeLocation(1, 34)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(3, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(5, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("f", None)}
    assert test_output.assigned_variables == {VariableInformation("f", None): {CodeLocation(1, 0)}}
    assert test_output.referenced_functions.keys() == {VariableInformation("reduce", None)}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(2, 3),
                                                                                     CodeLocation(3, 17),
                                                                                     CodeLocation(5, 17)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_comprehension_CodeLocation():
    logic = """
sum = reduce(lambda x, y: x + y, [cat ** cat for cat in range(4)])
return sum > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("sum", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("cat", None)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(1, 26)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(1, 30)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {CodeLocation(1, 34), CodeLocation(1, 41)}
    assert test_output.used_variables[VariableInformation("sum", None)] == {CodeLocation(2, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("sum", None),
                                                     VariableInformation("cat", None)}
    assert test_output.assigned_variables[VariableInformation("sum", None)] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables[VariableInformation("cat", None)] == {CodeLocation(1, 49)}
    assert test_output.referenced_functions.keys() == {VariableInformation("reduce", None),
                                                       VariableInformation("range", None)}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(1, 6)}
    assert test_output.referenced_functions[VariableInformation("range", None)] == {CodeLocation(1, 56)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables[VariableInformation("numbers", None)] == {CodeLocation(2, 30)}
    assert test_output.used_variables[VariableInformation("result", None)] == {CodeLocation(3, 15), CodeLocation(4, 26),
                                                                               CodeLocation(6, 26)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(2, 23), CodeLocation(2, 27)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(3, 3)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(4, 11)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(6, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("numbers", None),
                                                     VariableInformation("result", None)}
    assert test_output.assigned_variables[VariableInformation("numbers", None)] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables[VariableInformation("result", None)] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("map", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(2, 9)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(3, 10),
                                                                                   CodeLocation(4, 21),
                                                                                   CodeLocation(6, 21)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(4, 17)}
    assert test_output.referenced_functions[VariableInformation("min", None)] == {CodeLocation(6, 17)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_map_lambda_CodeLocation():
    logic = """
a = [1,2,3,4]
b = [17,12,11,10]
c = [-1,-4,5,9]
my_map_list = list(map(lambda x,y,z:x+y-z, a,b,c))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("a", None),
                                                 VariableInformation("b", None),
                                                 VariableInformation("c", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("z", None)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(4, 43)}
    assert test_output.used_variables[VariableInformation("b", None)] == {CodeLocation(4, 45)}
    assert test_output.used_variables[VariableInformation("c", None)] == {CodeLocation(4, 47)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(4, 36)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(4, 38)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(4, 40)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a", None),
                                                     VariableInformation("b", None),
                                                     VariableInformation("c", None),
                                                     VariableInformation("my_map_list", None)}
    assert test_output.assigned_variables[VariableInformation("a", None)] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables[VariableInformation("b", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("c", None)] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables[VariableInformation("my_map_list", None)] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("list", None),
                                                       VariableInformation("map", None)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(4, 14)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(4, 19)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_lambda_expression_CodeLocation():
    logic = """                               
add = (lambda x, y: x + y)(2, 3)              
return ff1 == add"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("add", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None)}
    assert test_output.used_variables[VariableInformation("add", None)] == {CodeLocation(2, 14)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(2, 7)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(1, 20)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(1, 24)}
    assert test_output.assigned_variables.keys() == {VariableInformation("add", None)}
    assert test_output.assigned_variables[VariableInformation("add", None)] == {CodeLocation(1, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables.keys() == {VariableInformation("a_list", None),
                                                 VariableInformation("y_list", None),
                                                 VariableInformation("a", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("x", None)}
    assert test_output.used_variables[VariableInformation("a_list", None)] == {CodeLocation(4, 9), CodeLocation(10, 46)}
    assert test_output.used_variables[VariableInformation("y_list", None)] == {CodeLocation(6, 8), CodeLocation(7, 16)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(4, 4), CodeLocation(5, 21),
                                                                          CodeLocation(6, 29)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(7, 3), CodeLocation(8, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(10, 11)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(10, 40)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a_list", None),
                                                     VariableInformation("y_list", None)}
    assert test_output.assigned_variables == {VariableInformation("a_list", None): {CodeLocation(2, 0)},
                                              VariableInformation("y_list", None): {CodeLocation(3, 0)}}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation.create_var(["ff1", "isin"]),
                                                       VariableInformation("abs", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation.create_var(["y_list", "add"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(5, 7),
                                                                                                  CodeLocation(6, 19)}
    assert test_output.referenced_functions[VariableInformation.create_var(["ff1", "isin"])] == {CodeLocation(7, 3)}
    assert test_output.referenced_functions[VariableInformation("abs", None)] == {CodeLocation(5, 17)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(7, 12)}
    assert test_output.referenced_functions[VariableInformation("min", None)] == {CodeLocation(10, 17)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(10, 21)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(10, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["y_list", "add"])] == {CodeLocation(6, 8)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules == {ModuleInformation("math"): {CodeLocation(1, 7)}}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


#TODO
# Issue #1
# don't allow user to overwrite module
def test_math_overwrite_module_CodeLocation():
    logic = """
import math
math = math.sqrt(10)
return ff1 > math"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("math", None),
                                                 VariableInformation("ff1", None)}
    assert test_output.used_variables[VariableInformation("math", None)] == {CodeLocation(3, 13)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(3, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("math", None)}
    assert test_output.assigned_variables[VariableInformation("math", None)] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(2, 7)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules == {ModuleInformation("math"): {CodeLocation(1, 7)}}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_math_expression_2_CodeLocation():
    logic = """
import math
x = 10
y = math.sqrt(10)
return ff1 > x"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x", None),
                                                 VariableInformation("ff1", None)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(4, 13)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(4, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x", None),
                                                     VariableInformation("y", None)}
    assert test_output.assigned_variables[VariableInformation("x", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("y", None)] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(3, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules == {ModuleInformation("math"): {CodeLocation(1, 7)}}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_math_expression_3_CodeLocation():
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
    assert test_output.used_variables.keys() == {VariableInformation("a_list", None),
                                                 VariableInformation("y_list", None),
                                                 VariableInformation("a", None), VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None), VariableInformation("x", None)}
    assert test_output.used_variables[VariableInformation("a_list", None)] == {CodeLocation(4, 9), CodeLocation(7, 15),
                                                                               CodeLocation(10, 46)}
    assert test_output.used_variables[VariableInformation("y_list", None)] == {CodeLocation(6, 8)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(4, 4), CodeLocation(5, 21),
                                                                          CodeLocation(6, 32)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(7, 3), CodeLocation(8, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(10, 11)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(10, 40)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a_list", None),
                                                     VariableInformation("y_list", None)}
    assert test_output.assigned_variables[VariableInformation("a_list", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("y_list", None)] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation("abs", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation.create_var(["y_list", "append"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(5, 7),
                                                                                                  CodeLocation(6, 22)}
    assert test_output.referenced_functions[VariableInformation("abs", None)] == {CodeLocation(5, 17)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(7, 11)}
    assert test_output.referenced_functions[VariableInformation("min", None)] == {CodeLocation(10, 17)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(10, 21)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(10, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["y_list", "append"])] == {
        CodeLocation(6, 8)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_math_expression_4_CodeLocation():
    logic = """
import math
x.y = 10
a.b = math.sqrt(10)
return ff1 > x.y"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["x", "y"]),
                                                 VariableInformation("ff1", None)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y"])] == {CodeLocation(4, 13)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(4, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["x", "y"]),
                                                     VariableInformation.create_var(["a", "b"])}
    assert test_output.assigned_variables[VariableInformation.create_var(["x", "y"])] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation.create_var(["a", "b"])] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(3, 6)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules == {ModuleInformation("math"): {CodeLocation(1, 7)}}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables.keys() == {VariableInformation("a_list", None),
                                                 VariableInformation("y_list", None),
                                                 VariableInformation("a", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("z", None)}
    assert test_output.used_variables[VariableInformation("a_list", None)] == {CodeLocation(5, 9), CodeLocation(11, 46)}
    assert test_output.used_variables[VariableInformation("y_list", None)] == {CodeLocation(7, 8), CodeLocation(8, 16)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(5, 4), CodeLocation(6, 21),
                                                                          CodeLocation(7, 29)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(8, 3), CodeLocation(9, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(11, 11)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(11, 40)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(6, 34)}
    assert test_output.assigned_variables.keys() == {"a_list", "y_list", "ff1", "ff2", "z"}
    assert test_output.assigned_variables["a_list"] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables["y_list"] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables["ff1"] == {CodeLocation(4, 1)}
    assert test_output.assigned_variables["ff2"] == {CodeLocation(4, 6)}
    assert test_output.assigned_variables["z"] == {CodeLocation(4, 11)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["math", "sqrt"]),
                                                       VariableInformation.create_var(["ff1", "isin"]),
                                                       VariableInformation("abs", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation.create_var(["y_list", "add"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(6, 7),
                                                                                                  CodeLocation(7, 19)}
    assert test_output.referenced_functions[VariableInformation.create_var(["ff1", "isin"])] == {CodeLocation(8, 3)}
    assert test_output.referenced_functions["abs"] == {CodeLocation(6, 17)}
    assert test_output.referenced_functions["max"] == {CodeLocation(8, 12)}
    assert test_output.referenced_functions["min"] == {CodeLocation(11, 17)}
    assert test_output.referenced_functions["list"] == {CodeLocation(11, 21)}
    assert test_output.referenced_functions["map"] == {CodeLocation(11, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["y_list", "add"])] == {CodeLocation(7, 8)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules == {ModuleInformation("math"): {CodeLocation(1, 7)}}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_tuple_assignment_CodeLocation():
    logic = """
(x, y, z) = (-11, 2, 3)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {VariableInformation("x", None),
                                                     VariableInformation("y", None),
                                                     VariableInformation("z", None)}
    assert test_output.assigned_variables == {VariableInformation("x", None): {CodeLocation(2, 1)},
                                              VariableInformation("y", None): {CodeLocation(2, 4)},
                                              VariableInformation("z", None): {CodeLocation(2, 7)}}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_object_CodeLocation():
    logic = """
a.b.c.d.e > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c", "d", "e"])}
    assert test_output.used_variables == {
        VariableInformation.create_var(["a", "b", "c", "d", "e"]): {CodeLocation(2, 0)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_object_function_CodeLocation():
    logic = """
a.b.c() > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {VariableInformation.create_var(["a", "b"]): {CodeLocation(2, 0)}}
    assert test_output.assigned_variables == {}
    assert test_output.referenced_functions == {VariableInformation.create_var(["a", "b", "c"]): {CodeLocation(2, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_object_function_2_CodeLocation():
    logic = """
a.b.c > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"])}
    assert test_output.used_variables == {VariableInformation.create_var(["a", "b", "c"]): {CodeLocation(2, 0)}}
    assert test_output.assigned_variables == {}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_feeder_function_function_CodeLocation():
    logic = """ff1.lower() == 'my value'"""
    test_output = determine_variables(logic)
    assert test_output.used_variables == {VariableInformation("ff1", None): {CodeLocation(1, 0)}}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions == {VariableInformation.create_var(["ff1", "lower"]): {CodeLocation(1, 0)}}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_determine_flag_feeders_CodeLocation():
    logic = """
unused1, unused2 = fish, bird
return cat < 10 and fish > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("cat", None),
                                                 VariableInformation("fish", None),
                                                 VariableInformation("bird", None)}
    assert test_output.used_variables[VariableInformation("cat", None)] == {CodeLocation(3, 7)}
    assert test_output.used_variables[VariableInformation("fish", None)] == {CodeLocation(2, 19), CodeLocation(3, 20)}
    assert test_output.used_variables[VariableInformation("bird", None)] == {CodeLocation(2, 25)}
    assert test_output.assigned_variables.keys() == {VariableInformation("unused1", None),
                                                     VariableInformation("unused2", None)}
    assert test_output.assigned_variables[VariableInformation("unused1", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("unused2", None)] == {CodeLocation(2, 9)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables.keys() == {VariableInformation("a", None),
                                                 VariableInformation("b", None),
                                                 VariableInformation("c", None),
                                                 VariableInformation("map_step", None),
                                                 VariableInformation("filter_step", None),
                                                 VariableInformation("reduce_step", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("z", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(5, 40), CodeLocation(8, 7)}
    assert test_output.used_variables[VariableInformation("b", None)] == {CodeLocation(5, 42), CodeLocation(10, 9)}
    assert test_output.used_variables[VariableInformation("c", None)] == {CodeLocation(5, 44)}
    assert test_output.used_variables[VariableInformation("map_step", None)] == {CodeLocation(6, 43)}
    assert test_output.used_variables[VariableInformation("filter_step", None)] == {CodeLocation(7, 56)}
    assert test_output.used_variables[VariableInformation("reduce_step", None)] == {CodeLocation(8, 13),
                                                                                    CodeLocation(10, 15)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(5, 33), CodeLocation(6, 36),
                                                                          CodeLocation(7, 39), CodeLocation(7, 44)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(5, 35), CodeLocation(7, 46),
                                                                          CodeLocation(7, 53)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(5, 37)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(11, 11), CodeLocation(13, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(9, 11), CodeLocation(13, 17)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a", None),
                                                     VariableInformation("b", None),
                                                     VariableInformation("c", None),
                                                     VariableInformation("map_step", None),
                                                     VariableInformation("filter_step", None),
                                                     VariableInformation("reduce_step", None)}
    assert test_output.assigned_variables[VariableInformation("a", None)] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("b", None)] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables[VariableInformation("c", None)] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("list", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation("filter", None),
                                                       VariableInformation("reduce", None),
                                                       VariableInformation("max", None)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(5, 11),
                                                                                   CodeLocation(6, 14),
                                                                                   CodeLocation(7, 14)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(5, 16)}
    assert test_output.referenced_functions[VariableInformation("filter", None)] == {CodeLocation(6, 19)}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(7, 19)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(8, 3),
                                                                                  CodeLocation(10, 5)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables.keys() == {VariableInformation("a", None),
                                                 VariableInformation("b", None),
                                                 VariableInformation("c", None),
                                                 VariableInformation("x", None),
                                                 VariableInformation("y", None),
                                                 VariableInformation("z", None),
                                                 VariableInformation("ff1", None),
                                                 VariableInformation("ff2", None),
                                                 VariableInformation("ff3", None),
                                                 VariableInformation("d", None)}
    assert test_output.used_variables[VariableInformation("a", None)] == {CodeLocation(7, 112), CodeLocation(8, 7),
                                                                          CodeLocation(9, 21)}
    assert test_output.used_variables[VariableInformation("b", None)] == {CodeLocation(7, 114), CodeLocation(10, 9),
                                                                          CodeLocation(11, 21)}
    assert test_output.used_variables[VariableInformation("c", None)] == {CodeLocation(7, 116), CodeLocation(12, 9),
                                                                          CodeLocation(13, 21)}
    assert test_output.used_variables[VariableInformation("x", None)] == {CodeLocation(7, 24), CodeLocation(7, 29),
                                                                          CodeLocation(7, 64), CodeLocation(7, 105)}
    assert test_output.used_variables[VariableInformation("y", None)] == {CodeLocation(7, 39), CodeLocation(7, 107)}
    assert test_output.used_variables[VariableInformation("z", None)] == {CodeLocation(7, 109)}
    assert test_output.used_variables[VariableInformation("ff1", None)] == {CodeLocation(9, 11), CodeLocation(13, 11)}
    assert test_output.used_variables[VariableInformation("ff2", None)] == {CodeLocation(11, 11)}
    assert test_output.used_variables[VariableInformation("ff3", None)] == {CodeLocation(15, 11)}
    assert test_output.used_variables[VariableInformation("d", None)] == {CodeLocation(8, 13), CodeLocation(10, 15),
                                                                          CodeLocation(12, 15)}
    assert test_output.assigned_variables.keys() == {VariableInformation("a", None),
                                                     VariableInformation("b", None),
                                                     VariableInformation("c", None),
                                                     VariableInformation("d", None)}
    assert test_output.assigned_variables[VariableInformation("a", None)] == {CodeLocation(4, 0)}
    assert test_output.assigned_variables[VariableInformation("b", None)] == {CodeLocation(5, 0)}
    assert test_output.assigned_variables[VariableInformation("c", None)] == {CodeLocation(6, 0)}
    assert test_output.assigned_variables[VariableInformation("d", None)] == {CodeLocation(7, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("reduce", None),
                                                       VariableInformation("list", None),
                                                       VariableInformation("filter", None),
                                                       VariableInformation("map", None),
                                                       VariableInformation("max", None),
                                                       VariableInformation("min", None),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation("reduce", None)] == {CodeLocation(7, 4)}
    assert test_output.referenced_functions[VariableInformation("list", None)] == {CodeLocation(7, 42),
                                                                                   CodeLocation(7, 83)}
    assert test_output.referenced_functions[VariableInformation("filter", None)] == {CodeLocation(7, 47)}
    assert test_output.referenced_functions[VariableInformation("map", None)] == {CodeLocation(7, 88)}
    assert test_output.referenced_functions[VariableInformation("max", None)] == {CodeLocation(8, 3),
                                                                                  CodeLocation(11, 17),
                                                                                  CodeLocation(12, 5)}
    assert test_output.referenced_functions[VariableInformation("min", None)] == {CodeLocation(9, 17),
                                                                                  CodeLocation(10, 5),
                                                                                  CodeLocation(13, 17)}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(7, 68)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math"),
                                                     ModuleInformation("pandas")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(2, 7)}
    assert test_output.referenced_modules[ModuleInformation("pandas")] == {CodeLocation(3, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_variables_in_list_CodeLocation():
    logic = """
animals = [cat, dog, fish]
return cat in animals"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("animals"),
                                                 VariableInformation("cat"),
                                                 VariableInformation("dog"),
                                                 VariableInformation("fish")}
    assert test_output.used_variables[VariableInformation("animals")] == {CodeLocation(3, 14)}
    assert test_output.used_variables[VariableInformation("cat")] == {CodeLocation(2, 11), CodeLocation(3, 7)}
    assert test_output.used_variables[VariableInformation("dog")] == {CodeLocation(2, 16)}
    assert test_output.used_variables[VariableInformation("fish")] == {CodeLocation(2, 21)}
    assert test_output.assigned_variables.keys() == {"animals"}
    assert test_output.assigned_variables[VariableInformation("animals")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_with_no_as_CodeLocation():
    logic = """
with method(item):
    return ff1 > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation("item")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 11)}
    assert test_output.used_variables[VariableInformation("item")] == {CodeLocation(2, 12)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation('method')}
    assert test_output.referenced_functions[VariableInformation("method")] == {CodeLocation(2, 5)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_with_using_as_CodeLocation():
    logic = """
with method(ff1, ff2) as my_with:
    return my_with > 100"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation("ff2"),
                                                 VariableInformation("my_with")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(2, 12)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(2, 17)}
    assert test_output.used_variables[VariableInformation("my_with")] == {CodeLocation(3, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("my_with")}
    assert test_output.assigned_variables[VariableInformation("my_with")] == {CodeLocation(2, 25)}
    assert test_output.referenced_functions.keys() == {VariableInformation('method')}
    assert test_output.referenced_functions[VariableInformation("method")] == {CodeLocation(2, 5)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_func_CodeLocation():
    logic = """
def myfunc(xyz):
    return xyz+10
myfunc(ff1) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation("xyz")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(4, 7)}
    assert test_output.used_variables[VariableInformation("xyz")] == {CodeLocation(3, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("xyz")}
    assert test_output.assigned_variables[VariableInformation("xyz")] == {CodeLocation(2, 11)}
    assert test_output.referenced_functions.keys() == {VariableInformation("myfunc")}
    assert test_output.referenced_functions[VariableInformation("myfunc")] == {CodeLocation(4, 0)}
    assert test_output.defined_functions.keys() == {VariableInformation("myfunc")}
    assert test_output.defined_functions[VariableInformation("myfunc")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_list_comprehension_CodeLocation():
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
    assert test_output.used_variables[VariableInformation("names")] == {CodeLocation(5, 14)}
    assert test_output.used_variables[VariableInformation.create_var(["name", "id"])] == {CodeLocation(2, 13)}
    assert test_output.used_variables[VariableInformation("target")] == {CodeLocation(3, 60)}
    assert test_output.used_variables[VariableInformation.create_var(["three_up_stack_node", "targets"])] == {
        CodeLocation(3, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["ast", "Tuple"])] == {CodeLocation(3, 68)}
    assert test_output.used_variables[VariableInformation("name")] == {CodeLocation(4, 42)}
    assert test_output.used_variables[VariableInformation.create_var(["target", "elts"])] == {CodeLocation(4, 16)}
    assert test_output.used_variables[VariableInformation.create_var(["ast", "Name"])] == {CodeLocation(4, 48)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("names", None),
                                                     VariableInformation("target", None),
                                                     VariableInformation("name", None)}
    assert test_output.assigned_variables[VariableInformation("names")] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("target")] == {CodeLocation(3, 8)}
    assert test_output.assigned_variables[VariableInformation("name")] == {CodeLocation(4, 8)}
    assert test_output.referenced_functions.keys() == {VariableInformation("set", None),
                                                       VariableInformation("isinstance", None)}
    assert test_output.referenced_functions[VariableInformation("set")] == {CodeLocation(2, 8)}
    assert test_output.referenced_functions[VariableInformation("isinstance")] == {CodeLocation(3, 49),
                                                                                   CodeLocation(4, 31)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_class_reference_CodeLocation():
    logic = """
isinstance(ff1, int)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation("int")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(2, 11)}
    assert test_output.used_variables[VariableInformation("int")] == {CodeLocation(2, 16)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("isinstance")}
    assert test_output.referenced_functions[VariableInformation("isinstance")] == {CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_class_reference_CodeLocation():
    logic = """
isinstance(a.b.Class, ff1)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1"),
                                                 VariableInformation.create_var(["a", "b", "Class"])}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(2, 22)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "Class"])] == {CodeLocation(2, 11)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("isinstance")}
    assert test_output.referenced_functions[VariableInformation("isinstance")] == {CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_object_reference_CodeLocation():
    logic = """
my_function(a.b.c, c.d.e)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["c", "d", "e"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(2, 12)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(2, 19)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["my_function"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["my_function"])] == {CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_object_reference_complex_function_CodeLocation():
    logic = """
a.b.c.my_function(a.b.c, c.d.e)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["c", "d", "e"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(2, 18),
                                                                                           CodeLocation(2, 0)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(2, 25)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["a", "b", "c", "my_function"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["a", "b", "c", "my_function"])] == {
        CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_object_function_reference_complex_function_CodeLocation():
    logic = """
a.b.c.my_function(a.b.c(), c.d.e())"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b"]),
                                                 VariableInformation.create_var(["c", "d"]),
                                                 VariableInformation.create_var(["a", "b", "c"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b"])] == {CodeLocation(2, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d"])] == {CodeLocation(2, 27)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                       VariableInformation.create_var(["c", "d", "e"]),
                                                       VariableInformation.create_var(["a", "b", "c", "my_function"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(2, 18)}
    assert test_output.referenced_functions[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(2, 27)}
    assert test_output.referenced_functions[VariableInformation.create_var(["a", "b", "c", "my_function"])] == {
        CodeLocation(2, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_generator_CodeLocation():
    logic = """
eggs = (x*2 for x in [1, 2, 3, 4, 5])
return 10 in eggs"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("eggs")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(2, 8)}
    assert test_output.used_variables[VariableInformation("eggs")] == {CodeLocation(3, 13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("eggs")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(2, 16)}
    assert test_output.assigned_variables[VariableInformation("eggs")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_generator_with_yield_CodeLocation():
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
    assert test_output.used_variables.keys() == {VariableInformation("n"),
                                                 VariableInformation("m"),
                                                 VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("n")] == {CodeLocation(7, 10), CodeLocation(8, 8)}
    assert test_output.used_variables[VariableInformation("m")] == {CodeLocation(10, 10)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(13, 10)}
    assert test_output.assigned_variables.keys() == {VariableInformation("n"),
                                                     VariableInformation("m"),
                                                     VariableInformation("k")}
    assert test_output.assigned_variables[VariableInformation("n")] == {CodeLocation(4, 4)}
    assert test_output.assigned_variables[VariableInformation("m")] == {CodeLocation(8, 4)}
    assert test_output.assigned_variables[VariableInformation("k")] == {CodeLocation(11, 4)}
    assert test_output.referenced_functions.keys() == {VariableInformation("my_gen"),
                                                       VariableInformation("print")}
    assert test_output.referenced_functions[VariableInformation("my_gen")] == {CodeLocation(15, 12)}
    assert test_output.referenced_functions[VariableInformation("print")] == {CodeLocation(5, 4), CodeLocation(9, 4),
                                                                              CodeLocation(12, 4)}
    assert test_output.defined_functions.keys() == {VariableInformation("my_gen")}
    assert test_output.defined_functions[VariableInformation("my_gen")] == {CodeLocation(3, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_comprehension_2_CodeLocation():
    logic = """
eggs = [x*2 for x in [1, 2, 3, 4, 5]]
return 10 in eggs"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("eggs")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(2, 8)}
    assert test_output.used_variables[VariableInformation("eggs")] == {CodeLocation(3, 13)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("eggs")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(2, 16)}
    assert test_output.assigned_variables[VariableInformation("eggs")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_fizzbuzz_comprehension_CodeLocation():
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
    assert test_output.used_variables.keys() == {VariableInformation("n"),
                                                 VariableInformation("fizzbuzz")}
    assert test_output.used_variables[VariableInformation("n")] == {CodeLocation(3, 16),
                                                                    CodeLocation(3, 23),
                                                                    CodeLocation(3, 38),
                                                                    CodeLocation(4, 17),
                                                                    CodeLocation(4, 24),
                                                                    CodeLocation(5, 17),
                                                                    CodeLocation(5, 24),
                                                                    CodeLocation(6, 9)}
    assert test_output.used_variables[VariableInformation("fizzbuzz")] == {CodeLocation(9, 19)}
    assert test_output.assigned_variables.keys() == {VariableInformation("n"),
                                                     VariableInformation("fizzbuzz")}
    assert test_output.assigned_variables[VariableInformation("n")] == {CodeLocation(7, 8)}
    assert test_output.assigned_variables[VariableInformation("fizzbuzz")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("range")}
    assert test_output.referenced_functions[VariableInformation("range")] == {CodeLocation(7, 13)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_simple_set_return_another_CodeLocation():
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


def test_simple_function_dont_use_CodeLocation():
    logic = """
def my_function():
    k = 4
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("k")}
    assert test_output.assigned_variables[VariableInformation("k")] == {CodeLocation(3, 4)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == {VariableInformation("my_function")}
    assert test_output.defined_functions[VariableInformation("my_function")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_simple_function_dont_use_complex_CodeLocation():
    logic = """
def my_function():
    a.b.k = 4
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["a", "b", "k"])}
    assert test_output.assigned_variables[VariableInformation.create_var(["a", "b", "k"])] == {CodeLocation(3, 4)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == {VariableInformation("my_function")}
    assert test_output.defined_functions[VariableInformation("my_function")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_assign():
    logic = """
x.y.z = 5"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.assigned_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_use():
    logic = """
x.y.z > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_in_function_CodeLocation():
    logic = """
def my_function():
    x = 2
    a.b.k = 4
    return 1
return ff1"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(6, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["a", "b", "k"]),
                                                     VariableInformation("x")}
    assert test_output.assigned_variables[VariableInformation.create_var(["a", "b", "k"])] == {CodeLocation(4, 4)}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(3, 4)}
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == {VariableInformation("my_function")}
    assert test_output.defined_functions[VariableInformation("my_function")] == {CodeLocation(2, 4)}
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_complex_assign():
    logic = """
x.y.z = 5"""
    test_output = determine_variables(logic)
    assert test_output.assigned_variables.keys() == {VariableInformation.create_var(["x", "y", "z"])}


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
    assert test_output.used_variables[VariableInformation("result")] == {CodeLocation(3, 11)}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(2, 13)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(2, 17)}
    assert test_output.used_variables[VariableInformation("zde")] == {CodeLocation(6, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(5, 19)}
    assert test_output.used_variables[VariableInformation.create_var(["b", "c"])] == {CodeLocation(5, 26)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(5, 35)}
    assert test_output.used_variables[VariableInformation("ezde")] == {CodeLocation(9, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(8, 21)}
    assert test_output.used_variables[VariableInformation.create_var(["d", "e"])] == {CodeLocation(8, 28)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(8, 37)}
    assert test_output.used_variables[VariableInformation("fin")] == {CodeLocation(12, 11)}
    assert test_output.used_variables[VariableInformation.create_var(["e", "f", "g"])] == {CodeLocation(11, 19)}
    assert test_output.used_variables[VariableInformation.create_var(["f", "g"])] == {CodeLocation(11, 26)}
    assert test_output.used_variables[VariableInformation("ff3")] == {CodeLocation(11, 35)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None),
                                                     VariableInformation("zde", None),
                                                     VariableInformation("ezde", None),
                                                     VariableInformation("fin", None)}
    assert test_output.assigned_variables[VariableInformation("result")] == {CodeLocation(2, 4)}
    assert test_output.assigned_variables[VariableInformation("zde")] == {CodeLocation(5, 4)}
    assert test_output.assigned_variables[VariableInformation("ezde")] == {CodeLocation(8, 4)}
    assert test_output.assigned_variables[VariableInformation("fin")] == {CodeLocation(11, 4)}
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
    assert test_output.referenced_functions[VariableInformation("fun_0")] == {CodeLocation(2, 21)}
    assert test_output.referenced_functions[VariableInformation("zde_func")] == {CodeLocation(5, 10)}
    assert test_output.referenced_functions[VariableInformation("ezde_func")] == {CodeLocation(8, 11)}
    assert test_output.referenced_functions[VariableInformation("fun_func")] == {CodeLocation(11, 10)}
    assert test_output.referenced_functions[VariableInformation.create_var(["b", "c", "d"])] == {CodeLocation(5, 26)}
    assert test_output.referenced_functions[VariableInformation.create_var(["d", "e", "f"])] == {CodeLocation(8, 28)}
    assert test_output.referenced_functions[VariableInformation.create_var(["f", "g", "h"])] == {CodeLocation(11, 26)}
    assert test_output.referenced_functions[VariableInformation("fun_1")] == {CodeLocation(5, 40)}
    assert test_output.referenced_functions[VariableInformation("fun_2")] == {CodeLocation(8, 42)}
    assert test_output.referenced_functions[VariableInformation("fun_3")] == {CodeLocation(11, 40)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables[VariableInformation("result")] == {CodeLocation(4, 15)}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(3, 17)}
    assert test_output.used_variables[VariableInformation("y")] == {CodeLocation(3, 21)}
    assert test_output.used_variables[VariableInformation("zde")] == {CodeLocation(7, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(6, 23)}
    assert test_output.used_variables[VariableInformation.create_var(["b", "c"])] == {CodeLocation(6, 30)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(6, 39)}
    assert test_output.used_variables[VariableInformation("ezde")] == {CodeLocation(10, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["c", "d", "e"])] == {CodeLocation(9, 25)}
    assert test_output.used_variables[VariableInformation.create_var(["d", "e"])] == {CodeLocation(9, 32)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(9, 41)}
    assert test_output.used_variables[VariableInformation("fin")] == {CodeLocation(13, 15)}
    assert test_output.used_variables[VariableInformation.create_var(["e", "f", "g"])] == {CodeLocation(12, 23)}
    assert test_output.used_variables[VariableInformation.create_var(["f", "g"])] == {CodeLocation(12, 30)}
    assert test_output.used_variables[VariableInformation("ff3")] == {CodeLocation(12, 39)}
    assert test_output.assigned_variables.keys() == {VariableInformation("result", None),
                                                     VariableInformation("zde", None),
                                                     VariableInformation("ezde", None),
                                                     VariableInformation("fin", None)}
    assert test_output.assigned_variables[VariableInformation("result")] == {CodeLocation(3, 8)}
    assert test_output.assigned_variables[VariableInformation("zde")] == {CodeLocation(6, 8)}
    assert test_output.assigned_variables[VariableInformation("ezde")] == {CodeLocation(9, 8)}
    assert test_output.assigned_variables[VariableInformation("fin")] == {CodeLocation(12, 8)}
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
    assert test_output.referenced_functions[VariableInformation("fun_0")] == {CodeLocation(3, 25)}
    assert test_output.referenced_functions[VariableInformation("zde_func")] == {CodeLocation(6, 14)}
    assert test_output.referenced_functions[VariableInformation("ezde_func")] == {CodeLocation(9, 15)}
    assert test_output.referenced_functions[VariableInformation("fun_func")] == {CodeLocation(12, 14)}
    assert test_output.referenced_functions[VariableInformation.create_var(["b", "c", "d"])] == {CodeLocation(6, 30)}
    assert test_output.referenced_functions[VariableInformation.create_var(["d", "e", "f"])] == {CodeLocation(9, 32)}
    assert test_output.referenced_functions[VariableInformation.create_var(["f", "g", "h"])] == {CodeLocation(12, 30)}
    assert test_output.referenced_functions[VariableInformation("fun_1")] == {CodeLocation(6, 44)}
    assert test_output.referenced_functions[VariableInformation("fun_2")] == {CodeLocation(9, 46)}
    assert test_output.referenced_functions[VariableInformation("fun_3")] == {CodeLocation(12, 44)}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(14, 7)}
    assert test_output.defined_functions.keys() == {VariableInformation("my_func", None)}
    assert test_output.defined_functions[VariableInformation("my_func")] == {CodeLocation(1, 4)}
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
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(3, 7)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.defined_classes["MyClass"] == {CodeLocation(1, 6)}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


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
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(4, 17)}
    assert test_output.used_variables[VariableInformation.create_var(["my_val", "val"])] == {CodeLocation(5, 7)}
    assert test_output.assigned_variables.keys() == {VariableInformation("my_val")}
    assert test_output.assigned_variables[VariableInformation("my_val")] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("MyClass")}
    assert test_output.referenced_functions[VariableInformation("MyClass")] == {CodeLocation(4, 9)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == {"MyClass"}
    assert test_output.defined_classes["MyClass"] == {CodeLocation(1, 6)}
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_dictionary_CodeLocation():
    logic = """
dict[ff] > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("dict"),
                                                 VariableInformation("ff")}
    assert test_output.used_variables == {VariableInformation("dict"): {CodeLocation(1, 0)},
                                          VariableInformation("ff"): {CodeLocation(1, 5)}}
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
    assert test_output.used_variables[VariableInformation("list")] == {CodeLocation(1, 4)}
    assert test_output.used_variables[VariableInformation("ff")] == {CodeLocation(1, 9)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("len")}
    assert test_output.referenced_functions[VariableInformation("len")] == {CodeLocation(1, 0)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_simple_flag_CodeLocation():
    logic = """
f["MY_FLAG"]"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("f")}
    assert test_output.used_variables[VariableInformation("f")] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == set()
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == set()
    assert test_output.referenced_flags.keys() == {"MY_FLAG"}
    assert test_output.referenced_flags["MY_FLAG"] == {CodeLocation(1, 3)}
    assert test_output.errors == []


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
    assert test_output.referenced_flags["MY_FLAG"] == {CodeLocation(1, 7)}
    assert test_output.errors == []


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


def test_function_with_vars_using_import_function_CodeLocation():
    logic = """
import math
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(2, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(2, 36)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func"),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(2, 0)}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(2, 8),
                                                                                                  CodeLocation(2, 26)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_function_with_vars_using_import_function_2_CodeLocation():
    logic = """
import pandas as pd, math
import numpy as np
import datetime
my_func(math.sqrt(a.b.c), math.sqrt(x.y.z))"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["a", "b", "c"]),
                                                 VariableInformation.create_var(["x", "y", "z"])}
    assert test_output.used_variables[VariableInformation.create_var(["a", "b", "c"])] == {CodeLocation(4, 18)}
    assert test_output.used_variables[VariableInformation.create_var(["x", "y", "z"])] == {CodeLocation(4, 36)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func"),
                                                       VariableInformation.create_var(["math", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation("my_func")] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions[VariableInformation.create_var(["math", "sqrt"])] == {CodeLocation(4, 8),
                                                                                                  CodeLocation(4, 26)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math"),
                                                     ModuleInformation("pandas", "pd"),
                                                     ModuleInformation("numpy", "np"),
                                                     ModuleInformation("datetime")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 21)}
    assert test_output.referenced_modules[ModuleInformation("pandas", "pd")] == {CodeLocation(1, 7)}
    assert test_output.referenced_modules[ModuleInformation("numpy", "np")] == {CodeLocation(2, 7)}
    assert test_output.referenced_modules[ModuleInformation("datetime")] == {CodeLocation(3, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_function_with_vars_using_import_value_CodeLocation():
    logic = """
import math
my_func(math.PI, math.E)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation.create_var(["math", "PI"]),
                                                 VariableInformation.create_var(["math", "E"])}
    assert test_output.used_variables[VariableInformation.create_var(["math", "PI"])] == {CodeLocation(2, 8)}
    assert test_output.used_variables[VariableInformation.create_var(["math", "E"])] == {CodeLocation(2, 17)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("my_func")}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 7)}
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
    assert test_output.used_variables[VariableInformation("username")] == {CodeLocation(3, 47)}
    assert test_output.used_variables[VariableInformation("password")] == {CodeLocation(3, 64)}
    assert test_output.used_variables[VariableInformation("dsn_tns")] == {CodeLocation(3, 81)}
    assert test_output.assigned_variables.keys() == {VariableInformation("engine")}
    assert test_output.assigned_variables["engine"] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("create_engine")}
    assert test_output.referenced_functions[VariableInformation("create_engine")] == {CodeLocation(3, 9)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("sqlalchemy"),
                                                     ModuleInformation("flask")}
    assert test_output.referenced_modules[ModuleInformation("sqlalchemy")] == {CodeLocation(1, 5)}
    assert test_output.referenced_modules[ModuleInformation("flask")] == {CodeLocation(2, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_CodeLocation():
    logic = """
import math as m
x = m.sqrt(10)
y = m.sqrt(x)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x")}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["m", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["m", "sqrt"])] == {CodeLocation(2, 4),
                                                                                               CodeLocation(3, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math", "m")}
    assert test_output.referenced_modules[ModuleInformation("math", "m")] == {CodeLocation(1, 7)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_2_CodeLocation():
    logic = """
from math import sqrt as sq
return sq(ff1) > 10"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("ff1")}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(2, 10)}
    assert test_output.assigned_variables.keys() == set()
    assert test_output.referenced_functions.keys() == {VariableInformation("sq")}
    assert test_output.referenced_functions[VariableInformation("sq")] == {CodeLocation(2, 7)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_3_CodeLocation():
    logic = """
from math import cos as c, sin as s
x = c(10)
y = s(10)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("c"),
                                                       VariableInformation("s")}
    assert test_output.referenced_functions[VariableInformation("c")] == {CodeLocation(2, 4)}
    assert test_output.referenced_functions[VariableInformation("s")] == {CodeLocation(3, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_4_CodeLocation():
    logic = """
from math import (cos as c, sin as s)
x = c(10)
y = s(10)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == set()
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(2, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(3, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("c"),
                                                       VariableInformation("s")}
    assert test_output.referenced_functions[VariableInformation("c")] == {CodeLocation(2, 4)}
    assert test_output.referenced_functions[VariableInformation("s")] == {CodeLocation(3, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math")}
    assert test_output.referenced_modules[ModuleInformation("math")] == {CodeLocation(1, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_import_with_as_5_CodeLocation():
    logic = """
import math as m
from m import sqrt as sq
x = m.sqrt(10)
y = m.sqrt(x)"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x")}
    assert test_output.used_variables[VariableInformation("x")] == {CodeLocation(4, 11)}
    assert test_output.assigned_variables.keys() == {VariableInformation("x"),
                                                     VariableInformation("y")}
    assert test_output.assigned_variables[VariableInformation("x")] == {CodeLocation(3, 0)}
    assert test_output.assigned_variables[VariableInformation("y")] == {CodeLocation(4, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation.create_var(["m", "sqrt"])}
    assert test_output.referenced_functions[VariableInformation.create_var(["m", "sqrt"])] == {CodeLocation(3, 4),
                                                                                               CodeLocation(4, 4)}
    assert test_output.defined_functions.keys() == set()
    assert test_output.defined_classes.keys() == set()
    assert test_output.referenced_modules.keys() == {ModuleInformation("math", "m"),
                                                     ModuleInformation("m")}
    assert test_output.referenced_modules[ModuleInformation("math", "m")] == {CodeLocation(1, 7)}
    assert test_output.referenced_modules[ModuleInformation("m")] == {CodeLocation(2, 5)}
    assert test_output.referenced_flags.keys() == set()
    assert test_output.errors == []


def test_special_lambda_CodeLocation():
    logic = """
high_ord_func = lambda x, func: x + func(x)
return high_ord_func(ff1, lambda x: x * x) > ff2"""
    test_output = determine_variables(logic)
    assert test_output.used_variables.keys() == {VariableInformation("x"),
                                                 VariableInformation("ff1"),
                                                 VariableInformation("ff2")}
    assert test_output.used_variables[VariableInformation('x')] == {CodeLocation(1, 32),
                                                                    CodeLocation(1, 41),
                                                                    CodeLocation(2, 36),
                                                                    CodeLocation(2, 40)}
    assert test_output.used_variables[VariableInformation("ff1")] == {CodeLocation(2, 21)}
    assert test_output.used_variables[VariableInformation("ff2")] == {CodeLocation(2, 45)}
    assert test_output.assigned_variables.keys() == {VariableInformation("high_ord_func")}
    assert test_output.assigned_variables[VariableInformation("high_ord_func")] == {CodeLocation(1, 0)}
    assert test_output.referenced_functions.keys() == {VariableInformation("func"),
                                                       VariableInformation("high_ord_func")}
    assert test_output.referenced_functions[VariableInformation("func")] == {CodeLocation(1, 36)}
    assert test_output.referenced_functions[VariableInformation("high_ord_func")] == {CodeLocation(2, 7)}
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
    assert test_output.used_variables[VariableInformation("improper")] == {CodeLocation(1, 0)}
    assert test_output.assigned_variables.keys() == {VariableInformation('x')}
    assert test_output.assigned_variables[VariableInformation('x')] == {CodeLocation(3, 0)}
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


