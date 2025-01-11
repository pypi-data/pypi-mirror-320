"""Base settings for all services."""

import os
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic_settings import BaseSettings as PydanticBaseSettings


def load_yaml_config() -> Dict[str, Any]:
    """Load YAML configuration."""
    config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class BaseSettings(PydanticBaseSettings):
    """Base settings class for all services."""

    # Service info
    SERVICE_NAME: str
    DESCRIPTION: str
    VERSION: str
    ENV: str = "development"
    DEBUG: bool = True
    ENABLE_DOCS: bool = True

    # HTTP Server
    HTTP_HOST: str = "0.0.0.0"
    HTTP_PORT: int = 8000
    HTTP_WORKERS: int = 1
    API_PREFIX: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_PREFIX: str = ""
    REDIS_TTL: int = 3600

    # Metrics
    METRICS_ENABLED: bool = True
    METRICS_PORT: Optional[int] = None

    class Config:
        """Pydantic config."""

        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ) -> Tuple[Any, ...]:
            """Customize settings sources."""
            config = load_yaml_config()

            # Map YAML config to settings
            settings = {
                f"{cls.get_service_prefix()}{k}": v
                for k, v in {
                    "SERVICE_NAME": config["service"]["name"],
                    "DESCRIPTION": config["service"]["description"],
                    "VERSION": config["service"]["version"],
                    "ENV": config["service"]["env"],
                    "DEBUG": config["service"]["debug"],
                    "ENABLE_DOCS": config["service"]["enable_docs"],
                    "HTTP_HOST": config["http"]["host"],
                    "HTTP_PORT": config["http"]["port"],
                    "HTTP_WORKERS": config["http"]["workers"],
                    "API_PREFIX": config["http"]["api_prefix"],
                    "LOG_LEVEL": config["logging"]["level"],
                    "LOG_FILE": config["logging"]["file"],
                    "MONGODB_URL": config["mongodb"]["url"],
                    "MONGODB_DB_NAME": config["mongodb"]["db_name"],
                    "MONGODB_MIN_POOL_SIZE": config["mongodb"]["min_pool_size"],
                    "MONGODB_MAX_POOL_SIZE": config["mongodb"]["max_pool_size"],
                    "REDIS_URL": config["redis"]["url"],
                    "REDIS_DB": config["redis"]["db"],
                    "REDIS_PREFIX": config["redis"]["prefix"],
                    "REDIS_TTL": config["redis"]["ttl"],
                    "METRICS_ENABLED": config["metrics"]["enabled"],
                    "METRICS_PORT": config["metrics"]["port"],
                }.items()
            }

            return (
                init_settings,
                env_settings,
                file_secret_settings,
                lambda: settings,
            )

        @classmethod
        def get_service_prefix(cls) -> str:
            """Get service prefix for environment variables."""
            # Extract service name from class module path
            module_path = cls.__module__.split(".")
            if len(module_path) >= 2:
                service_name = module_path[0].replace("-", "_").upper()
                return f"{service_name}_"
            return ""
