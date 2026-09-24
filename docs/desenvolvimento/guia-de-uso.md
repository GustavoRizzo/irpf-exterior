# Guia de uso

Todos os exemplos abaixo são executados como testes (`tests/test_guia_de_uso.py`),
então não podem ficar desatualizados em relação à biblioteca.

```python
>>> from datetime import date
>>> from decimal import Decimal
>>> from irpf_exterior import (
...     ApuracaoResgate, Cambio, brl, entrada, eur, explicar,
... )

```

## 1. Dinheiro é tipado e nunca vira `float`

Quantias são sempre `Decimal`, construídas a partir de texto. Os helpers
`brl()` e `eur()` fazem isso:

```python
>>> brl("10000.00") + brl("200.00")
Money(quantia=Decimal('10200.00'), moeda=BRL)

```

Misturar moedas é erro — apanhado pelo mypy antes de rodar e pelo `Money` em
execução:

```python
>>> brl("10.00") + eur("1.00")
Traceback (most recent call last):
    ...
TypeError: não é possível operar BRL com EUR

```

Converter é sempre explícito, e o câmbio diz de que data ele é:

```python
>>> cambio = Cambio(Decimal("6.00"), date(2025, 3, 10), "PTAX")
>>> print(cambio.para_eur(brl("13200.00")))
EUR 2,200.00

```

## 2. Apurar um resgate

O construtor principal recebe o aporte, o resgate e os dois câmbios. Os nomes
são os do glossário: `I`, `F`, `C_i`, `C_f`.

```python
>>> apuracao = ApuracaoResgate.de_cf(
...     I=entrada("I", brl("10000.00"), "extrato: aporte"),
...     F=brl("13200.00"),
...     C_i=Cambio(Decimal("5.00"), date(2024, 5, 2), "PTAX"),
...     C_f=Cambio(Decimal("6.00"), date(2025, 3, 10), "PTAX"),
... )
>>> print(apuracao.R_br.valor)     # rendimento na base brasileira
BRL 3,200.00
>>> print(apuracao.R_eu.valor)     # rendimento na base portuguesa
EUR 200.00
>>> print(apuracao.IR_ptbr.valor)  # retido em Portugal, já em reais
BRL 336.00
>>> print(apuracao.IR_br.valor)    # devido no Brasil, antes da compensação
BRL 480.00
>>> print(apuracao.IR_ef.valor)    # o maior dos dois: é o que se paga
BRL 480.00

```

Quanto ainda falta recolher aqui, já descontado o imposto português:

```python
>>> print(apuracao.a_pagar_no_brasil())
BRL 144.00

```

Envolver a entrada em `entrada(...)` é opcional: serve para registrar de onde
o número veio. Um `Money` cru também é aceito, como o `F` acima.

## 3. Preencher a declaração

```python
>>> for campo, calculado in apuracao.de_para_receita().items():
...     print(f"{campo}: {calculado.valor}")
Rendimento ou Perda: BRL 3,200.00
Imposto pago no Exterior: BRL 336.00

```

O campo "Imposto pago no Exterior" é declarado em reais — por isso é o
`IR_ptbr`, e não o `IR_pt` apurado em euros.

## 4. Explicar um número

Qualquer campo da apuração carrega a sua própria árvore de cálculo:

```python
>>> print(explicar(apuracao.R_br))
BRL 3,200.00  ←  Fórmula 6: R_br = F - I  [Lei 14.754/2023, Art. 2º]
  F:
    BRL 13,200.00  ←  input F
  I:
    BRL 10,000.00  ←  input I  [extrato: aporte]

```

Metadados ausentes simplesmente não aparecem: o `F` acima foi passado sem
fonte, e a biblioteca não inventa uma.

## 5. Quando o câmbio final não é conhecido diretamente

Se o que se tem é a *variação* cambial, use o construtor alternativo — ele
deriva `C_f` pela Fórmula 1 e delega ao principal:

```python
>>> por_variacao = ApuracaoResgate.de_cd(
...     I=brl("10000.00"),
...     F=brl("13200.00"),
...     C_i=Cambio(Decimal("5.00"), date(2024, 5, 2)),
...     C_d=Decimal("1.00"),
...     data_final=date(2025, 3, 10),
... )
>>> por_variacao.C_f.valor
Decimal('6.00')

```

## 6. Alíquotas: escolher por data ou informar explicitamente

Por padrão, as alíquotas saem da tabela pela data do câmbio final:

```python
>>> print(apuracao.T_br)
T_br = 15% (desde 2024-01-01) [Lei 14.754/2023, Art. 2º]

```

Sem data de referência, a biblioteca só decide se houver uma única vigência
cadastrada; caso contrário, ela pede o dado em vez de adivinhar:

```python
>>> from irpf_exterior import Aliquota, aliquota_vigente
>>> tabela = (
...     Aliquota("T_br", Decimal("0.15"), date(2024, 1, 1), date(2029, 12, 31)),
...     Aliquota("T_br", Decimal("0.20"), date(2030, 1, 1)),
... )
>>> aliquota_vigente(tabela, "T_br", None)
Traceback (most recent call last):
    ...
ValueError: T_br: há 2 vigências cadastradas. Informe a data de referência ou passe a alíquota explicitamente.

```

Para reproduzir um ano passado, injete a tabela daquela época — ou passe a
alíquota direto:

```python
>>> historica = ApuracaoResgate.de_cf(
...     I=brl("10000.00"),
...     F=brl("13200.00"),
...     C_i=Cambio(Decimal("5.00")),
...     C_f=Cambio(Decimal("6.00")),
...     T_br=Aliquota("T_br", Decimal("0.20"), date(2030, 1, 1)),
...     T_pt=Aliquota("T_pt", Decimal("0.28"), date(2024, 1, 1)),
... )
>>> print(historica.IR_br.valor)
BRL 640.00

```

## 7. Buscar dados de fora: as portas

O núcleo não acessa a rede. Ele apenas declara o formato do que espera, em
`portas.py`; o adaptador é seu, e fica fora da biblioteca:

```python
>>> from irpf_exterior import ProvedorDeCambio
>>> class PtaxFalso:
...     """Um adaptador de brinquedo — o de verdade chamaria a API do BC."""
...     def cambio_em(self, dia: date) -> Cambio:
...         return Cambio(Decimal("6.00"), dia, "PTAX (falso)")
>>> provedor: ProvedorDeCambio = PtaxFalso()
>>> print(provedor.cambio_em(date(2025, 3, 10)))
R$ 6.00/€ em 2025-03-10 (PTAX (falso))

```

O consumidor usa a porta para obter o dado e **então** chama a função pura;
nenhuma função de cálculo recebe uma porta.

## 8. As fórmulas isoladamente

Cada fórmula pode ser usada sozinha, sempre com argumentos nomeados:

```python
>>> from irpf_exterior import REGISTRO, ir_br
>>> resultado = ir_br(R_br=brl("3200.00"), T_br=apuracao.T_br)
>>> print(resultado.valor)
BRL 480.00
>>> print(REGISTRO["IR_br"])
Fórmula 11: IR_br = max(0, R_br · T_br)  [Lei 14.754/2023, Art. 2º]

```

O `REGISTRO` é o que alimenta o catálogo de auditoria:

```python
>>> len(REGISTRO)
16

```

## 9. Valeu a pena ter investido?

O `R_br` mistura o que a **aplicação** rendeu com o que o **câmbio** rendeu. A
apuração separa os dois, e a soma fecha exatamente:

```python
>>> print(apuracao.R_cc.valor)     # rendimento cambial (isento se parado)
BRL 2,000.00
>>> print(apuracao.R_eubr.valor)   # prêmio da aplicação, por fora do câmbio
BRL 1,200.00
>>> apuracao.R_cc.valor + apuracao.R_eubr.valor == apuracao.R_br.valor
True

```

`J_eu` é o juro da aplicação limpo de câmbio — o único número comparável com
outra aplicação em euros. Repare como ele difere do `J`, apurado em reais:

```python
>>> apuracao.J_eu.valor    # a aplicação rendeu 10% em euros
Decimal('0.1')
>>> apuracao.J.valor       # mas 32% em reais, graças ao câmbio
Decimal('0.32')

```

E a pergunta final: investir foi melhor do que ter deixado o dinheiro parado
numa conta não remunerada?

```python
>>> print(apuracao.V_inv.valor)
BRL 720.00
>>> apuracao.investir_compensou()
True

```

Nem sempre a resposta é sim. Aqui a aplicação rende **+1% em euros** — não deu
prejuízo — mas o euro sobe 60%, e o ganho cambial (que seria isento parado)
passa a pagar 15%:

```python
>>> contraintuitivo = ApuracaoResgate.de_cf(
...     I=brl("10000.00"),
...     F=brl("16160.00"),
...     C_i=Cambio(Decimal("5.00"), date(2024, 5, 2)),
...     C_f=Cambio(Decimal("8.00"), date(2025, 3, 10)),
... )
>>> contraintuitivo.J_eu.valor              # a aplicação rendeu
Decimal('0.01')
>>> print(contraintuitivo.R_eubr.valor)     # prêmio da aplicação
BRL 160.00
>>> print(contraintuitivo.IR_ef.valor)      # imposto sobre tudo, inclusive o câmbio
BRL 924.00
>>> print(contraintuitivo.V_inv.valor)      # parado teria rendido mais
BRL -764.00
>>> contraintuitivo.investir_compensou()
False

```

A leitura da Fórmula 16: investir só compensa se o prêmio da aplicação
(`R_eubr`) superar o imposto **inteiro** (`IR_ef`) — inclusive a parcela que
incide sobre o ganho cambial, isenta se o dinheiro estivesse parado.
