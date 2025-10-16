from functools import lru_cache
import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_env_filename():
    runtime_env = os.getenv("ENV")
    return f".env.{runtime_env}" if runtime_env else ".env"


class EnvironmentSettings(BaseSettings):
    # Application settings
    API_VERSION: str
    APP_NAME: str
    APP_DESC: str
    APP_PORT: int
    OPENAI_API_KEY: Optional[str] = None
    # Vertex AI settings
    MODEL_NAME: str = "gemini-2.5-pro"
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-east1"
    GOOGLE_APPLICATION_CREDENTIALS: str = "service-account.json"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    TTL_SECONDS: int = 3600

    # User credentials for external service
    USER_PHONE: str
    USER_PASSWORD: str
    USER_COUNTRY: str = "VI"
    
    # Planning API settings
    PLANNING_API_URL: str
    PLANNING_API_KEY: str
    
    # MCP Server Configuration
    BASE_URL: str
    OXII_MCP_SERVER_URL: str = "http://oxii-server:9031/sse"

    DEBUG_MODE: bool = False
    MAX_ITERATIONS: int = 100

    model_config = SettingsConfigDict(env_file=get_env_filename(), env_file_encoding="utf-8")

@lru_cache
def get_environment_variables():
    return EnvironmentSettings()

env = get_environment_variables()