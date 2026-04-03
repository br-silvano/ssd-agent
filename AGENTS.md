# SSD Agent — Contexto Global

## Missão
Transformar um briefing bruto em artefatos de software auditáveis, seguindo a cadeia:
briefing → domain spec → contratos → testes → implementação → revisão.

## Regra fundamental
**Nunca escrever código sem antes produzir e persistir:**
1. `workspace/briefing/normalized.json`
2. `workspace/domain-spec/spec.md`
3. `workspace/contracts/openapi.yaml` (e schemas relacionados)
4. `workspace/tests/` (BDD + TDD)

## Stack alvo padrão
- Backend: Python + FastAPI + Celery
- Frontend: Next.js + React
- IA: LangChain + Claude
- DB: PostgreSQL + pgvector

## Gates HITL obrigatórios
- **Scope Freeze** → após Domain Spec (subagent: domain)
- **Contract Freeze** → após Contratos (subagent: contracts)
- **Implementation Freeze** → após Testes + primeira Implementação (subagent: implementation)

## Formato de artefatos
Sempre salvar artefatos em `workspace/<etapa>/` antes de prosseguir.
Usar structured output (JSON) nas etapas 1–3 para garantir consistência.

## Idioma
Responder sempre em português.

---

## Configuração do Zed

### Wiring (settings.json)

Em `~/.config/zed/settings.json`, adicione o SSD Agent como `agent_servers`:

```json
{
  "agent_servers": {
    "SSD Agent": {
      "type": "custom",
      "command": "/caminho/absoluto/para/ssd-agent/run_agent.sh",
      "args": ["-m", "ssd_agent"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      },
      "cwd": "/caminho/absoluto/para/ssd-agent"
    }
  }
}
```

> **Nota**: ajuste o `command` e `cwd` para o caminho absoluto onde o repositório foi clonado.
> O script `run_agent.sh` usa `$(dirname "$0")` para ser portável, mas o Zed exige paths absolutos.

### Como usar

1. Abra o painel do assistente (`Ctrl+?`)
2. Selecione **SSD Agent** no seletor de modelo
3. Cole o briefing do projeto diretamente no chat
4. O agente executa cada etapa e persiste os artefatos em `workspace/`
5. Nos três gates, revise o artefato apresentado e responda:
   - `aprovar` — continua o pipeline
   - qualquer texto — vira feedback para o subagente retrabalhar

### Modelo e permissões recomendadas

```json
{
  "agent": {
    "inline_assistant_model": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-6-latest",
      "enable_thinking": false
    },
    "tool_permissions": {
      "default": "allow"
    }
  }
}
```

### Troubleshooting

| Problema | Causa provável |
|----------|---------------|
| Agente não inicia | `ANTHROPIC_API_KEY` não definida no `.env` ou no `env` do Zed |
| `run_agent.sh` falha | `.venv/` não existe — rode `make dev` primeiro |
| Pipeline trava no gate | Responda `aprovar` ou forneça feedback no chat |

---

## Comandos

### Instalação
```bash
make install          # pip install -e ".[dev]"
make dev              # instala + copia .env.example → .env
```

### Lint e Type Check
```bash
make lint             # ruff check src/ && mypy src/
ruff check src/       # apenas lint
mypy src/             # apenas type check
```

### Testes
```bash
make test             # pytest workspace/tests/ -v --tb=short
pytest tests/test_foo.py -v           # teste individual
pytest tests/test_foo.py::test_bar -v # teste específico
pytest -k "keyword" -v                # testes por padrão no nome
```

### Execução
```bash
make run-cli                          # CLI interativo
make run-cli-file BRIEFING=brief.txt  # CLI com arquivo
make run-acp                          # servidor ACP (stdio para Zed)
python -m ssd_agent.cli               # equivalente a make run-cli
python -m ssd_agent                   # equivalente a make run-acp
```

### Limpeza
```bash
make clean-workspace  # limpa e recria workspace/
```

---

## Code Style

### Imports
- Ordem: stdlib → third-party → local (separados por linha em branco)
- Usar `from __future__ import annotations` como primeira linha em todos os módulos
- Preferir imports explícitos: `from pydantic import BaseModel, Field`
- Imports locais relativos ao pacote: `from ..schemas import DomainSpec`

### Formatação
- Ruff como linter e formatter (configuração padrão)
- 4 espaços para indentação, sem tabs
- Linhas com tamanho razoável (deixar ruff decidir)
- Aspas duplas para strings, aspas simples apenas quando necessário

### Tipagem
- Type hints obrigatórios em assinaturas de funções e métodos
- Usar `Optional[X]` ou `X | None` (Python 3.10+) para valores opcionais
- `dict[str, Any]` para dicts sem schema fixo
- `list[X]` ao invés de `List[X]` (builtin generics, Python 3.9+)
- Pydantic v2 para modelos de dados com validação

### Naming Conventions
- **Módulos/pacotes**: `snake_case` (`subagents.py`, `deep_agents/`)
- **Classes**: `PascalCase` (`SSDAgent`, `NormalizedBriefing`, `GateInput`)
- **Funções/métodos**: `snake_case` (`normalize_briefing`, `_is_approval`)
- **Variáveis privadas**: prefixo `_` (`_sessions`, `_WORKSPACE`, `_MODEL`)
- **Constantes**: `UPPER_SNAKE_CASE` (`_APPROVAL_TOKENS`, `ALL_SUBAGENTS`)
- **Artefatos**: `snake_case` com extensão adequada (`normalized.json`, `spec.md`)

### Error Handling
- Logging via `logging` module, nunca `print` para erros em produção
- Em modo ACP (stdin não-tty), log vai para `stderr` para não poluir o protocolo
- Usar `sys.excepthook` para capturar erros fatais no entrypoint
- Pydantic valida schemas automaticamente — deixar exceções propagarem
- CLI usa `sys.exit(1)` para erros de input inválido

### Estrutura de Código
- Docstrings obrigatórias em classes públicas e funções de módulo
- Docstring de módulo na primeira linha descrevendo o propósito
- Classes com atributos de tipo declarados (`_conn: Client`)
- Métodos privados com `_` prefix quando não fazem parte da API pública
- Singletons de módulo para recursos compartilhados (`supervisor`, `_checkpointer`)

### Pydantic Models
- Usar `Field(description=...)` para documentar campos
- `default_factory=list` para listas vazias (nunca `=[]`)
- `model_dump_json(indent=2)` para serialização legível
- `model_dump()` para dicts Python

### Convenções de Testes
- Arquivos: `test_<modulo>_<acao>.py`
- Funções: `test_<entidade>_<acao>_<contexto>`
- pytest-asyncio para testes async
- `--tb=short` para output conciso
- Testes gerados em `workspace/tests/` (não versionados)

### Git
- `.env` nunca commitado — usar `.env.example` como template
- `workspace/` ignorado exceto `.gitkeep` para estrutura
- Commits em português, focados no "porquê" não no "o quê"
