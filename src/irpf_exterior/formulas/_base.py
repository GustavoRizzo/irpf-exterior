"""O tipo `Formula`, o decorador `@formula` e o `REGISTRO`.

Uma fórmula é uma função pura sobre valores do domínio. O decorador a envolve
num objeto que conhece os próprios metadados, desembrulha entradas rastreadas
e devolve o resultado já rastreado — de modo que a auditoria (dor 2.4) é
consequência de chamar a fórmula, não trabalho extra de quem chama.

**Limitação de tipagem (seção 4.6 da arquitetura).** Uma `Formula` guarda uma
função de aridade arbitrária (`Callable[..., T]`) e é chamada com
`**entradas: object`, porque cada entrada pode chegar crua ou embrulhada num
`Calculado`. Isso custa a verificação estática dos *argumentos* de uma fórmula
decorada — o retorno continua tipado, e os tipos das entradas são conferidos em
execução pelo `Money`. Este é o único módulo do domínio onde `Any` é permitido,
e a exceção está registrada no `pyproject.toml`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from irpf_exterior.rastreio import Calculado

__all__ = ["REGISTRO", "Formula", "formula"]

_REGISTRO_MUTAVEL: dict[str, Formula[object]] = {}

REGISTRO: Mapping[str, Formula[object]] = MappingProxyType(_REGISTRO_MUTAVEL)
"""Catálogo das fórmulas, preenchido na importação e só lido depois.

É a fonte do catálogo de auditoria (seção 9.1): a documentação é gerada a
partir do código, e não mantida em paralelo com ele.
"""


@dataclass(frozen=True, slots=True)
class Formula[T]:
    """Uma fórmula do documento de referência, com os seus metadados.

    Chamar uma `Formula` exige argumentos **nomeados**: numa expressão com
    `I`, `F`, `C_i` e `C_f`, a ordem posicional é exatamente o tipo de erro
    que produz um número plausível e errado (dor 2.1).
    """

    nome: str
    ref: str
    expr: str
    latex: str
    calcular: Callable[..., T]
    lei: str | None = None

    @property
    def descricao(self) -> str:
        """Texto que aparece na árvore de auditoria (ex.: `Fórmula 6: R_br = F - I`)."""
        return f"{self.ref}: {self.expr}"

    def __call__(self, **entradas: object) -> Calculado[T]:
        """Calcula a fórmula e devolve o resultado rastreado.

        Cada entrada pode ser um valor cru ou um `Calculado`; no segundo caso
        o valor é desembrulhado antes do cálculo e o `Calculado` original é
        preservado como ramo da árvore de proveniência.
        """
        argumentos = {
            nome: (valor.valor if isinstance(valor, Calculado) else valor)
            for nome, valor in entradas.items()
        }
        return Calculado(
            valor=self.calcular(**argumentos),
            descricao=self.descricao,
            fonte=self.lei,
            entradas=tuple(entradas.items()),
        )

    def __str__(self) -> str:
        """A descrição da fórmula, com a base legal quando houver."""
        return self.descricao if self.lei is None else f"{self.descricao}  [{self.lei}]"


def formula[T](
    *,
    nome: str,
    ref: str,
    expr: str,
    latex: str,
    lei: str | None = None,
) -> Callable[[Callable[..., T]], Formula[T]]:
    """Transforma uma função pura numa `Formula` registrada no `REGISTRO`.

    Args:
        nome: o nome da variável no glossário (ex.: `IR_br`).
        ref: a referência no documento de origem (ex.: `Fórmula 11`).
        expr: a expressão em texto legível.
        latex: a mesma expressão em LaTeX, para a documentação de auditoria.
        lei: a base legal, quando a fórmula decorre diretamente de uma.

    Raises:
        ValueError: já existe uma fórmula registrada com esse nome.
    """

    def decorar(funcao: Callable[..., T]) -> Formula[T]:
        objeto = Formula(nome=nome, ref=ref, expr=expr, latex=latex, calcular=funcao, lei=lei)
        if nome in _REGISTRO_MUTAVEL:
            raise ValueError(f"Fórmula {nome!r} registrada duas vezes.")
        _REGISTRO_MUTAVEL[nome] = objeto
        return objeto

    return decorar
