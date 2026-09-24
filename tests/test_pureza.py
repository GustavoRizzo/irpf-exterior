"""A pureza da biblioteca é verificada, não apenas prometida.

O núcleo não depende de dados nem de conexões externas (seção 3 da
arquitetura). Isso é fácil de escrever num README e fácil de quebrar sem
querer — um `import requests` "só para testar" passa despercebido numa
revisão. Este módulo transforma a regra em teste.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

NUCLEO = Path(__file__).resolve().parents[1] / "src" / "irpf_exterior"

MODULOS_PROIBIDOS = frozenset(
    {
        # rede
        "socket",
        "ssl",
        "http",
        "urllib",
        "urllib3",
        "ftplib",
        "smtplib",
        "requests",
        "httpx",
        "aiohttp",
        "urllib.request",
        # arquivo, processo e ambiente
        "os",
        "io",
        "pathlib",
        "shutil",
        "tempfile",
        "glob",
        "subprocess",
        "sqlite3",
        "pickle",
        "shelve",
        "csv",
        "configparser",
        # não determinismo
        "random",
        "secrets",
        "time",
        "uuid",
    }
)
"""Qualquer um destes transforma um cálculo reproduzível num cálculo datado."""

CHAMADAS_PROIBIDAS = frozenset({"open", "input", "print", "eval", "exec", "compile"})
"""Efeito colateral direto dentro do núcleo."""

ATRIBUTOS_PROIBIDOS = frozenset({"today", "now", "utcnow", "fromtimestamp"})
"""O relógio é do consumidor: datas chegam por parâmetro (princípio 4.1)."""

# `simbolico.py` é o único módulo que pode importar uma dependência externa, e
# só a do extra opcional `simbolico`, que serve para gerar documentação.
EXCECOES_DE_IMPORT: dict[str, frozenset[str]] = {"simbolico.py": frozenset({"sympy"})}


MODULOS = tuple(sorted(NUCLEO.rglob("*.py")))
"""Todos os arquivos Python da biblioteca, resolvidos na coleta."""


def _raiz(nome: str) -> str:
    return nome.split(".", 1)[0]


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda p: p.name)
def test_nucleo_nao_importa_nada_proibido(modulo: Path) -> None:
    """Nenhum módulo do núcleo toca rede, disco, processo ou aleatoriedade."""
    permitidos = EXCECOES_DE_IMPORT.get(modulo.name, frozenset())
    arvore = ast.parse(modulo.read_text(encoding="utf-8"), filename=str(modulo))

    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(_raiz(alias.name) for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            importados.add(_raiz(no.module))

    proibidos = (importados & MODULOS_PROIBIDOS) - permitidos
    assert not proibidos, (
        f"{modulo.name} importa {sorted(proibidos)}. O núcleo recebe tudo por "
        "parâmetro; buscar o dado é trabalho do consumidor."
    )


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda p: p.name)
def test_nucleo_nao_tem_efeito_colateral(modulo: Path) -> None:
    """Sem `open`, `print` ou leitura do relógio dentro da biblioteca."""
    arvore = ast.parse(modulo.read_text(encoding="utf-8"), filename=str(modulo))

    encontrados: list[str] = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        alvo = no.func
        if isinstance(alvo, ast.Name) and alvo.id in CHAMADAS_PROIBIDAS:
            encontrados.append(f"{alvo.id}() na linha {no.lineno}")
        elif isinstance(alvo, ast.Attribute) and alvo.attr in ATRIBUTOS_PROIBIDOS:
            encontrados.append(f".{alvo.attr}() na linha {no.lineno}")

    assert not encontrados, f"{modulo.name} tem efeito colateral: {encontrados}"


def test_biblioteca_nao_declara_dependencia_de_runtime() -> None:
    """O pacote instalado não arrasta nada consigo.

    O extra `simbolico` existe só para gerar documentação e rodar os testes
    simbólicos; quem instala a biblioteca para calcular imposto não precisa
    dele.
    """
    import tomllib

    pyproject = NUCLEO.parents[1] / "pyproject.toml"
    projeto = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]

    assert projeto["dependencies"] == [], (
        f"dependências de runtime apareceram: {projeto['dependencies']}"
    )
    assert set(projeto["optional-dependencies"]) == {"simbolico"}


def test_portas_declaram_contrato_sem_implementar_nada() -> None:
    """`portas.py` pode existir numa lib pura porque só descreve formatos.

    Declarar o formato de uma cotação não é buscar uma cotação. Se este
    módulo passar a importar algo de fora, a regra foi quebrada.
    """
    portas = NUCLEO / "portas.py"
    arvore = ast.parse(portas.read_text(encoding="utf-8"), filename=str(portas))

    externos = {
        _raiz(no.module)
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module and no.level == 0
    }
    permitidos = {"__future__", "datetime", "typing", "irpf_exterior"}
    assert externos <= permitidos, f"portas.py importa {sorted(externos - permitidos)}"

    corpos = [
        no
        for classe in ast.walk(arvore)
        if isinstance(classe, ast.ClassDef)
        for no in classe.body
        if isinstance(no, ast.FunctionDef)
    ]
    for metodo in corpos:
        significativos = [n for n in metodo.body if not isinstance(n, ast.Expr)]
        assert not significativos, f"porta {metodo.name} tem implementação"
