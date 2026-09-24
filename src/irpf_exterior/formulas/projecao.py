"""Fórmulas 17–19: projeção e pontos de equilíbrio, para simulação.

As Fórmulas 1–16 apuram um investimento que já aconteceu, em que `F` é um fato
lido no extrato. Estas três servem à pergunta anterior — "se eu investir, e o
câmbio terminar em X, ainda compensa?" — quando `F` ainda não existe.

Em simulação **não se pode variar `C_f` mantendo `F` fixo**: os dois não são
independentes (`F = I_eu · (1 + J_eu) · C_f`). Por isso a projeção deriva `F`
a partir do juro esperado, o que deixa os eixos `J_eu` e `C_f` ortogonais.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money
from irpf_exterior.dominio.parametros import Aliquota
from irpf_exterior.formulas._base import formula

__all__ = [
    "Equilibrio",
    "NuncaCompensa",
    "PontoDeEquilibrio",
    "SempreCompensa",
    "c_eq",
    "f_proj",
    "j_eq",
]

UM = Decimal("1")


@dataclass(frozen=True, slots=True)
class Equilibrio:
    """Existe um ponto de virada, e é este valor."""

    valor: Decimal

    def __str__(self) -> str:
        """Mostra o valor de virada."""
        return f"equilíbrio em {self.valor:.4f}"


@dataclass(frozen=True, slots=True)
class SempreCompensa:
    """Não há ponto de virada: investir compensa em todo o eixo.

    Guarda o motivo para que a auditoria não precise redescobri-lo.
    """

    motivo: str

    def __str__(self) -> str:
        """Mostra por que não existe ponto de virada."""
        return f"sem equilíbrio ({self.motivo})"


@dataclass(frozen=True, slots=True)
class NuncaCompensa:
    """Não há ponto de virada porque investir perde em todo o eixo."""

    motivo: str

    def __str__(self) -> str:
        """Mostra por que investir não compensa em lugar nenhum."""
        return f"sem equilíbrio ({self.motivo})"


type PontoDeEquilibrio = Equilibrio | SempreCompensa | NuncaCompensa
"""Ou existe um ponto de virada, ou existe a razão de não haver nenhum.

São duas razões opostas — investir compensa sempre, ou nunca —, e confundi-las
seria pior do que não responder. Tratado com `match` + `assert_never`, para que
um caso novo não passe batido.
"""


@formula(
    nome="F_proj",
    ref="Fórmula 17",
    expr="F_proj = I_eu · (1 + J_eu) · C_f",
    latex=r"F_{proj} = I_{eu} \cdot (1 + J_{eu}) \cdot C_f",
)
def f_proj(I_eu: Money[EUR], J_eu: Decimal, C_f: Cambio) -> Money[BRL]:
    """O `F` que resultaria de um juro `J_eu` e de um câmbio final `C_f`.

    Alimentando este valor de volta nas Fórmulas 1–16, toda a apuração e toda
    a auditoria funcionam igual: simular não é um caminho de cálculo paralelo,
    é a mesma apuração com um `F` projetado.
    """
    return C_f.para_brl(I_eu.vezes(UM + J_eu))


@formula(
    nome="C_eq",
    ref="Fórmula 18",
    expr="C_eq = C_i · T_br / (T_br · (1 + J_eu) - J_eu)",
    latex=r"C_{eq} = \frac{C_i \cdot T_{br}}{T_{br}\,(1 + J_{eu}) - J_{eu}}",
    lei="Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada)",
)
def c_eq(C_i: Cambio, J_eu: Decimal, T_br: Aliquota) -> PontoDeEquilibrio:
    """O câmbio final a partir do qual investir deixa de compensar.

    Só existe no regime em que o imposto brasileiro prevalece — é lá que o
    ganho cambial, isento se o dinheiro ficasse parado, entra na base de
    cálculo. Quando `J_eu >= T_br / (1 - T_br)` (≈ 17,65% com T_br de 15%),
    nenhum câmbio torna o investimento pior que a conta parada.

    O resultado é **assintótico** perto dessa fronteira: a 17,6% de juro o
    equilíbrio já passa de R$ 1.800/€. Um valor desses é matematicamente
    correto e economicamente equivalente a `SempreCompensa` — quem exibe o
    número deve tratá-lo como tal, em vez de plotá-lo num eixo.

    Com juro não positivo não existe equilíbrio pelo motivo oposto: sem prêmio
    algum, investir nunca supera a conta parada. A forma fechada devolveria um
    câmbio qualquer, porque foi derivada supondo imposto devido — e com
    prejuízo o imposto é zero, por piso.
    """
    if J_eu <= 0:
        return NuncaCompensa(
            f"juro de {J_eu:.4%} não paga prêmio nenhum sobre deixar o dinheiro parado"
        )
    denominador = T_br.valor * (UM + J_eu) - J_eu
    if denominador <= 0:
        fronteira = T_br.valor / (UM - T_br.valor)
        return SempreCompensa(
            f"juro de {J_eu:.4%} atinge a fronteira de {fronteira:.4%}, "
            "acima da qual nenhum câmbio torna investir pior que ficar parado"
        )
    return Equilibrio(C_i.valor * T_br.valor / denominador)


@formula(
    nome="J_eq",
    ref="Fórmula 19",
    expr="J_eq = max(0, T_br · (C_f - C_i) / (C_f · (1 - T_br)))",
    latex=r"J_{eq} = \max\left(0,\ \frac{T_{br}\,(C_f - C_i)}{C_f\,(1 - T_{br})}\right)",
    lei="Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada)",
)
def j_eq(C_i: Cambio, C_f: Cambio, T_br: Aliquota) -> Decimal:
    """O juro mínimo para a aplicação apenas empatar com o dinheiro parado.

    É exatamente o que cobre o imposto sobre o ganho cambial, diluído pelo
    valor investido. Sem ganho cambial não há imposto a cobrir, e o mínimo é
    zero: qualquer juro positivo já compensa.

    O piso em zero não é cosmético. Com o câmbio em queda a forma fechada
    devolveria um juro negativo, mas ali o rendimento em reais é negativo e o
    imposto é zero por piso (Fórmula 11) — de modo que o equilíbrio verdadeiro
    é exatamente `J_eu = 0`, e não o número que a álgebra sugere.
    """
    bruto = T_br.valor * (C_f.valor - C_i.valor) / (C_f.valor * (UM - T_br.valor))
    return bruto if bruto > 0 else Decimal("0")
