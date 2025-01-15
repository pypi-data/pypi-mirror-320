import server

def test_addition():
    assert server.addition(2, 3) == 5

def test_subtraction():
    assert server.subtraction(10, 3) == 7

def test_multiplication():
    assert server.multiplication(3, 5) == 20

def test_multiplication():
    assert server.multiplication(5, 0) == 0

def test_division():
    assert server.division(10, 5) == 2

def test_division():
    assert server.division(8, 0) == "cannot divide by zero"