"""
Modelos Pydantic para saída estruturada em cada etapa do pipeline SSD.
Cada modelo é o contrato de artefato entre um subagente e o próximo.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Etapa 1: Briefing Normalization ──────────────────────────────────────────

class NormalizedBriefing(BaseModel):
    objetivo: str = Field(description="O que o sistema deve fazer em uma frase")
    escopo: list[str] = Field(description="O que está dentro do escopo")
    nao_escopo: list[str] = Field(description="O que está explicitamente fora do escopo")
    usuarios: list[str] = Field(description="Tipos de usuários/atores")
    regras_de_negocio: list[str] = Field(description="Regras invariantes do domínio")
    restricoes_tecnicas: list[str] = Field(description="Restrições de stack, performance, etc.")
    riscos: list[str] = Field(description="Riscos identificados")
    perguntas_em_aberto: list[str] = Field(description="Dúvidas que precisam de resposta antes de prosseguir")


# ── Etapa 2: Domain Specification ────────────────────────────────────────────

class Entidade(BaseModel):
    nome: str
    atributos: list[str]
    invariantes: list[str] = Field(default_factory=list)

class CasoDeUso(BaseModel):
    nome: str
    ator: str
    descricao: str
    fluxo_principal: list[str]
    excecoes: list[str] = Field(default_factory=list)
    criterios_de_aceite: list[str]

class DomainSpec(BaseModel):
    contexto: str = Field(description="Parágrafo descrevendo o domínio")
    glossario: dict[str, str] = Field(description="Termos do domínio e suas definições")
    entidades: list[Entidade]
    eventos: list[str] = Field(description="Eventos de domínio relevantes")
    politicas: list[str] = Field(description="Políticas de negócio")
    casos_de_uso: list[CasoDeUso]
    criterios_de_aceite_globais: list[str]


# ── Etapa 3: Contract Generation ─────────────────────────────────────────────

class EndpointContract(BaseModel):
    metodo: str  # GET, POST, PUT, DELETE, PATCH
    path: str
    descricao: str
    request_schema: Optional[str] = None  # referência ao JSON schema
    response_schema: str
    erros: list[str] = Field(default_factory=list)

class ContractManifest(BaseModel):
    endpoints: list[EndpointContract]
    schemas: list[str] = Field(description="Nomes dos JSON schemas gerados em workspace/contracts/schemas/")
    erros_catalogados: list[str] = Field(description="Códigos e descrições de erros em errors.md")


# ── Etapa 4: Test Design ──────────────────────────────────────────────────────

class CenarioBDD(BaseModel):
    feature: str
    cenario: str
    dado: list[str]   # Given
    quando: list[str] # When
    entao: list[str]  # Then

class TestManifest(BaseModel):
    cenarios_bdd: list[CenarioBDD]
    arquivos_tdd: list[str] = Field(description="Paths dos arquivos de teste gerados")
    cobertura_por_regra: dict[str, list[str]] = Field(
        description="Mapeamento: regra_de_negocio → [test_ids]"
    )
