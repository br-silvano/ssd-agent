"""
Supervisor Agent — orquestra o pipeline SSD completo.

Fluxo:
  briefing → normalize → [domain] → SCOPE FREEZE
           → [contracts]          → CONTRACT FREEZE
           → [tests] → [implementation] → IMPLEMENTATION FREEZE
           → [review] → done

Os gates HITL são implementados como ferramentas com interrupt_on,
o que pausa a execução e aguarda Command(resume=...) do caller (ACPBridge).
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if not sys.stdin.isatty():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(name)s: %(message)s",
        stream=sys.stderr,
    )

load_dotenv("/home/debian/projects/ssd-agent/.env")
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel

from ..schemas import NormalizedBriefing
from .subagents import ALL_SUBAGENTS

_MODEL = os.getenv("SSD_MODEL", "claude-sonnet-4-20250514")

# ─────────────────────────────────────────────────────────────────────────────
# Shared state
# ─────────────────────────────────────────────────────────────────────────────

_checkpointer = MemorySaver()
_store = InMemoryStore()
_WORKSPACE = Path(os.getenv("SSD_WORKSPACE", "workspace"))


# ─────────────────────────────────────────────────────────────────────────────
# Gate tools — interrupt_on vai pausar aqui aguardando aprovação humana
# ─────────────────────────────────────────────────────────────────────────────

class GateInput(BaseModel):
    resumo: str
    artefato_path: str


@tool(args_schema=GateInput)
def scope_freeze(resumo: str, artefato_path: str) -> str:
    """
    Gate 1 — Scope Freeze.
    Pausa o pipeline após a Domain Spec para revisão humana.
    Apresenta o resumo da spec e aguarda aprovação ou feedback.
    """
    return f"[SCOPE FREEZE] Domain Spec em: {artefato_path}\n\n{resumo}"


@tool(args_schema=GateInput)
def contract_freeze(resumo: str, artefato_path: str) -> str:
    """
    Gate 2 — Contract Freeze.
    Pausa o pipeline após os contratos para revisão humana.
    """
    return f"[CONTRACT FREEZE] Contratos em: {artefato_path}\n\n{resumo}"


@tool(args_schema=GateInput)
def implementation_freeze(resumo: str, artefato_path: str) -> str:
    """
    Gate 3 — Implementation Freeze.
    Pausa o pipeline após testes + implementação inicial para revisão humana.
    """
    return f"[IMPLEMENTATION FREEZE] Implementação em: {artefato_path}\n\n{resumo}"


# ─────────────────────────────────────────────────────────────────────────────
# Briefing normalization tool — etapa 1 inline no supervisor
# ─────────────────────────────────────────────────────────────────────────────

class BriefingInput(BaseModel):
    briefing_bruto: str


@tool(args_schema=BriefingInput)
def normalize_briefing(briefing_bruto: str) -> str:
    """
    Normaliza o briefing bruto em JSON estruturado e salva em
    workspace/briefing/normalized.json.
    Usa structured output via Anthropic para garantir consistência.
    """
    llm = ChatAnthropic(model=_MODEL)
    structured_llm = llm.with_structured_output(NormalizedBriefing)

    result: NormalizedBriefing = structured_llm.invoke(
        f"""Normalize o seguinte briefing em um objeto estruturado.
Seja preciso: extraia apenas o que está explícito ou claramente implícito.
Liste perguntas_em_aberto para qualquer ambiguidade.

BRIEFING:
{briefing_bruto}"""
    )

    out_path = _WORKSPACE / "briefing" / "normalized.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    return f"Briefing normalizado salvo em {out_path}.\n\n{result.model_dump_json(indent=2)}"


# ─────────────────────────────────────────────────────────────────────────────
# Supervisor factory
# ─────────────────────────────────────────────────────────────────────────────

SUPERVISOR_PROMPT = """Você é o Supervisor do pipeline SSD (Spec-Driven Development).

Seu trabalho é coordenar a linha de produção de artefatos, garantindo que
cada etapa seja concluída e persistida antes de avançar para a próxima.

## Sequência obrigatória

1. **normalize_briefing** — normaliza o briefing recebido e salva em workspace/briefing/
2. **task(domain)** — gera Domain Spec completa; salva em workspace/domain-spec/
3. **scope_freeze** — apresenta resumo da spec; aguarda aprovação humana
4. **task(contracts)** — gera openapi.yaml + schemas + errors.md; salva em workspace/contracts/
5. **contract_freeze** — apresenta resumo dos contratos; aguarda aprovação humana
6. **task(tests)** — gera BDD + TDD; salva em workspace/tests/
7. **task(implementation)** — implementa guiado por contratos + testes; salva em workspace/implementation/
8. **implementation_freeze** — apresenta resumo; aguarda aprovação humana
9. **task(review)** — refatora, documenta, gera changelog; salva em workspace/review/

## Regras
- Nunca pule etapas.
- Se um gate retornar feedback (não aprovação), retorne ao agente anterior com o feedback.
- Após o gate 3 aprovado, o pipeline está completo — apresente um resumo de todos os artefatos.
- Responda sempre em português.
"""


def create_supervisor() -> object:
    """
    Cria e retorna o Supervisor Agent configurado com:
    - FilesystemBackend + StoreBackend para persistência
    - 5 subagentes especializados
    - 3 gates HITL com interrupt_on
    - Skills por domínio
    """
    return create_deep_agent(
        name="ssd-supervisor",
        model=_MODEL,
        system_prompt=SUPERVISOR_PROMPT,
        tools=[normalize_briefing, scope_freeze, contract_freeze, implementation_freeze],
        subagents=ALL_SUBAGENTS,
        backend=FilesystemBackend(root_dir=".", virtual_mode=False),
        skills=["./skills/"],
        interrupt_on={
            "scope_freeze": True,
            "contract_freeze": True,
            "implementation_freeze": True,
        },
        checkpointer=_checkpointer,
        store=_store,
    )


# Singleton — criado uma vez e reutilizado pela ACPBridge
supervisor = create_supervisor()
