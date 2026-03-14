from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CargoZen"
    APP_ENV: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [s.strip() for s in self.CORS_ORIGINS.split(",") if s.strip()]

    # Snowflake
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_AUTHENTICATOR: str = "snowflake"
    SNOWFLAKE_WAREHOUSE: str = "CARGOZEN_WH"
    SNOWFLAKE_DATABASE: str = "CARGOZEN_DB"
    SNOWFLAKE_SCHEMA: str = "AUTH"
    SNOWFLAKE_ROLE: str = "ACCOUNTADMIN"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()