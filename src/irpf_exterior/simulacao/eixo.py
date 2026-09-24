"""Os eixos ao longo dos quais um cenário pode ser variado."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

__all__ = ["Eixo", "EixoCambioFinal", "EixoJuro", "em_torno_de", "intervalo"]


@dataclass(frozen=True, slots=True)
class EixoCambioFinal:
    """Varia o câmbio do resgate, mantendo o juro esperado da aplicação."""

    valores: tuple[Decimal, ...]
    nome: str = "C_f"


@dataclass(frozen=True, slots=True)
class EixoJuro:
    """Varia o juro da aplicação em euros, mantendo o câmbio esperado."""

    valores: tuple[Decimal, ...]
    nome: str = "J_eu"


type Eixo = EixoCambioFinal | EixoJuro
"""Tratado com `match` + `assert_never`: um eixo novo não passa despercebido."""


def intervalo(de: str | Decimal, ate: str | Decimal, passo: str | Decimal) -> tuple[Decimal, ...]:
    """Valores de `de` até `ate`, de `passo` em `passo`, incluindo as pontas.

    Cada valor é calculado como `de + i · passo`, e não por soma acumulada,
    para que o erro não se propague ao longo do eixo.

    >>> intervalo("1.0", "1.4", "0.2")
    (Decimal('1.0'), Decimal('1.2'), Decimal('1.4'))
    """
    inicio, fim, incremento = Decimal(de), Decimal(ate), Decimal(passo)
    if incremento <= 0:
        raise ValueError(f"passo deve ser positivo, recebido {incremento}")
    if fim < inicio:
        raise ValueError(f"intervalo invertido: {inicio} até {fim}")
    quantidade = int((fim - inicio) / incremento)
    return tuple(inicio + i * incremento for i in range(quantidade + 1))


def em_torno_de(
    base: str | Decimal, variacao: str | Decimal, pontos: int = 21
) -> tuple[Decimal, ...]:
    """`pontos` valores simétricos em torno de `base`, até ±`variacao` (relativa).

    Útil para perguntar "e se eu estiver errado em ±20%?" sem calcular as
    pontas à mão. O número de pontos é ímpar para que a base caia no centro.

    As casas decimais do resultado vêm da aritmética, não da base — o valor é
    o mesmo, mas o `repr` pode trazer zeros a mais.

    >>> em_torno_de("5.00", "0.20", pontos=3)
    (Decimal('4.0000'), Decimal('5.0000'), Decimal('6.0000'))
    """
    centro, amplitude = Decimal(base), Decimal(variacao)
    if pontos < 3 or pontos % 2 == 0:
        raise ValueError(f"pontos deve ser ímpar e >= 3, recebido {pontos}")
    if amplitude <= 0:
        raise ValueError(f"variação deve ser positiva, recebida {amplitude}")
    metade = (pontos - 1) // 2
    passo = centro * amplitude / metade
    return tuple(centro + (i - metade) * passo for i in range(pontos))
