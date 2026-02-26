from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str

    # Telegram
    telegram_bot_token: str

    # JWT
    secret_key: str
    access_token_expire_minutes: int = 1440

    # Claude API
    anthropic_api_key: str

    # S3
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str
    s3_region: str = "us-east-1"

    # App
    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]
