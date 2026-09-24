# irpf-exterior — convenções do projeto

Biblioteca de domínio (sem aplicação). As decisões de arquitetura estão em
[`pre-project-docs/ARQUITETURA.md`](pre-project-docs/ARQUITETURA.md) e as fórmulas em
[`pre-project-docs/Imposto sobre Investimento Extrangeiro.md`](pre-project-docs/Imposto%20sobre%20Investimento%20Extrangeiro.md).
Na dúvida entre duas implementações, vale a que respeita melhor a seção 4 da arquitetura.

## Comandos

Use o `justfile` — é a nomenclatura única do projeto. `just` lista as receitas.

```bash
just sync     # uv sync --all-extras
just test     # pytest; inclui doctests de src/ e do guia de uso
just types    # mypy estrito; Any só é permitido em formulas/_base.py
just lint     # ruff check + format --check (não altera nada)
just fmt      # ruff check --fix + format
just docs     # regenera docs/auditoria/ (há teste que cobra isso)
just check    # lint + types + test
```

`test` e `docs` usam `[positional-arguments]`, então repassam argumentos com
aspas preservadas: `just test -k "formula_12 or compensacao"`. O justfile limpa
`VIRTUAL_ENV` (o pyenv deixa a dele ativo e o uv avisaria em toda chamada).

⚠️ Não rode `ruff format` na raiz sem checar: ele reformata blocos de código
dentro de arquivos Markdown, inclusive os de `pre-project-docs/` (por isso a
pasta está em `extend-exclude`).

## Convenções

- Os nomes das variáveis seguem o glossário do documento de fórmulas (`I`, `F`,
  `C_i`, `R_br`, `IR_ptbr`, ...), não o estilo PEP 8 — daí `N803`/`N806`/`E741`
  desligados no ruff. `C_%` vira `C_pct` no código.
- Núcleo puro: nada de `date.today()`, rede, arquivo ou variável de ambiente
  dentro de `src/irpf_exterior/`. Tudo chega por parâmetro.
- Dados são `@dataclass(frozen=True, slots=True)`; coleções internas são
  `tuple` ou `MappingProxyType`.
- Quantias são sempre `Decimal` criado de `str`. `Money` recusa `float`.
- Toda fórmula nova chega com testes nas quatro categorias aplicáveis
  (`tests/unit`, `tests/propriedades`, `tests/simbolico`, `tests/cenarios`) e
  com uma entrada correspondente no modelo de `simbolico.py` — há um teste que
  cobra a correspondência entre o `REGISTRO` e o modelo simbólico.
- Alíquota nunca é editada no lugar: fecha-se o `fim` da vigência antiga e
  acrescenta-se uma linha nova.
- Cenário tributário novo (resgate parcial, dividendo) ganha uma classe de
  apuração própria, não um parâmetro opcional em `ApuracaoResgate`.
