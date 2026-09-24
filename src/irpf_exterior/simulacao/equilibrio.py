"""Os pontos de virada, resolvidos em forma fechada — sem varrer nada.

Responder "a partir de que câmbio deixa de compensar?" não exige simular
duzentos cenários: a equação `V_inv = 0` tem solução algébrica. Estas funções
a aplicam, e são honestas quando ela não existe.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from irpf_exterior.apuracoes.resgate import ApuracaoResgate
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota, aliquota_vigente
from irpf_exterior.formulas.projecao import PontoDeEquilibrio, c_eq, j_eq
from irpf_exterior.rastreio import Calculado
from irpf_exterior.simulacao.cenario import Cenario

__all__ = ["Regime", "cambio_de_equilibrio", "juro_de_equilibrio", "regime_vigente"]

type Regime = Literal["Brasil", "Portugal"]
"""Qual dos dois impostos prevalece — e, com ele, qual base de cálculo vale."""


def regime_vigente(apuracao: ApuracaoResgate) -> Regime:
    """Diz qual imposto prevaleceu na compensação.

    Importa para a análise porque só no regime brasileiro existe ponto de
    equilíbrio: Portugal tributa apenas o rendimento da aplicação, enquanto o
    Brasil tributa também o ganho cambial, que seria isento se o dinheiro
    ficasse parado.
    """
    return "Portugal" if apuracao.IR_ptbr.valor > apuracao.IR_br.valor else "Brasil"


def _t_br(tabela: tuple[Aliquota, ...], explicita: Aliquota | None, cenario: Cenario) -> Aliquota:
    """A alíquota brasileira informada, ou a vigente na data do resgate."""
    if explicita is not None:
        return explicita
    return aliquota_vigente(tabela, "T_br", cenario.C_f.data)


def cambio_de_equilibrio(
    cenario: Cenario,
    *,
    tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
    T_br: Aliquota | None = None,
) -> Calculado[PontoDeEquilibrio]:
    """O câmbio final a partir do qual investir deixa de compensar (Fórmula 18).

    Devolve `SempreCompensa` quando o juro esperado é alto o bastante para que
    nenhum câmbio torne o investimento pior que a conta parada.
    """
    return c_eq(C_i=cenario.C_i, J_eu=cenario.J_eu, T_br=_t_br(tabela, T_br, cenario))


def juro_de_equilibrio(
    cenario: Cenario,
    *,
    tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
    T_br: Aliquota | None = None,
) -> Calculado[Decimal]:
    """O juro mínimo para a aplicação empatar com o dinheiro parado (Fórmula 19).

    Ao contrário do câmbio de equilíbrio, este sempre existe: pode ser zero
    (câmbio estável) ou negativo (câmbio em queda).
    """
    return j_eq(C_i=cenario.C_i, C_f=cenario.C_f, T_br=_t_br(tabela, T_br, cenario))
