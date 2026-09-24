# Guia de Arquitetura — Biblioteca de Domínio Tributário (Investimentos no Exterior)

> **Para quem é este documento:** para o agente (humano ou robô) que vai codificar a biblioteca. Ele descreve *por que* a biblioteca existe, *quais problemas* ela resolve, *quais decisões de arquitetura* já foram tomadas e *como* o código deve ser escrito. Na dúvida entre duas implementações, escolha a que respeita melhor os princípios da seção 4.
>
> **Fonte da verdade das fórmulas:** o documento `Imposto sobre Investimento Estrangeiro.md` (glossário de variáveis e Fórmulas 1 a 13). Os nomes de variáveis no código seguem esse glossário.

---

## 1. Visão geral

Estamos construindo uma **biblioteca** (não uma aplicação) que concentra as **regras de negócio** da apuração de imposto sobre investimentos no exterior feitos por residentes no Brasil, com foco inicial em aplicações em Portugal (euro). O ponto de partida legal é a Lei nº 14.754/2023 ("Lei das Offshores e Fundos Exclusivos") e a compensação do imposto retido em Portugal.

A biblioteca é o **núcleo de domínio** de uma arquitetura hexagonal: ela guarda a inteligência do problema (fórmulas, alíquotas, regras de compensação) e não sabe nada sobre de onde vêm os dados nem para onde vão os resultados. Interfaces de linha de comando, notebooks, APIs web, leitores de extrato e integrações com o Banco Central são **consumidores externos** da biblioteca e **não fazem parte dela**.

Não há, neste momento, preocupação com uma aplicação em produção. A prioridade é **correção, rastreabilidade e clareza**.

---

## 2. Dores e necessidades

Estas são as dificuldades que motivaram o projeto. Cada decisão de arquitetura deve atacar pelo menos uma delas.

**2.1. Duas moedas, câmbios de datas diferentes.** Cada cálculo mistura reais e euros, convertidos por cotações de dias diferentes ($C_i$ no aporte, $C_f$ no resgate). O erro mais provável é somar valores de moedas diferentes ou converter pelo câmbio errado, e esse erro não "explode": produz um número plausível e errado.

**2.2. Bases de cálculo diferentes em cada país.** Portugal tributa o rendimento apurado em euros, sem câmbio ($R_{eu}$). O Brasil tributa o rendimento apurado em reais, com câmbio ($R_{br}$). Os dois impostos precisam ser comparados para aplicar a compensação ($IR_{ef} = \max(IR_{ptbr}, IR_{br})$).

**2.3. Fórmulas duplicadas que divergem.** Cada fórmula foi documentada em duas versões (encadeada e "em termos de inputs"). Já aconteceu de as duas versões divergirem sem ninguém perceber (a segunda forma da Fórmula 1 estava errada). Qualquer subexpressão repetida à mão é um ponto de divergência futura.

**2.4. Necessidade de auditoria.** Um resultado precisa ser explicável: de qual fórmula veio, com quais entradas, sob qual artigo de lei, com qual cotação. Isso serve para conferir a declaração e para responder a um auditor.

**2.5. A lei muda.** Alíquotas e regras têm vigência. Um cálculo de um ano passado precisa continuar reproduzível com as regras daquele ano, mesmo depois que a lei mudar.

**2.6. Precisão monetária.** Ponto flutuante binário produz erros de centavos. Arredondamento é uma regra de negócio, não um detalhe técnico.

**2.7. Metadados nem sempre disponíveis.** Datas, fontes e descrições (de onde veio uma cotação, em que dia foi o aporte) **são úteis, mas nem sempre existem**. A biblioteca deve aproveitá-los quando fornecidos e funcionar sem eles, sem nunca inventar um valor que não recebeu.

**2.8. Crescimento previsto.** Hoje o escopo é um aporte e um resgate total. No futuro virão resgates parciais, dividendos/rendimentos periódicos, compensação de prejuízos e, possivelmente, reconstrução da posição em qualquer data ("time travel"). A arquitetura não pode exigir reescrita quando esses casos chegarem.

---

## 3. Objetivos

A biblioteca deve:

1. **Armazenar o domínio**: ser o único lugar onde as regras tributárias estão escritas.
2. **Tornar erros de moeda difíceis de escrever**: pegos pelo verificador de tipos antes da execução e, como segunda barreira, em tempo de execução.
3. **Definir cada conceito uma única vez**: fórmulas escritas na forma encadeada; formas expandidas são *derivadas*, nunca mantidas à mão.
4. **Produzir resultados auditáveis**: todo valor calculado carrega sua origem (fórmula, entradas, fonte legal).
5. **Versionar parâmetros por vigência**: alíquotas consultadas por data de referência.
6. **Ser totalmente testável sem infraestrutura**: nenhum teste do núcleo precisa de rede, arquivo, banco ou relógio.
7. **Ter dois públicos de documentação**: auditores (o que é calculado e por quê) e desenvolvedores (como usar a API).

**Fora de escopo (por enquanto):** leitura de extratos, acesso à API PTAX, geração de arquivo da declaração, interface com o usuário, persistência. Esses itens entram como *adaptadores* fora do núcleo, através das *portas* descritas na seção 5.6.

---

## 4. Princípios de arquitetura

### 4.1. Functional Core, Imperative Shell (Arquitetura Hexagonal)

O núcleo é composto **apenas** por funções puras e dados imutáveis. Todo efeito colateral (I/O, rede, relógio, aleatoriedade) mora fora da biblioteca, nos adaptadores.

- **DEVE:** receber tudo o que precisa por parâmetro, inclusive datas e tabelas de alíquotas.
- **NÃO DEVE:** chamar `date.today()`, `datetime.now()`, ler arquivos, acessar a rede ou variáveis de ambiente dentro do núcleo.

### 4.2. Programação funcional em Python

Python não impõe o paradigma funcional; a disciplina precisa ser explícita.

- Estruturas de dados são `@dataclass(frozen=True)`.
- Coleções dentro de estruturas imutáveis são `tuple`, `frozenset` ou `Mapping` (nunca `list` ou `dict`, porque `frozen` é raso).
- Nenhuma função altera seus argumentos; toda "mudança" devolve um valor novo.
- **Nunca** usar argumentos padrão mutáveis (`def f(x=[])`, `def f(x={})`). Usar `()`, `frozenset()`, `MappingProxyType({})` ou `None`.
- Uniões de tipos são tratadas com `match` + `assert_never` para que o mypy acuse casos esquecidos.

### 4.3. Classes para dados, funções para regras

**Critério:** se algo **descreve** uma coisa do domínio, é uma classe imutável; se **calcula ou decide** algo, é uma função.

- Classes podem ter métodos que **preservam as regras internas do próprio tipo** (ex.: `Money.__add__` recusa moedas diferentes).
- Regras de negócio (fórmulas, compensação, escolha de alíquota) são **funções**, porque combinam vários tipos e não pertencem naturalmente a nenhum deles.
- "Classes diferem em comportamento; instâncias diferem em dados": as fórmulas não são uma classe cada; são **instâncias** de um único tipo `Formula`, produzidas pelo decorador `@formula`.

### 4.4. Fonte única da verdade para cada conceito

Cada fórmula é escrita **na forma encadeada**, referenciando as fórmulas anteriores (ex.: `IR_pt` usa `R_eu`, que usa `F_eu` e `I_eu`). A forma expandida em termos dos inputs, útil para documentação, é **gerada** por computação simbólica (SymPy), nunca escrita à mão no código.

### 4.5. Nunca adivinhar

Metadados opcionais (data, fonte, descrição) podem ser omitidos, mas a biblioteca **não preenche lacunas com suposições**. Se uma regra precisa de uma informação ausente e não há como decidir sem ela, a biblioteca levanta um erro claro, pedindo o dado. Exemplo: sem data de referência, só é possível escolher uma alíquota se a tabela tiver uma única vigência para aquele nome, ou se a alíquota for passada explicitamente.

### 4.6. Tipagem estrita

- Todo o código é anotado e passa em `mypy --strict` (ou `pyright` em modo estrito).
- Proibido `Any` no domínio, exceto onde documentado (ver limitação na seção 5.4).
- Moedas usam tipos fantasma (`Money[BRL]`, `Money[EUR]`), não `NewType` (que não impede `BRL + EUR`).

---

## 5. Componentes do domínio

### 5.1. Moedas e dinheiro (Value Objects)

- `BRL`, `EUR`: classes vazias, usadas apenas como marcadores de tipo.
- `Money[M]`: valor imutável com `quantia: Decimal` e `moeda: type[M]`. Operações: `+`, `-` (mesma moeda, checado pelo mypy **e** em execução), `vezes(fator: Decimal)`, `arredondado()`.
- **Sempre `Decimal`**, criado a partir de `str` (`Decimal("0.15")`), nunca de `float`.

### 5.2. Câmbio

`Cambio` representa quanto 1 EUR vale em BRL. Campos: `valor: Decimal` (obrigatório), `data: date | None`, `fonte: str | None` (opcionais). Métodos: `para_eur(Money[BRL]) -> Money[EUR]` e `para_brl(Money[EUR]) -> Money[BRL]`. A conversão é **sempre explícita**; não existe conversão automática entre moedas.

### 5.3. Rastreabilidade: `Calculado[T]`

Todo valor produzido por uma fórmula é um `Calculado[T]`:

| Campo | Obrigatório | Conteúdo |
|---|---|---|
| `valor` | sim | o resultado (`Money`, `Decimal`, ...) |
| `descricao` | sim | referência e expressão da fórmula (ex.: `Fórmula 11: IR_br = R_br · T_br`) |
| `fonte` | não | base legal ou origem do input |
| `entradas` | não | tupla de pares `(nome, valor)`, onde o valor pode ser outro `Calculado` |

As entradas formam uma **árvore de auditoria**. A função `explicar(calculado)` a percorre e produz texto legível; ela deve omitir de forma limpa os metadados ausentes. Inputs brutos são criados por `entrada(nome, valor, fonte=None)`.

### 5.4. Fórmulas: `Formula` + decorador `@formula` + `REGISTRO`

Cada fórmula é uma **função pura** que recebe e devolve valores do domínio (nunca `Calculado`). O decorador `@formula(...)` a transforma num objeto `Formula` que:

- guarda metadados: `nome`, `ref` (ex.: "Fórmula 11"), `expr` (texto legível), `latex`, `lei` (opcional);
- ao ser chamado, aceita argumentos **nomeados**, crus ou `Calculado`, "desembrulha" os valores, chama a função pura e devolve um `Calculado` com as entradas registradas;
- é registrado no dicionário `REGISTRO`, usado para gerar a documentação de auditoria.

Regras:

- Fórmulas **sempre** chamadas com argumentos nomeados.
- O `REGISTRO` só é alterado durante a importação dos módulos de fórmulas (definição), nunca em tempo de cálculo.
- **Limitação conhecida:** `Formula.__call__` recebe `**entradas: object`, então o mypy não verifica os tipos dos argumentos passados à fórmula decorada. A verificação de tipos acontece dentro da função pura e em execução no `Money`. Melhorar isso (ex.: `ParamSpec`) é bem-vindo, mas não pode comprometer a legibilidade.

### 5.5. Parâmetros com vigência (Effective Dating)

`Aliquota(nome, valor, inicio, fim, fonte)`, organizadas numa tupla `TABELA_ALIQUOTAS`. A função pura `aliquota_vigente(tabela, nome, em)` devolve a alíquota vigente na data `em`.

- Quando a lei mudar: fechar o `fim` da linha antiga e acrescentar uma nova. **Nunca editar o valor de uma linha existente.**
- Se `em` for `None`: aceitar apenas se houver exatamente uma alíquota com aquele nome; caso contrário, erro pedindo a data ou a alíquota explícita (princípio 4.5).
- A tabela é sempre parâmetro com valor padrão, para permitir injeção em testes.

### 5.6. Portas (interfaces para o mundo externo)

O núcleo pode **declarar**, via `typing.Protocol`, as interfaces de que um consumidor precisará, por exemplo `ProvedorDeCambio` (data → `Cambio`) e `RepositorioDeAliquotas` (→ tabela). **As implementações (adaptadores) ficam fora da biblioteca.** Nenhuma função de cálculo recebe uma porta: o consumidor usa a porta para obter os dados e então chama a função pura.

### 5.7. Apurações (resultado + orquestração)

Cada cenário tributário tem um **objeto de resultado imutável** (ex.: `ApuracaoResgate`) cujos campos são `Calculado`. Esse objeto **não contém lógica de cálculo**: ele é construído por **construtores nomeados** (`classmethod`), que chamam as fórmulas na ordem certa.

- `ApuracaoResgate.de_cf(I, F, C_i, C_f, ...)`: construtor principal.
- `ApuracaoResgate.de_cd(I, F, C_i, C_d, ...)`: construtor alternativo que deriva `C_f` e delega ao principal.
- Cenários novos (dividendo, resgate parcial) ganham **novas classes de resultado**, reaproveitando as mesmas fórmulas. Não se acrescentam parâmetros opcionais a uma apuração existente para acomodar outro cenário.

---

## 6. Padrões de projeto utilizados

| Padrão | Onde aparece | Problema que resolve |
|---|---|---|
| Functional Core, Imperative Shell / Hexagonal | biblioteca inteira | testabilidade, independência de infraestrutura (2.8) |
| Value Object (DDD) | `Money`, `Cambio`, `Aliquota` | erros de moeda, precisão (2.1, 2.6) |
| Function Object / Command | `Formula` | metadados + contrato uniforme por fórmula (2.4) |
| Registry | `REGISTRO` | documentação gerada a partir do código (2.4) |
| Effective Dating (Temporal Property) | `Aliquota`, `aliquota_vigente` | mudança de lei, reprodutibilidade (2.5) |
| Named Constructors / Factory Method | `de_cf`, `de_cd` | formas alternativas de input |
| Árvore de proveniência (estilo Composite) | `Calculado.entradas` | auditoria (2.4) |
| Event Sourcing + fold *(futuro)* | histórico de eventos | resgates parciais, dividendos, time travel (2.8) |

---

## 7. Estrutura sugerida do projeto

```
<nome_da_lib>/
├── src/<nome_da_lib>/
│   ├── dominio/
│   │   ├── moeda.py          # BRL, EUR, Money, Cambio
│   │   └── parametros.py     # Aliquota, TABELA_ALIQUOTAS, aliquota_vigente
│   ├── rastreio.py           # Calculado, entrada, explicar
│   ├── formulas/
│   │   ├── _base.py          # Formula, @formula, REGISTRO
│   │   ├── cambio.py         # Fórmulas 1–4, 8
│   │   ├── rendimento.py     # Fórmulas 5–7
│   │   └── imposto.py        # Fórmulas 9–13
│   ├── apuracoes/
│   │   └── resgate.py        # ApuracaoResgate
│   └── portas.py             # Protocols (sem implementação)
├── tests/
│   ├── unit/                 # uma fórmula por vez, valores conhecidos
│   ├── propriedades/         # Hypothesis: invariantes
│   ├── simbolico/            # SymPy: equivalência das formas documentadas
│   └── cenarios/             # cenários completos de ponta a ponta ("golden")
└── docs/
    ├── auditoria/            # catálogo de fórmulas gerado a partir do REGISTRO
    └── desenvolvimento/      # guia de uso da API
```

---

## 8. Estratégia de testes

Testes são obrigatórios. Toda fórmula nova chega com testes das quatro categorias aplicáveis.

**8.1. Unitários.** Cada fórmula isolada, com valores calculados à mão. Como são funções puras, não precisam de mocks.

**8.2. Baseados em propriedades (Hypothesis).** Geram milhares de entradas e verificam invariantes. Exemplos obrigatórios:

- $IR_{ef} \ge IR_{br}$ e $IR_{ef} \ge IR_{ptbr}$, sempre.
- $IR_{br} \ge 0$ e $IR_{pt} \ge 0$, sempre (prejuízo não gera imposto negativo).
- Se $R_{br} > 0$, então $R_{liq} \le R_{br}$.
- Com câmbio constante ($C_i = C_f$), $R_{br} = R_{eu} \cdot C_i$.
- Somar `Money` de moedas diferentes sempre levanta `TypeError`.

**8.3. Simbólicos (SymPy).** Para cada fórmula que o documento de referência apresenta em mais de uma forma, verificar que `simplify(forma_A - forma_B) == 0`. Isso impede que a documentação diverja da definição (dor 2.3).

**8.4. Cenários (golden tests).** Casos completos com resultado conhecido, cobrindo pelo menos: Brasil cobra mais que Portugal; Portugal cobra mais que o Brasil; prejuízo em euros com ganho em reais (efeito cambial); câmbio constante.

**8.5. Verificação estática.** `mypy --strict` e `ruff` (incluindo a regra B006, argumentos padrão mutáveis) rodam em todo commit e devem passar sem erros.

---

## 9. Documentação

**9.1. Para auditores.** O objetivo é responder "o que foi calculado, como e com base em quê".

- Um **catálogo de fórmulas** gerado automaticamente a partir do `REGISTRO`: referência, nome, expressão em LaTeX, forma expandida (gerada via SymPy) e base legal.
- A saída de `explicar()` para cada apuração, mostrando a árvore completa de cálculo.
- Linguagem do domínio (termos do documento de referência), não termos de programação.

**9.2. Para desenvolvedores.** O objetivo é responder "como uso a biblioteca".

- Docstrings em todas as funções e classes públicas, com a referência da fórmula.
- Um guia de uso com exemplos executáveis (que também rodam como testes, via `doctest` ou equivalente).
- Este documento de arquitetura, mantido atualizado quando uma decisão mudar.

---

## 10. Roteiro e questões em aberto

**Próximos passos previstos:**

1. Resgates parciais: quantidade de cotas, posição acumulada, custo de aquisição proporcional em reais. $I$ passa a ser *calculado* a partir da posição.
2. Rendimentos periódicos (dividendos, juros), com imposto retido na fonte em Portugal.
3. Compensação de prejuízos, em função separada.
4. Event sourcing: histórico como tupla imutável de eventos (`Aporte | Resgate | Dividendo`), estado obtido por `fold`. Isso habilita "time travel": a posição em qualquer data é o fold dos eventos até ela.

**Questões a confirmar antes de codificar a regra correspondente:**

- Regra de arredondamento exigida pela Receita Federal (hoje: `ROUND_HALF_UP` a centavos, isolado em `Money.arredondado()`).
- Método de custo para resgates parciais (custo médio ou por lote).
- Datas de vigência exatas das alíquotas (a de `T_pt` na tabela atual é ilustrativa).
- Tratamento de taxas da corretora na base de cálculo.

---

## 11. Exemplos de solução

Os trechos abaixo mostram o estilo esperado. São referências, não código final.

### 11.1. Dinheiro tipado e câmbio com metadados opcionais

```python
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Generic, TypeVar


class BRL: ...


class EUR: ...


M = TypeVar("M", BRL, EUR)


@dataclass(frozen=True)
class Money(Generic[M]):
    quantia: Decimal
    moeda: type[M]

    def __add__(self, outro: Money[M]) -> Money[M]:
        if self.moeda is not outro.moeda:
            raise TypeError(f"{self.moeda.__name__} com {outro.moeda.__name__}")
        return Money(self.quantia + outro.quantia, self.moeda)

    def arredondado(self) -> Money[M]:
        return Money(self.quantia.quantize(Decimal("0.01"), ROUND_HALF_UP), self.moeda)


@dataclass(frozen=True)
class Cambio:
    valor: Decimal  # R$ por €
    data: date | None = None  # opcional
    fonte: str | None = None  # opcional

    def para_eur(self, m: Money[BRL]) -> Money[EUR]:
        return Money(m.quantia / self.valor, EUR)

    def para_brl(self, m: Money[EUR]) -> Money[BRL]:
        return Money(m.quantia * self.valor, BRL)
```

### 11.2. Fórmula pura com metadados

```python
@formula(
    nome="IR_br",
    ref="Fórmula 11",
    expr="IR_br = max(0, R_br · T_br)",
    latex=r"R_{br} \cdot T_{br}",
    lei="Lei 14.754/2023, Art. 2º",
)
def ir_br(R_br: Money[BRL], T_br: Aliquota) -> Money[BRL]:
    if R_br.quantia <= 0:
        return Money(Decimal("0"), BRL)
    return R_br.vezes(T_br.valor).arredondado()


@formula(
    nome="IR_ef",
    ref="Fórmula 12",
    expr="IR_ef = max(IR_ptbr, IR_br)",
    latex=r"\max(IR_{ptbr},\ IR_{br})",
    lei="Lei 14.754/2023, Art. 12",
)
def ir_ef(IR_ptbr: Money[BRL], IR_br: Money[BRL]) -> Money[BRL]:
    return IR_ptbr if IR_ptbr.quantia > IR_br.quantia else IR_br
```

### 11.3. Alíquota vigente, respeitando "nunca adivinhar"

```python
def aliquota_vigente(tabela: tuple[Aliquota, ...], nome: str, em: date | None) -> Aliquota:
    candidatas = tuple(a for a in tabela if a.nome == nome)
    if em is None:
        if len(candidatas) == 1:
            return candidatas[0]
        raise ValueError(f"{nome}: várias vigências; informe a data ou a alíquota.")
    for a in candidatas:
        if a.inicio <= em and (a.fim is None or em <= a.fim):
            return a
    raise LookupError(f"Nenhuma alíquota {nome} vigente em {em}")
```

### 11.4. Apuração: resultado imutável com construtores nomeados

```python
@dataclass(frozen=True)
class ApuracaoResgate:
    R_eu: Calculado[Money[EUR]]
    R_br: Calculado[Money[BRL]]
    IR_ptbr: Calculado[Money[BRL]]
    IR_br: Calculado[Money[BRL]]
    IR_ef: Calculado[Money[BRL]]

    @classmethod
    def de_cf(
        cls,
        I: Calculado[Money[BRL]],
        F: Calculado[Money[BRL]],
        C_i: Cambio,
        C_f: Cambio,
        tabela: tuple[Aliquota, ...] = TABELA_ALIQUOTAS,
    ) -> ApuracaoResgate:
        T_pt = aliquota_vigente(tabela, "T_pt", C_f.data)
        T_br = aliquota_vigente(tabela, "T_br", C_f.data)
        v_r_eu = r_eu(F_eu=f_eu(F=F, C_f=C_f), I_eu=i_eu(I=I, C_i=C_i))
        v_r_br = r_br(F=F, I=I)
        v_ir_ptbr = ir_ptbr(IR_pt=ir_pt(R_eu=v_r_eu, T_pt=T_pt), C_f=C_f)
        v_ir_br = ir_br(R_br=v_r_br, T_br=T_br)
        return cls(v_r_eu, v_r_br, v_ir_ptbr, v_ir_br, ir_ef(IR_ptbr=v_ir_ptbr, IR_br=v_ir_br))

    @classmethod
    def de_cd(
        cls,
        I: Calculado[Money[BRL]],
        F: Calculado[Money[BRL]],
        C_i: Cambio,
        C_d: Decimal,
        data_final: date | None = None,
        fonte: str | None = None,
        **kw: object,
    ) -> ApuracaoResgate:
        return cls.de_cf(I, F, C_i, Cambio(C_i.valor + C_d, data_final, fonte), **kw)
```

### 11.5. Uso e saída de auditoria

```python
a = ApuracaoResgate.de_cf(
    I=entrada("I", brl("10000.00"), "extrato: aporte"),
    F=entrada("F", brl("13200.00")),  # sem fonte: tudo bem
    C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
    C_f=Cambio(Decimal("6.00"), date(2025, 3, 10)),  # sem fonte: tudo bem
)
print(explicar(a.IR_ef))
```

```
BRL 480.00  ←  Fórmula 12: IR_ef = max(IR_ptbr, IR_br)  [Lei 14.754/2023, Art. 12]
  IR_ptbr:
    BRL 336.00  ←  Fórmula 10: IR_ptbr = IR_pt · C_f
      ...
  IR_br:
    BRL 480.00  ←  Fórmula 11: IR_br = max(0, R_br · T_br)  [Lei 14.754/2023, Art. 2º]
      R_br:
        BRL 3,200.00  ←  Fórmula 6: R_br = F - I
          F:
            BRL 13,200.00  ←  input F
          I:
            BRL 10,000.00  ←  input I  [extrato: aporte]
      T_br: T_br = 15% (desde 2024-01-01)
```

### 11.6. Testes nos três estilos

```python
# Unitário
def test_ir_br_cenario_a() -> None:
    r = ir_br(R_br=brl("3200.00"), T_br=T_BR_2024)
    assert r.valor == brl("480.00")


# Propriedade (Hypothesis)
@given(i=valores_brl(), f=valores_brl(), c_i=cambios(), c_f=cambios())
def test_ir_ef_nunca_menor_que_ir_br(i, f, c_i, c_f) -> None:
    a = ApuracaoResgate.de_cf(entrada("I", i), entrada("F", f), c_i, c_f)
    assert a.IR_ef.valor.quantia >= a.IR_br.valor.quantia


# Simbólico (SymPy): as formas documentadas da Fórmula 1 são equivalentes
def test_formula_1_formas_equivalentes() -> None:
    Ci, Cf = sp.symbols("C_i C_f", positive=True)
    Cd, Cp = Cf - Ci, (Cf - Ci) / Ci
    assert sp.simplify(Cp / (1 + Cp) * Cf - Cd) == 0
```
