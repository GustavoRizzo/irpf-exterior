"""Cada fórmula isolada, com valores conferidos à mão.

Cenário base: R$ 10.000 aportados a R$ 5,00/€ (€ 2.000) e resgatados por
R$ 13.200 a R$ 6,00/€ (€ 2.200).
"""

from datetime import date
from decimal import Decimal

from irpf_exterior.dominio.moeda import Cambio, brl, eur
from irpf_exterior.dominio.parametros import Aliquota
from irpf_exterior.formulas import (
    c_d,
    c_pct,
    f_eu,
    i_eu,
    ir_br,
    ir_ef,
    ir_pt,
    ir_ptbr,
    j,
    j_eu,
    r_br,
    r_cc,
    r_eu,
    r_eubr,
    r_liq,
    v_inv,
)

C_I = Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX")
C_F = Cambio(Decimal("6.00"), date(2025, 3, 10))
T_BR = Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1))
T_PT = Aliquota("T_pt", Decimal("0.28"), date(2024, 1, 1))


def test_formula_1_variacao_cambial() -> None:
    assert c_d(C_i=C_I, C_f=C_F).valor == Decimal("1.00")


def test_formula_2_taxa_de_variacao_cambial() -> None:
    assert c_pct(C_d=Decimal("1.00"), C_i=C_I).valor == Decimal("0.2")


def test_formula_3_valor_inicial_em_euros() -> None:
    assert i_eu(I=brl("10000.00"), C_i=C_I).valor == eur("2000")


def test_formula_4_valor_resgatado_em_euros() -> None:
    assert f_eu(F=brl("13200.00"), C_f=C_F).valor == eur("2200")


def test_formula_5_rendimento_bruto_em_euros() -> None:
    assert r_eu(F_eu=eur("2200"), I_eu=eur("2000")).valor == eur("200")


def test_formula_6_rendimento_bruto_em_reais() -> None:
    assert r_br(F=brl("13200.00"), I=brl("10000.00")).valor == brl("3200.00")


def test_formula_7_rendimento_percentual() -> None:
    assert j(R_br=brl("3200.00"), I=brl("10000.00")).valor == Decimal("0.32")


def test_formula_8_rendimento_em_conta_corrente() -> None:
    assert r_cc(I=brl("10000.00"), C_pct=Decimal("0.2")).valor == brl("2000.000")


def test_formula_9_imposto_em_portugal() -> None:
    assert ir_pt(R_eu=eur("200"), T_pt=T_PT).valor == eur("56.00")


def test_formula_9_prejuizo_nao_gera_imposto_negativo() -> None:
    assert ir_pt(R_eu=eur("-500"), T_pt=T_PT).valor == eur("0")


def test_formula_10_imposto_portugues_em_reais() -> None:
    assert ir_ptbr(IR_pt=eur("56.00"), C_f=C_F).valor == brl("336.00")


def test_formula_11_imposto_no_brasil() -> None:
    assert ir_br(R_br=brl("3200.00"), T_br=T_BR).valor == brl("480.00")


def test_formula_11_prejuizo_nao_gera_imposto_negativo() -> None:
    assert ir_br(R_br=brl("-1000.00"), T_br=T_BR).valor == brl("0")


def test_formula_12_compensacao_paga_o_maior() -> None:
    assert ir_ef(IR_ptbr=brl("336.00"), IR_br=brl("480.00")).valor == brl("480.00")
    assert ir_ef(IR_ptbr=brl("672.00"), IR_br=brl("60.00")).valor == brl("672.00")


def test_formula_12_empate_devolve_o_mesmo_valor() -> None:
    assert ir_ef(IR_ptbr=brl("480.00"), IR_br=brl("480.00")).valor == brl("480.00")


def test_formula_13_rendimento_liquido() -> None:
    assert r_liq(R_br=brl("3200.00"), IR_ef=brl("480.00")).valor == brl("2720.00")


def test_formula_carrega_descricao_e_base_legal() -> None:
    resultado = ir_br(R_br=brl("3200.00"), T_br=T_BR)
    assert resultado.descricao == "Fórmula 11: IR_br = max(0, R_br · T_br)"
    assert resultado.fonte == "Lei 14.754/2023, Art. 2º"


def test_formula_aceita_valor_cru_ou_rastreado() -> None:
    from irpf_exterior.rastreio import entrada

    cru = ir_br(R_br=brl("3200.00"), T_br=T_BR)
    rastreado = ir_br(R_br=entrada("R_br", brl("3200.00")), T_br=T_BR)
    assert cru.valor == rastreado.valor


def test_formula_14_rendimento_da_aplicacao_em_reais() -> None:
    """€ 200 de rendimento, convertidos pelo câmbio do resgate (R$ 6,00)."""
    assert r_eubr(R_eu=eur("200"), C_f=C_F).valor == brl("1200.00")


def test_formula_14_nao_arredonda_valor_analitico() -> None:
    """Não é quantia a recolher: preserva as casas para a decomposição fechar."""
    resultado = r_eubr(R_eu=eur("0.001"), C_f=Cambio(Decimal("6.00")))
    assert resultado.valor.quantia == Decimal("0.00600")


def test_formula_14_prejuizo_em_euros_vira_valor_negativo() -> None:
    """Ao contrário do imposto, o rendimento da aplicação não tem piso em zero."""
    assert r_eubr(R_eu=eur("-500"), C_f=Cambio(Decimal("8.00"))).valor == brl("-4000.00")


def test_formula_15_juro_da_aplicacao() -> None:
    """€ 200 sobre € 2.000 aplicados: 10%, sem qualquer efeito cambial."""
    assert j_eu(R_eu=eur("200"), I_eu=eur("2000")).valor == Decimal("0.1")


def test_formula_15_nao_se_confunde_com_o_rendimento_em_reais() -> None:
    """Mesmo cenário: J_eu é 10% (aplicação) enquanto J é 32% (aplicação + câmbio)."""
    juro_aplicacao = j_eu(R_eu=eur("200"), I_eu=eur("2000")).valor
    juro_em_reais = j(R_br=brl("3200.00"), I=brl("10000.00")).valor
    assert juro_aplicacao == Decimal("0.1")
    assert juro_em_reais == Decimal("0.32")
    assert juro_aplicacao < juro_em_reais


def test_formula_16_vantagem_de_ter_investido() -> None:
    assert v_inv(R_liq=brl("2720.00"), R_cc=brl("2000.00")).valor == brl("720.00")


def test_formula_16_negativa_quando_parado_seria_melhor() -> None:
    assert v_inv(R_liq=brl("5236.00"), R_cc=brl("6000.00")).valor == brl("-764.00")


def test_formula_16_carrega_a_base_legal_da_isencao() -> None:
    resultado = v_inv(R_liq=brl("2720.00"), R_cc=brl("2000.00"))
    assert resultado.fonte is not None
    assert "Art. 2º, §3º" in resultado.fonte
