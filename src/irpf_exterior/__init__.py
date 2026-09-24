"""Núcleo de domínio da apuração de IRPF sobre investimentos no exterior.

Regras da Lei 14.754/2023 e da compensação do imposto retido em Portugal,
escritas como funções puras sobre dados imutáveis. A biblioteca não lê
arquivos, não acessa a rede e não consulta o relógio: tudo o que ela precisa
chega por parâmetro.

Para apurar um investimento que já aconteceu, use este módulo. Para simular um
que ainda não aconteceu — variando o câmbio ou o juro esperado — veja
`irpf_exterior.simulacao`, que é uma camada adjacente e opcional: nada dela é
calculado sem ser pedido.

Exemplo mínimo:

>>> from datetime import date
>>> from decimal import Decimal
>>> a = ApuracaoResgate.de_cf(
...     I=entrada("I", brl("10000.00"), "extrato: aporte"),
...     F=brl("13200.00"),
...     C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
...     C_f=Cambio(Decimal("6.00"), date(2025, 3, 10)),
... )
>>> str(a.IR_ef.valor)
'BRL 480.00'
"""

from irpf_exterior.apuracoes.resgate import ApuracaoResgate
from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money, brl, eur
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota, aliquota_vigente
from irpf_exterior.formulas import (
    REGISTRO,
    Formula,
    c_d,
    c_pct,
    f_eu,
    i_eu,
    ir_br,
    ir_ef,
    ir_pt,
    ir_ptbr,
    j,
    j_eu,
    r_br,
    r_cc,
    r_eu,
    r_eubr,
    r_liq,
    v_inv,
)
from irpf_exterior.portas import ProvedorDeCambio, RepositorioDeAliquotas
from irpf_exterior.rastreio import Calculado, entrada, explicar

__version__ = "0.1.0"

__all__ = [
    "BRL",
    "EUR",
    "REGISTRO",
    "TABELA_ALIQUOTAS",
    "Aliquota",
    "ApuracaoResgate",
    "Calculado",
    "Cambio",
    "Formula",
    "Money",
    "ProvedorDeCambio",
    "RepositorioDeAliquotas",
    "__version__",
    "aliquota_vigente",
    "brl",
    "c_d",
    "c_pct",
    "entrada",
    "eur",
    "explicar",
    "f_eu",
    "i_eu",
    "ir_br",
    "ir_ef",
    "ir_pt",
    "ir_ptbr",
    "j",
    "j_eu",
    "r_br",
    "r_cc",
    "r_eu",
    "r_eubr",
    "r_liq",
    "v_inv",
]
