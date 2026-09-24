# irpf-exterior

Núcleo de domínio da apuração de IRPF sobre investimentos no exterior por
residentes no Brasil, sob a Lei nº 14.754/2023 ("Lei das Offshores"), com foco
inicial em aplicações em Portugal e a compensação do imposto lá retido.

É uma **biblioteca**, não uma aplicação: só funções puras e dados imutáveis.
Ela não lê arquivos, não acessa a rede e não consulta o relógio — tudo chega
por parâmetro. **Zero dependências de runtime.**

## Escopo

O que esta biblioteca faz:

- apura o imposto de um resgate, com a compensação Brasil–Portugal;
- explica cada número até as entradas, com fórmula, cotação e base legal;
- separa o que rendeu por câmbio do que rendeu pela aplicação;
- responde se investir compensou, ou compensaria, frente a deixar o dinheiro parado;
- simula cenários e resolve pontos de equilíbrio em forma fechada.

O que ela **não faz — e não passará a fazer**:

| Fora | Por quê |
| :--- | :--- |
| Buscar cotação (PTAX, BCB, qualquer provedor) | um resultado fiscal precisa ser reproduzível anos depois, sem rede |
| Ler extratos ou qualquer arquivo | entrada é parâmetro, não efeito colateral |
| Gerar o arquivo da declaração | formato de terceiro, muda por fora |
| Interface (web, CLI, notebook, Streamlit) | adaptador, mora em projeto separado |
| Persistir qualquer coisa | estado é do consumidor |

Isso não é purismo: uma cotação vinda da rede transforma um cálculo
determinístico num cálculo que depende do dia e do uptime de terceiros. Quem
busca a cotação é o consumidor; quem a recebe por parâmetro é a biblioteca.

`portas.py` declara os contratos (`typing.Protocol`) que um adaptador deve
cumprir — descrever o formato de uma cotação não é buscar uma cotação.

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
| `formulas/` | as fórmulas 1–13 (apuração), 14–16 (análise) e 17–19 (projeção), e o `REGISTRO` |
| `apuracoes/resgate.py` | `ApuracaoResgate` |
| `simulacao/` | cenários hipotéticos, varreduras preguiçosas e pontos de equilíbrio |
| `portas.py` | `Protocol`s para os adaptadores externos (contratos, sem implementação) |
| `simbolico.py` | modelos SymPy que *derivam* as formas expandidas |

### Simulação

Para quem ainda está decidindo investir, `irpf_exterior.simulacao` projeta o
valor resgatado a partir do juro esperado e responde onde está a virada:

```python
from irpf_exterior.simulacao import Cenario, cambio_de_equilibrio

hipotese = Cenario(
    I=brl("10000.00"),
    C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
    J_eu=Decimal("0.01"),  # a aplicação promete +1% em euros
    C_f=Cambio(Decimal("8.00"), date(2025, 3, 10)),
)

print(cambio_de_equilibrio(hipotese).valor)  # equilíbrio em 5.3004
```

Acima de R$ 5,30/€ não investir teria sido melhor — o imposto sobre o ganho
cambial, isento se o dinheiro ficasse parado, come mais do que a aplicação
rendeu. Nada é calculado antes de ser pedido.

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
- [`docs/desenvolvimento/guia-de-uso.md`](docs/desenvolvimento/guia-de-uso.md) — como usar a API, com exemplos que rodam como testes.
- [`docs/desenvolvimento/guia-de-contribuicao.md`](docs/desenvolvimento/guia-de-contribuicao.md) — como acrescentar uma fórmula sem quebrar as garantias.
- [`pre-project-docs/ARQUITETURA.md`](pre-project-docs/ARQUITETURA.md) — por que a biblioteca é assim.
