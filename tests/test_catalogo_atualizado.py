"""O catálogo de auditoria versionado precisa refletir o código atual."""

from pathlib import Path

import pytest
from scripts.gerar_catalogo import DESTINO_PADRAO, gerar

RAIZ = Path(__file__).resolve().parents[1]


def test_catalogo_versionado_esta_em_dia() -> None:
    caminho = RAIZ / DESTINO_PADRAO
    if not caminho.exists():  # pragma: no cover - só numa árvore incompleta
        pytest.skip(f"catálogo não encontrado em {caminho}")
    assert caminho.read_text(encoding="utf-8") == gerar(), (
        "catálogo desatualizado: rode `uv run python scripts/gerar_catalogo.py`"
    )
