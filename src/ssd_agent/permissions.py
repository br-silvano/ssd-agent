"""
Referência de permissões para o SSD Agent.

O SSD Agent usa o mecanismo HITL do Deep Agents (interrupt_on nos gates)
como camada principal de aprovação — não o sistema de permissões ACP.

Este módulo documenta a política de permissões para tool calls que o agente
eventualmente rotear para o editor (openFile, runTerminalCommand, etc.).

Para usar o PermissionBroker experimental do SDK:
    from acp.contrib.permissions import PermissionBroker
    broker = PermissionBroker(tracker)  # requer ToolCallTracker

Ver: https://agentclientprotocol.github.io/python-sdk/contrib/
"""

from __future__ import annotations

# Ações que exigem confirmação explícita do usuário no editor
REQUIRE_PERMISSION = frozenset(
    {
        "run_terminal",  # execução de shell no editor
        "edit_file",  # modificação de arquivo
        "delete_file",  # deleção de qualquer arquivo
        "install_package",  # instalação de dependência
    }
)

# Ações permitidas silenciosamente (read-only, seguras)
ALLOW_SILENTLY = frozenset(
    {
        "read_file",
        "list_directory",
        "search_codebase",
        "open_file",
    }
)
