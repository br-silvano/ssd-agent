---
name: bdd-tdd
description: Guia para gerar cenários BDD (Gherkin) e esqueleto TDD (pytest) a partir de Domain Spec e contratos OpenAPI. Produz matriz de cobertura mapeando regras de negócio para test IDs.
---

# BDD + TDD — Skill

## Formato .feature (Gherkin)

```gherkin
# language: pt
Feature: <Nome do Caso de Uso>
  Como <ator>
  Quero <ação>
  Para <objetivo>

  Scenario: <contexto feliz>
    Dado que <pré-condição>
    E <outra pré-condição>
    Quando <ação do usuário>
    Então <resultado esperado>
    E <outro resultado>

  Scenario: <caso de erro>
    Dado que <pré-condição inválida>
    Quando <ação>
    Então o sistema retorna erro "<código>"
    E a mensagem é "<mensagem do errors.md>"
```

## Esqueleto pytest

```python
# tests/unit/test_<entidade>_<acao>.py
import pytest
from unittest.mock import MagicMock


class Test<Entidade><Acao>:
    """
    Testa: <caso de uso>
    Regras cobertas: RN-01, RN-03
    """

    def test_<acao>_sucesso(self):
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...

    def test_<acao>_falha_<condicao>(self):
        # Arrange — estado inválido
        ...
        # Act + Assert
        with pytest.raises(ValueError, match="..."):
            ...
```

## Regras

1. Todo cenário BDD deriva de um caso de uso da Domain Spec
2. Todo endpoint do OpenAPI tem pelo menos 1 teste de integração
3. Toda invariante de entidade tem pelo menos 1 teste unitário
4. Nomenclatura: `test_<entidade>_<acao>_<contexto>`
5. Testes de integração mocam o banco mas não a lógica de domínio

## coverage_matrix.md — formato

```markdown
| Regra de Negócio | Test IDs |
|-----------------|----------|
| RN-01: ... | test_usuario_criar_sucesso, test_usuario_criar_email_duplicado |
```

## Checklist

- [ ] Um .feature por caso de uso
- [ ] Cada endpoint tem teste em tests/integration/
- [ ] Cada invariante tem teste em tests/unit/
- [ ] coverage_matrix.md cobre todas as regras do briefing
