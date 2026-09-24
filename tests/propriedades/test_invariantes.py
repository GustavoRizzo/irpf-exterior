"""Invariantes que precisam valer para *qualquer* entrada (seção 8.2).

Um caso de teste confere um número; uma propriedade confere uma regra. As
regras aqui são as que, se quebrarem, produzem um resultado plausível e
errado — o tipo de erro que a biblioteca existe para impedir.
"""

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from irpf_exterior import ApuracaoResgate, Cambio, brl, eur
from irpf_exterior.dominio.parametros import Aliquota

T_BR = Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1))
T_PT = Aliquota("T_pt", Decimal("0.28"), date(2024, 1, 1))

TOLERANCIA = Decimal("0.01")


def valores_brl() -> st.SearchStrategy[Decimal]:
    """Quantias em reais plausíveis para um aporte ou resgate."""
    return st.decimals(min_value=Decimal("1"), max_value=Decimal("10000000"), places=2)


def cotacoes() -> st.SearchStrategy[Decimal]:
    """Cotações EUR/BRL plausíveis."""
    return st.decimals(min_value=Decimal("0.5"), max_value=Decimal("50"), places=4)


def apurar(I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal) -> ApuracaoResgate:
    """Monta uma apuração com alíquotas fixas, sem depender da tabela."""
    return ApuracaoResgate.de_cf(
        I=brl(I), F=brl(F), C_i=Cambio(C_i), C_f=Cambio(C_f), T_br=T_BR, T_pt=T_PT
    )


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_imposto_efetivo_nunca_e_menor_que_os_dois(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    a = apurar(I, F, C_i, C_f)
    assert a.IR_ef.valor >= a.IR_br.valor
    assert a.IR_ef.valor >= a.IR_ptbr.valor


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_prejuizo_nunca_gera_imposto_negativo(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    a = apurar(I, F, C_i, C_f)
    assert a.IR_br.valor.quantia >= 0
    assert a.IR_pt.valor.quantia >= 0
    assert a.IR_ptbr.valor.quantia >= 0


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_lucro_liquido_nunca_supera_o_bruto(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    a = apurar(I, F, C_i, C_f)
    assume(a.R_br.valor.quantia > 0)
    assert a.R_liq.valor <= a.R_br.valor


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C=cotacoes())
def test_com_cambio_constante_as_duas_bases_coincidem(I: Decimal, F: Decimal, C: Decimal) -> None:
    """Sem variação cambial, R_br é exatamente R_eu convertido."""
    a = apurar(I, F, C, C)
    convertido = a.R_eu.valor.quantia * C
    assert abs(convertido - a.R_br.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_o_que_resta_pagar_nunca_e_negativo(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """O Brasil zera a dívida, mas não devolve o excedente retido em Portugal."""
    a = apurar(I, F, C_i, C_f)
    restante = a.a_pagar_no_brasil()
    assert restante.quantia >= 0
    assert restante.quantia <= a.IR_br.valor.quantia


@settings(max_examples=300)
@given(
    I=valores_brl(),
    F=valores_brl(),
    C_i=cotacoes(),
    C_d=st.decimals(min_value=Decimal("-0.4"), max_value=Decimal("10"), places=4),
)
def test_construtores_de_cf_e_de_cd_concordam(
    I: Decimal, F: Decimal, C_i: Decimal, C_d: Decimal
) -> None:
    assume(C_i + C_d > 0)
    por_cd = ApuracaoResgate.de_cd(
        I=brl(I), F=brl(F), C_i=Cambio(C_i), C_d=C_d, T_br=T_BR, T_pt=T_PT
    )
    por_cf = apurar(I, F, C_i, C_i + C_d)
    assert por_cd.IR_ef.valor == por_cf.IR_ef.valor


@settings(max_examples=200)
@given(a=valores_brl(), b=valores_brl())
def test_somar_moedas_diferentes_sempre_levanta_type_error(a: Decimal, b: Decimal) -> None:
    with pytest.raises(TypeError):
        brl(a) + eur(b)  # type: ignore[operator]


@settings(max_examples=300)
@given(I=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_dinheiro_parado_rende_o_cambio_e_nao_paga_imposto(
    I: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """R_cc é o que o mesmo dinheiro teria rendido parado em conta (Fórmula 8).

    Se o valor resgatado for exatamente o aporte convertido pelo câmbio final,
    o rendimento tributável se resume ao ganho cambial.
    """
    F = (I / C_i * C_f).quantize(Decimal("0.01"))
    a = apurar(I, F, C_i, C_f)
    assert abs(a.R_cc.valor.quantia - a.R_br.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_decomposicao_do_rendimento_fecha_exatamente(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """R_br = R_cc + R_eubr: câmbio e aplicação cobrem todo o rendimento.

    É a invariante central das Fórmulas 14–16. Se ela falhar, a comparação
    "valeu a pena investir?" passa a mentir, sem que nada exploda.
    """
    a = apurar(I, F, C_i, C_f)
    soma = a.R_cc.valor.quantia + a.R_eubr.valor.quantia
    assert abs(soma - a.R_br.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_vantagem_equivale_ao_premio_menos_o_imposto(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """V_inv = R_liq - R_cc é sempre o mesmo que R_eubr - IR_ef."""
    a = apurar(I, F, C_i, C_f)
    equivalente = a.R_eubr.valor.quantia - a.IR_ef.valor.quantia
    assert abs(equivalente - a.V_inv.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_vantagem_nunca_supera_o_premio_da_aplicacao(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """O imposto nunca é negativo, então investir nunca rende mais que R_eubr."""
    a = apurar(I, F, C_i, C_f)
    assert a.V_inv.valor.quantia <= a.R_eubr.valor.quantia + TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_juro_da_aplicacao_tem_o_sinal_do_rendimento_em_euros(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    """J_eu só é positivo quando a aplicação de fato rendeu, em euros."""
    a = apurar(I, F, C_i, C_f)
    assert (a.J_eu.valor > 0) == (a.R_eu.valor.quantia > 0)
    assert (a.J_eu.valor < 0) == (a.R_eu.valor.quantia < 0)


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C=cotacoes())
def test_sem_variacao_cambial_todo_o_rendimento_vem_da_aplicacao(
    I: Decimal, F: Decimal, C: Decimal
) -> None:
    """Com C_i = C_f, R_cc é exatamente zero e R_eubr carrega todo o R_br."""
    a = apurar(I, F, C, C)
    assert a.R_cc.valor.quantia == 0
    assert abs(a.R_eubr.valor.quantia - a.R_br.valor.quantia) <= TOLERANCIA


@settings(max_examples=300)
@given(I=valores_brl(), F=valores_brl(), C_i=cotacoes(), C_f=cotacoes())
def test_investir_compensou_concorda_com_o_sinal_da_vantagem(
    I: Decimal, F: Decimal, C_i: Decimal, C_f: Decimal
) -> None:
    a = apurar(I, F, C_i, C_f)
    assert a.investir_compensou() == (a.V_inv.valor.quantia > 0)
