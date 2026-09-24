"""Gera o catálogo de fórmulas para auditores a partir do `REGISTRO`.

A documentação de auditoria (seção 9.1) é *derivada* do código: ninguém
mantém uma segunda cópia das fórmulas num arquivo Markdown, que inevitavelmente
divergiria (dor 2.3). A forma expandida vem do modelo simbólico.

Uso:
    uv run python scripts/gerar_catalogo.py [destino.md]
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import irpf_exterior.formulas  # noqa: F401  (importar preenche o REGISTRO)
from irpf_exterior import ApuracaoResgate, Cambio, brl, entrada, explicar
from irpf_exterior.dominio.parametros import TABELA_ALIQUOTAS
from irpf_exterior.formulas._base import REGISTRO
from irpf_exterior.simbolico import latex_expandida

DESTINO_PADRAO = Path("docs/auditoria/catalogo-de-formulas.md")

CABECALHO = """<!-- Gerado por scripts/gerar_catalogo.py. Não edite à mão. -->
# Catálogo de fórmulas

Este documento responde, para cada valor que a biblioteca calcula: **o que é
calculado, como e com base em quê**. Ele é gerado a partir do próprio código,
então não pode divergir do que é executado.

A coluna *forma encadeada* é como a fórmula está escrita no código, em termos
das variáveis imediatamente anteriores. A coluna *forma expandida* é a mesma
fórmula reduzida apenas às variáveis de entrada ($I$, $F$, $C_i$, $C_f$,
$T_{pt}$, $T_{br}$), derivada por substituição simbólica — nunca escrita à mão.
"""


def _ordem(ref: str) -> int:
    """Ordena por número de fórmula, e não alfabeticamente."""
    return int(ref.rsplit(" ", 1)[-1])


def linhas_do_catalogo() -> Iterator[str]:
    """Produz o catálogo, fórmula por fórmula, na ordem do documento."""
    yield CABECALHO
    yield "## Fórmulas\n"
    for nome, formula in sorted(REGISTRO.items(), key=lambda par: _ordem(par[1].ref)):
        yield f"### {formula.ref} — {nome}\n"
        doc = (formula.calcular.__doc__ or "").strip().splitlines()
        if doc:
            yield f"{doc[0]}\n"
        yield "| | |"
        yield "| :--- | :--- |"
        lado_esquerdo = formula.latex.split(" = ", 1)[0]
        yield f"| Forma encadeada | $${formula.latex}$$ |"
        yield f"| Forma expandida | $${lado_esquerdo} = {latex_expandida(nome)}$$ |"
        yield f"| Base legal | {formula.lei or '—'} |"
        yield ""


def linhas_das_aliquotas() -> Iterator[str]:
    """Produz a tabela de alíquotas com as suas vigências."""
    yield "## Alíquotas e vigências\n"
    yield "Uma linha nunca é editada: quando a lei muda, fecha-se o fim da"
    yield "vigência antiga e acrescenta-se outra linha.\n"
    yield "| Alíquota | Valor | Início | Fim | Fonte |"
    yield "| :--- | ---: | :--- | :--- | :--- |"
    for a in TABELA_ALIQUOTAS:
        fim = a.fim.isoformat() if a.fim else "vigente"
        yield (
            f"| {a.nome} | {a.percentual.normalize()}% | {a.inicio.isoformat()} "
            f"| {fim} | {a.fonte or '—'} |"
        )
    yield ""


def linhas_do_exemplo() -> Iterator[str]:
    """Produz a árvore de auditoria de uma apuração completa."""
    apuracao = ApuracaoResgate.de_cf(
        I=entrada("I", brl("10000.00"), "extrato: aporte"),
        F=entrada("F", brl("13200.00"), "extrato: resgate"),
        C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
        C_f=Cambio(Decimal("6.00"), date(2025, 3, 10), "PTAX"),
    )
    yield "## Exemplo de árvore de auditoria\n"
    yield "Aporte de R$ 10.000,00 a R$ 5,00/€, resgatado por R$ 13.200,00 a R$ 6,00/€."
    yield "Cada linha mostra o valor, a fórmula que o produziu e, quando houver,"
    yield "a base legal e a origem do dado.\n"
    yield "```"
    yield explicar(apuracao.IR_ef)
    yield "```\n"
    yield "### Campos da declaração\n"
    yield "| Campo na Receita Federal | Valor | Variável |"
    yield "| :--- | ---: | :--- |"
    for campo, calculado in apuracao.de_para_receita().items():
        variavel = calculado.descricao.split(":")[1].split("=")[0].strip()
        yield f"| {campo} | {calculado.valor} | {variavel} |"
    yield ""


def gerar() -> str:
    """Monta o documento inteiro."""
    partes = (*linhas_do_catalogo(), *linhas_das_aliquotas(), *linhas_do_exemplo())
    return "\n".join(partes).rstrip() + "\n"


def main(argumentos: tuple[str, ...]) -> int:
    destino = Path(argumentos[0]) if argumentos else DESTINO_PADRAO
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar(), encoding="utf-8")
    print(f"catálogo gravado em {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:])))
