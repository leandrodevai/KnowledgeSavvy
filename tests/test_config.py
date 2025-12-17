"""
Tests for application configuration and settings.

Verifies that configuration loading, validation, and fallback mechanisms
work correctly across different deployment scenarios.
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestSSLConfiguration:
    """Test SSL certificate configuration."""

    @pytest.mark.unit
    def test_ssl_context_creation(self):
        """Verify SSL context is created with certifi bundle."""
        from config import ssl_config

        assert ssl_config.ssl_context is not None
        assert os.environ.get("SSL_CERT_FILE") is not None
        assert os.environ.get("REQUESTS_CA_BUNDLE") is not None

    @pytest.mark.unit
    def test_configure_ssl_function(self):
        """Test configure_ssl returns valid SSL context."""
        from config.ssl_config import configure_ssl

        context = configure_ssl()
        assert context is not None


class TestSettingsConfiguration:
    """Test application settings and configuration."""

    @pytest.mark.unit
    def test_settings_instance_creation(self):
        """Verify settings singleton can be instantiated."""
        from config.settings import settings

        assert settings is not None
        assert hasattr(settings, "resolved_database_url")

    @pytest.mark.unit
    @patch.dict(
        os.environ,
        {
            "POSTGRES_SERVER": "localhost",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_pass",
            "POSTGRES_DB": "test_db",
        },
    )
    def test_database_url_from_env(self):
        """Test database URL construction from environment variables."""
        # Create new settings instance with patched env vars
        from config.settings import AppSettings

        test_settings = AppSettings()
        url = test_settings.resolved_database_url

        assert "test_user" in url
        assert "localhost" in url
        assert "test_db" in url
        assert "test_pass" in url

    @pytest.mark.unit
    def test_settings_has_required_attributes(self):
        """Verify settings has all required configuration attributes."""
        from config.settings import settings

        required_attrs = [
            "resolved_database_url",
            "vector_store_backend",
        ]

        for attr in required_attrs:
            assert hasattr(settings, attr), f"Missing required attribute: {attr}"


class TestLoggingConfiguration:
    """Test logging setup and configuration."""

    @pytest.mark.unit
    def test_setup_logging_creates_handlers(self):
        """Verify setup_logging configures handlers correctly."""
        import logging

        from core.logger import setup_logging

        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        setup_logging()

        # Should have at least one handler configured
        assert len(root_logger.handlers) > 0

    @pytest.mark.unit
    def test_logger_exists_for_module(self):
        """Test that module-specific loggers can be created."""
        import logging

        logger = logging.getLogger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
