from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH) if _ENV_PATH.is_file() else ".env",
        extra="ignore",
    )

    database_url: str
    jwt_secret: str
    jwt_expiry_hours: int = 168  # 7 days
    cors_origins: str = "http://localhost:5173"
    groq_api_key: str | None = None
    gemini_api_key: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()


