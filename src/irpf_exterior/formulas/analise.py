"""Fórmulas 14–16: decomposição do rendimento e comparação com a conta parada.

**Nada aqui entra na declaração.** Estas três variáveis servem para *entender*
o resultado — separar o que a aplicação rendeu do que o câmbio rendeu — e para
responder "teria valido mais a pena deixar o dinheiro parado?". Nenhuma delas
altera o imposto devido.

A decomposição é exata: `R_br = R_cc + R_eubr`, com `R_cc` (Fórmula 8) no papel
de rendimento cambial e `R_eubr` (Fórmula 14) no de rendimento da aplicação.
"""

from __future__ import annotations

from decimal import Decimal

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money
from irpf_exterior.formulas._base import formula

__all__ = ["j_eu", "r_eubr", "v_inv"]


@formula(
    nome="R_eubr",
    ref="Fórmula 14",
    expr="R_eubr = R_eu · C_f",
    latex=r"R_{eubr} = R_{eu} \cdot C_f",
)
def r_eubr(R_eu: Money[EUR], C_f: Cambio) -> Money[BRL]:
    """Quanto a aplicação rendeu por fora do câmbio, em reais.

    É o "juro" ou prêmio da aplicação: o `R_eu` (apurado em euros) convertido
    pelo câmbio do resgate, do mesmo modo que `IR_pt` vira `IR_ptbr`. Converter
    por `C_f`, e não por `C_i`, é o que faz a decomposição fechar exatamente.

    Não é arredondado: é um valor analítico, não uma quantia a recolher.
    """
    return C_f.para_brl(R_eu)


@formula(
    nome="J_eu",
    ref="Fórmula 15",
    expr="J_eu = R_eu / I_eu",
    latex=r"J_{eu} = \frac{R_{eu}}{I_{eu}}",
)
def j_eu(R_eu: Money[EUR], I_eu: Money[EUR]) -> Decimal:
    """Rendimento percentual da aplicação em moeda local, sem efeito cambial.

    É o número que a corretora estrangeira anuncia, e o único comparável com
    outra aplicação em euros. Não confundir com `J` (Fórmula 7), que é apurado
    em reais e portanto mistura o desempenho da aplicação com o do câmbio.
    """
    return R_eu.razao(I_eu)


@formula(
    nome="V_inv",
    ref="Fórmula 16",
    expr="V_inv = R_liq - R_cc",
    latex=r"V_{inv} = R_{liq} - R_{cc}",
    lei="Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada)",
)
def v_inv(R_liq: Money[BRL], R_cc: Money[BRL]) -> Money[BRL]:
    """Quanto se ganhou por ter investido, em vez de deixar o dinheiro parado.

    Negativo significa que não investir teria sido melhor. Equivale a
    `R_eubr - IR_ef`: investir só compensa se o prêmio da aplicação superar o
    imposto inteiro, inclusive a parcela que incide sobre o ganho cambial —
    que seria isenta com o dinheiro parado.

    A comparação pressupõe que a alternativa era manter o mesmo valor em euros
    numa conta **não remunerada** no exterior, e ignora taxas de corretora,
    inflação e o custo de oportunidade de ter ficado em reais no Brasil.
    """
    return R_liq - R_cc
