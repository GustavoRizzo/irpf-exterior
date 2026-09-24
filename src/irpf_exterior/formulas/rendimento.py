"""Fórmulas 5–7: o rendimento bruto, nas duas bases de cálculo.

Aqui mora a dor 2.2: Portugal tributa `R_eu` (apurado em euros, sem câmbio) e
o Brasil tributa `R_br` (apurado em reais, com o câmbio embutido). São
grandezas diferentes, e os tipos impedem que sejam confundidas.
"""

from __future__ import annotations

from decimal import Decimal

from irpf_exterior.dominio.moeda import BRL, EUR, Money
from irpf_exterior.formulas._base import formula

__all__ = ["j", "r_br", "r_eu"]


@formula(
    nome="R_eu",
    ref="Fórmula 5",
    expr="R_eu = F_eu - I_eu",
    latex=r"R_{eu} = F_{eu} - I_{eu}",
)
def r_eu(F_eu: Money[EUR], I_eu: Money[EUR]) -> Money[EUR]:
    """Rendimento bruto apurado em euros — a base de cálculo portuguesa."""
    return F_eu - I_eu


@formula(
    nome="R_br",
    ref="Fórmula 6",
    expr="R_br = F - I",
    latex=r"R_{br} = F - I",
    lei="Lei 14.754/2023, Art. 2º",
)
def r_br(F: Money[BRL], I: Money[BRL]) -> Money[BRL]:
    """Rendimento bruto apurado em reais — a base de cálculo brasileira.

    Como `F` e `I` são convertidos por câmbios de datas diferentes, a variação
    cambial já está embutida nesta diferença.
    """
    return F - I


@formula(
    nome="J",
    ref="Fórmula 7",
    expr="J = R_br / I",
    latex=r"J = \frac{R_{br}}{I}",
)
def j(R_br: Money[BRL], I: Money[BRL]) -> Decimal:
    """Rendimento bruto em termos percentuais (adimensional)."""
    return R_br.razao(I)
