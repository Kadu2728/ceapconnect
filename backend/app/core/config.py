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

    # --- Assistente IA (EPIC 11 — Google Gemini) ---
    gemini_api_key: str = Field(
        default="",
        description=(
            "Chave da API do Google Gemini (aistudio.google.com/app/apikey). "
            "Vazio = assistente responde 'não configurado'."
        ),
    )
    gemini_model: str = Field(
        default="gemini-flash-lite-latest",
        description="Modelo do Gemini usado pelo assistente (mesmo do projeto VendIA).",
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

    # --- Envolver o responsável (EPIC 17) ---
    interview_offset_days: int = Field(
        default=21,
        description=(
            "Número de dias após a prova usado como data provisória da entrevista "
            "com o responsável, até o produto ter uma data real por edital."
        ),
    )
    interview_location: str = Field(
        default="Unidade CEAP — Pedreira, São Paulo/SP",
        description="Local da entrevista, exibido ao candidato e enviado ao responsável.",
    )
    resend_api_key: str = Field(
        default="",
        description=(
            "Chave da API do Resend (resend.com/api-keys) usada para avisar o "
            "responsável por e-mail. Vazio = o aviso por e-mail fica indisponível "
            "(o link de WhatsApp continua funcionando normalmente)."
        ),
    )
    resend_from_email: str = Field(
        default="onboarding@resend.dev",
        description=(
            "Remetente do e-mail de aviso. O domínio de teste do Resend "
            "(onboarding@resend.dev) funciona sem verificação de domínio próprio."
        ),
    )

    # --- PWA + push notifications (EPIC 18) ---
    vapid_public_key: str = Field(
        default="",
        description=(
            "Chave pública VAPID (par gerado uma vez com py-vapid) — enviada ao "
            "navegador para ele poder se inscrever no push. Vazio = push indisponível."
        ),
    )
    vapid_private_key: str = Field(
        default="",
        description="Chave privada VAPID — nunca exposta ao frontend.",
    )
    vapid_subject: str = Field(
        default="mailto:contato@ceappedreira.org.br",
        description="Contato do remetente exigido pelo protocolo Web Push (claim 'sub').",
    )

    # --- Predição de evasão (EPIC 14) ---
    internal_api_key: str = Field(
        default="",
        description=(
            "Chave usada por `POST /internal/risk/recompute` — protegida por API "
            "key de serviço, nunca por JWT de usuário. Vazio = endpoint sempre "
            "recusa (fail-closed), até a chave ser configurada em produção."
        ),
    )
    risk_recompute_interval_minutes: int = Field(
        default=60,
        description=(
            "Intervalo do job in-process (APScheduler) que recalcula o risco de "
            "evasão de todos os candidatos ativos."
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
