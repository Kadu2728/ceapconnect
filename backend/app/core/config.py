"""Configuração central da aplicação.

Todas as variáveis sensíveis (credenciais de banco, segredos JWT) são lidas
exclusivamente do ambiente (.env em desenvolvimento). Nunca hardcode valores
sensíveis neste arquivo.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "CEAP Connect API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False

    # --- Database ---
    database_url: str = Field(
        ...,
        description="String de conexão assíncrona do PostgreSQL (postgresql+asyncpg://...)",
    )
    database_ssl: bool = Field(
        default=False,
        description=(
            "Ativa TLS na conexão com o banco (obrigatório em provedores gerenciados "
            "como Neon; desnecessário no Postgres local via Docker)"
        ),
    )

    # --- JWT ---
    jwt_secret: str = Field(..., description="Segredo usado para assinar os tokens JWT")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- CORS ---
    cors_origins: str = "http://localhost:3000"

    # --- Assistente IA (EPIC 11 — Groq, nível gratuito) ---
    groq_api_key: str = Field(
        default="",
        description=(
            "Chave da API do Groq (console.groq.com — gratuita, sem cartão; começa "
            "com 'gsk_'). Vazio = assistente responde 'não configurado'."
        ),
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Modelo do Groq usado pelo assistente (nível gratuito).",
    )
    assistant_max_tokens: int = Field(
        default=1024,
        description="Limite de tokens da resposta do assistente por mensagem.",
    )

    # --- Candidate journey (EPIC 03) ---
    default_exam_offset_days: int = Field(
        default=75,
        description=(
            "Número de dias a partir do registro usado como data provisória da "
            "prova, até o produto ter uma data real configurável por edital."
        ),
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Converte a string separada por vírgula de CORS_ORIGINS em lista."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância cacheada de Settings (evita reler o .env a cada chamada)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
