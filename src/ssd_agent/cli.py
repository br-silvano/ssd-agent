"""
CLI standalone — roda o pipeline SSD direto no terminal, sem Zed nem ACP.

Útil para:
  - Desenvolvimento e debug do pipeline
  - CI/CD pipelines que não usam editor
  - Teste de novos briefings antes de expor via ACP

Uso:
  python -m ssd_agent.cli                         # modo interativo
  python -m ssd_agent.cli --briefing brief.txt    # a partir de arquivo
  python -m ssd_agent.cli --thread meu-projeto    # retoma sessão existente
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from langgraph.types import Command

from .deep_agents.supervisor import supervisor

# Tokens de aprovação reconhecidos pelo CLI
_APPROVAL_TOKENS = {"aprovar", "approve", "sim", "ok", "continuar", "yes"}


def _is_approval(text: str) -> bool:
    return any(token in text.strip().lower() for token in _APPROVAL_TOKENS)


def _print_separator(label: str = "") -> None:
    width = 70
    if label:
        pad = (width - len(label) - 2) // 2
        print(f"\n{'─' * pad} {label} {'─' * pad}\n")
    else:
        print(f"\n{'─' * width}\n")


def _extract_last_message(result: dict) -> str:
    messages = result.get("messages", [])
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or (msg.get("role", "") if isinstance(msg, dict) else "")
        if role in ("ai", "assistant"):
            content = getattr(msg, "content", None) or (msg.get("content", "") if isinstance(msg, dict) else "")
            return content or ""
    return ""


def run(briefing: str, thread_id: str = "cli-session") -> None:
    """
    Executa o pipeline SSD completo com interação HITL via stdin/stdout.

    Args:
        briefing: Texto bruto do briefing
        thread_id: Identificador da sessão (permite retomar)
    """
    config = {"configurable": {"thread_id": thread_id}}
    awaiting_gate = False
    gate_name = ""

    print(f"\n🚀  SSD Pipeline — thread: {thread_id}")
    _print_separator()

    # ── Primeira invocação: briefing → pipeline ───────────────────────────
    print("⏳ Iniciando pipeline...\n")
    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": briefing}]},
        config,
    )

    while True:
        # ── Gate HITL detectado ───────────────────────────────────────────
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

            awaiting_gate = True
            _print_separator(f"⏸  {gate_name}")
            print(gate_text)
            _print_separator()
            print("Digite 'aprovar' para continuar ou forneça feedback:\n> ", end="", flush=True)

            user_response = sys.stdin.readline().strip()

            if _is_approval(user_response):
                print(f"\n✅ {gate_name} aprovado. Continuando...\n")
                decision = [{"type": "approve"}]
            else:
                print(f"\n↩️  Feedback registrado. Retornando ao agente...\n")
                decision = [{"type": "reject", "message": user_response}]

            result = supervisor.invoke(
                Command(resume={"decisions": decision}),
                config,
            )
            continue

        # ── Pipeline concluído ────────────────────────────────────────────
        final = _extract_last_message(result)
        if final:
            _print_separator("✅ Pipeline Concluído")
            print(final)
            _print_separator()

        print("Artefatos salvos em workspace/")
        break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SSD Agent CLI — Spec-Driven Development pipeline standalone"
    )
    parser.add_argument(
        "--briefing",
        type=Path,
        help="Arquivo .txt com o briefing (padrão: lê do stdin)",
    )
    parser.add_argument(
        "--thread",
        default="cli-session",
        help="Thread ID da sessão (default: cli-session)",
    )
    args = parser.parse_args()

    if args.briefing:
        briefing = args.briefing.read_text(encoding="utf-8")
    else:
        print("Cole o briefing abaixo (Ctrl+D para finalizar):\n")
        briefing = sys.stdin.read()

    if not briefing.strip():
        print("Erro: briefing vazio.", file=sys.stderr)
        sys.exit(1)

    run(briefing=briefing, thread_id=args.thread)


if __name__ == "__main__":
    main()
