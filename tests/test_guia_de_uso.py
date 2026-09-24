"""O guia de uso roda como teste, para não poder envelhecer (seção 9.2)."""

import doctest
from pathlib import Path

import pytest

GUIA = Path(__file__).resolve().parents[1] / "docs" / "desenvolvimento" / "guia-de-uso.md"


def test_exemplos_do_guia_de_uso() -> None:
    if not GUIA.exists():  # pragma: no cover - só numa árvore incompleta
        pytest.skip(f"guia não encontrado em {GUIA}")
    resultado = doctest.testfile(
        str(GUIA),
        module_relative=False,
        optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
        verbose=False,
    )
    assert resultado.attempted > 0, "nenhum exemplo foi coletado do guia"
    assert resultado.failed == 0, f"{resultado.failed} exemplo(s) do guia falharam"
