---
name: api-contract
description: "Guia para gerar openapi.yaml (OpenAPI 3.1), JSON schemas e catálogo de erros a partir de uma Domain Spec. Regra principal: se não está no contrato, não existe na implementação."
---

# API Contract — Skill

## Estrutura openapi.yaml

```yaml
openapi: 3.1.0
info:
  title: <NomeSistema> API
  version: 0.1.0
  description: |
    <Descrição derivada da Domain Spec>

paths:
  /<recurso>:
    post:
      summary: <ação>
      operationId: <entidade>_<acao>
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/<Entidade>Input'
            examples:
              exemplo_basico:
                value: { ... }
      responses:
        '201':
          description: Criado com sucesso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/<Entidade>Output'
        '422':
          $ref: '#/components/responses/ValidationError'

components:
  schemas:
    <Entidade>Input:
      type: object
      required: [campo1, campo2]
      properties:
        campo1:
          type: string
          description: <derivado do glossário>
          example: "..."
  responses:
    ValidationError:
      description: Erro de validação
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
```

## Regras de contrato

1. Toda entidade da Domain Spec → schema correspondente
2. Todo caso de uso → pelo menos 1 endpoint
3. Toda invariante → validação documentada no schema (pattern, enum, minimum...)
4. Nomes de operationId no padrão `entidade_acao` (snake_case)
5. Sempre incluir exemplos em schemas e endpoints

## errors.md — formato

```markdown
# Catálogo de Erros

| Código | HTTP | Mensagem | Causa |
|--------|------|----------|-------|
| ERR_001 | 422 | Campo X obrigatório | ... |
| ERR_002 | 404 | Recurso não encontrado | ... |
```

## Checklist

- [ ] Toda entidade tem schema Input + Output
- [ ] Todos os endpoints têm exemplos
- [ ] errors.md cobre todos os casos de erro dos casos de uso
- [ ] manifest.json salvo com lista de endpoints e schemas
