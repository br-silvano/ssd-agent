"""
ACP Bridge — expõe o pipeline SSD como agente ACP para o Zed.

API real do SDK (agentclientprotocol/python-sdk >=0.7):
  - Agent base class com on_connect / initialize / new_session / prompt
  - Streaming via: await self._conn.session_update(session_id, update, source)
  - update_agent_message(text_block(text)) para chunks de texto
  - return PromptResponse(stop_reason="end_turn") para encerrar o turno
  - run_agent(agent_instance) como entrypoint

Fluxo de HITL via ACP:
  1. Supervisor atinge um gate → invoke retorna com __interrupt__
  2. ACPBridge envia update com mensagem de revisão
  3. Próximo prompt do usuário é roteado como Command(resume=...)
  4. Pipeline continua a partir do ponto de pausa
"""

from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from typing import Any

from acp import (
    PROTOCOL_VERSION,
    Agent,
    InitializeResponse,
    NewSessionResponse,
    PromptResponse,
    run_agent,
    text_block,
    update_agent_message,
)
from acp.interfaces import Client
from acp.schema import (
    AgentCapabilities,
    AgentMessageChunk,
    ClientCapabilities,
    HttpMcpServer,
    Implementation,
    McpServerStdio,
    SseMcpServer,
)
from langgraph.types import Command

from .deep_agents.supervisor import supervisor

# Configura logging para ACP (evita stdout pollution)
if not sys.stdin.isatty():
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s: %(message)s",
        stream=sys.stderr,
    )

# Tokens de aprovação reconhecidos
_APPROVAL_TOKENS = {"aprovar", "approve", "sim", "ok", "continuar", "prosseguir", "yes"}
_REJECTION_TOKENS = {"rejeitar", "reject", "não", "nao", "no", "voltar", "feedback"}

_AGENT_SOURCE = "ssd-agent"


def _is_approval(text: str) -> bool:
    lower = text.strip().lower()
    return any(token in lower for token in _APPROVAL_TOKENS)


def _extract_feedback(text: str) -> str:
    for token in _REJECTION_TOKENS:
        text = text.replace(token, "").strip()
    return text.strip()


def _extract_last_ai_message(result: dict) -> str:
    messages = result.get("messages", [])
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or (
            msg.get("role", "") if isinstance(msg, dict) else ""
        )
        if role in ("ai", "assistant"):
            return (
                getattr(msg, "content", None)
                or (msg.get("content", "") if isinstance(msg, dict) else "")
                or ""
            )
    return ""


class SSDAgent(Agent):
    """
    Agente ACP que expõe o pipeline SSD para editores compatíveis (Zed).

    Estado por sessão (keyed by session_id):
      thread_id        — identifica a thread no checkpointer do LangGraph
      awaiting_gate    — True quando aguardando resposta de aprovação HITL
      gate_name        — nome do gate atual para exibição
    """

    _conn: Client

    def __init__(self) -> None:
        super().__init__()
        # dict[session_id, dict] — estado por sessão ativa
        self._sessions: dict[str, dict] = {}

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_connect(self, conn: Client) -> None:
        self._conn = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: ClientCapabilities | None = None,
        client_info: Implementation | None = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=PROTOCOL_VERSION,
            agent_capabilities=AgentCapabilities(),
            agent_info=Implementation(
                name="ssd-agent",
                title="SSD Agent",
                version="0.1.0",
            ),
        )

    async def new_session(
        self,
        cwd: str,
        mcp_servers: list[HttpMcpServer | SseMcpServer | McpServerStdio] | None,
        session_id: str = "",
        **kwargs: Any,
    ) -> NewSessionResponse:
        thread_id = (
            f"ssd-{cwd.replace('/', '-').replace(chr(92), '-')}"
            if cwd
            else "ssd-default"
        )
        actual_session_id = session_id or str(uuid.uuid4())
        self._sessions[actual_session_id] = {
            "thread_id": thread_id,
            "awaiting_gate": False,
            "gate_name": "",
        }
        return NewSessionResponse(session_id=actual_session_id)

    # ── Processamento principal ───────────────────────────────────────────────

    async def prompt(
        self,
        prompt: list,
        session_id: str,
        message_id: str | None = None,
        **kwargs: Any,
    ) -> PromptResponse:
        # Extrai texto da mensagem
        user_text = ""
        for block in prompt:
            if isinstance(block, dict):
                user_text += block.get("text", "")
            else:
                user_text += getattr(block, "text", "")
        user_text = user_text.strip()

        # Garante estado da sessão
        state = self._sessions.setdefault(
            session_id,
            {
                "thread_id": "ssd-default",
                "awaiting_gate": False,
                "gate_name": "",
            },
        )
        config = {"configurable": {"thread_id": state["thread_id"]}}

        # ── Caminho 1: resposta a gate HITL ──────────────────────────────────
        if state["awaiting_gate"]:
            return await self._resume_gate(user_text, session_id, state, config)

        # ── Caminho 2: novo briefing / continuação de pipeline ────────────────
        return await self._invoke_supervisor(user_text, session_id, state, config)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _send(self, session_id: str, text: str) -> None:
        """Envia um chunk de texto via session_update."""
        chunk = update_agent_message(text_block(text))
        await self._conn.session_update(
            session_id=session_id,
            update=chunk,
            source=_AGENT_SOURCE,
        )

    async def _invoke_supervisor(
        self,
        message: str,
        session_id: str,
        state: dict,
        config: dict,
    ) -> PromptResponse:
        await self._send(session_id, "⏳ Iniciando pipeline SSD...\n")

        result = await asyncio.to_thread(
            supervisor.invoke,
            {"messages": [{"role": "user", "content": message}]},
            config,
        )

        return await self._process_result(result, session_id, state)

    async def _resume_gate(
        self,
        user_response: str,
        session_id: str,
        state: dict,
        config: dict,
    ) -> PromptResponse:
        state["awaiting_gate"] = False

        if _is_approval(user_response):
            await self._send(
                session_id,
                f"✅ {state['gate_name']} aprovado. Continuando pipeline...\n",
            )
            decision = [{"type": "approve"}]
        else:
            feedback = _extract_feedback(user_response) or user_response
            await self._send(
                session_id, "↩️ Feedback registrado. Retornando ao agente anterior...\n"
            )
            decision = [{"type": "reject", "message": feedback}]

        result = await asyncio.to_thread(
            supervisor.invoke,
            Command(resume={"decisions": decision}),
            config,
        )

        return await self._process_result(result, session_id, state)

    async def _process_result(
        self,
        result: dict,
        session_id: str,
        state: dict,
    ) -> PromptResponse:
        """Processa resultado do supervisor — detecta gates HITL ou resposta final."""

        if "__interrupt__" in result:
            interrupt = result["__interrupt__"]
            gate_value = interrupt[0].value if interrupt else {}
            gate_text = gate_value if isinstance(gate_value, str) else str(gate_value)

            if "SCOPE FREEZE" in gate_text:
                gate_name = "Scope Freeze"
            elif "CONTRACT FREEZE" in gate_text:
                gate_name = "Contract Freeze"
            else:
                gate_name = "Implementation Freeze"

            state["awaiting_gate"] = True
            state["gate_name"] = gate_name

            review_msg = (
                f"\n⏸ **{gate_name}**\n\n"
                f"{gate_text}\n\n"
                "---\n"
                "**Revise o artefato acima.** Responda:\n"
                "- `aprovar` — para continuar o pipeline\n"
                "- qualquer outro texto — como feedback para o agente retrabalhar\n"
            )
            await self._send(session_id, review_msg)
            return PromptResponse(stop_reason="end_turn")

        final_text = _extract_last_ai_message(result)
        if final_text:
            await self._send(session_id, final_text)

        return PromptResponse(stop_reason="end_turn")


# ── Entrypoint ────────────────────────────────────────────────────────────────


def _handle_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    sys.stderr.write(f"FATAL: {exc_type.__name__}: {exc_value}\n")


if not sys.stdin.isatty():
    sys.excepthook = _handle_exception


async def main() -> None:
    await run_agent(SSDAgent())


if __name__ == "__main__":
    asyncio.run(main())
