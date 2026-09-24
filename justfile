# Comandos do projeto. `just` sem argumentos lista tudo.
#
# O uv cuida do ambiente: não é preciso ativar a .venv antes.
# VIRTUAL_ENV é limpo porque o pyenv deixa a sua própria versão ativa no shell,
# e o uv avisaria, a cada chamada, que vai ignorá-la em favor da .venv daqui.

export VIRTUAL_ENV := ""

# Lista as receitas disponíveis
default:
    @just --list --unsorted

# Cria/atualiza a .venv com as dependências de desenvolvimento
sync:
    uv sync --all-extras

# Aceita argumentos do pytest: just test -q -k "formula_12 or compensacao"
[doc("Roda a suíte inteira: unit, propriedades, simbólico, cenários e doctests")]
[positional-arguments]
test *ARGS:
    uv run pytest "$@"

# Verifica estilo e formatação, sem alterar nada
lint:
    uv run ruff check .
    uv run ruff format --check .

# Corrige o que o ruff sabe corrigir e formata o código
fmt:
    uv run ruff check . --fix
    uv run ruff format .

# Verificação de tipos em modo estrito
types:
    uv run mypy

# Aceita um destino alternativo: just docs /tmp/previa.md
[doc("Regenera docs/auditoria/ a partir do REGISTRO (há teste que cobra isso)")]
[positional-arguments]
docs *ARGS:
    uv run python scripts/gerar_catalogo.py "$@"

# Tudo que um CI cobraria: lint, tipos e testes
check: lint types test

# Apaga caches de ferramentas e bytecode
clean:
    rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis
    find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
