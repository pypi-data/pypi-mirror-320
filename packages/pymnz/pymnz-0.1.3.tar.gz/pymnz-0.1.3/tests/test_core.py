import pymnz


def test_soma():
    resultado = pymnz.calculos.soma(10, 10)
    assert resultado == 20, 'Resultado inesperado'


def test_divisao():
    resultado = pymnz.calculos.divisao(10, 5)
    assert resultado == 2, 'Resultado inesperado'


def test_multiplicacao():
    resultado = pymnz.calculos.multiplicacao(10, 5)
    assert resultado == 50, 'Resultado inesperado'
