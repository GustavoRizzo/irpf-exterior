"""Apuração de um resgate total: um aporte, um resgate, dois câmbios.

O objeto de resultado não calcula nada: ele é construído por construtores
nomeados que encadeiam as fórmulas na ordem certa (seção 5.7). Cenários
futuros (resgate parcial, dividendo) ganham classes próprias em vez de
parâmetros opcionais aqui.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from types import MappingProxyType

from irpf_exterior.dominio.moeda import BRL, EUR, Cambio, Money
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS, Aliquota, aliquota_vigente
from irpf_exterior.formulas.analise import j_eu, r_eubr, v_inv
from irpf_exterior.formulas.cambio import c_d, c_pct, f_eu, i_eu, r_cc
from irpf_exterior.formulas.imposto import ir_br, ir_ef, ir_pt, ir_ptbr, r_liq
from irpf_exterior.formulas.rendimento import j, r_br, r_eu
from irpf_exterior.rastreio import Calculado, entrada

__all__ = ["ApuracaoResgate", "ValorBRL"]

type ValorBRL = Money[BRL] | Calculado[Money[BRL]]
"""Um valor em reais, cru ou já rastreado — os dois servem como entrada."""


def _rastreado(nome: str, valor: ValorBRL) -> Calculado[Money[BRL]]:
    """Normaliza a entrada para `Calculado`, sem acrescentar metadados."""
    if isinstance(valor, Calculado):
        return valor
    return entrada(nome, valor)


def _aliquota(
    explicita: Aliquota | None,
    tabela: tuple[Aliquota, ...],
    nome: str,
    em: date | None,
) -> Aliquota:
    """Usa a alíquota informada; na falta dela, consulta a tabela por vigência."""
    if explicita is not None:
        return explicita
    return aliquota_vigente(tabela, nome, em)


@dataclass(frozen=True, slots=True)
class ApuracaoResgate:
    """Resultado completo e auditável de um resgate total.

    Todos os campos são `Calculado`: qualquer um deles pode ser passado a
    `explicar()` para obter a árvore que levou àquele número.
    """

    I: Calculado[Money[BRL]]
    F: Calculado[Money[BRL]]
    C_d: Calculado[Decimal]
    C_pct: Calculado[Decimal]
    I_eu: Calculado[Money[EUR]]
    F_eu: Calculado[Money[EUR]]
    R_eu: Calculado[Money[EUR]]
    R_br: Calculado[Money[BRL]]
    J: Calculado[Decimal]
    R_cc: Calculado[Money[BRL]]
    IR_pt: Calculado[Money[EUR]]
    IR_ptbr: Calculado[Money[BRL]]
    IR_br: Calculado[Money[BRL]]
    IR_ef: Calculado[Money[BRL]]
    R_liq: Calculado[Money[BRL]]
    R_eubr: Calculado[Money[BRL]]
    J_eu: Calculado[Decimal]
    V_inv: Calculado[Money[BRL]]
    T_br: Aliquota
    T_pt: Aliquota
    C_i: Cambio
    C_f: Cambio

    @classmethod
    def de_cf(
        cls,
        *,
        I: ValorBRL,
        F: ValorBRL,
        C_i: Cambio,
        C_f: Cambio,
        tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
        T_br: Aliquota | None = None,
        T_pt: Aliquota | None = None,
    ) -> ApuracaoResgate:
        """Apura a partir dos dois câmbios (construtor principal).

        Args:
            I: valor aportado, em reais pelo câmbio do dia do aporte.
            F: valor resgatado bruto, em reais pelo câmbio do dia do resgate.
            C_i: câmbio do aporte.
            C_f: câmbio do resgate; a sua data define a vigência das alíquotas.
            tabela: tabela de alíquotas (injetável em testes).
            T_br: alíquota brasileira explícita, dispensando a consulta.
            T_pt: alíquota portuguesa explícita, dispensando a consulta.
        """
        c_I = _rastreado("I", I)
        c_F = _rastreado("F", F)
        a_br = _aliquota(T_br, tabela, "T_br", C_f.data)
        a_pt = _aliquota(T_pt, tabela, "T_pt", C_f.data)

        v_c_d = c_d(C_i=C_i, C_f=C_f)
        v_c_pct = c_pct(C_d=v_c_d, C_i=C_i)
        v_i_eu = i_eu(I=c_I, C_i=C_i)
        v_f_eu = f_eu(F=c_F, C_f=C_f)
        v_r_eu = r_eu(F_eu=v_f_eu, I_eu=v_i_eu)
        v_r_br = r_br(F=c_F, I=c_I)
        v_j = j(R_br=v_r_br, I=c_I)
        v_r_cc = r_cc(I=c_I, C_pct=v_c_pct)
        v_ir_pt = ir_pt(R_eu=v_r_eu, T_pt=a_pt)
        v_ir_ptbr = ir_ptbr(IR_pt=v_ir_pt, C_f=C_f)
        v_ir_br = ir_br(R_br=v_r_br, T_br=a_br)
        v_ir_ef = ir_ef(IR_ptbr=v_ir_ptbr, IR_br=v_ir_br)
        v_r_liq = r_liq(R_br=v_r_br, IR_ef=v_ir_ef)
        v_r_eubr = r_eubr(R_eu=v_r_eu, C_f=C_f)
        v_j_eu = j_eu(R_eu=v_r_eu, I_eu=v_i_eu)
        v_v_inv = v_inv(R_liq=v_r_liq, R_cc=v_r_cc)

        return cls(
            I=c_I,
            F=c_F,
            C_d=v_c_d,
            C_pct=v_c_pct,
            I_eu=v_i_eu,
            F_eu=v_f_eu,
            R_eu=v_r_eu,
            R_br=v_r_br,
            J=v_j,
            R_cc=v_r_cc,
            IR_pt=v_ir_pt,
            IR_ptbr=v_ir_ptbr,
            IR_br=v_ir_br,
            IR_ef=v_ir_ef,
            R_liq=v_r_liq,
            R_eubr=v_r_eubr,
            J_eu=v_j_eu,
            V_inv=v_v_inv,
            T_br=a_br,
            T_pt=a_pt,
            C_i=C_i,
            C_f=C_f,
        )

    @classmethod
    def de_cd(
        cls,
        *,
        I: ValorBRL,
        F: ValorBRL,
        C_i: Cambio,
        C_d: Decimal,
        data_final: date | None = None,
        fonte: str | None = None,
        tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
        T_br: Aliquota | None = None,
        T_pt: Aliquota | None = None,
    ) -> ApuracaoResgate:
        """Apura quando se conhece a *variação* cambial em vez do câmbio final.

        Deriva `C_f = C_i + C_d` (Fórmula 1) e delega a `de_cf`.
        """
        return cls.de_cf(
            I=I,
            F=F,
            C_i=C_i,
            C_f=Cambio(C_i.valor + C_d, data_final, fonte),
            tabela=tabela,
            T_br=T_br,
            T_pt=T_pt,
        )

    def de_para_receita(self) -> Mapping[str, Calculado[Money[BRL]]]:
        """Mapeia os campos da ficha "Bens e Direitos → Aplicação Financeira".

        Ambos os campos são declarados em reais, por isso o imposto pago no
        exterior é `IR_ptbr` (já convertido) e não o `IR_pt` em euros.
        """
        return MappingProxyType(
            {
                "Rendimento ou Perda": self.R_br,
                "Imposto pago no Exterior": self.IR_ptbr,
            }
        )

    def a_pagar_no_brasil(self) -> Money[BRL]:
        """Quanto ainda resta recolher no Brasil depois da compensação.

        Zero quando Portugal já reteve mais do que o Brasil cobraria — a
        diferença a maior não é restituída.
        """
        saldo = self.IR_br.valor - self.IR_ptbr.valor
        return saldo if saldo.quantia > 0 else saldo.zerado()

    def investir_compensou(self) -> bool:
        """Diz se investir rendeu mais do que teria rendido o dinheiro parado.

        É o sinal de `V_inv` (Fórmula 16). Um empate exato conta como não ter
        compensado: o risco da aplicação não foi pago por nada.
        """
        return self.V_inv.valor.quantia > 0
