---
name: domain-spec
description: Guia para produzir Domain Specs de alta qualidade a partir de briefings normalizados. Cobre glossário, entidades, invariantes, eventos, políticas, casos de uso e critérios de aceite.
---

# Domain Spec — Skill

## Estrutura obrigatória de spec.md

```markdown
# Domain Spec: <Nome do Sistema>

## Contexto
<Parágrafo descrevendo o domínio e o problema que o sistema resolve>

## Glossário
| Termo | Definição |
|-------|-----------|
| ...   | ...       |

## Entidades
### <NomeEntidade>
- **Atributos**: id, nome, ...
- **Invariantes**: <regras que nunca podem ser violadas>

## Eventos de Domínio
- `<EntidadeCriada>` — quando ...
- `<StatusAtualizado>` — quando ...

## Políticas
- Se <condição>, então <consequência>

## Casos de Uso
### UC-01: <Nome>
- **Ator**: ...
- **Fluxo principal**: 1. ... 2. ...
- **Exceções**: ...
- **Critérios de aceite**: [ ] ...

## Pontos em Aberto
- ⚠️ ...
```

## Checklist antes de salvar

- [ ] Todo termo do glossário aparece nas entidades ou casos de uso
- [ ] Toda regra do briefing virou invariante, política ou critério de aceite
- [ ] Cada caso de uso tem pelo menos 3 critérios de aceite
- [ ] Ambiguidades documentadas como ⚠️ Ponto em Aberto
- [ ] spec.json gerado com mesma estrutura para consumo do próximo agente
