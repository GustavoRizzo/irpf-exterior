"""Rastreabilidade: todo valor calculado carrega de onde veio.

Responde à dor 2.4 (auditoria). Um `Calculado[T]` é o valor mais a sua
proveniência; como as entradas podem ser outros `Calculado`, o conjunto forma
uma árvore que `explicar()` imprime de cima a baixo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

__all__ = ["Calculado", "entrada", "explicar"]

_INDENTACAO = "  "
_SETA = "  ←  "


@dataclass(frozen=True, slots=True)
class Calculado[T]:
    """Um valor acompanhado da sua origem.

    Attributes:
        valor: o resultado em si (`Money`, `Decimal`, ...).
        descricao: referência e expressão da fórmula, ou `input <nome>`.
        fonte: base legal ou origem do dado, quando conhecida.
        entradas: pares `(nome, valor)`; o valor pode ser outro `Calculado`.
    """

    valor: T
    descricao: str
    fonte: str | None = None
    entradas: tuple[tuple[str, object], ...] = field(default=())

    def __str__(self) -> str:
        """Uma linha: o valor, a fórmula e (se houver) a fonte."""
        linha = f"{_formatar(self.valor)}{_SETA}{self.descricao}"
        return linha if self.fonte is None else f"{linha}  [{self.fonte}]"


def entrada[T](nome: str, valor: T, fonte: str | None = None) -> Calculado[T]:
    """Embrulha um dado bruto como folha da árvore de auditoria.

    >>> from irpf_exterior.dominio.moeda import brl
    >>> print(entrada("I", brl("10000.00"), "extrato: aporte"))
    BRL 10,000.00  ←  input I  [extrato: aporte]
    """
    return Calculado(valor=valor, descricao=f"input {nome}", fonte=fonte)


def _formatar(valor: object) -> str:
    """Formata um valor de domínio para leitura humana."""
    if isinstance(valor, Decimal):
        return f"{valor.quantize(Decimal('0.000001')).normalize():f}"
    return str(valor)


def explicar[T](calculado: Calculado[T], _nivel: int = 0) -> str:
    """Percorre a árvore de proveniência e devolve um texto legível.

    Metadados ausentes são omitidos em silêncio (dor 2.7): a saída nunca
    inventa uma fonte ou uma data que não foi fornecida.
    """
    recuo = _INDENTACAO * _nivel
    linhas = [f"{recuo}{calculado}"]
    for nome, valor in calculado.entradas:
        if isinstance(valor, Calculado):
            linhas.append(f"{recuo}{_INDENTACAO}{nome}:")
            linhas.append(explicar(valor, _nivel + 2))
        else:
            linhas.append(f"{recuo}{_INDENTACAO}{nome}: {_formatar(valor)}")
    return "\n".join(linhas)
