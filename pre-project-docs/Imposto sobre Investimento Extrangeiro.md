#IR 

A "Lei das _Offshores_ e Fundos Exclusivos", [Lei nº 14.754/2023](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm), que passou a vigorar em 2024 mudou muito as coisas.

# Dinheiro parado em Conta (corrente)
**Não é tributado**, pois "o dinheiro parado não gera fato gerador de imposto". Não importa a variação cambial. (*Art. 2º, §3º*)
> "A variação cambial de depósitos em conta-corrente ou em cartão de débito ou crédito no exterior não ficará sujeita à incidência do IRPF, desde que os depósitos **não sejam remunerados** e sejam mantidos em instituição financeira no exterior reconhecida e autorizada a funcionar pela autoridade monetária do país em que estiver situada."
**Atenção:** a isenção só vale se a conta **não for remunerada** (sem juros/rendimento). Se a conta render (ex.: conta remunerada, poupança estrangeira), ela deixa de se enquadrar aqui e passa a ser tratada como "aplicação financeira no exterior" (*Art. 3º, §1º, I*), sujeita à tributação normal.
**Na declaração de IR**: Você apenas precisará declarar o saldo da conta na ficha de "Bens e Direitos" na sua Declaração de Ajuste Anual, convertendo o valor em euros para reais usando a cotação do Banco Central para o dia 31 de dezembro do ano-calendário.

# Investimento extrangeiro
Paga imposto sim:
- 15% áliquota unica (não é regressivel) (*Art. 2º*)
- inclui cambio?
	- **A variação cambial compõe o lucro tributável**
- E se eu já tiver pego imposto fora?
	- "O Brasil e Portugal possuem um acordo para evitar a dupla tributação. A lei permite que você **compense** o imposto pago em Portugal contra o imposto devido no Brasil." (*Art. 12*)
	- _Exemplo:_ Se o seu ganho gerou um imposto devido de 15% no Brasil, mas Portugal já reteve 28% na fonte, você informa isso na sua declaração brasileira. O Brasil reconhece que você já pagou, zera a sua dívida aqui (mas não te devolve a diferença dos 13%).
- é só no momento que vendo a aplicação? e se eu estiver rolando ela?
	- Só paga o imposto no momento da venda
	- Se carregar a posição, o valor do bem não muda, continua aparecendo na declaração como *custo de Aquisição em Reais*
- E se for um rendimento que vai caindo parcialmente ao longo do tempo, como faz?
	- Sim, vc vai ser taxado por cada pagamento.
	- Na ficha de **Rendimentos no Exterior**, o valor bruto recebido (convertido em Reais).
	- Na ficha de **Imposto Pago no Exterior**, o valor retido em Portugal (convertido em Reais) para que o programa faça a compensação automaticamente e zere a sua guia de pagamento.
- 
A Receita Federal exige que o ganho seja calculado em **Reais (BRL)**. O cálculo funciona assim:
1. **Valor de Aplicação (Custo):** Você converte o valor investido em euros para reais pela cotação do dia em que fez o investimento.
2. **Valor de Resgate (Venda):** Você converte o valor resgatado em euros para reais pela cotação do dia em que o investimento voltou para sua conta.
3. **Base de Cálculo:** O lucro tributável é a diferença entre o Valor de Resgate (em R$) e o Valor de Aplicação (em R$).

Perguntas frequentes:
- o meu investimento não rendeu euros, porem o cambio valorizou: vai ter imposto.
- a aplicação rendeu (juro positivo), mas eu teria ganho mais deixando o dinheiro parado na conta: **pode acontecer, e não é raro.** Investir faz o ganho cambial — que seria isento se o dinheiro estivesse parado — virar base de cálculo. Ver [[#🧭 Decomposição do rendimento: aplicação vs. câmbio|Decomposição do rendimento]] e a [[#16. Vantagem de ter Investido ($V_{inv}$)|Fórmula 16]].
- 


# Matemática sobre investimentos em PT

## 📖 Glossário de Variáveis

| Variável    | Descrição                                                                                                                                    |   Unidade    |    Input?    | Fórmula                                                      |                                  Ref.                                  |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------------------- | :----------: | :----------: | :----------------------------------------------------------- | :--------------------------------------------------------------------: |
| $T_{pt}$    | Taxa de imposto em Portugal (2026: 28% sobre a variação do rendimento em moeda local, sem considerar câmbio)                                 |     $\%$     | 🔒 Constante | $T_{pt} = 28\%$                                              |                                   —                                    |
| $T_{br}$    | Taxa de imposto no Brasil (2026: 15% sobre o rendimento considerando a variação do valor em reais, ou seja, já levando o câmbio em conta)    |     $\%$     | 🔒 Constante | $T_{br} = 15\%$                                              |                                   —                                    |
| $I$         | Valor inicial                                                                                                                                | $\text{R\$}$ |   ✅ Input    | —                                                            |                                   —                                    |
| $F$         | Valor final — valor resgatado **bruto** (antes dos impostos)                                                                                 | $\text{R\$}$ |   ✅ Input    | —                                                            |                                   —                                    |
| $C_i$       | Valor do câmbio inicial (sentido: quanto 1 unidade da moeda estrangeira vale em reais)                                                       | $\text{R\$}$ |   ✅ Input    | —                                                            |                                   —                                    |
| $C_f$       | Valor do câmbio final (sentido: quanto 1 unidade da moeda estrangeira vale em reais)                                                         | $\text{R\$}$ |   ✅ Input    | —                                                            |                                   —                                    |
| $C_d$       | Diferença do valor do câmbio                                                                                                                 | $\text{R\$}$ | ⚙️ Calculado | $C_d = C_f - C_i$                                            |              [[#1. Variação Cambial ($C_d$)\|Fórmula 1]]               |
| $C_\%$      | Taxa de variação do câmbio no período                                                                                                        |     $\%$     | ⚙️ Calculado | $C_\% = \dfrac{C_d}{C_i}$                                    |          [[#2. Taxa de Variação Cambial ($C_\%$)\|Fórmula 2]]          |
| $I_{eu}$    | Valor inicial em moeda estrangeira (euro)                                                                                                    |     $€$      | ⚙️ Calculado | $I_{eu} = \dfrac{I}{C_i}$                                    |    [[#3. Valor Inicial em Moeda Estrangeira ($I_{eu}$)\|Fórmula 3]]    |
| $F_{eu}$    | Valor resgatado em moeda estrangeira (euro)                                                                                                  |     $€$      | ⚙️ Calculado | $F_{eu} = \dfrac{F}{C_f}$                                    |   [[#4. Valor Resgatado em Moeda Estrangeira ($F_{eu}$)\|Fórmula 4]]   |
| $R_{eu}$    | Rendimento Bruto Estrangeiro — rendimento da aplicação em moeda estrangeira (antes dos impostos)                                             |     $€$      | ⚙️ Calculado | $R_{eu} = F_{eu} - I_{eu} = \dfrac{F}{C_f} - \dfrac{I}{C_i}$ |       [[#5. Rendimento Bruto Estrangeiro ($R_{eu}$)\|Fórmula 5]]       |
| $R_{br}$    | Rendimento Bruto — rendimento da aplicação em R\$ (antes dos impostos)                                                                       | $\text{R\$}$ | ⚙️ Calculado | $R_{br} = F - I$                                             |             [[#6. Rendimento Bruto ($R_{br}$)\|Fórmula 6]]             |
| $J$         | Rendimento Bruto percentual (antigo "Juros") — rendimento percentual do período                                                              |     $\%$     | ⚙️ Calculado | $J = \dfrac{R_{br}}{I} = \dfrac{F - I}{I}$                   |          [[#7. Rendimento Bruto Percentual ($J$)\|Fórmula 7]]          |
| $R_{cc}$    | **Rendimento Cambial** — a parcela do rendimento que vem só da variação do câmbio. É também, por definição, o que o dinheiro teria rendido **parado** em conta não remunerada (sem incidência de imposto). Par de $R_{eubr}$ | $\text{R\$}$ | ⚙️ Calculado | $R_{cc} = I \cdot C_\%$                                      |       [[#8. Rendimento em Conta Corrente / Rendimento Cambial ($R_{cc}$)\|Fórmula 8]]       |
| $IR_{pt}$   | Valor do imposto retido em Portugal, incide sobre a base de cálculo $R_{eu}$ (em moeda estrangeira)                                          |     $€$      | ⚙️ Calculado | $IR_{pt} = R_{eu} \cdot T_{pt}$                              |       [[#9. Imposto retido em Portugal ($IR_{pt}$)\|Fórmula 9]]        |
| $IR_{ptbr}$ | Imposto Retido Estrangeiro — o $IR_{pt}$ (apurado em euros), convertido para Reais                                                           | $\text{R\$}$ | ⚙️ Calculado | $IR_{ptbr} = IR_{pt} \cdot C_f$                              | [[#10. Imposto Retido Estrangeiro em Reais ($IR_{ptbr}$)\|Fórmula 10]] |
| $IR_{br}$   | Valor Imposto BR — imposto a recolher no Brasil, incide sobre a base de cálculo $R_{br}$                                                     | $\text{R\$}$ | ⚙️ Calculado | $IR_{br} = R_{br} \cdot T_{br}$                              |     [[#11. Imposto a recolher no Brasil ($IR_{br}$)\|Fórmula 11]]      |
| $IR_{ef}$   | Imposto Efetivo — o que de fato é cobrado, considerando a compensação Brasil-Portugal (não é redutível a uma fórmula fechada, é condicional) | $\text{R\$}$ | ⚙️ Calculado | $IR_{ef} = \max(IR_{ptbr},\ IR_{br})$                        |            [[#12. Imposto Efetivo ($IR_{ef}$)\|Fórmula 12]]            |
| $R_{liq}$   | Rendimento Líquido (Lucro) — o que sobra do rendimento depois de descontado o imposto efetivo                                                | $\text{R\$}$ | ⚙️ Calculado | $R_{liq} = R_{br} - IR_{ef}$                                 |          [[#13. Rendimento Líquido ($R_{liq}$)\|Fórmula 13]]           |
| $R_{eubr}$  | **Rendimento da Aplicação** ("juro"/prêmio da aplicação) — quanto a aplicação rendeu **por fora do câmbio**, convertido para Reais. Par de $R_{cc}$ | $\text{R\$}$ | ⚙️ Calculado | $R_{eubr} = R_{eu} \cdot C_f$                                | [[#14. Rendimento da Aplicação em Reais ($R_{eubr}$)\|Fórmula 14]] |
| $J_{eu}$    | Juro da Aplicação — o rendimento percentual da aplicação em moeda local, limpo de qualquer efeito cambial (é o "juro" que a corretora anuncia) | $\%$ | ⚙️ Calculado | $J_{eu} = \dfrac{R_{eu}}{I_{eu}}$                            | [[#15. Juro da Aplicação ($J_{eu}$)\|Fórmula 15]] |
| $V_{inv}$   | Vantagem de ter Investido — quanto se ganhou (ou se perdeu, se negativo) por ter investido em vez de deixar o dinheiro parado na conta | $\text{R\$}$ | ⚙️ Calculado | $V_{inv} = R_{liq} - R_{cc}$                                 | [[#16. Vantagem de ter Investido ($V_{inv}$)\|Fórmula 16]] |

> **Convenção:** tudo que é chamado de "**Bruto**" (ex.: $R_{br}$, $J$, e o próprio $F$) significa **antes dos impostos**.
> **Sobre o sufixo `pt`/`br`/`eu`:** ele indica o *contexto/país* da variável (ex.: imposto de Portugal, base brasileira), e quando isso não deixa a moeda óbvia, o sufixo cresce encadeando o destino da conversão — ex.: $IR_{pt}$ (imposto de Portugal, em €) → $IR_{ptbr}$ (o mesmo imposto, convertido pro contexto/moeda do Brasil), e da mesma forma $R_{eu}$ (rendimento da aplicação, em €) → $R_{eubr}$ (o mesmo rendimento, em R\$).
> **Sobre os pares:** $R_{cc}$ (cambial) e $R_{eubr}$ (aplicação) são as duas metades complementares do $R_{br}$ — ver [[#🧭 Decomposição do rendimento: aplicação vs. câmbio|Decomposição do rendimento]].

---

## 📐 Fórmulas de Cálculo

### 1. Variação Cambial ($C_d$)
Quanto o câmbio variou em termos absolutos, em reais por euro — a diferença entre o câmbio final ($C_f$) e o inicial ($C_i$):

$$C_d = C_f - C_i$$

### 2. Taxa de Variação Cambial ($C_\%$)
A variação percentual do câmbio no período é a diferença cambial ($C_d$) relativa ao câmbio inicial ($C_i$):

$$C_\% = \frac{C_d}{C_i}$$

**Versão em termos de inputs/constantes:**

$$C_\% = \frac{C_f - C_i}{C_i}$$

### 3. Valor Inicial em Moeda Estrangeira ($I_{eu}$)
Converte o valor inicial (em reais) para a moeda estrangeira, usando o câmbio do dia do investimento:

$$I_{eu} = \frac{I}{C_i}$$

### 4. Valor Resgatado em Moeda Estrangeira ($F_{eu}$)
Converte o valor resgatado (em reais) para a moeda estrangeira, usando o câmbio do dia do resgate:

$$F_{eu} = \frac{F}{C_f}$$

### 5. Rendimento Bruto Estrangeiro ($R_{eu}$)
O rendimento bruto da aplicação, mas em moeda estrangeira (antes dos impostos), é a diferença entre o valor resgatado e o valor inicial, ambos convertidos:

$$R_{eu} = F_{eu} - I_{eu}$$

$$R_{eu} = \frac{F}{C_f} - \frac{I}{C_i}$$

### 6. Rendimento Bruto ($R_{br}$)
O rendimento bruto da aplicação, em reais (antes dos impostos), é a diferença entre o valor final e o valor inicial:

$$R_{br} = F - I$$

### 7. Rendimento Bruto Percentual ($J$)
$J$ (antes chamado de "Juros") é o rendimento bruto em termos percentuais — o quanto o investimento rendeu, em proporção ao valor inicial, antes dos impostos:

$$J = \frac{R_{br}}{I}$$

$$J = \frac{F - I}{I}$$

### 8. Rendimento em Conta Corrente / Rendimento Cambial ($R_{cc}$)
Quanto o dinheiro parado em conta corrente rende em reais, apenas pelo efeito da variação cambial — não incide imposto (dinheiro parado não gera fato gerador, ver *Art. 2º, §3º* no topo do documento).

Esta variável tem **dois papéis**, e é o mesmo número nos dois:
1. **Cenário alternativo:** o que o dinheiro teria rendido se tivesse ficado parado (isento).
2. **Parcela do resultado real:** o quanto do $R_{br}$ veio do câmbio, e não da aplicação. Nesse papel ela é o par de $R_{eubr}$ (ver [[#🧭 Decomposição do rendimento: aplicação vs. câmbio|Decomposição do rendimento]]).

$$R_{cc} = I \cdot C_\%$$

**Versão em termos de inputs/constantes:**

$$R_{cc} = I \cdot \frac{C_f - C_i}{C_i}$$

### 9. Imposto retido em Portugal ($IR_{pt}$)
A base de cálculo do imposto em Portugal é o Rendimento Bruto Estrangeiro ($R_{eu}$, apurado em euros, sem conversão pra reais). Basta aplicar a alíquota $T_{pt}$ sobre essa base:

$$IR_{pt} = R_{eu} \cdot T_{pt}$$

$$IR_{pt} = \left(\frac{F}{C_f} - \frac{I}{C_i}\right) \cdot T_{pt}$$

### 10. Imposto Retido Estrangeiro em Reais ($IR_{ptbr}$)
O mesmo imposto retido em Portugal ($IR_{pt}$), mas convertido para Reais pelo câmbio final — útil para comparar diretamente com $IR_{br}$:

$$IR_{ptbr} = IR_{pt} \cdot C_f$$

$$IR_{ptbr} = \left(\frac{F}{C_f} - \frac{I}{C_i}\right) \cdot T_{pt} \cdot C_f$$

### 11. Imposto a recolher no Brasil ($IR_{br}$)
A base de cálculo do imposto no Brasil é o Rendimento Bruto ($R_{br}$, que já embute a variação cambial via $F$). Basta aplicar a alíquota $T_{br}$ sobre essa base:

$$IR_{br} = R_{br} \cdot T_{br}$$

$$IR_{br} = (F - I) \cdot T_{br}$$

### 12. Imposto Efetivo ($IR_{ef}$)
Não é uma fórmula fechada — é **condicional**, pois depende da compensação entre Brasil e Portugal (ver seção *Investimento extrangeiro* acima). O que você efetivamente paga é sempre o **maior** dos dois valores: se Portugal já reteve mais do que o Brasil cobraria, o Brasil zera a diferença (mas não devolve o excedente); se reteve menos, você paga a diferença no Brasil até completar $IR_{br}$:

$$IR_{ef} = \begin{cases} IR_{ptbr}, & \text{se } IR_{ptbr} > IR_{br} \\ IR_{br}, & \text{se } IR_{ptbr} \le IR_{br} \end{cases}$$

$$IR_{ef} = \max(IR_{ptbr},\ IR_{br})$$

**Versão em termos de inputs/constantes:**

$$IR_{ef} = \max\left(\ \left(\frac{F}{C_f} - \frac{I}{C_i}\right) \cdot T_{pt} \cdot C_f\ ,\ \ (F - I) \cdot T_{br}\ \right)$$

### 13. Rendimento Líquido ($R_{liq}$)
O lucro que de fato sobra, já descontado o imposto efetivamente pago:

$$R_{liq} = R_{br} - IR_{ef}$$

**Versão em termos de inputs/constantes:**

$$R_{liq} = (F - I) - \max\left(\ \left(\frac{F}{C_f} - \frac{I}{C_i}\right) \cdot T_{pt} \cdot C_f\ ,\ \ (F - I) \cdot T_{br}\ \right)$$

---

## 🧭 Decomposição do rendimento: aplicação vs. câmbio

> **Nada aqui entra na declaração.** As três variáveis desta seção ($R_{eubr}$, $J_{eu}$, $V_{inv}$) servem para *entender* o resultado e para responder "valeu a pena ter investido?". Nenhuma delas altera o imposto devido.

O $R_{br}$ (Fórmula 6) mistura duas coisas de naturezas bem diferentes: o que a **aplicação** rendeu e o que o **câmbio** rendeu. Só a primeira depende da qualidade do investimento; a segunda você teria tido de qualquer jeito, apenas por manter euros. Separar as duas é o que permite responder à pergunta que vem depois do imposto: *teria valido mais a pena deixar o dinheiro parado na conta?*

A separação é **exata** — não é uma aproximação:

$$R_{br} = \underbrace{R_{cc}}_{\text{rendimento cambial}} + \underbrace{R_{eubr}}_{\text{rendimento da aplicação}}$$

**Demonstração.** Partindo de $F = F_{eu} \cdot C_f$, $I = I_{eu} \cdot C_i$ e $F_{eu} = I_{eu} + R_{eu}$:

$$R_{br} = F - I = (I_{eu} + R_{eu}) \cdot C_f - I_{eu} \cdot C_i = I_{eu} \cdot \underbrace{(C_f - C_i)}_{C_d} + R_{eu} \cdot C_f$$

E como $I_{eu} \cdot C_d = \dfrac{I}{C_i} \cdot C_d = I \cdot C_\% = R_{cc}$, sobra exatamente $R_{br} = R_{cc} + R_{eubr}$. $\blacksquare$

### 14. Rendimento da Aplicação em Reais ($R_{eubr}$)
O quanto a aplicação rendeu **por fora do câmbio** — o "juro" ou prêmio que a aplicação pagou —, expresso em Reais. É o $R_{eu}$ (apurado em euros, Fórmula 5) convertido pelo câmbio do resgate, exatamente como $IR_{pt}$ vira $IR_{ptbr}$ na Fórmula 10:

$$R_{eubr} = R_{eu} \cdot C_f$$

**Versão em termos de inputs/constantes:**

$$R_{eubr} = \left(\frac{F}{C_f} - \frac{I}{C_i}\right) \cdot C_f$$

> **Por que converter pelo câmbio final ($C_f$), e não pelo inicial?** Porque é essa a escolha que faz a decomposição fechar exatamente ($R_{cc} + R_{eubr} = R_{br}$, demonstrado acima). Ela também é a leitura economicamente correta: o rendimento da aplicação só existiu, e só ficou disponível, no dia do resgate — é com o câmbio daquele dia que ele vira reais.

### 15. Juro da Aplicação ($J_{eu}$)
O rendimento percentual da aplicação em moeda local, limpo de qualquer efeito cambial. É o número que a corretora portuguesa anuncia, e o único que se pode comparar honestamente com outra aplicação em euros:

$$J_{eu} = \frac{R_{eu}}{I_{eu}}$$

**Versão em termos de inputs/constantes:**

$$J_{eu} = \frac{\dfrac{F}{C_f} - \dfrac{I}{C_i}}{\dfrac{I}{C_i}} = \frac{F \cdot C_i}{I \cdot C_f} - 1$$

> **Não confundir com $J$ (Fórmula 7).** $J = \dfrac{R_{br}}{I}$ é o rendimento percentual *em reais*, e portanto contamina o desempenho da aplicação com a variação do câmbio. Um $J$ alto com $J_{eu}$ baixo significa que quem rendeu foi o euro, não a aplicação.

### 16. Vantagem de ter Investido ($V_{inv}$)
A comparação direta entre os dois mundos: de um lado o que efetivamente sobrou depois do imposto ($R_{liq}$, Fórmula 13); do outro o que o mesmo dinheiro teria rendido parado em conta não remunerada, sem imposto nenhum ($R_{cc}$, Fórmula 8):

$$V_{inv} = R_{liq} - R_{cc}$$

Se $V_{inv} < 0$, teria valido mais a pena **não** ter investido.

**Forma equivalente (substituindo a decomposição):**

$$V_{inv} = R_{eubr} - IR_{ef}$$

Esta segunda forma é a mais reveladora, e vale ler em voz alta: **investir só compensa se o que a aplicação rendeu por fora do câmbio ($R_{eubr}$) superar o imposto inteiro ($IR_{ef}$)** — inclusive a parcela do imposto que incide sobre o ganho cambial, que seria **isenta** se o dinheiro estivesse parado. O ponto de equilíbrio é $R_{eubr} = IR_{ef}$.

**Premissas da comparação** (importantes, porque a resposta muda se elas mudarem):
- A alternativa considerada é manter o mesmo valor **em euros**, numa conta **não remunerada** no exterior (*Art. 2º, §3º*). Se a conta for remunerada, ela deixa de ser isenta, vira "aplicação financeira no exterior" e esta comparação não se aplica.
- Não entram na conta: taxas da corretora, custo de oportunidade de ter deixado o dinheiro em reais no Brasil, nem inflação.

### ⚠️ O caso contraintuitivo: a aplicação rendeu e mesmo assim perdeu

Vale a pena registrar o cenário que motivou estas fórmulas, porque ele contraria a intuição. **Uma aplicação com juro positivo pode ser pior do que não ter feito nada.**

Aporte de R\$ 10.000,00 com o euro a R\$ 5,00 (€ 2.000,00). A aplicação rende **+1% em euros** e, no período, o euro sobe 60%, para R\$ 8,00:

| Variável | Valor | Leitura |
| :--- | ---: | :--- |
| $J_{eu}$ | $+1\%$ | a aplicação rendeu — não deu prejuízo |
| $R_{cc}$ | R\$ 6.000,00 | o que o câmbio rendeu sozinho |
| $R_{eubr}$ | R\$ 160,00 | o que a aplicação rendeu, por fora do câmbio |
| $R_{br}$ | R\$ 6.160,00 | a base de cálculo brasileira ($6.000 + 160$) |
| $IR_{ef}$ | R\$ 924,00 | imposto sobre **tudo**, inclusive sobre os R\$ 6.000 cambiais |
| $R_{liq}$ | R\$ 5.236,00 | o que sobrou tendo investido |
| **Parado** | **R\$ 6.000,00** | o que teria sobrado sem investir (isento) |
| $V_{inv}$ | **−R\$ 764,00** | **deixar parado teria sido R\$ 764,00 melhor** |

O mecanismo: os R\$ 6.000,00 de ganho cambial seriam **isentos** com o dinheiro parado, mas ao investir eles entram na base de cálculo e pagam 15%. Esses R\$ 900,00 de imposto extra não são cobertos pelos R\$ 160,00 que a aplicação rendeu. Conferindo pela forma equivalente: $V_{inv} = 160 - 924 = -764$. ✓

**Regra prática que sai daí:** quanto maior a variação cambial no período, maior o "pedágio" que a aplicação precisa pagar só para empatar com a conta parada. O pedágio é $R_{cc} \cdot T_{br}$ sempre que o imposto brasileiro for o que prevalece.

---

## 🔗 De-Para com o Sistema da Receita Federal

Mapeamento entre os campos da ficha **Bens e Direitos → Aplicação Financeira (R\$)** (tela de "Detalhe: Bem e Direito", grupo 06/01 — Depósito em conta corrente) e as variáveis deste documento. Os dois campos da caixa "Aplicação Financeira" são declarados em **Reais**, então o de-para respeita a mesma unidade:

| Campo na Receita Federal | Variável equivalente | Observação |
| :--- | :---: | :--- |
| Rendimento ou Perda | $R_{br}$ | Já está em R\$ (Fórmula 6) — bate direto com o campo. |
| Imposto pago no Exterior | $IR_{ptbr}$ | O campo é em R\$, então é o $IR_{pt}$ (apurado em €) **já convertido** pelo câmbio (Fórmula 10) — não o $IR_{pt}$ bruto em euros. |

---
