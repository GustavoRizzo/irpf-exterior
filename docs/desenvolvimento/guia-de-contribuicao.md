# Guia de contribuição

Este documento é para quem vai **mexer** na biblioteca. Para apenas usá-la,
veja o [guia de uso](guia-de-uso.md).

A regra geral: na dúvida entre duas implementações, vale a que respeita melhor
a [seção 4 da arquitetura](../../pre-project-docs/ARQUITETURA.md). O que segue
são as consequências práticas dela, e as armadilhas que já custaram caro.

---

## 1. O contrato: a biblioteca é pura

Só regras de negócio. Nada de rede, disco, relógio, ambiente ou aleatoriedade
dentro de `src/irpf_exterior/`. Tudo chega por parâmetro.

Isso **não é uma convenção de honra** — está verificado em
[`tests/test_pureza.py`](../../tests/test_pureza.py), que percorre a AST de
cada módulo do núcleo e falha se encontrar:

- import de rede (`socket`, `urllib`, `requests`, `httpx`, ...);
- import de disco ou processo (`os`, `pathlib`, `open`, `subprocess`, ...);
- import não determinístico (`random`, `time`, `uuid`);
- chamada de `date.today()`, `datetime.now()`, `print()`, `input()`;
- qualquer dependência de runtime nova no `pyproject.toml`.

A única exceção é `simbolico.py`, que pode importar SymPy — é o extra opcional
usado para gerar documentação, não para calcular imposto.

> **Por quê.** Um resultado fiscal precisa ser reproduzível anos depois, com os
> mesmos números, sem rede. Uma cotação buscada na hora transforma um cálculo
> determinístico num cálculo que depende do dia e do uptime de terceiros.

Precisa de dado externo? Declare a **porta** (`typing.Protocol`) em
`portas.py` e implemente o adaptador **em outro projeto**. Descrever o formato
de uma cotação não é buscar uma cotação — e há um teste que garante que
`portas.py` continue só descrevendo.

---

## 2. O ciclo de uma fórmula nova

Cinco passos, nesta ordem. Pular o primeiro é o erro mais caro.

### Passo 1 — Documento de referência primeiro

A fonte da verdade é
[`Imposto sobre Investimento Extrangeiro.md`](../../pre-project-docs/Imposto%20sobre%20Investimento%20Extrangeiro.md):
a fórmula entra lá **antes** de entrar no código, com número, entrada no
glossário e a justificativa. O código segue o documento, nunca o contrário.

Se a fórmula tem uma "versão em termos de inputs" publicada, ela vira teste no
passo 5 — não uma segunda cópia mantida à mão.

### Passo 2 — Função pura decorada

Em `formulas/`, no módulo que couber (`cambio`, `rendimento`, `imposto`,
`analise`, `projecao`). A função recebe e devolve valores do domínio — **nunca**
`Calculado`; o decorador cuida disso.

```python
@formula(
    nome="IR_br",
    ref="Fórmula 11",
    expr="IR_br = max(0, R_br · T_br)",
    latex=r"IR_{br} = R_{br} \cdot T_{br}",
    lei="Lei 14.754/2023, Art. 2º",
)
def ir_br(R_br: Money[BRL], T_br: Aliquota) -> Money[BRL]:
    """Imposto devido no Brasil, antes da compensação do imposto estrangeiro."""
    if R_br.quantia <= 0:
        return R_br.zerado()
    return R_br.vezes(T_br.valor).arredondado()
```

A **primeira linha da docstring** vira a descrição da fórmula no catálogo de
auditoria. Escreva-a para um auditor, não para um programador.

Sobre arredondar: **só quantia a recolher arredonda** (`IR_pt`, `IR_ptbr`,
`IR_br`). Valores analíticos como `R_eubr` não, porque arredondá-los
introduziria erro nas identidades sem nenhum ganho.

### Passo 3 — Registrar

Exporte em `formulas/__init__.py` e, se for API pública, em
`irpf_exterior/__init__.py`. O `REGISTRO` se preenche sozinho na importação;
ele só é escrito na definição, nunca em tempo de cálculo.

### Passo 4 — Modelo simbólico

`simbolico.py` tem **dois** modelos, porque são duas parametrizações da mesma
realidade:

| Modelo | `J_eu` | `F` | Para quê |
| :--- | :--- | :--- | :--- |
| `DEFINICOES` | derivado | **input** | apurar o que já aconteceu |
| `DEFINICOES_SIMULACAO` | **input** | derivado | simular o que ainda não aconteceu |

A fórmula nova entra no que couber. Há um teste que confere
`set(REGISTRO) == set(DEFINICOES) | set(DEFINICOES_SIMULACAO)`, então esquecer
este passo quebra a suíte — de propósito.

### Passo 5 — Testes nas quatro categorias

| Diretório | O que cobre |
| :--- | :--- |
| `tests/unit/` | a fórmula isolada, com valores conferidos à mão |
| `tests/propriedades/` | invariantes sob milhares de entradas (Hypothesis) |
| `tests/simbolico/` | a forma publicada bate com a derivada (SymPy) |
| `tests/cenarios/` | casos completos de ponta a ponta, com números conhecidos |

Os testes de propriedade são os que mais pagam: **os dois bugs mais sérios do
projeto foram encontrados por eles**, não por revisão.

Por fim, `just docs` regenera o catálogo. Há um teste que falha se o arquivo
versionado sair de sincronia com o código.

---

## 3. Convenções de código

- **Nomes seguem o glossário do documento**, não a PEP 8: `I`, `F`, `C_i`,
  `R_br`, `IR_ptbr`. Por isso `N803`, `N806` e `E741` estão desligados no ruff.
  `C_%` vira `C_pct` (o símbolo não é identificador válido).
- **Quantias são sempre `Decimal` criado de `str`.** `Money` recusa `float` em
  tempo de execução, e `Money[BRL] + Money[EUR]` é erro de tipo e de execução.
- **Dados são `@dataclass(frozen=True, slots=True)`**; coleções internas são
  `tuple` ou `MappingProxyType`, porque `frozen` é raso.
- **Uniões com `match` + `assert_never`**, para que um caso novo não passe
  despercebido pelo mypy. Veja `PontoDeEquilibrio` e `Eixo`.
- **Cenário tributário novo ganha classe própria**, não um parâmetro opcional
  numa apuração existente.
- **Alíquota nunca é editada no lugar**: fecha-se o `fim` da vigência antiga e
  acrescenta-se uma linha nova. É o que mantém um cálculo de 2024 reproduzível
  depois que a lei mudar.

---

## 4. Armadilhas já encontradas

Todas custaram retrabalho. Valem para qualquer regra futura.

### O piso em zero do imposto quebra formas fechadas

As Fórmulas 18 e 19 saíram de `sp.solve(V_inv = 0)`, que resolve a álgebra
**supondo imposto devido**. Onde o imposto é zero por piso, a solução deixa de
valer e devolve números plausíveis e errados:

- com o câmbio em queda, `J_eq` dava juro *negativo*; o equilíbrio real é zero;
- com juro não positivo, `C_eq` dava um câmbio onde `V_inv = -638`, não zero.

Qualquer fórmula obtida por `solve` tem esse risco. Confira as hipóteses da
derivação e ponha guardas explícitas no código.

### Formas fechadas podem ser assintóticas

O câmbio de equilíbrio cresce sem limite ao se aproximar de
`J_eu = T_br / (1 - T_br)` ≈ 17,65%: a 17,6% ele já passa de R$ 1.800/€. O
número está certo e é inútil. Quem exibe precisa tratá-lo como "compensa
sempre".

### Prefira um tipo-união a um número enganoso

Quando não há resposta, diga **qual** não-resposta é. `SempreCompensa` e
`NuncaCompensa` são coisas opostas, e devolver `None` — ou pior, um número —
para as duas esconderia a diferença.

### Não adivinhe

Metadado ausente não é preenchido com suposição. Sem data de referência, a
alíquota só é escolhida se houver uma única vigência; caso contrário o erro
pede o dado. Prefira falhar pedindo a informação a acertar por sorte.

---

## 5. A documentação se mantém sozinha

Três mecanismos impedem que ela envelheça — todos quebram a suíte se violados:

| Documento | Como se mantém |
| :--- | :--- |
| [`docs/auditoria/`](../auditoria/catalogo-de-formulas.md) | gerado do `REGISTRO` + SymPy por `just docs`; teste compara o arquivo versionado com o que o código produziria hoje |
| [`guia-de-uso.md`](guia-de-uso.md) | todos os exemplos rodam como doctest |
| docstrings | a primeira linha vira a descrição no catálogo |

Não edite `docs/auditoria/` à mão: rode `just docs`.

---

## 6. Comandos

```bash
just          # lista as receitas
just check    # lint + types + test — o que um CI cobraria
just test -k "equilibrio or simulacao"   # repassa argumentos ao pytest
just docs     # regenera o catálogo de auditoria
```

`just check` precisa passar limpo antes de qualquer commit: `mypy --strict`
sem erros, `ruff` sem apontamentos, suíte inteira verde.

> `Any` é proibido no domínio. A única exceção é `formulas/_base.py`, onde a
> assinatura genérica de `Formula.calcular` exige — e a exceção está declarada
> no `pyproject.toml`, não escondida num `# type: ignore`.
