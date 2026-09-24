# irpf-exterior — convenções do projeto

Biblioteca de domínio (sem aplicação). As decisões de arquitetura estão em
[`pre-project-docs/ARQUITETURA.md`](pre-project-docs/ARQUITETURA.md) e as fórmulas em
[`pre-project-docs/Imposto sobre Investimento Extrangeiro.md`](pre-project-docs/Imposto%20sobre%20Investimento%20Extrangeiro.md).
Na dúvida entre duas implementações, vale a que respeita melhor a seção 4 da arquitetura.

Antes de acrescentar uma fórmula ou mexer no núcleo, leia
[`docs/desenvolvimento/guia-de-contribuicao.md`](docs/desenvolvimento/guia-de-contribuicao.md):
ele tem o ciclo de cinco passos e as armadilhas já encontradas.

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

## Fluxo de trabalho

⛔ **Nunca rode `git commit`, `git push` ou crie PRs por conta própria.** O autor
revisa cada alteração minuciosamente antes de commitar. O máximo permitido é
*sugerir* uma mensagem de commit no final da resposta, como texto — nunca
executá-la. Isso vale mesmo quando a tarefa parece concluída e os testes passam.

## Convenções

- Os nomes das variáveis seguem o glossário do documento de fórmulas (`I`, `F`,
  `C_i`, `R_br`, `IR_ptbr`, ...), não o estilo PEP 8 — daí `N803`/`N806`/`E741`
  desligados no ruff. `C_%` vira `C_pct` no código.
- **A biblioteca é pura, e isso não é negociável.** Só regras de negócio: nada
  de `date.today()`, rede, arquivo, variável de ambiente ou qualquer dado
  externo dentro de `src/irpf_exterior/`. Tudo chega por parâmetro.
  - ⛔ Não implemente cliente de PTAX, Banco Central ou qualquer provedor de
    cotações aqui — nem "só para testar". Cotação é `Cambio(valor, data, fonte)`
    recebido por parâmetro; quem busca é o consumidor.
  - ⛔ Não adicione leitura de extrato, geração do arquivo da declaração,
    persistência nem interface (web, CLI, notebook, Streamlit). São adaptadores,
    e moram em **projetos separados**.
  - ✅ `portas.py` pode declarar `Protocol`s novos — contrato não é dependência.
    Mas ele só importa da *standard library* e do próprio domínio; se precisar
    de outro import, a regra foi quebrada.
  - A biblioteca não tem dependências de runtime (só o extra `simbolico`, para
    gerar documentação). Acrescentar uma é decisão do autor, não do agente.
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
- Fórmula obtida por `solve` do SymPy carrega duas armadilhas já encontradas:
  o **piso em zero do imposto** invalida a álgebra onde não há imposto devido
  (precisa de guarda explícita no código), e o resultado pode ser
  **assintótico** — matematicamente certo e economicamente inútil. Em ambos os
  casos, prefira um tipo-união explícito a devolver um número enganoso.
- `simbolico.py` tem **dois** modelos: apuração (`J_eu` derivado de `F`) e
  simulação (`J_eu` dado, `F` derivado). Fórmula nova entra no que couber, e o
  teste de cobertura confere a união dos dois contra o `REGISTRO`.
