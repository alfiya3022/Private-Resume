
import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Verity API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security: these values must be supplied through environment configuration.
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database: provide the URL appropriate for the current runtime.
    DATABASE_URL: str

    # Ollama Local AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b-instruct"

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    HF_HOME: str = "/root/.cache/huggingface"

    # LayoutLMv3 Master Resume Extraction
    LAYOUTLM_MODEL_NAME_OR_PATH: str = "microsoft/layoutlmv3-base"
    LAYOUTLM_DEVICE: str = "cpu"
    ENABLE_LAYOUTLM_EXTRACTION: bool = True

    # Storage
    STORAGE_DIR: str = "./storage"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, value: Union[str, List[str]]
    ) -> List[str]:
        if isinstance(value, str):
            value = value.strip()

            if value.startswith("["):
                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise ValueError(
                        "BACKEND_CORS_ORIGINS must be a JSON list or comma-separated string"
                    )
                return parsed

            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
