"""Simulação: varreduras sob demanda e pontos de equilíbrio em forma fechada.

As Fórmulas 1–16 apuram o que já aconteceu. Este pacote serve à pergunta
anterior — "se eu investir, e o câmbio terminar em X, ainda compensa?" — e
nada aqui é calculado antes de ser pedido.
"""

from irpf_exterior.simulacao.cenario import Cenario, apurar
from irpf_exterior.simulacao.eixo import (
    Eixo,
    EixoCambioFinal,
    EixoJuro,
    em_torno_de,
    intervalo,
)
from irpf_exterior.simulacao.equilibrio import (
    Regime,
    cambio_de_equilibrio,
    juro_de_equilibrio,
    regime_vigente,
)
from irpf_exterior.simulacao.varredura import (
    COLUNAS_PADRAO,
    Ponto,
    Varredura,
    executar,
    para_tabela,
    serie,
)

__all__ = [
    "COLUNAS_PADRAO",
    "Cenario",
    "Eixo",
    "EixoCambioFinal",
    "EixoJuro",
    "Ponto",
    "Regime",
    "Varredura",
    "apurar",
    "cambio_de_equilibrio",
    "em_torno_de",
    "executar",
    "intervalo",
    "juro_de_equilibrio",
    "para_tabela",
    "regime_vigente",
    "serie",
]
