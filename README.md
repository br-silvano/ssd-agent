# SSD Agent

Pipeline **Spec-Driven Development** auditável, exposto como agente ACP para o editor **Zed**.

## Arquitetura

```
Zed (ACP client)
  ↓ JSON-RPC 2.0 via stdio
ACPBridge (agent.py)         ← interface ACP, streaming, HITL routing
  ↓ invoke / Command(resume)
SupervisorAgent              ← Deep Agents harness, orquestração do pipeline
  ↓ task()
  ├── domain                 ← Domain Spec
  ├── contracts              ← OpenAPI + schemas + errors
  ├── tests                  ← BDD + TDD
  ├── implementation         ← Código guiado por contrato + testes
  └── review                 ← Refactor + docs + changelog
```

### Gates HITL

| Gate | Depois de | Como responder |
|------|-----------|----------------|
| Scope Freeze | Domain Spec | `aprovar` ou feedback de texto |
| Contract Freeze | Contratos | `aprovar` ou feedback de texto |
| Implementation Freeze | Implementação | `aprovar` ou feedback de texto |

---

## Setup

```bash
# 1. Clonar e instalar
git clone https://github.com/br-silvano/ssd-agent
cd ssd-agent
pip install -e .

# 2. Variáveis de ambiente
cp .env.example .env
# editar .env com ANTHROPIC_API_KEY

# 3. Testar o agente standalone
python -m ssd_agent
```

---

## Wiring com Zed

Em `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
      "SSD Agent": {
          "type": "custom",
          "command": "/home/debian/projects/ssd-agent/run_agent.sh",
          "args": ["-m", "ssd_agent"],
          "env": {
              "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
          },
          "cwd": "/home/debian/projects/ssd-agent"
      }
  }
}
```

---

## Como usar no Zed

1. Abra o painel do assistente (`Ctrl+?`)
2. Cole o briefing do projeto diretamente no chat
3. O agente executa cada etapa e persiste os artefatos em `workspace/`
4. Nos três gates, revise o artefato apresentado e responda:
   - `aprovar` — continua o pipeline
   - qualquer texto — vira feedback para o subagente retrabalhar

---

## Estrutura de artefatos gerados

```
workspace/
├── briefing/
│   └── normalized.json          # Etapa 1
├── domain-spec/
│   ├── spec.md                  # Etapa 2 — legível
│   └── spec.json                # Etapa 2 — para o próximo agente
├── contracts/
│   ├── openapi.yaml             # Etapa 3
│   ├── schemas/                 # JSON schemas por entidade
│   ├── errors.md                # Catálogo de erros
│   └── manifest.json            # Índice de contratos
├── tests/
│   ├── bdd/                     # .feature por caso de uso
│   ├── unit/                    # pytest unitários
│   ├── integration/             # pytest de integração
│   └── coverage_matrix.md       # regra → test IDs
├── implementation/
│   ├── src/                     # Código fonte
│   └── gaps.md                  # Gaps contrato↔testes
└── review/
    ├── inconsistencies.md
    ├── TECHNICAL_DOCS.md
    ├── CHANGELOG.md
    └── suggestions.md
```

---

## Skills disponíveis

| Skill | Carregada por |
|-------|---------------|
| `domain-spec` | domain subagent |
| `api-contract` | contracts subagent |
| `bdd-tdd` | tests subagent |
| `implementation` | implementation subagent |
| `review` | review subagent |

Skills são carregadas progressivamente — só entram no contexto quando o subagente relevante está ativo.
