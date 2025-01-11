from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings
from starlette.config import Config

# Simplify the path resolution logic
current_file_dir = Path(__file__).resolve().parent
possible_env_paths = [
    current_file_dir.parent.parent / ".env",  # ../../.env
    current_file_dir.parent.parent.parent / ".env",  # ../../../.env
    Path.cwd() / ".env",  # .env in current working directory
]

# Try to find the .env file
env_path = None
for path in possible_env_paths:
    if path.exists():
        env_path = path
        break

# If no .env file is found, create a default config without requiring .env
if env_path:
    config = Config(str(env_path))
else:
    config = Config()  # Will use environment variables without .env file


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY", default="KJBNLabs")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class DatabaseSettings(BaseSettings):
    pass


class MySQLSettings(DatabaseSettings):
    MYSQL_USER: str = config("MYSQL_USER", default="username")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default="password")
    MYSQL_SERVER: str = config("MYSQL_SERVER", default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", default=3306)
    MYSQL_DB: str = config("MYSQL_DB", default="dbname")
    MYSQL_URI: str = (
        f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    MYSQL_SYNC_PREFIX: str = config("MYSQL_SYNC_PREFIX", default="mysql://")
    MYSQL_ASYNC_PREFIX: str = config("MYSQL_ASYNC_PREFIX", default="mysql+aiomysql://")


class RedisCacheSettings(BaseSettings):
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT", default=6379)
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class ApplicationSettings(BaseSettings):
    AUTH_GRPC_SERVER_ADDRESS: str = config(
        "AUTH_GRPC_SERVER_ADDRESS", default="localhost:50051"
    )
    PORT: str = config("PORT", default="8000")
    GOOGLE_APPLICATION_CREDENTIALS: str = config(
        "GOOGLE_APPLICATION_CREDENTIALS", default=""
    )
    AUTH_CALLBACK_URL: str = config(
        "AUTH_CALLBACK_URL", default="http://localhost:8080/api/v1/auth/auth_callback"
    )


class Settings(
    CryptSettings,
    MySQLSettings,
    RedisCacheSettings,
    DefaultRateLimitSettings,
    EnvironmentSettings,
    ApplicationSettings,
):
    pass


settings = Settings()
