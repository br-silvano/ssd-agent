---
name: implementation
description: Guia para implementar código Python/FastAPI e Next.js/React guiado por contratos OpenAPI e testes existentes. Clean Code, SOLID e DDD tático quando justificado.
---

# Implementation — Skill

## Estrutura de projeto Python/FastAPI

```
implementation/
├── src/
│   ├── domain/
│   │   ├── entities/        # Entidades e Value Objects
│   │   ├── repositories/    # Interfaces (ABCs)
│   │   └── services/        # Domain Services
│   ├── application/
│   │   ├── use_cases/       # Um arquivo por caso de uso
│   │   └── dtos/            # Input/Output schemas (Pydantic)
│   ├── infrastructure/
│   │   ├── repositories/    # Implementações concretas (SQLAlchemy)
│   │   └── database/        # Engine, session, migrations
│   └── api/
│       ├── routers/         # Um router por recurso
│       └── main.py          # FastAPI app factory
```

## Regras de implementação

1. **Contrato primeiro**: cada endpoint implementado deve corresponder exatamente ao openapi.yaml
2. **Testes guiam**: não adicione lógica que não está coberta por um teste existente
3. **Docstrings mínimas**: toda função pública tem docstring de 1 linha
4. **Sem magic strings**: use Enum ou constantes nomeadas
5. **Erros explícitos**: use os códigos de errors.md, nunca strings genéricas
6. **Injeção de dependência**: use FastAPI `Depends()` para repositórios e serviços

## Padrão de router FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException, status
from ..application.use_cases.<use_case> import <UseCase>
from ..application.dtos.<dto> import <Input>, <Output>

router = APIRouter(prefix="/<recurso>", tags=["<Recurso>"])


@router.post("/", response_model=<Output>, status_code=status.HTTP_201_CREATED)
async def criar_<recurso>(
    body: <Input>,
    use_case: <UseCase> = Depends(),
) -> <Output>:
    """<Descrição do endpoint do openapi.yaml>"""
    return await use_case.execute(body)
```

## Gaps

Se encontrar gap entre contrato e testes, documente em gaps.md:

```markdown
## Gap: <endpoint>
- **Contrato diz**: ...
- **Teste espera**: ...
- **Decisão**: implementar conforme contrato, ajustar teste na Review
```

## Checklist

- [ ] Todos os endpoints do openapi.yaml implementados
- [ ] Todos os testes existentes passam
- [ ] gaps.md vazio ou com gaps documentados
- [ ] Nenhuma lógica sem cobertura de teste
