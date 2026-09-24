"""Portas: o formato dos dados que o núcleo espera do mundo externo.

Só contratos, nenhuma implementação. Os adaptadores (PTAX, leitor de extrato,
banco de dados) vivem **fora** desta biblioteca. Nenhuma função de cálculo
recebe uma porta: o consumidor usa a porta para obter os dados e só então
chama a função pura.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from irpf_exterior.dominio.moeda import Cambio
from irpf_exterior.dominio.parametros import Aliquota

__all__ = ["ProvedorDeCambio", "RepositorioDeAliquotas"]


class ProvedorDeCambio(Protocol):
    """Fornece a cotação EUR/BRL de uma data (ex.: um cliente da API PTAX)."""

    def cambio_em(self, dia: date) -> Cambio:
        """Devolve a cotação vigente no dia, ou levanta erro se não houver.

        A implementação não deve "aproximar" um dia sem cotação (feriado, fim
        de semana) sem que o consumidor tenha pedido: adivinhar aqui é
        adivinhar no resultado (princípio 4.5).
        """
        ...


class RepositorioDeAliquotas(Protocol):
    """Fornece a tabela de alíquotas a ser usada numa apuração."""

    def tabela(self) -> tuple[Aliquota, ...]:
        """Devolve a tabela completa, com todas as vigências conhecidas."""
        ...
