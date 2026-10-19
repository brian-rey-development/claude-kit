# Every gate CI runs. `make check` before each commit; `make format` fixes what it can.
PY := uvx --python 3.9 --with-requirements requirements.txt

.PHONY: check lint types test test-shell test-mods format

check: lint types test test-shell test-mods

lint:
	uvx ruff check .
	uvx ruff format --check .

types:
	$(PY) --with pytest pyright

test:
	$(PY) --with pytest pytest

test-shell:
	shellcheck install.sh bin/kit statusline/statusline.sh statusline/subagents.sh

test-mods:
	./bin/kit cards
	for mod in mods/*/; do claude plugin validate "$$mod" && claude plugin test "$$mod" || exit 1; done

format:
	uvx ruff format .
	uvx ruff check --fix .
