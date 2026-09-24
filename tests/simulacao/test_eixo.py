"""Construção dos eixos de varredura."""

from decimal import Decimal

import pytest

from irpf_exterior.simulacao import em_torno_de, intervalo


def test_intervalo_inclui_as_duas_pontas() -> None:
    assert intervalo("1.0", "1.4", "0.2") == (Decimal("1.0"), Decimal("1.2"), Decimal("1.4"))


def test_intervalo_para_antes_quando_o_passo_nao_divide_exato() -> None:
    assert intervalo("1.0", "1.5", "0.2") == (
        Decimal("1.0"),
        Decimal("1.2"),
        Decimal("1.4"),
    )


def test_intervalo_nao_acumula_erro_ao_longo_do_eixo() -> None:
    """Cada valor é `de + i · passo`, nunca uma soma acumulada."""
    valores = intervalo("0.1", "1.0", "0.1")
    assert valores[-1] == Decimal("1.0")
    assert len(valores) == 10


def test_intervalo_de_um_unico_ponto() -> None:
    assert intervalo("5.00", "5.00", "0.10") == (Decimal("5.00"),)


def test_intervalo_recusa_passo_nao_positivo() -> None:
    with pytest.raises(ValueError, match="passo deve ser positivo"):
        intervalo("1.0", "2.0", "0")


def test_intervalo_recusa_limites_invertidos() -> None:
    with pytest.raises(ValueError, match="intervalo invertido"):
        intervalo("2.0", "1.0", "0.1")


def test_em_torno_de_mantem_a_base_no_centro() -> None:
    valores = em_torno_de("5.00", "0.20", pontos=3)
    assert valores == (Decimal("4.00"), Decimal("5.00"), Decimal("6.00"))


def test_em_torno_de_e_simetrico() -> None:
    valores = em_torno_de("5.00", "0.20", pontos=11)
    centro = valores[len(valores) // 2]
    assert centro == Decimal("5.00")
    assert valores[0] + valores[-1] == centro * 2


def test_em_torno_de_recusa_numero_par_de_pontos() -> None:
    with pytest.raises(ValueError, match="ímpar"):
        em_torno_de("5.00", "0.20", pontos=10)


def test_em_torno_de_recusa_variacao_nao_positiva() -> None:
    with pytest.raises(ValueError, match="variação deve ser positiva"):
        em_torno_de("5.00", "0", pontos=5)
