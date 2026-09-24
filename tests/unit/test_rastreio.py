"""A árvore de auditoria e a omissão limpa de metadados ausentes (dor 2.7)."""

from decimal import Decimal

from irpf_exterior.dominio.moeda import brl
from irpf_exterior.formulas import r_br
from irpf_exterior.rastreio import Calculado, entrada, explicar


def test_entrada_sem_fonte_nao_inventa_metadado() -> None:
    assert str(entrada("F", brl("13200.00"))) == "BRL 13,200.00  ←  input F"


def test_entrada_com_fonte_a_exibe() -> None:
    texto = str(entrada("I", brl("10000.00"), "extrato: aporte"))
    assert texto.endswith("[extrato: aporte]")


def test_explicar_percorre_a_arvore_inteira() -> None:
    resultado = r_br(F=entrada("F", brl("13200.00")), I=entrada("I", brl("10000.00")))
    linhas = explicar(resultado).splitlines()
    assert linhas[0].startswith("BRL 3,200.00  ←  Fórmula 6: R_br = F - I")
    assert "  F:" in linhas
    assert any("BRL 13,200.00  ←  input F" in linha for linha in linhas)


def test_explicar_indenta_por_profundidade() -> None:
    folha = Calculado(valor=brl("1.00"), descricao="input X")
    raiz = Calculado(valor=brl("1.00"), descricao="raiz", entradas=(("X", folha),))
    linhas = explicar(raiz).splitlines()
    assert linhas[1] == "  X:"
    assert linhas[2].startswith("    BRL 1.00")


def test_decimais_sao_formatados_sem_ruido() -> None:
    calculado = Calculado(valor=Decimal("0.200000"), descricao="input C_pct")
    assert str(calculado).startswith("0.2  ←")
