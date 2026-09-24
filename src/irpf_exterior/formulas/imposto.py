"""Fórmulas 9–13: imposto em cada país, compensação e resultado líquido."""

from __future__ import annotations

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money
from irpf_exterior.dominio.parametros import Aliquota
from irpf_exterior.formulas._base import formula

__all__ = ["ir_br", "ir_ef", "ir_pt", "ir_ptbr", "r_liq"]


@formula(
    nome="IR_pt",
    ref="Fórmula 9",
    expr="IR_pt = max(0, R_eu · T_pt)",
    latex=r"IR_{pt} = R_{eu} \cdot T_{pt}",
    lei="CIRS Art. 72.º — taxa liberatória sobre o rendimento em euros",
)
def ir_pt(R_eu: Money[EUR], T_pt: Aliquota) -> Money[EUR]:
    """Imposto retido em Portugal, sobre o rendimento apurado em euros.

    Prejuízo não gera imposto negativo: o piso é zero.
    """
    if R_eu.quantia <= 0:
        return R_eu.zerado()
    return R_eu.vezes(T_pt.valor).arredondado()


@formula(
    nome="IR_ptbr",
    ref="Fórmula 10",
    expr="IR_ptbr = IR_pt · C_f",
    latex=r"IR_{ptbr} = IR_{pt} \cdot C_f",
)
def ir_ptbr(IR_pt: Money[EUR], C_f: Cambio) -> Money[BRL]:
    """O imposto português convertido para reais pelo câmbio do resgate.

    É este valor — e não o `IR_pt` em euros — que vai ao campo "Imposto pago
    no Exterior" da declaração.
    """
    return C_f.para_brl(IR_pt).arredondado()


@formula(
    nome="IR_br",
    ref="Fórmula 11",
    expr="IR_br = max(0, R_br · T_br)",
    latex=r"IR_{br} = R_{br} \cdot T_{br}",
    lei="Lei 14.754/2023, Art. 2º",
)
def ir_br(R_br: Money[BRL], T_br: Aliquota) -> Money[BRL]:
    """Imposto devido no Brasil, antes da compensação do imposto estrangeiro.

    Prejuízo não gera imposto negativo: o piso é zero.
    """
    if R_br.quantia <= 0:
        return R_br.zerado()
    return R_br.vezes(T_br.valor).arredondado()


@formula(
    nome="IR_ef",
    ref="Fórmula 12",
    expr="IR_ef = max(IR_ptbr, IR_br)",
    latex=r"IR_{ef} = \max(IR_{ptbr},\ IR_{br})",
    lei="Lei 14.754/2023, Art. 12",
)
def ir_ef(IR_ptbr: Money[BRL], IR_br: Money[BRL]) -> Money[BRL]:
    """Imposto efetivamente suportado, já aplicada a compensação.

    O Brasil abate o imposto pago em Portugal, mas não devolve o excedente:
    paga-se sempre o maior dos dois.
    """
    return IR_ptbr if IR_ptbr > IR_br else IR_br


@formula(
    nome="R_liq",
    ref="Fórmula 13",
    expr="R_liq = R_br - IR_ef",
    latex=r"R_{liq} = R_{br} - IR_{ef}",
)
def r_liq(R_br: Money[BRL], IR_ef: Money[BRL]) -> Money[BRL]:
    """O que sobra do rendimento depois do imposto efetivamente pago."""
    return R_br - IR_ef
