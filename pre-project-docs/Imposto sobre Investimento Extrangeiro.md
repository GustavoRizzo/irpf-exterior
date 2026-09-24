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
| $F_{proj}$  | Valor Resgatado Projetado — o $F$ que *resultaria* de um juro $J_{eu}$ e de um câmbio final $C_f$. Usado em simulação, quando $F$ ainda não existe | $\text{R\$}$ | ⚙️ Calculado | $F_{proj} = I_{eu} \cdot (1 + J_{eu}) \cdot C_f$             | [[#17. Valor Resgatado Projetado ($F_{proj}$)\|Fórmula 17]] |
| $C_{eq}$    | Câmbio de Equilíbrio — o $C_f$ a partir do qual investir deixa de compensar, dado um juro $J_{eu}$ (só existe no regime brasileiro, e apenas com $0 < J_{eu} < \frac{T_{br}}{1-T_{br}}$) | $\text{R\$}$ | ⚙️ Calculado | $C_{eq} = \dfrac{C_i \cdot T_{br}}{T_{br}(1 + J_{eu}) - J_{eu}}$ | [[#18. Câmbio de Equilíbrio ($C_{eq}$)\|Fórmula 18]] |
| $J_{eq}$    | Juro de Equilíbrio — o juro mínimo que a aplicação precisa render para empatar com o dinheiro parado, dado um câmbio $C_f$ | $\%$ | ⚙️ Calculado | $J_{eq} = \max\left(0,\ \dfrac{T_{br}\,(C_f - C_i)}{C_f\,(1 - T_{br})}\right)$ | [[#19. Juro de Equilíbrio ($J_{eq}$)\|Fórmula 19]] |

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

## 🔮 Simulação: e se o câmbio (ou o juro) for outro?

> **Para quem ainda está decidindo.** As Fórmulas 1–16 apuram um investimento que já aconteceu: $F$ é um fato, lido no extrato. Esta seção serve à pergunta anterior — *"se eu investir, e o câmbio terminar em X, ainda compensa?"* — quando $F$ ainda não existe.

### A parametrização muda

Em simulação **não se pode variar $C_f$ mantendo $F$ fixo**. Os dois não são independentes: o valor resgatado em reais é, por construção, o montante em euros convertido pelo câmbio do dia. Quem segura $F$ e mexe em $C_f$ está, sem perceber, dizendo que a aplicação rendeu outra coisa.

A relação é:

$$F = \underbrace{\frac{I}{C_i}}_{I_{eu}} \cdot (1 + J_{eu}) \cdot C_f$$

Por isso a simulação é parametrizada por $(I,\ C_i,\ J_{eu},\ C_f)$ e **deriva** o $F$, em vez de recebê-lo. A vantagem é que os dois eixos ficam **ortogonais**: $J_{eu}$ mede só o desempenho da aplicação, $C_f$ mede só o câmbio, e mexer em um não contamina o outro.

### 17. Valor Resgatado Projetado ($F_{proj}$)
O $F$ que resultaria de um determinado juro e de um determinado câmbio final. É a inversa da Fórmula 15 (que extrai $J_{eu}$ de um $F$ conhecido), encadeada com a conversão para reais:

$$F_{proj} = I_{eu} \cdot (1 + J_{eu}) \cdot C_f$$

**Versão em termos de inputs/constantes:**

$$F_{proj} = \frac{I}{C_i} \cdot (1 + J_{eu}) \cdot C_f$$

> Alimentando $F_{proj}$ de volta nas Fórmulas 1–16, toda a apuração (e a auditoria) funciona igual: a simulação não é um caminho de cálculo paralelo, é a mesma apuração com um $F$ projetado.

### Os dois regimes, e por que só um tem equilíbrio

O $IR_{ef}$ é o **maior** entre o imposto português e o brasileiro (Fórmula 12), e cada um incide sobre uma base diferente. Isso parte a análise em dois regimes:

| Regime | Quando | $V_{inv}$ vale | Investir pode perder para a conta parada? |
| :--- | :--- | :--- | :--- |
| **Portugal prevalece** | $IR_{ptbr} > IR_{br}$ | $R_{eubr} \cdot (1 - T_{pt})$ | **Não.** É sempre positivo se a aplicação rendeu. |
| **Brasil prevalece** | $IR_{br} \ge IR_{ptbr}$ | $R_{eubr} - T_{br} \cdot R_{br}$ | **Sim.** É aqui que existe ponto de equilíbrio. |

A razão é direta: Portugal tributa **só o rendimento da aplicação** ($R_{eu}$), então sempre sobra $(1 - T_{pt})$ do prêmio. O Brasil tributa **o rendimento inteiro** ($R_{br}$), que inclui o ganho cambial — e esse ganho seria isento com o dinheiro parado. Só o imposto brasileiro cobra pedágio sobre algo que você teria de graça.

**Consequência prática:** investir só pode ser pior do que não investir quando o imposto brasileiro é o que prevalece.

### 18. Câmbio de Equilíbrio ($C_{eq}$)
Dado um juro esperado $J_{eu}$, o câmbio final a partir do qual investir deixa de compensar. Sai de resolver $V_{inv} = 0$ para $C_f$ no regime brasileiro:

$$C_{eq} = \frac{C_i \cdot T_{br}}{T_{br}\,(1 + J_{eu}) - J_{eu}}$$

Leitura: com $C_f < C_{eq}$ investir compensa; acima disso, o imposto sobre o ganho cambial come mais do que a aplicação rendeu.

> **Quando não existe equilíbrio — por excesso.** Se $J_{eu} \ge \dfrac{T_{br}}{1 - T_{br}}$ o denominador deixa de ser positivo e **nenhum câmbio** torna o investimento pior que a conta parada. Com $T_{br} = 15\%$, essa fronteira é $J_{eu} \approx 17{,}65\%$: uma aplicação que renda mais que isso em euros compensa sempre. A aproximação é **assintótica**: a 17,6% o equilíbrio já passa de R\$ 1.800/€, o que na prática é a mesma resposta.

> **Quando não existe equilíbrio — por falta.** Se $J_{eu} \le 0$ não há prêmio algum a comparar, e investir perde em todo o eixo. A forma fechada devolveria um câmbio qualquer, porque foi derivada **supondo imposto devido**; com prejuízo, o imposto é zero por piso (Fórmula 11) e a álgebra deixa de valer. São dois "não existe equilíbrio" de sinais opostos, e confundi-los seria pior do que não responder.

### 19. Juro de Equilíbrio ($J_{eq}$)
O espelho da anterior: dado um câmbio final esperado, o juro **mínimo** que a aplicação precisa render para apenas empatar com o dinheiro parado:

$$J_{eq} = \max\left(0,\ \frac{T_{br}\,(C_f - C_i)}{C_f\,(1 - T_{br})}\right)$$

> **Por que o piso em zero.** Com o câmbio em queda a fração fica negativa, mas ali o rendimento em reais também é negativo e o imposto é **zero por piso** (Fórmula 11) — de modo que o equilíbrio verdadeiro é exatamente $J_{eu} = 0$, e não o número que a álgebra sugere. A fração foi derivada supondo imposto devido; fora dessa hipótese ela não vale.

**Forma equivalente, em termos do rendimento cambial** (válida quando há imposto devido)**:**

$$J_{eq} = \frac{T_{br} \cdot R_{cc}}{I_{eu} \cdot C_f \cdot (1 - T_{br})}$$

Esta segunda forma diz o que está acontecendo: o juro mínimo é exatamente o que cobre **o imposto sobre o ganho cambial**, diluído pelo valor investido. Sem ganho cambial ($C_f \le C_i$) não há imposto a cobrir e o $J_{eq}$ é zero — qualquer juro positivo já compensa.

> $C_{eq}$ e $J_{eq}$ são **inversas uma da outra**: aplicar uma sobre o resultado da outra devolve o valor original.

### Exemplo

Aporte de R\$ 10.000,00 com o euro a R\$ 5,00, numa aplicação que promete **+1% em euros**:

| Pergunta | Resposta |
| :--- | :--- |
| Até que câmbio compensa investir? | $C_{eq} = \dfrac{5{,}00 \cdot 0{,}15}{0{,}15 \cdot 1{,}01 - 0{,}01} \approx$ **R\$ 5,30** |
| Se eu acho que o euro vai a R\$ 8,00, quanto a aplicação precisa render? | $J_{eq} = \dfrac{0{,}15 \cdot (8 - 5)}{8 \cdot 0{,}85} \approx$ **6,62%** |

Ou seja: a 1% de juro, basta o euro passar de R\$ 5,30 para que valha mais a pena não ter investido. E se a expectativa é o euro a R\$ 8,00, só faz sentido investir numa aplicação que renda mais de 6,62% em euros.

---

## 🔗 De-Para com o Sistema da Receita Federal

Mapeamento entre os campos da ficha **Bens e Direitos → Aplicação Financeira (R\$)** (tela de "Detalhe: Bem e Direito", grupo 06/01 — Depósito em conta corrente) e as variáveis deste documento. Os dois campos da caixa "Aplicação Financeira" são declarados em **Reais**, então o de-para respeita a mesma unidade:

| Campo na Receita Federal | Variável equivalente | Observação |
| :--- | :---: | :--- |
| Rendimento ou Perda | $R_{br}$ | Já está em R\$ (Fórmula 6) — bate direto com o campo. |
| Imposto pago no Exterior | $IR_{ptbr}$ | O campo é em R\$, então é o $IR_{pt}$ (apurado em €) **já convertido** pelo câmbio (Fórmula 10) — não o $IR_{pt}$ bruto em euros. |

---
