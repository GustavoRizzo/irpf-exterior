"""Modelo simbólico das fórmulas (requer o extra `simbolico`, que traz SymPy).

Existe por causa da dor 2.3: o documento de referência apresenta várias
fórmulas em duas versões — a encadeada e a "em termos de inputs" — e as duas
já divergiram uma vez. Aqui a forma encadeada é a única escrita à mão; a
expandida é **derivada** por substituição (princípio 4.4), o que a torna
impossível de divergir.

Este módulo não participa de nenhum cálculo monetário: ele serve à
documentação de auditoria e aos testes simbólicos.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

import sympy as sp

__all__ = [
    "DEFINICOES",
    "DEFINICOES_SIMULACAO",
    "INPUTS",
    "INPUTS_SIMULACAO",
    "SIMBOLOS",
    "encadeada",
    "expandida",
    "expandida_simulacao",
    "latex_expandida",
]

_NOMES_INPUT = ("I", "F", "C_i", "C_f", "T_pt", "T_br")

SIMBOLOS: Mapping[str, sp.Symbol] = MappingProxyType(
    {
        nome: sp.Symbol(nome, positive=nome.startswith(("C_", "T_")), real=True)
        for nome in (
            *_NOMES_INPUT,
            "C_d",
            "C_pct",
            "I_eu",
            "F_eu",
            "R_eu",
            "R_br",
            "J",
            "R_cc",
            "IR_pt",
            "IR_ptbr",
            "IR_br",
            "IR_ef",
            "R_liq",
            "R_eubr",
            "J_eu",
            "V_inv",
            "F_proj",
            "C_eq",
            "J_eq",
        )
    }
)
"""Um símbolo por variável do glossário. Câmbios e alíquotas são positivos."""

INPUTS: frozenset[str] = frozenset(_NOMES_INPUT)
"""As variáveis que não derivam de nenhuma outra."""

_s = SIMBOLOS

_DEFINICOES_MUTAVEL: dict[str, sp.Expr] = {
    "C_d": _s["C_f"] - _s["C_i"],
    "C_pct": _s["C_d"] / _s["C_i"],
    "I_eu": _s["I"] / _s["C_i"],
    "F_eu": _s["F"] / _s["C_f"],
    "R_eu": _s["F_eu"] - _s["I_eu"],
    "R_br": _s["F"] - _s["I"],
    "J": _s["R_br"] / _s["I"],
    "R_cc": _s["I"] * _s["C_pct"],
    "IR_pt": _s["R_eu"] * _s["T_pt"],
    "IR_ptbr": _s["IR_pt"] * _s["C_f"],
    "IR_br": _s["R_br"] * _s["T_br"],
    "IR_ef": sp.Max(_s["IR_ptbr"], _s["IR_br"]),
    "R_liq": _s["R_br"] - _s["IR_ef"],
    "R_eubr": _s["R_eu"] * _s["C_f"],
    "J_eu": _s["R_eu"] / _s["I_eu"],
    "V_inv": _s["R_liq"] - _s["R_cc"],
}

DEFINICOES: Mapping[str, sp.Expr] = MappingProxyType(_DEFINICOES_MUTAVEL)
"""Cada fórmula na forma encadeada, exatamente como o código a implementa.

O piso em zero de `IR_pt` e `IR_br` não é modelado: aqui interessa a álgebra
das formas documentadas, não o tratamento de prejuízo. O mesmo vale para o
piso de `J_eq` e para as guardas de `C_eq` — é justamente por a álgebra ignorar
os pisos que o código precisa tratá-los.
"""


_DEFINICOES_SIMULACAO_MUTAVEL: dict[str, sp.Expr] = {
    "I_eu": _s["I"] / _s["C_i"],
    "F_proj": _s["I_eu"] * (1 + _s["J_eu"]) * _s["C_f"],
    "C_eq": _s["C_i"] * _s["T_br"] / (_s["T_br"] * (1 + _s["J_eu"]) - _s["J_eu"]),
    "J_eq": _s["T_br"] * (_s["C_f"] - _s["C_i"]) / (_s["C_f"] * (1 - _s["T_br"])),
}

DEFINICOES_SIMULACAO: Mapping[str, sp.Expr] = MappingProxyType(_DEFINICOES_SIMULACAO_MUTAVEL)
"""A mesma realidade, parametrizada para simulação.

Aqui `J_eu` é **input** e `F` é derivado — o inverso do modelo de apuração.
É essa troca que torna os eixos `J_eu` e `C_f` ortogonais. As fórmulas de
equilíbrio só fazem sentido nesta parametrização: elas respondem por um `F`
que ainda não existe.
"""

INPUTS_SIMULACAO: frozenset[str] = INPUTS | {"J_eu"}
"""Em simulação o juro é dado e o valor resgatado é consequência."""


def _expandir(nome: str, definicoes: Mapping[str, sp.Expr]) -> sp.Expr:
    """Substitui as variáveis derivadas até sobrarem apenas inputs."""
    try:
        expressao = definicoes[nome]
    except KeyError:
        raise KeyError(
            f"{nome!r} não é uma variável derivada. Derivadas: {', '.join(sorted(definicoes))}."
        ) from None
    while True:
        derivadas = {
            simbolo
            for simbolo in expressao.free_symbols
            if str(simbolo) in definicoes and str(simbolo) != nome
        }
        if not derivadas:
            return sp.simplify(expressao)
        expressao = expressao.subs({s: definicoes[str(s)] for s in derivadas})


def expandida_simulacao(nome: str) -> sp.Expr:
    """A forma expandida no modelo de simulação (com `J_eu` como input).

    >>> sorted(str(s) for s in expandida_simulacao("C_eq").free_symbols)
    ['C_i', 'J_eu', 'T_br']
    """
    return _expandir(nome, DEFINICOES_SIMULACAO)


def encadeada(nome: str) -> sp.Expr:
    """A definição de `nome` em termos das variáveis imediatamente anteriores."""
    try:
        return DEFINICOES[nome]
    except KeyError:
        raise KeyError(
            f"{nome!r} não é uma variável derivada. Derivadas: {', '.join(sorted(DEFINICOES))}."
        ) from None


def expandida(nome: str) -> sp.Expr:
    """A definição de `nome` reduzida somente a inputs, por substituição.

    >>> sp.simplify(expandida("R_eu") - (SIMBOLOS["F"] / SIMBOLOS["C_f"]
    ...                                  - SIMBOLOS["I"] / SIMBOLOS["C_i"]))
    0
    """
    return _expandir(nome, DEFINICOES)


def latex_expandida(nome: str) -> str:
    """A forma expandida em LaTeX, para o catálogo de auditoria.

    Procura primeiro no modelo de apuração e, se a fórmula não existir lá,
    no de simulação — é assim que as Fórmulas 17–19 entram no catálogo.
    """
    modelo = DEFINICOES if nome in DEFINICOES else DEFINICOES_SIMULACAO
    return sp.latex(_expandir(nome, modelo))
