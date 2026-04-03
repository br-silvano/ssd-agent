# SSD Agent — Nível 1 (System Context)

> Visão macro: atores humanos, o sistema principal e sistemas externos.

## Diagrama

```mermaid
C4Context
  title System Context – SSD Agent

  Person(dev, "Desenvolvedor", "Fornece o briefing e revisa os artefatos nos gates HITL")
  Person_Ext(reviewer, "Tech Lead / Revisor", "Valida consistência entre artefatos na etapa de review")

  System(ssd, "SSD Agent", "Pipeline de Spec-Driven Development que transforma briefing em código testado e revisado")

  System_Ext(zed, "Zed Editor", "IDE que se comunica via protocolo ACP (stdio)")
  System_Ext(anthropic, "Anthropic Claude", "LLM usado para normalização, geração de artefatos e raciocínio")
  System_Ext(deepagents, "Deep Agents SDK", "Framework que provê subagentes, filesystem backend e skills")
  System_Ext(langgraph, "LangGraph", "Orquestração de grafo com checkpointer e suporte a interrupts HITL")

  Rel(dev, ssd, "Fornece briefing e aprova gates", "stdin / ACP")
  Rel(reviewer, ssd, "Valida artefatos finais", "feedback")
  Rel(ssd, zed, "Comunica via protocolo ACP", "stdio")
  Rel(ssd, anthropic, "Invoca LLM para gerar artefatos", "HTTPS / API Key")
  Rel(ssd, deepagents, "Cria e orquestra subagentes", "SDK import")
  Rel(ssd, langgraph, "Persiste estado e pausa em gates", "MemorySaver / InMemoryStore")

  UpdateElementStyle(dev, $bgColor="#e8f5e9", $fontColor="#1b5e20", $borderColor="#4caf50")
  UpdateElementStyle(reviewer, $bgColor="#e8f5e9", $fontColor="#1b5e20", $borderColor="#4caf50")
  UpdateElementStyle(ssd, $bgColor="#1565c0", $fontColor="#ffffff", $borderColor="#0d47a1")
  UpdateElementStyle(zed, $bgColor="#fff3e0", $fontColor="#e65100", $borderColor="#ff9800")
  UpdateElementStyle(anthropic, $bgColor="#fff3e0", $fontColor="#e65100", $borderColor="#ff9800")
  UpdateElementStyle(deepagents, $bgColor="#fff3e0", $fontColor="#e65100", $borderColor="#ff9800")
  UpdateElementStyle(langgraph, $bgColor="#fff3e0", $fontColor="#e65100", $borderColor="#ff9800")

  UpdateRelStyle(dev, ssd, $textColor="#1b5e20", $lineColor="#4caf50")
  UpdateRelStyle(reviewer, ssd, $textColor="#1b5e20", $lineColor="#4caf50")
  UpdateRelStyle(ssd, zed, $textColor="#e65100", $lineColor="#ff9800")
  UpdateRelStyle(ssd, anthropic, $textColor="#e65100", $lineColor="#ff9800")
  UpdateRelStyle(ssd, deepagents, $textColor="#e65100", $lineColor="#ff9800")
  UpdateRelStyle(ssd, langgraph, $textColor="#e65100", $lineColor="#ff9800")
```

## Elementos

| Alias | Tipo | Descrição |
|-------|------|-----------|
| `dev` | Person | Desenvolvedor que inicia o pipeline com um briefing e responde aos gates HITL |
| `reviewer` | Person_Ext | Tech Lead que valida a consistência final dos artefatos |
| `ssd` | System | O sistema SSD Agent — pipeline completo de briefing → código |
| `zed` | System_Ext | Editor Zed que se integra via protocolo ACP |
| `anthropic` | System_Ext | API da Anthropic (Claude) usada como motor de IA |
| `deepagents` | System_Ext | SDK que provê subagentes especializados, filesystem backend e skills |
| `langgraph` | System_Ext | Framework de orquestração com checkpointer e interrupt mechanism |

## Paleta de Cores

| Elemento | Cor | Significado |
|----------|-----|-------------|
| Pessoas (dev, reviewer) | Verde (#4caf50) | Atores humanos que interagem com o sistema |
| SSD Agent (sistema central) | Azul (#1565c0) | Sistema principal sendo descrito |
| Sistemas externos | Laranja (#ff9800) | Dependências externas necessárias |
