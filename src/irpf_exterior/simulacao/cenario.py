"""O cenário de simulação: a parametrização em que `F` ainda não existe."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from irpf_exterior.apuracoes.resgate import ApuracaoResgate
from irpf_exterior.dominio.moeda import BRL, Cambio, Money
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota
from irpf_exterior.formulas.cambio import i_eu
from irpf_exterior.formulas.projecao import f_proj
from irpf_exterior.rastreio import entrada

__all__ = ["Cenario", "apurar"]


@dataclass(frozen=True, slots=True)
class Cenario:
    """Uma hipótese completa de investimento, com `F` derivado do juro.

    Ao contrário de `ApuracaoResgate`, que recebe o `F` lido no extrato, aqui
    o valor resgatado é *projetado* (Fórmula 17). É isso que torna os eixos
    `J_eu` e `C_f` ortogonais: variar um não mexe no outro.
    """

    I: Money[BRL]
    C_i: Cambio
    J_eu: Decimal
    C_f: Cambio


def apurar(
    cenario: Cenario,
    *,
    tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
    T_br: Aliquota | None = None,
    T_pt: Aliquota | None = None,
) -> ApuracaoResgate:
    """Projeta o `F` do cenário e roda a apuração completa sobre ele.

    O `F` entra como `Calculado`, então a árvore de auditoria mostra que ele
    veio da Fórmula 17 e com que juro — simular não perde rastreabilidade.
    """
    c_I = entrada("I", cenario.I)
    v_i_eu = i_eu(I=c_I, C_i=cenario.C_i)
    v_f = f_proj(I_eu=v_i_eu, J_eu=cenario.J_eu, C_f=cenario.C_f)
    return ApuracaoResgate.de_cf(
        I=c_I, F=v_f, C_i=cenario.C_i, C_f=cenario.C_f, tabela=tabela, T_br=T_br, T_pt=T_pt
    )
