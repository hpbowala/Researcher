"""
Tests for the configuration module.
"""

import os
import tempfile

import yaml

from researcher.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_config_initialization(self):
        """Test Config initialization."""
        config = Config()
        assert config is not None
        assert hasattr(config, "_config")

    def test_load_config_from_file(self):
        """Test loading configuration from YAML file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {
                "api": {"openai": {"api_key": "test-key", "model": "gpt-4"}},
                "app": {"environment": "test"},
            }
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get("api.openai.api_key") == "test-key"
            assert config.get("api.openai.model") == "gpt-4"
            assert config.get("app.environment") == "test"
        finally:
            os.unlink(config_path)

    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {"api": {"openai": {"api_key": "test-key"}}}
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get("api.openai.api_key") == "test-key"
            assert config.get("api.openai.nonexistent") is None
            assert config.get("api.openai.nonexistent", "default") == "default"
        finally:
            os.unlink(config_path)

    def test_resolve_env_vars(self):
        """Test environment variable resolution."""
        # Set environment variable
        os.environ["TEST_API_KEY"] = "env-test-key"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {
                "api": {"openai": {"api_key": "${TEST_API_KEY:default-key}"}}
            }
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get("api.openai.api_key") == "env-test-key"
        finally:
            os.unlink(config_path)
            # Clean up environment variable
            if "TEST_API_KEY" in os.environ:
                del os.environ["TEST_API_KEY"]

    def test_get_api_key(self):
        """Test getting API key for specific service."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {
                "api": {
                    "openai": {"api_key": "openai-test-key"},
                    "bright_data": {"api_key": "bright-data-test-key"},
                }
            }
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get_api_key("openai") == "openai-test-key"
            assert config.get_api_key("bright_data") == "bright-data-test-key"
            assert config.get_api_key("nonexistent") is None
        finally:
            os.unlink(config_path)

    def test_get_openai_config(self):
        """Test getting OpenAI configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {
                "api": {
                    "openai": {
                        "api_key": "test-key",
                        "base_url": "https://api.openai.com/v1",
                        "model": "gpt-4",
                        "max_tokens": 1000,
                    }
                }
            }
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            openai_config = config.get_openai_config()
            assert openai_config["api_key"] == "test-key"
            assert openai_config["base_url"] == "https://api.openai.com/v1"
            assert openai_config["model"] == "gpt-4"
            assert openai_config["max_tokens"] == 1000
        finally:
            os.unlink(config_path)

    def test_environment_checks(self):
        """Test environment checking methods."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            test_config = {"app": {"environment": "production", "debug": True}}
            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = Config(config_path)
            assert not config.is_development()
            assert config.is_debug()
        finally:
            os.unlink(config_path)
