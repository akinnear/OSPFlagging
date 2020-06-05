from flagging.src.VariableInformation import VariableInformation


def test_Create_complex_VariableInformation_str():
    a = VariableInformation("a")
    b = VariableInformation("b", a)
    c = VariableInformation("c", b)

    assert "a.b.c" == str(a)
    assert "[a.]b.c" == str(b)
    assert "[a.b.]c" == str(c)

def test_Create_complex_VariableInformation_equality():
    a = VariableInformation("a")
    b = VariableInformation("b", a)
    c = VariableInformation("c", b)
    assert a.child == b
    assert b.child == c
    assert c.child is None

def test_variable_information_as_key():
    a = VariableInformation("a")
    b = VariableInformation("b", a)
    c = VariableInformation("c", b)

    test_set = {a, b, c}
    assert a in test_set
    assert b in test_set
    assert c in test_set


