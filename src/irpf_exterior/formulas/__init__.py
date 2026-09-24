"""As fórmulas do documento de referência, na forma encadeada.

As Fórmulas 1–13 apuram o imposto; as 14–16 decompõem o rendimento e
comparam o investimento com deixar o dinheiro parado, sem afetar o
imposto devido.

Importar este pacote basta para que o `REGISTRO` fique completo.
"""

from irpf_exterior.formulas._base import REGISTRO, Formula, formula
from irpf_exterior.formulas.analise import j_eu, r_eubr, v_inv
from irpf_exterior.formulas.cambio import c_d, c_pct, f_eu, i_eu, r_cc
from irpf_exterior.formulas.imposto import ir_br, ir_ef, ir_pt, ir_ptbr, r_liq
from irpf_exterior.formulas.projecao import c_eq, f_proj, j_eq
from irpf_exterior.formulas.rendimento import j, r_br, r_eu

__all__ = [
    "REGISTRO",
    "Formula",
    "c_d",
    "c_eq",
    "c_pct",
    "f_eu",
    "f_proj",
    "formula",
    "i_eu",
    "ir_br",
    "ir_ef",
    "ir_pt",
    "ir_ptbr",
    "j",
    "j_eq",
    "j_eu",
    "r_br",
    "r_cc",
    "r_eu",
    "r_eubr",
    "r_liq",
    "v_inv",
]
