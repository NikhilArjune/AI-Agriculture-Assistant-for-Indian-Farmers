from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_secret_key: str = "change-this-secret"
    debug: bool = True
    app_title: str = "Agri AI Platform"
    app_version: str = "0.1.0"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/agri_db"
    mongo_db_name: str = "agri_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "agri_knowledge"

    # LLM
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1024
    # Comma-separated models tried (in order) when the primary hits its daily quota.
    # Each Gemini model has a separate free-tier bucket, so this multiplies capacity.
    llm_fallback_models: str = ""
    llm_vision_fallback_models: str = ""

    groq_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    anthropic_api_key: str = ""

    # Embeddings
    embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"

    # STT / TTS
    stt_model: str = "whisper-large-v3-turbo"
    tts_provider: str = "groq"
    tts_model: str = "canopylabs/orpheus-v1-english"
    tts_voice: str = "autumn"

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # File storage
    storage_backend: Literal["local", "s3"] = "local"
    upload_dir: str = "./uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "ap-south-1"

    # External APIs
    openweather_api_key: str = ""
    agmarknet_api_key: str = ""
    myscheme_api_key: str = ""
    msg91_auth_key: str = ""
    fcm_server_key: str = ""

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "agri-ai-platform"

    # Sentry
    sentry_dsn: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
