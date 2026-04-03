---
name: review
description: Guia para auditar consistência entre artefatos SSD, refatorar código para legibilidade, gerar documentação técnica, changelog e sugestões de melhoria.
---

# Review — Skill

## Checklist de consistência

### Briefing → Domain Spec
- [ ] Todos os objetivos do briefing aparecem como casos de uso
- [ ] Todas as regras de negócio são invariantes ou políticas
- [ ] Pontos em aberto da spec foram resolvidos ou documentados

### Domain Spec → Contratos
- [ ] Toda entidade tem schema OpenAPI correspondente
- [ ] Todo caso de uso tem endpoint correspondente
- [ ] Todos os erros dos casos de uso estão no errors.md

### Contratos → Testes
- [ ] Todo endpoint tem pelo menos 1 teste de integração
- [ ] Toda invariante tem pelo menos 1 teste unitário
- [ ] coverage_matrix.md cobre todas as regras

### Testes → Implementação
- [ ] Todos os testes passam
- [ ] Nenhum endpoint do openapi.yaml está sem implementação
- [ ] gaps.md foi resolvido ou justificado

## Formato TECHNICAL_DOCS.md

```markdown
# Documentação Técnica: <Nome do Sistema>

## Arquitetura
<Diagrama textual ou descrição das camadas>

## Fluxos Principais
### <Caso de Uso>
1. ...
2. ...

## Decisões Técnicas
| Decisão | Alternativa Considerada | Motivo |
|---------|------------------------|--------|

## Como Rodar
...
```

## Sugestões de melhoria (suggestions.md)

Categorias: Performance | Segurança | Legibilidade | Escalabilidade

```markdown
## [Performance] <Título>
**Onde**: `src/...`
**Problema**: ...
**Sugestão**: ...
**Impacto estimado**: Alto / Médio / Baixo
```

## CHANGELOG.md — formato

```markdown
## [0.1.0] — <data>
### Adicionado
- ...
### Alterado
- ...
```

## Checklist final

- [ ] inconsistencies.md vazio ou com itens justificados
- [ ] TECHNICAL_DOCS.md completo
- [ ] CHANGELOG.md com versão inicial
- [ ] suggestions.md com pelo menos 3 sugestões
- [ ] Código refatorado para legibilidade sem mudança de comportamento
