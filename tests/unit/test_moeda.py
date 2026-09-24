"""Money e Cambio: as barreiras contra misturar moedas (dor 2.1)."""

from datetime import date
from decimal import Decimal

import pytest

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money, brl, eur


def test_soma_de_moedas_iguais() -> None:
    assert brl("10.00") + brl("2.50") == brl("12.50")


def test_soma_de_moedas_diferentes_levanta_type_error() -> None:
    with pytest.raises(TypeError, match="BRL com EUR"):
        brl("10.00") + eur("1.00")  # type: ignore[operator]


def test_subtracao_de_moedas_diferentes_levanta_type_error() -> None:
    with pytest.raises(TypeError, match="BRL com EUR"):
        brl("10.00") - eur("1.00")  # type: ignore[operator]


def test_comparacao_de_moedas_diferentes_levanta_type_error() -> None:
    with pytest.raises(TypeError, match="BRL com EUR"):
        _ = brl("10.00") > eur("1.00")  # type: ignore[operator]


def test_quantia_float_e_recusada() -> None:
    with pytest.raises(TypeError, match="deve ser Decimal"):
        Money(10.0, BRL)  # type: ignore[arg-type]


def test_arredondamento_half_up() -> None:
    assert brl("1.005").arredondado() == brl("1.01")
    assert brl("1.004").arredondado() == brl("1.00")
    assert brl("-1.005").arredondado() == brl("-1.01")


def test_conversao_ida_e_volta_preserva_a_moeda() -> None:
    cambio = Cambio(Decimal("6.00"))
    assert cambio.para_eur(brl("600.00")) == eur("100")
    assert cambio.para_brl(eur("100")).moeda is BRL


def test_cambio_nao_positivo_e_recusado() -> None:
    with pytest.raises(ValueError, match="deve ser positivo"):
        Cambio(Decimal("0"))


def test_cambio_float_e_recusado() -> None:
    with pytest.raises(TypeError, match="deve ser Decimal"):
        Cambio(6.0)  # type: ignore[arg-type]


def test_str_do_cambio_omite_metadados_ausentes() -> None:
    assert str(Cambio(Decimal("6.00"))) == "R$ 6.00/€"
    assert str(Cambio(Decimal("6.00"), date(2025, 3, 10))) == "R$ 6.00/€ em 2025-03-10"


def test_razao_e_adimensional() -> None:
    assert brl("3200.00").razao(brl("10000.00")) == Decimal("0.32")


def test_zerado_preserva_a_moeda() -> None:
    assert eur("-500").zerado() == Money(Decimal("0"), EUR)
