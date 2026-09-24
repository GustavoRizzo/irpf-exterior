"""Varredura: descrever é barato, executar é sob demanda.

Uma `Varredura` só **descreve** a simulação — construí-la não calcula nada.
`executar` devolve um iterador preguiçoso, de modo que quem precisa apenas do
ponto de equilíbrio não paga pelos duzentos pontos de um gráfico.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, replace
from decimal import Decimal
from types import MappingProxyType
from typing import assert_never

from irpf_exterior.apuracoes.resgate import ApuracaoResgate
from irpf_exterior.dominio.moeda import Cambio
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota
from irpf_exterior.simulacao.cenario import Cenario, apurar
from irpf_exterior.simulacao.eixo import Eixo, EixoCambioFinal, EixoJuro

__all__ = ["COLUNAS_PADRAO", "Ponto", "Varredura", "executar", "para_tabela", "serie"]

FONTE_SIMULADA = "simulação"


@dataclass(frozen=True, slots=True)
class Ponto:
    """Um ponto da varredura: o valor do eixo e a apuração que ele produz.

    A apuração vem inteira, então qualquer ponto de um gráfico pode ser
    passado a `explicar()` — a auditoria não se perde na simulação.
    """

    valor: Decimal
    cenario: Cenario
    apuracao: ApuracaoResgate


@dataclass(frozen=True, slots=True)
class Varredura:
    """A descrição de uma simulação. Construí-la não calcula nada."""

    base: Cenario
    eixo: Eixo
    tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS
    T_br: Aliquota | None = None
    T_pt: Aliquota | None = None


def _variar(cenario: Cenario, eixo: Eixo, valor: Decimal) -> Cenario:
    """Devolve o cenário com o valor do eixo substituído."""
    match eixo:
        case EixoCambioFinal():
            simulado = Cambio(valor, cenario.C_f.data, FONTE_SIMULADA)
            return replace(cenario, C_f=simulado)
        case EixoJuro():
            return replace(cenario, J_eu=valor)
        case _:  # pragma: no cover - o mypy garante a exaustividade
            assert_never(eixo)


def executar(varredura: Varredura) -> Iterator[Ponto]:
    """Percorre o eixo, uma apuração por vez, sem materializar a varredura.

    A cotação simulada preserva a data do cenário base — é a data prevista do
    resgate, e é ela que decide a vigência das alíquotas — mas troca a fonte
    por "simulação", para que nenhum valor hipotético se passe por cotação
    real na auditoria.
    """
    for valor in varredura.eixo.valores:
        cenario = _variar(varredura.base, varredura.eixo, valor)
        yield Ponto(
            valor=valor,
            cenario=cenario,
            apuracao=apurar(
                cenario,
                tabela=varredura.tabela,
                T_br=varredura.T_br,
                T_pt=varredura.T_pt,
            ),
        )


def serie[T](
    varredura: Varredura, extrair: Callable[[ApuracaoResgate], T]
) -> Iterator[tuple[Decimal, T]]:
    """Só a coluna que o gráfico precisa, sem reter as apurações na memória.

    >>> # serie(v, lambda a: a.V_inv.valor.quantia)
    """
    for ponto in executar(varredura):
        yield ponto.valor, extrair(ponto.apuracao)


COLUNAS_PADRAO: Mapping[str, Callable[[ApuracaoResgate], Decimal]] = MappingProxyType(
    {
        "R_cc": lambda a: a.R_cc.valor.quantia,
        "R_eubr": lambda a: a.R_eubr.valor.quantia,
        "R_br": lambda a: a.R_br.valor.quantia,
        "IR_ef": lambda a: a.IR_ef.valor.quantia,
        "R_liq": lambda a: a.R_liq.valor.quantia,
        "V_inv": lambda a: a.V_inv.valor.quantia,
        "J_eu": lambda a: a.J_eu.valor,
    }
)
"""As colunas mais úteis para um gráfico comparativo. Substituível."""


def para_tabela(
    varredura: Varredura,
    colunas: Mapping[str, Callable[[ApuracaoResgate], Decimal]] = COLUNAS_PADRAO,
) -> Iterator[Mapping[str, Decimal]]:
    """Uma linha por ponto, pronta para virar DataFrame ou tabela na tela.

    A biblioteca não desenha nada: entrega os números e o consumidor escolhe
    a ferramenta (`pd.DataFrame(list(para_tabela(v)))` resolve no notebook).
    """
    nome_do_eixo = varredura.eixo.nome
    for ponto in executar(varredura):
        linha = {nome_do_eixo: ponto.valor}
        linha.update({nome: extrair(ponto.apuracao) for nome, extrair in colunas.items()})
        yield MappingProxyType(linha)
