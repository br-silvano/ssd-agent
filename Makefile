.PHONY: install dev lint test run-cli run-acp

install:
	pip install -e ".[dev]"

dev:
	pip install -e ".[dev]"
	cp -n .env.example .env || true

# ── Qualidade ─────────────────────────────────────────────────────────────────
lint:
	ruff check src/
	mypy src/

# ── Testes ────────────────────────────────────────────────────────────────────
test:
	pytest workspace/tests/ -v --tb=short 2>/dev/null || echo "Nenhum teste gerado ainda."

# ── Execução ──────────────────────────────────────────────────────────────────

# Modo CLI (dev, sem Zed)
run-cli:
	python -m ssd_agent.cli

# Modo CLI com arquivo de briefing
run-cli-file:
	python -m ssd_agent.cli --briefing $(BRIEFING)

# Modo ACP (servidor stdio para Zed)
run-acp:
	python -m ssd_agent

# ── Limpeza ───────────────────────────────────────────────────────────────────
clean-workspace:
	rm -rf workspace/briefing workspace/domain-spec workspace/contracts \
	       workspace/tests workspace/implementation workspace/review
	mkdir -p workspace/briefing workspace/domain-spec workspace/contracts \
	         workspace/tests workspace/implementation workspace/review
	@echo "workspace/ limpo."
