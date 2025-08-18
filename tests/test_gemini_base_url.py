"""Tests for Gemini base URL configuration."""

import os
import pytest
from unittest.mock import patch, MagicMock

from providers.gemini import GeminiModelProvider


class TestGeminiBaseURL:
    """Test Gemini base URL configuration."""

    def test_default_base_url(self):
        """Test that default base URL is used when not specified."""
        with patch.dict(os.environ, {}, clear=True):
            # Import config after clearing environment to get default
            from config import GEMINI_BASE_URL
            assert GEMINI_BASE_URL == "https://generativelanguage.googleapis.com"

    def test_custom_base_url_from_env(self):
        """Test that custom base URL is loaded from environment variable."""
        custom_url = "https://custom-gemini-api.example.com"
        
        with patch.dict(os.environ, {"GEMINI_BASE_URL": custom_url}):
            # Re-import config to pick up the environment variable
            import importlib
            import config
            importlib.reload(config)
            
            assert config.GEMINI_BASE_URL == custom_url

    def test_gemini_provider_uses_default_base_url(self):
        """Test that GeminiModelProvider uses default base URL."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the genai.Client to avoid actual API calls
            with patch('providers.gemini.genai.Client') as mock_client:
                provider = GeminiModelProvider("test-api-key")
                
                # Access the client property to trigger initialization
                _ = provider.client
                
                # Verify that genai.Client was called with only api_key (no base_url)
                mock_client.assert_called_once_with(api_key="test-api-key")

    def test_gemini_provider_uses_custom_base_url(self):
        """Test that GeminiModelProvider uses custom base URL when provided."""
        custom_url = "https://custom-gemini-api.example.com"
        
        with patch.dict(os.environ, {"GEMINI_BASE_URL": custom_url}):
            # Re-import config to pick up the environment variable
            import importlib
            import config
            importlib.reload(config)
            
            # Mock the genai.Client to avoid actual API calls
            with patch('providers.gemini.genai.Client') as mock_client:
                provider = GeminiModelProvider("test-api-key")
                
                # Access the client property to trigger initialization
                _ = provider.client
                
                # Verify that genai.Client was called with custom base_url
                mock_client.assert_called_once_with(api_key="test-api-key", base_url=custom_url)

    def test_gemini_provider_constructor_base_url_override(self):
        """Test that base_url can be overridden in constructor."""
        constructor_url = "https://constructor-override.example.com"
        
        # Mock the genai.Client to avoid actual API calls
        with patch('providers.gemini.genai.Client') as mock_client:
            provider = GeminiModelProvider("test-api-key", base_url=constructor_url)
            
            # Access the client property to trigger initialization
            _ = provider.client
            
            # Verify that genai.Client was called with constructor override URL
            mock_client.assert_called_once_with(api_key="test-api-key", base_url=constructor_url)

    def test_base_url_validation_valid_urls(self):
        """Test that valid URLs pass validation."""
        from config import _validate_gemini_base_url
        
        valid_urls = [
            "https://generativelanguage.googleapis.com",
            "https://custom-api.example.com",
            "http://localhost:8080",
            "https://api.example.com/",  # With trailing slash
        ]
        
        for url in valid_urls:
            result = _validate_gemini_base_url(url)
            # Should remove trailing slash
            expected = url.rstrip('/')
            assert result == expected

    def test_base_url_validation_invalid_urls(self):
        """Test that invalid URLs raise ValueError."""
        from config import _validate_gemini_base_url
        
        invalid_urls = [
            "ftp://invalid-protocol.com",
            "not-a-url",
            "gemini-api.com",  # Missing protocol
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Gemini base URL must start with http:// or https://"):
                _validate_gemini_base_url(url)

    def test_base_url_validation_empty_url(self):
        """Test that empty URL returns default."""
        from config import _validate_gemini_base_url
        
        result = _validate_gemini_base_url("")
        assert result == "https://generativelanguage.googleapis.com"
        
        result = _validate_gemini_base_url(None)
        assert result == "https://generativelanguage.googleapis.com"