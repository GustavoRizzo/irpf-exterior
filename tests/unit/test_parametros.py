"""Alíquotas por vigência, incluindo o princípio "nunca adivinhar" (4.5)."""

from datetime import date
from decimal import Decimal

import pytest

from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota, aliquota_vigente

T_BR_ATE_2029 = Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1), date(2029, 12, 31))
T_BR_DESDE_2030 = Aliquota("T_br", Decimal("0.20"), date(2030, 1, 1))
TABELA_DUPLA = (T_BR_ATE_2029, T_BR_DESDE_2030)
TABELA_UNICA = (T_BR_ATE_2029,)


def test_escolhe_a_vigencia_da_data() -> None:
    assert aliquota_vigente(TABELA_DUPLA, "T_br", date(2025, 3, 10)).valor == Decimal("0.15")
    assert aliquota_vigente(TABELA_DUPLA, "T_br", date(2031, 3, 10)).valor == Decimal("0.20")


def test_sem_data_aceita_apenas_vigencia_unica() -> None:
    assert aliquota_vigente(TABELA_UNICA, "T_br", None) is T_BR_ATE_2029


def test_sem_data_e_com_varias_vigencias_pede_a_data() -> None:
    with pytest.raises(ValueError, match="Informe a data de referência"):
        aliquota_vigente(TABELA_DUPLA, "T_br", None)


def test_nome_desconhecido_lista_os_disponiveis() -> None:
    with pytest.raises(LookupError, match="Disponíveis: T_br"):
        aliquota_vigente(TABELA_DUPLA, "T_xx", date(2025, 1, 1))


def test_data_fora_de_qualquer_vigencia() -> None:
    with pytest.raises(LookupError, match="vigente em 2023-06-01"):
        aliquota_vigente(TABELA_DUPLA, "T_br", date(2023, 6, 1))


def test_vigencias_sobrepostas_sao_denunciadas() -> None:
    sobreposta = (T_BR_ATE_2029, Aliquota("T_br", Decimal("0.18"), date(2025, 1, 1)))
    with pytest.raises(ValueError, match="se sobrepõem"):
        aliquota_vigente(sobreposta, "T_br", date(2026, 1, 1))


def test_fim_anterior_ao_inicio_e_recusado() -> None:
    with pytest.raises(ValueError, match="anterior ao início"):
        Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1), date(2023, 1, 1))


def test_valor_float_e_recusado() -> None:
    with pytest.raises(TypeError, match="deve ser Decimal"):
        Aliquota("T_br", 0.15, date(2024, 1, 1))  # type: ignore[arg-type]


def test_tabela_padrao_tem_as_duas_aliquotas_vigentes_hoje() -> None:
    em = date(2026, 9, 24)
    assert aliquota_vigente(TABELA_ALIQUOTAS, "T_br", em).valor == Decimal("0.15")
    assert aliquota_vigente(TABELA_ALIQUOTAS, "T_pt", em).valor == Decimal("0.28")
