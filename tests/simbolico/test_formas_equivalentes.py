"""SymPy: as formas documentadas não podem divergir da definição (dor 2.3).

O documento de referência apresenta várias fórmulas em duas versões. Aqui a
versão "em termos de inputs" que ele publica é confrontada com a forma
expandida *derivada* da definição encadeada.
"""

import sympy as sp

from irpf_exterior.formulas import REGISTRO
from irpf_exterior.simbolico import DEFINICOES, INPUTS, SIMBOLOS, expandida

S = SIMBOLOS
I, F, C_i, C_f, T_pt, T_br = (S["I"], S["F"], S["C_i"], S["C_f"], S["T_pt"], S["T_br"])

# As formas "em termos de inputs" exatamente como o documento as publica.
FORMAS_PUBLICADAS = {
    "C_pct": (C_f - C_i) / C_i,
    "R_eu": F / C_f - I / C_i,
    "J": (F - I) / I,
    "R_cc": I * (C_f - C_i) / C_i,
    "IR_pt": (F / C_f - I / C_i) * T_pt,
    "IR_ptbr": (F / C_f - I / C_i) * T_pt * C_f,
    "IR_br": (F - I) * T_br,
    "IR_ef": sp.Max((F / C_f - I / C_i) * T_pt * C_f, (F - I) * T_br),
    "R_liq": (F - I) - sp.Max((F / C_f - I / C_i) * T_pt * C_f, (F - I) * T_br),
    "R_eubr": (F / C_f - I / C_i) * C_f,
    "J_eu": F * C_i / (I * C_f) - 1,
    "V_inv": (F / C_f - I / C_i) * C_f - sp.Max((F / C_f - I / C_i) * T_pt * C_f, (F - I) * T_br),
}


def test_toda_forma_publicada_corresponde_a_uma_formula() -> None:
    assert set(FORMAS_PUBLICADAS) <= set(DEFINICOES)


def test_formas_publicadas_equivalem_as_derivadas() -> None:
    divergentes = {
        nome: (expandida(nome), publicada)
        for nome, publicada in FORMAS_PUBLICADAS.items()
        if sp.simplify(expandida(nome) - publicada) != 0
    }
    assert not divergentes, f"formas divergentes: {divergentes}"


def test_expansao_so_deixa_inputs() -> None:
    for nome in DEFINICOES:
        restantes = {str(s) for s in expandida(nome).free_symbols}
        assert restantes <= INPUTS, f"{nome} ainda depende de {restantes - INPUTS}"


def test_modelo_simbolico_cobre_o_registro_de_formulas() -> None:
    """Nenhuma fórmula implementada pode ficar de fora do modelo simbólico."""
    assert set(REGISTRO) == set(DEFINICOES)


def test_decomposicao_do_rendimento_e_identidade_algebrica() -> None:
    """R_br = R_cc + R_eubr, demonstrado simbolicamente e não por amostragem.

    Esta é a identidade que sustenta toda a seção de decomposição do documento
    de referência; se ela deixar de valer, as Fórmulas 14 e 16 perdem o sentido.
    """
    diferenca = expandida("R_br") - expandida("R_cc") - expandida("R_eubr")
    assert sp.simplify(diferenca) == 0


def test_vantagem_de_investir_equivale_ao_premio_menos_o_imposto() -> None:
    """V_inv = R_liq - R_cc é algebricamente o mesmo que R_eubr - IR_ef."""
    equivalente = expandida("R_eubr") - expandida("IR_ef")
    assert sp.simplify(expandida("V_inv") - equivalente) == 0


def test_juro_da_aplicacao_nao_depende_do_cambio_quando_ele_e_constante() -> None:
    """Com C_i = C_f, J_eu colapsa em (F - I) / I: o câmbio some da expressão."""
    C = sp.Symbol("C", positive=True)
    sem_variacao = expandida("J_eu").subs({C_i: C, C_f: C})
    assert sp.simplify(sem_variacao - (F - I) / I) == 0
