r"""Fórmulas 1–4 e 8: variação cambial e conversão entre moedas.

No código, a variável $C_\%$ do glossário chama-se `C_pct` (o símbolo `%`
não é válido num identificador Python).
"""

from __future__ import annotations

from decimal import Decimal

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money
from irpf_exterior.formulas._base import formula

__all__ = ["c_d", "c_pct", "f_eu", "i_eu", "r_cc"]


@formula(
    nome="C_d",
    ref="Fórmula 1",
    expr="C_d = C_f - C_i",
    latex=r"C_d = C_f - C_i",
)
def c_d(C_i: Cambio, C_f: Cambio) -> Decimal:
    """Variação cambial absoluta, em reais por euro."""
    return C_f.valor - C_i.valor


@formula(
    nome="C_pct",
    ref="Fórmula 2",
    expr="C_% = C_d / C_i",
    latex=r"C_\% = \frac{C_d}{C_i}",
)
def c_pct(C_d: Decimal, C_i: Cambio) -> Decimal:
    """Variação cambial relativa ao câmbio inicial (adimensional)."""
    return C_d / C_i.valor


@formula(
    nome="I_eu",
    ref="Fórmula 3",
    expr="I_eu = I / C_i",
    latex=r"I_{eu} = \frac{I}{C_i}",
)
def i_eu(I: Money[BRL], C_i: Cambio) -> Money[EUR]:
    """Valor aportado, convertido para euros pelo câmbio do dia do aporte."""
    return C_i.para_eur(I)


@formula(
    nome="F_eu",
    ref="Fórmula 4",
    expr="F_eu = F / C_f",
    latex=r"F_{eu} = \frac{F}{C_f}",
)
def f_eu(F: Money[BRL], C_f: Cambio) -> Money[EUR]:
    """Valor resgatado bruto, convertido para euros pelo câmbio do resgate."""
    return C_f.para_eur(F)


@formula(
    nome="R_cc",
    ref="Fórmula 8",
    expr="R_cc = I · C_%",
    latex=r"R_{cc} = I \cdot C_\%",
    lei="Lei 14.754/2023, Art. 2º, §3º",
)
def r_cc(I: Money[BRL], C_pct: Decimal) -> Money[BRL]:
    """Ganho cambial de dinheiro parado em conta não remunerada.

    Não é fato gerador de imposto: aparece na apuração para deixar explícito
    quanto do resultado veio apenas do câmbio, e não da aplicação.
    """
    return I.vezes(C_pct)
