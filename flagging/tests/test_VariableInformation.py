from flagging.src.VariableInformation import VariableInformation


def test_Create_complex_VariableInformation_str():
    a = VariableInformation("a")
    b = VariableInformation("b", a)
    c = VariableInformation("c", b)

    assert "a.b.c" == str(a)
    assert "b.c" == str(b)
    assert "c" == str(c)

def test_Create_complex_VariableInformation_equality():
    a = VariableInformation("a")
    b = VariableInformation("b", a)
    c = VariableInformation("c", b)
    assert a.child == b
    assert b.child == c
    assert c.child is None
