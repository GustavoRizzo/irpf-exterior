"""Varredura: descrição barata, execução preguiçosa."""

from datetime import date
from decimal import Decimal

import pytest

from irpf_exterior import Cambio, brl
from irpf_exterior.simulacao import (
    Cenario,
    EixoCambioFinal,
    EixoJuro,
    Varredura,
    executar,
    intervalo,
    para_tabela,
    serie,
)
from irpf_exterior.simulacao.varredura import FONTE_SIMULADA

BASE = Cenario(
    I=brl("10000.00"),
    C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
    J_eu=Decimal("0.10"),
    C_f=Cambio(Decimal("6.00"), date(2025, 3, 10), "PTAX"),
)


def test_execucao_e_preguicosa() -> None:
    """Um valor inválido no fim do eixo não impede consumir o primeiro ponto.

    Se a varredura calculasse tudo de antemão, o câmbio negativo explodiria
    já na construção — é esta a garantia de que nada roda antes da hora.
    """
    eixo = EixoCambioFinal((Decimal("6.00"), Decimal("7.00"), Decimal("-1.00")))
    varredura = Varredura(base=BASE, eixo=eixo)

    primeiro = next(executar(varredura))
    assert primeiro.valor == Decimal("6.00")

    with pytest.raises(ValueError, match="câmbio deve ser positivo"):
        list(executar(varredura))


def test_construir_a_varredura_nao_calcula_nada() -> None:
    """Descrever é O(1): nem um câmbio inválido atrapalha a construção."""
    eixo = EixoCambioFinal((Decimal("-1.00"),) * 1000)
    assert Varredura(base=BASE, eixo=eixo).eixo.valores[0] == Decimal("-1.00")


def test_eixo_de_cambio_preserva_o_juro() -> None:
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("4.00", "8.00", "2.00")))
    pontos = list(executar(varredura))

    assert [p.valor for p in pontos] == [Decimal("4.00"), Decimal("6.00"), Decimal("8.00")]
    assert {p.cenario.J_eu for p in pontos} == {Decimal("0.10")}
    assert [p.cenario.C_f.valor for p in pontos] == [p.valor for p in pontos]


def test_eixo_de_juro_preserva_o_cambio() -> None:
    varredura = Varredura(base=BASE, eixo=EixoJuro(intervalo("0.00", "0.20", "0.10")))
    pontos = list(executar(varredura))

    assert [p.cenario.J_eu for p in pontos] == [
        Decimal("0.00"),
        Decimal("0.10"),
        Decimal("0.20"),
    ]
    assert {p.cenario.C_f.valor for p in pontos} == {Decimal("6.00")}


def test_cambio_simulado_nao_se_passa_por_cotacao_real() -> None:
    """A data do resgate é preservada (decide a vigência), a fonte não."""
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("4.00", "4.00", "1.00")))
    ponto = next(executar(varredura))

    assert ponto.cenario.C_f.fonte == FONTE_SIMULADA
    assert ponto.cenario.C_f.fonte != BASE.C_f.fonte
    assert ponto.cenario.C_f.data == date(2025, 3, 10)


def test_cada_ponto_carrega_a_apuracao_inteira() -> None:
    """Auditoria não se perde na simulação: dá para explicar qualquer ponto."""
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("6.00", "6.00", "1.00")))
    ponto = next(executar(varredura))

    assert ponto.apuracao.R_br.valor == brl("3200.00")
    assert ponto.apuracao.V_inv.valor == brl("720.00")


def test_serie_extrai_apenas_a_coluna_pedida() -> None:
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("4.00", "6.00", "2.00")))
    pares = list(serie(varredura, lambda a: a.V_inv.valor.quantia))

    assert [valor for valor, _ in pares] == [Decimal("4.00"), Decimal("6.00")]
    assert all(isinstance(v, Decimal) for _, v in pares)


def test_tabela_nomeia_a_coluna_conforme_o_eixo() -> None:
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("6.00", "6.00", "1.00")))
    linha = next(iter(para_tabela(varredura)))

    assert linha["C_f"] == Decimal("6.00")
    assert linha["R_liq"] == Decimal("2720.00")
    assert set(linha) >= {"C_f", "R_cc", "R_eubr", "R_br", "IR_ef", "R_liq", "V_inv"}


def test_tabela_do_eixo_de_juro_usa_o_outro_nome() -> None:
    varredura = Varredura(base=BASE, eixo=EixoJuro(intervalo("0.10", "0.10", "0.10")))
    linha = next(iter(para_tabela(varredura)))

    assert "J_eu" in linha
    assert "C_f" not in linha


def test_colunas_podem_ser_substituidas() -> None:
    varredura = Varredura(base=BASE, eixo=EixoCambioFinal(intervalo("6.00", "6.00", "1.00")))
    linha = next(iter(para_tabela(varredura, {"so_isso": lambda a: a.IR_ef.valor.quantia})))

    assert set(linha) == {"C_f", "so_isso"}
