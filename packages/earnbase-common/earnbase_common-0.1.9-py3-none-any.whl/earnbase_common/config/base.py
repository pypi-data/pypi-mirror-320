"""Base settings for all services."""

import os
from typing import Any, Dict, Optional

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

    def __init__(self, **kwargs):
        """Initialize settings with values from YAML."""
        config = load_yaml_config()

        # Set required values from YAML
        for key in self.__annotations__:
            if key in kwargs:
                continue
            yaml_key = key.lower()
            if yaml_key in config:
                kwargs[key] = config[yaml_key]
            elif "." in yaml_key:
                # Handle nested keys like "access_token.secret_key"
                parts = yaml_key.split(".")
                value = config
                for part in parts:
                    value = value.get(part, {})
                if value:
                    kwargs[key] = value

        super().__init__(**kwargs)

    @classmethod
    def get_service_prefix(cls) -> str:
        """Get service prefix for environment variables."""
        module_path = cls.__module__.split(".")
        if len(module_path) >= 2:
            service_name = module_path[0].replace("-", "_").upper()
            return f"{service_name}_"
        return ""
