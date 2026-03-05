from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    backend_url: str = "http://backend:8000"
    mock_backend: bool = True
    log_level: str = "DEBUG"


settings = Settings()  # type: ignore[call-arg]
