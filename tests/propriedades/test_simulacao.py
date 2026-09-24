"""Invariantes da simulação, sob milhares de cenários (seção 8.2)."""

from datetime import date
from decimal import Decimal

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from irpf_exterior import Cambio, brl
from irpf_exterior.dominio.parametros import Aliquota
from irpf_exterior.formulas.projecao import Equilibrio, NuncaCompensa, SempreCompensa
from irpf_exterior.simulacao import (
    Cenario,
    EixoCambioFinal,
    Varredura,
    apurar,
    cambio_de_equilibrio,
    executar,
    juro_de_equilibrio,
    regime_vigente,
)

T_BR = Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1))
T_PT = Aliquota("T_pt", Decimal("0.28"), date(2024, 1, 1))
TOLERANCIA = Decimal("0.01")


def valores_brl() -> st.SearchStrategy[Decimal]:
    return st.decimals(min_value=Decimal("100"), max_value=Decimal("10000000"), places=2)


def cotacoes() -> st.SearchStrategy[Decimal]:
    return st.decimals(min_value=Decimal("0.5"), max_value=Decimal("50"), places=4)


def juros() -> st.SearchStrategy[Decimal]:
    return st.decimals(min_value=Decimal("-0.9"), max_value=Decimal("3"), places=4)


def cenario(I: Decimal, C_i: Decimal, J: Decimal, C_f: Decimal) -> Cenario:
    return Cenario(I=brl(I), C_i=Cambio(C_i), J_eu=J, C_f=Cambio(C_f))


@settings(max_examples=300)
@given(I=valores_brl(), C_i=cotacoes(), J=juros(), C_f=cotacoes())
def test_juro_projetado_volta_intacto(I: Decimal, C_i: Decimal, J: Decimal, C_f: Decimal) -> None:
    """Fórmulas 17 e 15 são inversas: projetar e reextrair devolve o mesmo juro."""
    apurada = apurar(cenario(I, C_i, J, C_f), T_br=T_BR, T_pt=T_PT)
    assert abs(apurada.J_eu.valor - J) < Decimal("0.000001")


@settings(max_examples=300)
@given(I=valores_brl(), C_i=cotacoes(), J=juros(), C_f=cotacoes())
def test_decomposicao_continua_fechando_sob_projecao(
    I: Decimal, C_i: Decimal, J: Decimal, C_f: Decimal
) -> None:
    """Mudar a parametrização não pode quebrar R_br = R_cc + R_eubr."""
    a = apurar(cenario(I, C_i, J, C_f), T_br=T_BR, T_pt=T_PT)
    soma = a.R_cc.valor.quantia + a.R_eubr.valor.quantia
    assert abs(soma - a.R_br.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), C_i=cotacoes(), J=juros(), C_f=cotacoes())
def test_no_regime_portugues_investir_sempre_compensa(
    I: Decimal, C_i: Decimal, J: Decimal, C_f: Decimal
) -> None:
    """Portugal tributa só o prêmio, então nunca engole o ganho cambial."""
    a = apurar(cenario(I, C_i, J, C_f), T_br=T_BR, T_pt=T_PT)
    assume(regime_vigente(a) == "Portugal")
    assume(a.R_eubr.valor.quantia > 0)
    assert a.V_inv.valor.quantia > 0


@settings(max_examples=200)
@given(
    I=valores_brl(),
    C_i=cotacoes(),
    J=st.decimals(min_value=Decimal("0.001"), max_value=Decimal("0.17"), places=4),
)
def test_no_cambio_de_equilibrio_a_vantagem_se_anula(I: Decimal, C_i: Decimal, J: Decimal) -> None:
    """A forma fechada da Fórmula 18 tem de bater com a apuração completa."""
    base = cenario(I, C_i, J, C_i)
    ponto = cambio_de_equilibrio(base, T_br=T_BR).valor
    assume(isinstance(ponto, Equilibrio))
    assert isinstance(ponto, Equilibrio)

    no_ponto = apurar(
        Cenario(I=base.I, C_i=base.C_i, J_eu=J, C_f=Cambio(ponto.valor)),
        T_br=T_BR,
        T_pt=T_PT,
    )
    assume(regime_vigente(no_ponto) == "Brasil")
    relativo = abs(no_ponto.V_inv.valor.quantia) / I
    assert relativo < Decimal("0.0001")


@settings(max_examples=200)
@given(I=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_no_juro_de_equilibrio_a_vantagem_se_anula(I: Decimal, C_i: Decimal, C_f: Decimal) -> None:
    """O mesmo para a Fórmula 19, pelo outro eixo."""
    base = cenario(I, C_i, Decimal("0"), C_f)
    minimo = juro_de_equilibrio(base, T_br=T_BR).valor
    assume(minimo > 0)  # com o câmbio em queda o equilíbrio é o próprio zero

    no_ponto = apurar(
        Cenario(I=base.I, C_i=base.C_i, J_eu=minimo, C_f=base.C_f), T_br=T_BR, T_pt=T_PT
    )
    assume(regime_vigente(no_ponto) == "Brasil")
    relativo = abs(no_ponto.V_inv.valor.quantia) / I
    assert relativo < Decimal("0.0001")


@settings(max_examples=200)
@given(I=valores_brl(), C_i=cotacoes(), J=juros(), C_f=cotacoes())
def test_juro_de_equilibrio_acompanha_o_sinal_da_variacao_cambial(
    I: Decimal, C_i: Decimal, J: Decimal, C_f: Decimal
) -> None:
    """Só há juro mínimo a bater quando o câmbio subiu; caindo, ele é negativo."""
    minimo = juro_de_equilibrio(cenario(I, C_i, J, C_f), T_br=T_BR).valor
    assert (minimo > 0) == (C_f > C_i)
    assert (minimo == 0) == (C_f <= C_i)


@settings(max_examples=100)
@given(I=valores_brl(), C_i=cotacoes(), J=juros())
def test_varredura_nao_altera_o_cenario_base(I: Decimal, C_i: Decimal, J: Decimal) -> None:
    """Imutabilidade: percorrer o eixo não toca no cenário que foi descrito."""
    base = cenario(I, C_i, J, C_i)
    varredura = Varredura(
        base=base,
        eixo=EixoCambioFinal((Decimal("3.00"), Decimal("7.00"))),
        T_br=T_BR,
        T_pt=T_PT,
    )
    list(executar(varredura))
    assert varredura.base == base
    assert base.C_f.valor == C_i


@settings(max_examples=200)
@given(C_i=cotacoes(), J=juros())
def test_acima_da_fronteira_nunca_existe_equilibrio(C_i: Decimal, J: Decimal) -> None:
    """A fronteira T_br/(1-T_br) separa os dois desfechos, sem exceção."""
    fronteira = T_BR.valor / (Decimal("1") - T_BR.valor)
    resultado = cambio_de_equilibrio(cenario(Decimal("10000"), C_i, J, C_i), T_br=T_BR).valor
    if J <= 0:
        assert isinstance(resultado, NuncaCompensa)
    elif fronteira < J:
        assert isinstance(resultado, SempreCompensa)
    else:
        assert isinstance(resultado, Equilibrio)
