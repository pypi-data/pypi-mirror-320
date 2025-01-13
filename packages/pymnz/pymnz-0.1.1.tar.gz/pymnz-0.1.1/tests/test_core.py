from pymnz import core


def test_soma():
    resultado = core.soma(10, 20)
    assert resultado == 30
