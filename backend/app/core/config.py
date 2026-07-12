from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Incident Investigator"
    environment: str = Field(default="local", validation_alias="APP_ENV")
    database_url: str = Field(default="sqlite:///./incident_investigator.db", validation_alias="DATABASE_URL")
    llm_provider: str = Field(default="mock", validation_alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", validation_alias="OPENAI_MODEL")
    max_upload_bytes: int = Field(default=2_000_000, validation_alias="MAX_UPLOAD_BYTES")
    redact_ip_addresses: bool = Field(default=False, validation_alias="REDACT_IP_ADDRESSES")
    sample_data_dir: Path = Field(default=Path("../sample-data"), validation_alias="SAMPLE_DATA_DIR")


@lru_cache
def get_settings() -> Settings:
    return Settings()

