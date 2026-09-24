<!-- Gerado por scripts/gerar_catalogo.py. Não edite à mão. -->
# Catálogo de fórmulas

Este documento responde, para cada valor que a biblioteca calcula: **o que é
calculado, como e com base em quê**. Ele é gerado a partir do próprio código,
então não pode divergir do que é executado.

A coluna *forma encadeada* é como a fórmula está escrita no código, em termos
das variáveis imediatamente anteriores. A coluna *forma expandida* é a mesma
fórmula reduzida apenas às variáveis de entrada ($I$, $F$, $C_i$, $C_f$,
$T_{pt}$, $T_{br}$), derivada por substituição simbólica — nunca escrita à mão.

## Fórmulas

### Fórmula 1 — C_d

Variação cambial absoluta, em reais por euro.

| | |
| :--- | :--- |
| Forma encadeada | $$C_d = C_f - C_i$$ |
| Forma expandida | $$C_d = C_{f} - C_{i}$$ |
| Base legal | — |

### Fórmula 2 — C_pct

Variação cambial relativa ao câmbio inicial (adimensional).

| | |
| :--- | :--- |
| Forma encadeada | $$C_\% = \frac{C_d}{C_i}$$ |
| Forma expandida | $$C_\% = \frac{C_{f} - C_{i}}{C_{i}}$$ |
| Base legal | — |

### Fórmula 3 — I_eu

Valor aportado, convertido para euros pelo câmbio do dia do aporte.

| | |
| :--- | :--- |
| Forma encadeada | $$I_{eu} = \frac{I}{C_i}$$ |
| Forma expandida | $$I_{eu} = \frac{I}{C_{i}}$$ |
| Base legal | — |

### Fórmula 4 — F_eu

Valor resgatado bruto, convertido para euros pelo câmbio do resgate.

| | |
| :--- | :--- |
| Forma encadeada | $$F_{eu} = \frac{F}{C_f}$$ |
| Forma expandida | $$F_{eu} = \frac{F}{C_{f}}$$ |
| Base legal | — |

### Fórmula 5 — R_eu

Rendimento bruto apurado em euros — a base de cálculo portuguesa.

| | |
| :--- | :--- |
| Forma encadeada | $$R_{eu} = F_{eu} - I_{eu}$$ |
| Forma expandida | $$R_{eu} = - \frac{I}{C_{i}} + \frac{F}{C_{f}}$$ |
| Base legal | — |

### Fórmula 6 — R_br

Rendimento bruto apurado em reais — a base de cálculo brasileira.

| | |
| :--- | :--- |
| Forma encadeada | $$R_{br} = F - I$$ |
| Forma expandida | $$R_{br} = F - I$$ |
| Base legal | Lei 14.754/2023, Art. 2º |

### Fórmula 7 — J

Rendimento bruto em termos percentuais (adimensional).

| | |
| :--- | :--- |
| Forma encadeada | $$J = \frac{R_{br}}{I}$$ |
| Forma expandida | $$J = \frac{F - I}{I}$$ |
| Base legal | — |

### Fórmula 8 — R_cc

Ganho cambial de dinheiro parado em conta não remunerada.

| | |
| :--- | :--- |
| Forma encadeada | $$R_{cc} = I \cdot C_\%$$ |
| Forma expandida | $$R_{cc} = \frac{I \left(C_{f} - C_{i}\right)}{C_{i}}$$ |
| Base legal | Lei 14.754/2023, Art. 2º, §3º |

### Fórmula 9 — IR_pt

Imposto retido em Portugal, sobre o rendimento apurado em euros.

| | |
| :--- | :--- |
| Forma encadeada | $$IR_{pt} = R_{eu} \cdot T_{pt}$$ |
| Forma expandida | $$IR_{pt} = - \frac{I T_{pt}}{C_{i}} + \frac{F T_{pt}}{C_{f}}$$ |
| Base legal | CIRS Art. 72.º — taxa liberatória sobre o rendimento em euros |

### Fórmula 10 — IR_ptbr

O imposto português convertido para reais pelo câmbio do resgate.

| | |
| :--- | :--- |
| Forma encadeada | $$IR_{ptbr} = IR_{pt} \cdot C_f$$ |
| Forma expandida | $$IR_{ptbr} = \frac{T_{pt} \left(- C_{f} I + C_{i} F\right)}{C_{i}}$$ |
| Base legal | — |

### Fórmula 11 — IR_br

Imposto devido no Brasil, antes da compensação do imposto estrangeiro.

| | |
| :--- | :--- |
| Forma encadeada | $$IR_{br} = R_{br} \cdot T_{br}$$ |
| Forma expandida | $$IR_{br} = T_{br} \left(F - I\right)$$ |
| Base legal | Lei 14.754/2023, Art. 2º |

### Fórmula 12 — IR_ef

Imposto efetivamente suportado, já aplicada a compensação.

| | |
| :--- | :--- |
| Forma encadeada | $$IR_{ef} = \max(IR_{ptbr},\ IR_{br})$$ |
| Forma expandida | $$IR_{ef} = \max\left(T_{br} \left(F - I\right), \frac{T_{pt} \left(- C_{f} I + C_{i} F\right)}{C_{i}}\right)$$ |
| Base legal | Lei 14.754/2023, Art. 12 |

### Fórmula 13 — R_liq

O que sobra do rendimento depois do imposto efetivamente pago.

| | |
| :--- | :--- |
| Forma encadeada | $$R_{liq} = R_{br} - IR_{ef}$$ |
| Forma expandida | $$R_{liq} = F - I - \max\left(T_{br} \left(F - I\right), - \frac{T_{pt} \left(C_{f} I - C_{i} F\right)}{C_{i}}\right)$$ |
| Base legal | — |

### Fórmula 14 — R_eubr

Quanto a aplicação rendeu por fora do câmbio, em reais.

| | |
| :--- | :--- |
| Forma encadeada | $$R_{eubr} = R_{eu} \cdot C_f$$ |
| Forma expandida | $$R_{eubr} = - \frac{C_{f} I}{C_{i}} + F$$ |
| Base legal | — |

### Fórmula 15 — J_eu

Rendimento percentual da aplicação em moeda local, sem efeito cambial.

| | |
| :--- | :--- |
| Forma encadeada | $$J_{eu} = \frac{R_{eu}}{I_{eu}}$$ |
| Forma expandida | $$J_{eu} = -1 + \frac{C_{i} F}{C_{f} I}$$ |
| Base legal | — |

### Fórmula 16 — V_inv

Quanto se ganhou por ter investido, em vez de deixar o dinheiro parado.

| | |
| :--- | :--- |
| Forma encadeada | $$V_{inv} = R_{liq} - R_{cc}$$ |
| Forma expandida | $$V_{inv} = - \frac{C_{f} I}{C_{i}} + F - \max\left(F T_{br} - I T_{br}, - \frac{C_{f} I T_{pt}}{C_{i}} + F T_{pt}\right)$$ |
| Base legal | Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada) |

### Fórmula 17 — F_proj

O `F` que resultaria de um juro `J_eu` e de um câmbio final `C_f`.

| | |
| :--- | :--- |
| Forma encadeada | $$F_{proj} = I_{eu} \cdot (1 + J_{eu}) \cdot C_f$$ |
| Forma expandida | $$F_{proj} = \frac{C_{f} I \left(J_{eu} + 1\right)}{C_{i}}$$ |
| Base legal | — |

### Fórmula 18 — C_eq

O câmbio final a partir do qual investir deixa de compensar.

| | |
| :--- | :--- |
| Forma encadeada | $$C_{eq} = \frac{C_i \cdot T_{br}}{T_{br}\,(1 + J_{eu}) - J_{eu}}$$ |
| Forma expandida | $$C_{eq} = \frac{C_{i} T_{br}}{J_{eu} T_{br} - J_{eu} + T_{br}}$$ |
| Base legal | Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada) |

### Fórmula 19 — J_eq

O juro mínimo para a aplicação apenas empatar com o dinheiro parado.

| | |
| :--- | :--- |
| Forma encadeada | $$J_{eq} = \max\left(0,\ \frac{T_{br}\,(C_f - C_i)}{C_f\,(1 - T_{br})}\right)$$ |
| Forma expandida | $$J_{eq} = \frac{T_{br} \left(- C_{f} + C_{i}\right)}{C_{f} \left(T_{br} - 1\right)}$$ |
| Base legal | Lei 14.754/2023, Art. 2º, §3º (isenção da conta não remunerada) |

## Alíquotas e vigências

Uma linha nunca é editada: quando a lei muda, fecha-se o fim da
vigência antiga e acrescenta-se outra linha.

| Alíquota | Valor | Início | Fim | Fonte |
| :--- | ---: | :--- | :--- | :--- |
| T_br | 15% | 2024-01-01 | vigente | Lei 14.754/2023, Art. 2º |
| T_pt | 28% | 2024-01-01 | vigente | CIRS Art. 72.º (taxa liberatória) — vigência ilustrativa, confirmar |

## Exemplo de árvore de auditoria

Aporte de R$ 10.000,00 a R$ 5,00/€, resgatado por R$ 13.200,00 a R$ 6,00/€.
Cada linha mostra o valor, a fórmula que o produziu e, quando houver,
a base legal e a origem do dado.

```
BRL 480.00  ←  Fórmula 12: IR_ef = max(IR_ptbr, IR_br)  [Lei 14.754/2023, Art. 12]
  IR_ptbr:
    BRL 336.00  ←  Fórmula 10: IR_ptbr = IR_pt · C_f
      IR_pt:
        EUR 56.00  ←  Fórmula 9: IR_pt = max(0, R_eu · T_pt)  [CIRS Art. 72.º — taxa liberatória sobre o rendimento em euros]
          R_eu:
            EUR 200.00  ←  Fórmula 5: R_eu = F_eu - I_eu
              F_eu:
                EUR 2,200.00  ←  Fórmula 4: F_eu = F / C_f
                  F:
                    BRL 13,200.00  ←  input F  [extrato: resgate]
                  C_f: R$ 6.00/€ em 2025-03-10 (PTAX)
              I_eu:
                EUR 2,000.00  ←  Fórmula 3: I_eu = I / C_i
                  I:
                    BRL 10,000.00  ←  input I  [extrato: aporte]
                  C_i: R$ 5.00/€ em 2024-05-02 (PTAX)
          T_pt: T_pt = 28% (desde 2024-01-01) [CIRS Art. 72.º (taxa liberatória) — vigência ilustrativa, confirmar]
      C_f: R$ 6.00/€ em 2025-03-10 (PTAX)
  IR_br:
    BRL 480.00  ←  Fórmula 11: IR_br = max(0, R_br · T_br)  [Lei 14.754/2023, Art. 2º]
      R_br:
        BRL 3,200.00  ←  Fórmula 6: R_br = F - I  [Lei 14.754/2023, Art. 2º]
          F:
            BRL 13,200.00  ←  input F  [extrato: resgate]
          I:
            BRL 10,000.00  ←  input I  [extrato: aporte]
      T_br: T_br = 15% (desde 2024-01-01) [Lei 14.754/2023, Art. 2º]
```

### Campos da declaração

| Campo na Receita Federal | Valor | Variável |
| :--- | ---: | :--- |
| Rendimento ou Perda | BRL 3,200.00 | R_br |
| Imposto pago no Exterior | BRL 336.00 | IR_ptbr |
