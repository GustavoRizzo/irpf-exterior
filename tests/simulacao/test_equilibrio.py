"""Pontos de virada em forma fechada, e os regimes tributários."""

from datetime import date
from decimal import Decimal

from irpf_exterior import Cambio, brl
from irpf_exterior.formulas.projecao import Equilibrio, NuncaCompensa, SempreCompensa
from irpf_exterior.simulacao import (
    Cenario,
    apurar,
    cambio_de_equilibrio,
    juro_de_equilibrio,
    regime_vigente,
)

C_I = Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX")
C_F = Cambio(Decimal("8.00"), date(2025, 3, 10))


def cenario(J_eu: str, C_f: Cambio = C_F) -> Cenario:
    return Cenario(I=brl("10000.00"), C_i=C_I, J_eu=Decimal(J_eu), C_f=C_f)


def test_cambio_de_equilibrio_do_exemplo_documentado() -> None:
    """Com juro de 1%, investir deixa de compensar acima de R$ 5,30."""
    resultado = cambio_de_equilibrio(cenario("0.01")).valor
    assert isinstance(resultado, Equilibrio)
    assert round(resultado.valor, 4) == Decimal("5.3004")


def test_no_cambio_de_equilibrio_a_vantagem_e_praticamente_zero() -> None:
    """Confere a forma fechada rodando a apuração completa naquele ponto."""
    base = cenario("0.01")
    ponto = cambio_de_equilibrio(base).valor
    assert isinstance(ponto, Equilibrio)

    no_ponto = apurar(Cenario(I=base.I, C_i=base.C_i, J_eu=base.J_eu, C_f=Cambio(ponto.valor)))
    assert abs(no_ponto.V_inv.valor.quantia) < Decimal("0.01")
    assert regime_vigente(no_ponto) == "Brasil"


def test_acima_da_fronteira_nenhum_cambio_torna_investir_pior() -> None:
    resultado = cambio_de_equilibrio(cenario("0.20")).valor
    assert isinstance(resultado, SempreCompensa)
    assert "17.6471%" in resultado.motivo


def test_o_equilibrio_e_assintotico_perto_da_fronteira() -> None:
    """Aproximar-se de 17,647% por baixo empurra o equilíbrio para o infinito.

    Não há salto: o câmbio de equilíbrio cresce sem limite até o juro cruzar a
    fronteira, quando deixa de existir. Um `C_eq` absurdamente alto já é, na
    prática, a mesma resposta que `SempreCompensa` — quem monta gráfico precisa
    saber disso para não plotar um ponto em R$ 12.500/€.
    """
    equilibrios = []
    for juro in ("0.10", "0.17", "0.176", "0.1764"):
        resultado = cambio_de_equilibrio(cenario(juro)).valor
        assert isinstance(resultado, Equilibrio)
        equilibrios.append(resultado.valor)

    assert equilibrios == sorted(equilibrios), "o equilíbrio deve crescer com o juro"
    assert equilibrios[0] < Decimal("12")
    assert equilibrios[-1] > Decimal("10000")

    # cruzada a fronteira, o ponto de virada simplesmente não existe mais
    assert isinstance(cambio_de_equilibrio(cenario("0.18")).valor, SempreCompensa)


def test_juro_de_equilibrio_do_exemplo_documentado() -> None:
    """Se o euro for a R$ 8,00, a aplicação precisa render mais de 6,62%."""
    assert round(juro_de_equilibrio(cenario("0.01")).valor, 4) == Decimal("0.0662")


def test_no_juro_de_equilibrio_a_vantagem_e_praticamente_zero() -> None:
    base = cenario("0.01")
    minimo = juro_de_equilibrio(base).valor

    no_ponto = apurar(Cenario(I=base.I, C_i=base.C_i, J_eu=minimo, C_f=base.C_f))
    assert abs(no_ponto.V_inv.valor.quantia) < Decimal("0.01")


def test_sem_variacao_cambial_qualquer_juro_positivo_compensa() -> None:
    """Sem ganho cambial não há imposto sobre ele, então o mínimo é zero."""
    assert juro_de_equilibrio(cenario("0.05", C_f=Cambio(Decimal("5.00")))).valor == 0


def test_com_cambio_em_queda_o_juro_minimo_continua_zero() -> None:
    """Sem ganho cambial não há imposto a cobrir; a álgebra sugeriria negativo.

    A fração da Fórmula 19 foi derivada supondo imposto devido. Com o câmbio
    caindo, o rendimento em reais é negativo e o imposto é zero por piso, de
    modo que o equilíbrio verdadeiro é exatamente zero.
    """
    assert juro_de_equilibrio(cenario("0.05", C_f=Cambio(Decimal("4.00")))).valor == 0


def test_com_juro_nao_positivo_investir_nunca_compensa() -> None:
    """O outro "não existe equilíbrio": sem prêmio, não há o que comparar."""
    for juro in ("-0.10", "0"):
        resultado = cambio_de_equilibrio(cenario(juro)).valor
        assert isinstance(resultado, NuncaCompensa), juro
        assert "não paga prêmio" in resultado.motivo


def test_regime_portugues_quando_o_cambio_quase_nao_varia() -> None:
    """Com pouco ganho cambial, a base brasileira encolhe e Portugal prevalece."""
    apuracao = apurar(cenario("0.10", C_f=Cambio(Decimal("5.00"))))
    assert regime_vigente(apuracao) == "Portugal"
    assert apuracao.V_inv.valor.quantia > 0


def test_no_regime_portugues_investir_compensa_mesmo_com_juro_baixo() -> None:
    apuracao = apurar(cenario("0.001", C_f=Cambio(Decimal("5.00"))))
    assert regime_vigente(apuracao) == "Portugal"
    assert apuracao.investir_compensou()
