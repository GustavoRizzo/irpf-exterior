# irpf-exterior

Núcleo de domínio da apuração de IRPF sobre investimentos no exterior por
residentes no Brasil, sob a Lei nº 14.754/2023 ("Lei das Offshores"), com foco
inicial em aplicações em Portugal e a compensação do imposto lá retido.

É uma **biblioteca**, não uma aplicação: só funções puras e dados imutáveis.
Ela não lê arquivos, não acessa a rede e não consulta o relógio — tudo chega
por parâmetro. CLIs, notebooks, APIs web e clientes do PTAX são consumidores
externos, através das portas em `portas.py`.

## Instalação

```bash
just sync               # ambiente de desenvolvimento (ou: uv sync --all-extras)
uv add irpf-exterior    # como dependência de outro projeto
```

Requer Python 3.14+. O extra `simbolico` (SymPy) só é necessário para gerar a
documentação de auditoria e rodar os testes simbólicos.

## Uso

```python
from datetime import date
from decimal import Decimal

from irpf_exterior import ApuracaoResgate, Cambio, brl, entrada, explicar

apuracao = ApuracaoResgate.de_cf(
    I=entrada("I", brl("10000.00"), "extrato: aporte"),
    F=brl("13200.00"),  # sem fonte: tudo bem
    C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
    C_f=Cambio(Decimal("6.00"), date(2025, 3, 10)),
)

print(apuracao.IR_ef.valor)  # BRL 480.00
print(apuracao.a_pagar_no_brasil())  # BRL 144.00 (já compensado o IR português)
print(explicar(apuracao.IR_ef))  # a árvore inteira do cálculo
```

Os campos da declaração saem prontos:

```python
for campo, valor in apuracao.de_para_receita().items():
    print(f"{campo}: {valor.valor}")
```

## O que está aqui

| Módulo | Conteúdo |
| --- | --- |
| `dominio/moeda.py` | `BRL`, `EUR`, `Money[M]`, `Cambio` |
| `dominio/parametros.py` | `Aliquota`, `TABELA_ALIQUOTAS`, `aliquota_vigente` |
| `rastreio.py` | `Calculado`, `entrada`, `explicar` |
| `formulas/` | as fórmulas 1–13 (apuração) e 14–16 (análise), e o `REGISTRO` |
| `apuracoes/resgate.py` | `ApuracaoResgate` |
| `portas.py` | `Protocol`s para os adaptadores externos |
| `simbolico.py` | modelo SymPy que *deriva* as formas expandidas |

## Desenvolvimento

Os comandos estão no [`justfile`](justfile) — `just` sem argumentos lista todos:

```bash
just sync     # cria a .venv com as dependências de desenvolvimento
just test     # unit, propriedades, simbólicos, cenários e doctests
just types    # mypy estrito
just lint     # ruff check + format --check
just fmt      # corrige e formata
just docs     # regenera docs/auditoria/ a partir do REGISTRO
just check    # lint + types + test, o que um CI cobraria
```

`just test` e `just docs` repassam argumentos:
`just test -q -k "formula_12 or compensacao"`.

Sem o [`just`](https://github.com/casey/just) instalado, todo comando funciona
direto (`uv run pytest`, `uv run mypy`, ...); o justfile só unifica os nomes.

## Documentação

- [`docs/auditoria/catalogo-de-formulas.md`](docs/auditoria/catalogo-de-formulas.md) — o que é calculado e com que base legal (gerado a partir do código).
- [`docs/desenvolvimento/guia-de-uso.md`](docs/desenvolvimento/guia-de-uso.md) — como usar a API.
- [`pre-project-docs/ARQUITETURA.md`](pre-project-docs/ARQUITETURA.md) — por que a biblioteca é assim.
