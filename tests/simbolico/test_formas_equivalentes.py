"""SymPy: as formas documentadas não podem divergir da definição (dor 2.3).

O documento de referência apresenta várias fórmulas em duas versões. Aqui a
versão "em termos de inputs" que ele publica é confrontada com a forma
expandida *derivada* da definição encadeada.
"""

import sympy as sp

from irpf_exterior.formulas import REGISTRO
from irpf_exterior.simbolico import (
    DEFINICOES,
    DEFINICOES_SIMULACAO,
    INPUTS,
    INPUTS_SIMULACAO,
    SIMBOLOS,
    expandida,
    expandida_simulacao,
)

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
    """Nenhuma fórmula implementada pode ficar de fora dos modelos simbólicos.

    São dois modelos porque são duas parametrizações da mesma realidade: na
    apuração `J_eu` é derivado de um `F` conhecido; em simulação `J_eu` é dado
    e o `F` é consequência.
    """
    assert set(REGISTRO) == set(DEFINICOES) | set(DEFINICOES_SIMULACAO)


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


# --------------------------------------------------------------------------
# Modelo de simulação (Fórmulas 17-19): J_eu é input, F é derivado.
# --------------------------------------------------------------------------

J_eu, T_br_s = SIMBOLOS["J_eu"], SIMBOLOS["T_br"]


def test_projecao_so_deixa_inputs_de_simulacao() -> None:
    for nome in DEFINICOES_SIMULACAO:
        restantes = {str(s) for s in expandida_simulacao(nome).free_symbols}
        assert restantes <= INPUTS_SIMULACAO, f"{nome} depende de {restantes - INPUTS_SIMULACAO}"


def test_formula_17_e_a_inversa_da_15() -> None:
    """Projetar F a partir de J_eu e reextrair J_eu devolve o mesmo juro.

    Garante que simulação e apuração descrevem o mesmo sistema: o `F` que a
    Fórmula 17 projeta é exatamente o `F` que a Fórmula 15 leria de volta.
    """
    F_projetado = expandida_simulacao("F_proj")
    juro_reextraido = expandida("J_eu").subs(F, F_projetado)
    assert sp.simplify(juro_reextraido - J_eu) == 0


def test_no_cambio_de_equilibrio_a_vantagem_se_anula() -> None:
    """Substituindo C_f por C_eq no regime brasileiro, V_inv vira exatamente 0."""
    I_eu_s = I / C_i
    R_eubr_s = I_eu_s * J_eu * C_f
    R_br_s = I_eu_s * (1 + J_eu) * C_f - I
    vantagem_br = R_eubr_s - T_br_s * R_br_s

    no_equilibrio = vantagem_br.subs(C_f, expandida_simulacao("C_eq"))
    assert sp.simplify(no_equilibrio) == 0


def test_no_juro_de_equilibrio_a_vantagem_se_anula() -> None:
    """O espelho do anterior: substituindo J_eu por J_eq, V_inv vira 0."""
    I_eu_s = I / C_i
    R_eubr_s = I_eu_s * J_eu * C_f
    R_br_s = I_eu_s * (1 + J_eu) * C_f - I
    vantagem_br = R_eubr_s - T_br_s * R_br_s

    no_equilibrio = vantagem_br.subs(J_eu, expandida_simulacao("J_eq"))
    assert sp.simplify(no_equilibrio) == 0


def test_cambio_e_juro_de_equilibrio_sao_inversas() -> None:
    """Aplicar uma sobre o resultado da outra devolve o valor original."""
    ida = expandida_simulacao("C_eq").subs(J_eu, expandida_simulacao("J_eq"))
    assert sp.simplify(ida - C_f) == 0


def test_no_regime_portugues_investir_sempre_compensa() -> None:
    """Portugal tributa só o prêmio, então sobra (1 - T_pt) dele — sempre positivo.

    É por isso que o ponto de equilíbrio só existe no regime brasileiro: só o
    Brasil cobra imposto sobre o ganho cambial, que seria isento se o dinheiro
    ficasse parado.
    """
    I_eu_s = I / C_i
    R_eubr_s = I_eu_s * J_eu * C_f
    vantagem_pt = sp.simplify(R_eubr_s - T_pt * R_eubr_s)

    assert sp.simplify(vantagem_pt - R_eubr_s * (1 - T_pt)) == 0
    assert sp.solve(sp.Eq(vantagem_pt, 0), C_f) == []


def test_fronteira_acima_da_qual_nao_ha_equilibrio() -> None:
    """O denominador de C_eq zera exatamente em J_eu = T_br / (1 - T_br)."""
    denominador = T_br_s * (1 + J_eu) - J_eu
    raiz = sp.solve(sp.Eq(denominador, 0), J_eu)[0]
    assert sp.simplify(raiz - T_br_s / (1 - T_br_s)) == 0
    assert abs(float(raiz.subs(T_br_s, sp.Rational(15, 100))) - 0.17647058) < 1e-7
