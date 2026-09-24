"""Cenários completos de ponta a ponta, com resultados conferidos à mão.

Cobre as quatro situações que a seção 8.4 exige: Brasil cobrando mais que
Portugal, Portugal cobrando mais que o Brasil, prejuízo em euros com ganho em
reais (puro efeito cambial) e câmbio constante.
"""

from datetime import date
from decimal import Decimal

from irpf_exterior import ApuracaoResgate, Cambio, brl, entrada, eur, explicar

APORTE = date(2024, 5, 2)
RESGATE = date(2025, 3, 10)


def apurar(I: str, F: str, C_i: str, C_f: str) -> ApuracaoResgate:
    return ApuracaoResgate.de_cf(
        I=entrada("I", brl(I), "extrato: aporte"),
        F=entrada("F", brl(F), "extrato: resgate"),
        C_i=Cambio(Decimal(C_i), APORTE, "PTAX"),
        C_f=Cambio(Decimal(C_f), RESGATE, "PTAX"),
    )


def test_brasil_cobra_mais_que_portugal() -> None:
    """€2.000 -> €2.200 com o euro subindo de R$5,00 para R$6,00."""
    a = apurar("10000.00", "13200.00", "5.00", "6.00")

    assert a.I_eu.valor == eur("2000")
    assert a.F_eu.valor == eur("2200")
    assert a.R_eu.valor == eur("200")
    assert a.R_br.valor == brl("3200.00")
    assert a.J.valor == Decimal("0.32")
    assert a.IR_pt.valor == eur("56.00")
    assert a.IR_ptbr.valor == brl("336.00")
    assert a.IR_br.valor == brl("480.00")
    assert a.IR_ef.valor == brl("480.00")
    assert a.R_liq.valor == brl("2720.00")
    assert a.a_pagar_no_brasil() == brl("144.00")

    # decomposição: dos R$ 3.200, dois terços vieram do câmbio
    assert a.R_cc.valor == brl("2000.00")
    assert a.R_eubr.valor == brl("1200.00")
    assert a.R_cc.valor + a.R_eubr.valor == a.R_br.valor
    assert a.J_eu.valor == Decimal("0.1")
    assert a.V_inv.valor == brl("720.00")
    assert a.investir_compensou()


def test_portugal_cobra_mais_que_o_brasil() -> None:
    """Ganho grande em euros com o euro caindo de R$5,00 para R$4,00.

    Portugal retém R$ 672,00; o Brasil só cobraria R$ 60,00. Paga-se o maior,
    e a diferença a maior não é restituída.
    """
    a = apurar("10000.00", "10400.00", "5.00", "4.00")

    assert a.R_eu.valor == eur("600")
    assert a.R_br.valor == brl("400.00")
    assert a.IR_pt.valor == eur("168.00")
    assert a.IR_ptbr.valor == brl("672.00")
    assert a.IR_br.valor == brl("60.00")
    assert a.IR_ef.valor == brl("672.00")
    assert a.R_liq.valor == brl("-272.00")
    assert a.a_pagar_no_brasil() == brl("0")

    # o câmbio destruiu R$ 2.000, a aplicação criou R$ 2.400
    assert a.R_cc.valor == brl("-2000.00")
    assert a.R_eubr.valor == brl("2400.00")
    assert a.V_inv.valor == brl("1728.00")
    assert a.investir_compensou()


def test_prejuizo_em_euros_com_ganho_em_reais() -> None:
    """Perdeu €500, mas o euro subiu de R$5,00 para R$8,00: o Brasil tributa.

    É a pergunta frequente do documento de referência — o investimento não
    rendeu em euros, e ainda assim há imposto, porque a base brasileira
    embute a variação cambial.
    """
    a = apurar("10000.00", "12000.00", "5.00", "8.00")

    assert a.R_eu.valor == eur("-500")
    assert a.IR_pt.valor == eur("0")
    assert a.IR_ptbr.valor == brl("0")
    assert a.R_br.valor == brl("2000.00")
    assert a.IR_br.valor == brl("300.00")
    assert a.IR_ef.valor == brl("300.00")
    assert a.a_pagar_no_brasil() == brl("300.00")

    # investir foi um mau negócio: o câmbio rendeu R$ 6.000 e a aplicação
    # destruiu R$ 4.000, além de gerar imposto que parado não haveria
    assert a.R_cc.valor == brl("6000.00")
    assert a.R_eubr.valor == brl("-4000.00")
    assert a.J_eu.valor == Decimal("-0.25")
    assert a.V_inv.valor == brl("-4300.00")
    assert not a.investir_compensou()


def test_cambio_constante_zera_o_efeito_cambial() -> None:
    """Sem variação cambial, R_cc é zero e as duas bases só diferem pela conversão."""
    a = apurar("11000.00", "13200.00", "5.50", "5.50")

    assert a.C_d.valor == Decimal("0")
    assert a.C_pct.valor == Decimal("0")
    assert a.R_cc.valor == brl("0")
    assert a.R_eu.valor == eur("400")
    assert a.R_br.valor == brl("2200.00")
    assert a.R_eu.valor.quantia * Decimal("5.50") == a.R_br.valor.quantia
    assert a.IR_ptbr.valor == brl("616.00")
    assert a.IR_br.valor == brl("330.00")
    assert a.IR_ef.valor == brl("616.00")


def test_de_para_da_receita_usa_os_valores_em_reais() -> None:
    a = apurar("10000.00", "13200.00", "5.00", "6.00")
    campos = a.de_para_receita()

    assert campos["Rendimento ou Perda"].valor == brl("3200.00")
    assert campos["Imposto pago no Exterior"].valor == brl("336.00")


def test_auditoria_mostra_a_arvore_inteira_ate_os_inputs() -> None:
    a = apurar("10000.00", "13200.00", "5.00", "6.00")
    texto = explicar(a.IR_ef)

    assert "Fórmula 12: IR_ef = max(IR_ptbr, IR_br)" in texto
    assert "Lei 14.754/2023, Art. 12" in texto
    assert "input I  [extrato: aporte]" in texto
    assert "R$ 5.00/€ em 2024-05-02 (PTAX)" in texto


def test_construtor_por_variacao_cambial_concorda_com_o_principal() -> None:
    por_cd = ApuracaoResgate.de_cd(
        I=brl("10000.00"),
        F=brl("13200.00"),
        C_i=Cambio(Decimal("5.00"), APORTE),
        C_d=Decimal("1.00"),
        data_final=RESGATE,
    )
    assert por_cd.C_f.valor == Decimal("6.00")
    assert por_cd.IR_ef.valor == brl("480.00")


def test_aplicacao_rendeu_e_mesmo_assim_investir_foi_pior() -> None:
    """O caso contraintuitivo documentado na seção de decomposição.

    A aplicação rende +1% em euros — não deu prejuízo — mas o euro sobe 60%.
    Parado, os R$ 6.000,00 de ganho cambial seriam isentos; investidos, entram
    na base de cálculo e pagam 15%. Os R$ 900,00 de imposto extra não são
    cobertos pelos R$ 160,00 que a aplicação rendeu.
    """
    a = apurar("10000.00", "16160.00", "5.00", "8.00")

    assert a.J_eu.valor == Decimal("0.01")  # a aplicação rendeu
    assert a.R_cc.valor == brl("6000.00")  # o câmbio sozinho
    assert a.R_eubr.valor == brl("160.00")  # o prêmio da aplicação
    assert a.R_br.valor == brl("6160.00")  # base de cálculo brasileira
    assert a.IR_ef.valor == brl("924.00")  # imposto sobre tudo
    assert a.R_liq.valor == brl("5236.00")  # sobrou tendo investido
    assert a.V_inv.valor == brl("-764.00")  # parado teria sido melhor
    assert not a.investir_compensou()

    # as duas formas da Fórmula 16 coincidem
    assert a.V_inv.valor == a.R_eubr.valor - a.IR_ef.valor
    # e a decomposição fecha
    assert a.R_cc.valor + a.R_eubr.valor == a.R_br.valor


def test_ponto_de_equilibrio_entre_investir_e_deixar_parado() -> None:
    """Quando o prêmio da aplicação iguala o imposto, tanto faz ter investido.

    Com o euro subindo de R$ 5,00 para R$ 8,00, o imposto brasileiro prevalece,
    então o prêmio precisa cobrir 15% de todo o R_br para empatar.
    """
    a = apurar("10000.00", "17058.82", "5.00", "8.00")

    assert a.IR_ef.valor == brl("1058.82")
    assert a.R_eubr.valor == brl("1058.82")
    assert a.V_inv.valor == brl("0.00")
    assert not a.investir_compensou()  # empate não paga o risco da aplicação


def test_auditoria_da_vantagem_mostra_os_dois_mundos() -> None:
    """A árvore de V_inv desce até o que foi investido e o que ficaria parado."""
    a = apurar("10000.00", "13200.00", "5.00", "6.00")
    texto = explicar(a.V_inv)

    assert "Fórmula 16: V_inv = R_liq - R_cc" in texto
    assert "Fórmula 13: R_liq = R_br - IR_ef" in texto
    assert "Fórmula 8: R_cc = I · C_%" in texto
    assert "Art. 2º, §3º" in texto
