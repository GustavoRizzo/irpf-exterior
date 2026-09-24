"""Projeção do F e consistência entre simulação e apuração."""

from datetime import date
from decimal import Decimal

from irpf_exterior import Cambio, brl, explicar
from irpf_exterior.simulacao import Cenario, apurar

BASE = Cenario(
    I=brl("10000.00"),
    C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
    J_eu=Decimal("0.10"),
    C_f=Cambio(Decimal("6.00"), date(2025, 3, 10)),
)


def test_projeta_o_valor_resgatado() -> None:
    """€ 2.000 rendendo 10% viram € 2.200, que a R$ 6,00 são R$ 13.200."""
    assert apurar(BASE).F.valor == brl("13200.00")


def test_apuracao_projetada_bate_com_a_apuracao_do_extrato() -> None:
    """O cenário simulado reproduz o golden test do resgate real."""
    a = apurar(BASE)
    assert a.R_br.valor == brl("3200.00")
    assert a.IR_ef.valor == brl("480.00")
    assert a.V_inv.valor == brl("720.00")


def test_juro_projetado_volta_intacto_na_apuracao() -> None:
    """Fórmulas 17 e 15 são inversas: o que foi projetado é o que se lê."""
    assert apurar(BASE).J_eu.valor == BASE.J_eu


def test_auditoria_mostra_que_o_f_foi_projetado() -> None:
    """Simular não perde rastreabilidade: o F carrega a Fórmula 17."""
    texto = explicar(apurar(BASE).R_br)
    assert "Fórmula 17: F_proj = I_eu · (1 + J_eu) · C_f" in texto
    assert "input I" in texto


def test_juro_negativo_projeta_perda() -> None:
    cenario = Cenario(I=brl("10000.00"), C_i=BASE.C_i, J_eu=Decimal("-0.25"), C_f=BASE.C_f)
    a = apurar(cenario)
    assert a.F.valor == brl("9000.00")
    assert a.IR_pt.valor.quantia == 0
