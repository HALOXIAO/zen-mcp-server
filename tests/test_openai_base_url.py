"""Tests for OpenAI base URL configuration functionality."""

import os
import pytest
from unittest.mock import patch, MagicMock

from providers.openai_provider import OpenAIModelProvider
from providers.base import ProviderType


class TestOpenAIBaseURL:
    """Test OpenAI base URL configuration."""

    def test_default_base_url_when_not_set(self):
        """Test that default OpenAI URL is used when OPENAI_BASE_URL is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the config import to avoid circular import issues
            with patch('providers.openai_provider.OPENAI_BASE_URL', 'https://api.openai.com/v1'):
                provider = OpenAIModelProvider(api_key="test-key")
                # Check that the provider was initialized with default URL
                assert provider.base_url == "https://api.openai.com/v1"

    def test_custom_base_url_from_config(self):
        """Test that custom base URL is used when OPENAI_BASE_URL is set."""
        custom_url = "https://custom-proxy.com/v1"
        with patch('providers.openai_provider.OPENAI_BASE_URL', custom_url):
            provider = OpenAIModelProvider(api_key="test-key")
            assert provider.base_url == custom_url

    def test_base_url_override_in_kwargs(self):
        """Test that base_url can be overridden via kwargs."""
        override_url = "https://override.com/v1"
        with patch('providers.openai_provider.OPENAI_BASE_URL', 'https://api.openai.com/v1'):
            provider = OpenAIModelProvider(api_key="test-key", base_url=override_url)
            assert provider.base_url == override_url

    @patch('config._validate_openai_base_url')
    def test_url_validation_called(self, mock_validate):
        """Test that URL validation is called during config loading."""
        mock_validate.return_value = "https://validated.com/v1"
        
        # Import config to trigger validation
        import config
        
        # Verify validation was called
        mock_validate.assert_called()

    def test_url_validation_adds_v1_suffix(self):
        """Test that URL validation adds /v1 suffix when missing."""
        from config import _validate_openai_base_url
        
        # Test URL without /v1
        result = _validate_openai_base_url("https://api.example.com")
        assert result == "https://api.example.com/v1"
        
        # Test URL with trailing slash
        result = _validate_openai_base_url("https://api.example.com/")
        assert result == "https://api.example.com/v1"
        
        # Test URL already with /v1
        result = _validate_openai_base_url("https://api.example.com/v1")
        assert result == "https://api.example.com/v1"

    def test_url_validation_requires_protocol(self):
        """Test that URL validation requires http/https protocol."""
        from config import _validate_openai_base_url
        
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            _validate_openai_base_url("api.example.com")
        
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            _validate_openai_base_url("ftp://api.example.com")

    def test_url_validation_handles_empty_url(self):
        """Test that URL validation returns default for empty URL."""
        from config import _validate_openai_base_url
        
        result = _validate_openai_base_url("")
        assert result == "https://api.openai.com/v1"
        
        result = _validate_openai_base_url(None)
        assert result == "https://api.openai.com/v1"

    @patch('openai.OpenAI')
    def test_provider_initialization_with_custom_url(self, mock_openai_client):
        """Test that OpenAI client is initialized with custom base URL."""
        custom_url = "https://custom-endpoint.com/v1"
        
        with patch('providers.openai_provider.OPENAI_BASE_URL', custom_url):
            provider = OpenAIModelProvider(api_key="test-key")
            
            # Verify OpenAI client was called with custom base_url
            mock_openai_client.assert_called_with(
                api_key="test-key",
                base_url=custom_url
            )

    def test_backward_compatibility(self):
        """Test that existing functionality works without OPENAI_BASE_URL set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('providers.openai_provider.OPENAI_BASE_URL', 'https://api.openai.com/v1'):
                provider = OpenAIModelProvider(api_key="test-key")
                
                # Test that provider type is correct
                assert provider.get_provider_type() == ProviderType.OPENAI
                
                # Test that model validation still works
                assert provider.validate_model_name("gpt-5")
                assert not provider.validate_model_name("invalid-model")

    @patch.dict(os.environ, {'OPENAI_BASE_URL': 'https://proxy.example.com'})
    def test_environment_variable_integration(self):
        """Test integration with environment variable."""
        # Reload config to pick up environment variable
        import importlib
        import config
        importlib.reload(config)
        
        # Verify the URL was processed correctly
        assert config.OPENAI_BASE_URL == "https://proxy.example.com/v1"

    def test_multiple_providers_with_different_urls(self):
        """Test that multiple provider instances can have different base URLs."""
        url1 = "https://provider1.com/v1"
        url2 = "https://provider2.com/v1"
        
        provider1 = OpenAIModelProvider(api_key="key1", base_url=url1)
        provider2 = OpenAIModelProvider(api_key="key2", base_url=url2)
        
        assert provider1.base_url == url1
        assert provider2.base_url == url2