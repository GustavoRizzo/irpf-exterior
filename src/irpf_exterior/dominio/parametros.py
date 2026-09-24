"""Alíquotas versionadas por vigência (*effective dating*).

Responde à dor 2.5: a lei muda, mas um cálculo de um ano passado precisa
continuar reproduzível com as regras daquele ano. Por isso uma linha da
tabela **nunca** é editada; fecha-se o `fim` da antiga e acrescenta-se outra.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

__all__ = ["TABELA_ALIQUOTAS", "Aliquota", "aliquota_vigente"]


@dataclass(frozen=True, slots=True)
class Aliquota:
    """Uma alíquota com período de vigência.

    `fim=None` significa "vigente até hoje, sem revogação conhecida".

    >>> str(Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1)))
    'T_br = 15% (desde 2024-01-01)'
    """

    nome: str
    valor: Decimal
    inicio: date
    fim: date | None = None
    fonte: str | None = None

    def __post_init__(self) -> None:
        """Recusa valor não-`Decimal` ou vigência invertida."""
        if not isinstance(self.valor, Decimal):
            raise TypeError(
                f"valor da alíquota deve ser Decimal, recebido {type(self.valor).__name__}"
            )
        if self.fim is not None and self.fim < self.inicio:
            raise ValueError(f"{self.nome}: fim {self.fim} anterior ao início {self.inicio}")

    def vigente_em(self, em: date) -> bool:
        """Diz se a alíquota vale na data `em`."""
        return self.inicio <= em and (self.fim is None or em <= self.fim)

    @property
    def percentual(self) -> Decimal:
        """A alíquota em pontos percentuais (0.15 -> 15)."""
        return self.valor * Decimal("100")

    def __str__(self) -> str:
        """Descrição curta, usada nas árvores de auditoria."""
        vigencia = (
            f"desde {self.inicio.isoformat()}"
            if self.fim is None
            else f"de {self.inicio.isoformat()} a {self.fim.isoformat()}"
        )
        pct = self.percentual.normalize()
        texto = f"{self.nome} = {pct}% ({vigencia})"
        return texto if self.fonte is None else f"{texto} [{self.fonte}]"


TABELA_ALIQUOTAS: tuple[Aliquota, ...] = (
    Aliquota(
        nome="T_br",
        valor=Decimal("0.15"),
        inicio=date(2024, 1, 1),
        fim=None,
        fonte="Lei 14.754/2023, Art. 2º",
    ),
    Aliquota(
        nome="T_pt",
        valor=Decimal("0.28"),
        inicio=date(2024, 1, 1),
        fim=None,
        fonte="CIRS Art. 72.º (taxa liberatória) — vigência ilustrativa, confirmar",
    ),
)
"""Tabela padrão. Injetável nos cálculos para testes e cenários históricos."""


def aliquota_vigente(
    tabela: tuple[Aliquota, ...],
    nome: str,
    em: date | None,
) -> Aliquota:
    """Devolve a alíquota `nome` vigente na data `em`.

    Respeita o princípio 4.5 ("nunca adivinhar"): sem data de referência, só
    responde se houver uma única vigência cadastrada para aquele nome.

    Raises:
        LookupError: nome inexistente, ou nenhuma vigência cobre `em`.
        ValueError: `em` é `None` e há mais de uma vigência para `nome`.

    >>> aliquota_vigente(TABELA_ALIQUOTAS, "T_br", date(2025, 3, 10)).valor
    Decimal('0.15')
    """
    candidatas = tuple(a for a in tabela if a.nome == nome)
    if not candidatas:
        conhecidas = ", ".join(sorted({a.nome for a in tabela})) or "(tabela vazia)"
        raise LookupError(f"Alíquota desconhecida: {nome!r}. Disponíveis: {conhecidas}.")
    if em is None:
        if len(candidatas) == 1:
            return candidatas[0]
        raise ValueError(
            f"{nome}: há {len(candidatas)} vigências cadastradas. "
            "Informe a data de referência ou passe a alíquota explicitamente."
        )
    vigentes = tuple(a for a in candidatas if a.vigente_em(em))
    if not vigentes:
        raise LookupError(f"Nenhuma alíquota {nome} vigente em {em.isoformat()}.")
    if len(vigentes) > 1:
        raise ValueError(
            f"{nome}: {len(vigentes)} vigências se sobrepõem em {em.isoformat()}; corrija a tabela."
        )
    return vigentes[0]
