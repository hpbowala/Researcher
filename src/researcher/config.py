"""
Configuration management for the researcher project.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for the researcher project."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config.yml file.
                         Defaults to 'config.yml' in project root.
        """
        # Load environment variables from .env file if it exists
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Load YAML configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yml"

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        return config or {}

    def _resolve_env_vars(self, value: str) -> str:
        """Resolve environment variable placeholders in string values."""
        if not isinstance(value, str):
            return value

        # Handle ${VAR:default} syntax
        if value.startswith("${") and value.endswith("}"):
            var_part = value[2:-1]  # Remove ${ and }
            if ":" in var_part:
                var_name, default = var_part.split(":", 1)
            else:
                var_name, default = var_part, ""

            return os.getenv(var_name, default)

        return value

    def _resolve_nested_dict(self, data: Any) -> Any:
        """Recursively resolve environment variables in nested dictionaries."""
        if isinstance(data, dict):
            return {
                key: self._resolve_nested_dict(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._resolve_nested_dict(item) for item in data]
        elif isinstance(data, str):
            return self._resolve_env_vars(data)
        else:
            return data

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation (e.g., 'api.openai.api_key')."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return self._resolve_nested_dict(value)

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        result = self.get(f"api.{service}.api_key")
        return str(result) if result is not None else None

    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return {
            "api_key": self.get("api.openai.api_key"),
            "base_url": self.get("api.openai.base_url"),
            "model": self.get("api.openai.model"),
            "max_tokens": self.get("api.openai.max_tokens"),
        }

    def get_bright_data_config(self) -> Dict[str, Any]:
        """Get Bright Data configuration."""
        return {
            "api_key": self.get("api.bright_data.api_key"),
            "base_url": self.get("api.bright_data.base_url"),
            "username": self.get("api.bright_data.username"),
        }

    def is_development(self) -> bool:
        """Check if running in development environment."""
        env = self.get("app.environment", "development")
        return str(env).lower() == "development"

    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        debug = self.get("app.debug", False)
        return bool(debug)


# Global configuration instance
config = Config()
