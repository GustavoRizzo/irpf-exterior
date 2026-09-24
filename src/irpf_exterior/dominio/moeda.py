"""Moedas, dinheiro tipado e câmbio (Value Objects do domínio).

Este módulo é a primeira barreira contra a dor 2.1 (duas moedas, câmbios de
datas diferentes): somar reais com euros é erro de tipagem *e* erro de
execução, e nenhuma conversão acontece implicitamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

__all__ = ["BRL", "EUR", "Cambio", "Money", "brl", "eur"]

CENTAVO = Decimal("0.01")
"""Unidade de arredondamento monetário (duas casas)."""


class BRL:
    """Marcador de tipo para o Real brasileiro. Nunca é instanciado."""


class EUR:
    """Marcador de tipo para o Euro. Nunca é instanciado."""


@dataclass(frozen=True, slots=True)
class Money[M: (BRL, EUR)]:
    """Uma quantia imutável numa moeda específica.

    A quantia é sempre `Decimal` (dor 2.6): construir a partir de `float`
    reintroduziria o erro binário que este tipo existe para evitar.

    >>> brl("10.00") + brl("2.50")
    Money(quantia=Decimal('12.50'), moeda=BRL)
    >>> brl("10.00") + eur("1.00")
    Traceback (most recent call last):
        ...
    TypeError: não é possível operar BRL com EUR
    """

    quantia: Decimal
    moeda: type[M]

    def __post_init__(self) -> None:
        """Recusa quantias que não sejam `Decimal` (ex.: `float`, `int`)."""
        if not isinstance(self.quantia, Decimal):
            raise TypeError(
                f"quantia deve ser Decimal, recebido {type(self.quantia).__name__}; "
                'use Decimal("10.00") ou o helper brl()/eur().'
            )

    def _exigir_mesma_moeda(self, outro: Money[M]) -> None:
        if self.moeda is not outro.moeda:
            raise TypeError(
                f"não é possível operar {self.moeda.__name__} com {outro.moeda.__name__}"
            )

    def __add__(self, outro: Money[M]) -> Money[M]:
        """Soma duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return Money(self.quantia + outro.quantia, self.moeda)

    def __sub__(self, outro: Money[M]) -> Money[M]:
        """Subtrai duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return Money(self.quantia - outro.quantia, self.moeda)

    def __neg__(self) -> Money[M]:
        """Inverte o sinal da quantia."""
        return Money(-self.quantia, self.moeda)

    def __lt__(self, outro: Money[M]) -> bool:
        """Compara duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return self.quantia < outro.quantia

    def __le__(self, outro: Money[M]) -> bool:
        """Compara duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return self.quantia <= outro.quantia

    def __gt__(self, outro: Money[M]) -> bool:
        """Compara duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return self.quantia > outro.quantia

    def __ge__(self, outro: Money[M]) -> bool:
        """Compara duas quantias da mesma moeda."""
        self._exigir_mesma_moeda(outro)
        return self.quantia >= outro.quantia

    def vezes(self, fator: Decimal) -> Money[M]:
        """Multiplica a quantia por um fator adimensional (ex.: uma alíquota)."""
        return Money(self.quantia * fator, self.moeda)

    def dividido_por(self, divisor: Decimal) -> Money[M]:
        """Divide a quantia por um fator adimensional."""
        return Money(self.quantia / divisor, self.moeda)

    def razao(self, outro: Money[M]) -> Decimal:
        """Razão entre duas quantias da mesma moeda; o resultado é adimensional."""
        self._exigir_mesma_moeda(outro)
        return self.quantia / outro.quantia

    def arredondado(self) -> Money[M]:
        """Arredonda a centavos com `ROUND_HALF_UP` (ver seção 10 da arquitetura)."""
        return Money(self.quantia.quantize(CENTAVO, rounding=ROUND_HALF_UP), self.moeda)

    def zerado(self) -> Money[M]:
        """Um zero na mesma moeda — útil para pisos (ex.: imposto nunca negativo)."""
        return Money(Decimal("0"), self.moeda)

    def __repr__(self) -> str:
        """Representação fiel, sem esconder casas decimais."""
        return f"Money(quantia=Decimal('{self.quantia}'), moeda={self.moeda.__name__})"

    def __str__(self) -> str:
        """Representação para leitura humana, arredondada a centavos.

        >>> str(brl("10000"))
        'BRL 10,000.00'
        """
        return f"{self.moeda.__name__} {self.arredondado().quantia:,.2f}"


def brl(quantia: str | Decimal) -> Money[BRL]:
    """Constrói uma quantia em reais a partir de texto (nunca de `float`).

    >>> brl("1234.56").moeda is BRL
    True
    """
    return Money(Decimal(quantia), BRL)


def eur(quantia: str | Decimal) -> Money[EUR]:
    """Constrói uma quantia em euros a partir de texto (nunca de `float`).

    >>> eur("1234.56").moeda is EUR
    True
    """
    return Money(Decimal(quantia), EUR)


@dataclass(frozen=True, slots=True)
class Cambio:
    """Quantos reais vale 1 euro numa data.

    `data` e `fonte` são metadados opcionais (dor 2.7): quando presentes,
    alimentam a auditoria e a escolha de alíquota por vigência; quando
    ausentes, nada é inventado.

    >>> Cambio(Decimal("6.00")).para_brl(eur("100"))
    Money(quantia=Decimal('600.00'), moeda=BRL)
    """

    valor: Decimal
    data: date | None = None
    fonte: str | None = None

    def __post_init__(self) -> None:
        """Recusa câmbio não-`Decimal` ou não-positivo."""
        if not isinstance(self.valor, Decimal):
            raise TypeError(
                f"valor do câmbio deve ser Decimal, recebido {type(self.valor).__name__}"
            )
        if self.valor <= 0:
            raise ValueError(f"câmbio deve ser positivo, recebido {self.valor}")

    def para_eur(self, quantia: Money[BRL]) -> Money[EUR]:
        """Converte reais em euros dividindo pela cotação."""
        return Money(quantia.quantia / self.valor, EUR)

    def para_brl(self, quantia: Money[EUR]) -> Money[BRL]:
        """Converte euros em reais multiplicando pela cotação."""
        return Money(quantia.quantia * self.valor, BRL)

    def __str__(self) -> str:
        """Cotação com os metadados que existirem.

        >>> str(Cambio(Decimal("6.00"), date(2025, 3, 10), "PTAX"))
        'R$ 6.00/€ em 2025-03-10 (PTAX)'
        """
        partes = [f"R$ {self.valor}/€"]
        if self.data is not None:
            partes.append(f"em {self.data.isoformat()}")
        if self.fonte is not None:
            partes.append(f"({self.fonte})")
        return " ".join(partes)
