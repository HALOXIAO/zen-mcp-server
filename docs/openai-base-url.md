# OpenAI Base URL Configuration

This document explains how to configure a custom base URL for the OpenAI provider in Zen MCP Server.

## Overview

The `OPENAI_BASE_URL` configuration allows you to use OpenAI-compatible endpoints or regional mirrors instead of the default OpenAI API endpoint. This is useful for:

- Using OpenAI-compatible services (like Azure OpenAI, local deployments)
- Connecting through proxy servers
- Using regional mirrors or alternative endpoints

## Configuration

### Environment Variable

Set the `OPENAI_BASE_URL` environment variable in your `.env` file:

```bash
# Default OpenAI API (used if not specified)
OPENAI_BASE_URL=https://api.openai.com/v1

# Custom proxy example
OPENAI_BASE_URL=https://your-proxy.com/v1

# Azure OpenAI example
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment/v1
```

### URL Format Requirements

- Must start with `http://` or `https://`
- Will automatically append `/v1` if not present
- Handles trailing slashes correctly

### Examples

```bash
# These URLs will be automatically normalized:
OPENAI_BASE_URL=https://api.example.com          # → https://api.example.com/v1
OPENAI_BASE_URL=https://api.example.com/         # → https://api.example.com/v1
OPENAI_BASE_URL=https://api.example.com/v1       # → https://api.example.com/v1 (unchanged)
```

## Usage

Once configured, all OpenAI API calls will use your custom base URL automatically. No code changes are required.

```python
# The provider will automatically use your configured base URL
from providers.openai_provider import OpenAIModelProvider

provider = OpenAIModelProvider(api_key="your-key")
# provider.base_url will be your configured OPENAI_BASE_URL
```

## Backward Compatibility

- If `OPENAI_BASE_URL` is not set, the default OpenAI API URL is used
- Existing configurations continue to work without changes
- All OpenAI models and features remain fully supported

## Validation

The system validates your base URL configuration:

- Ensures proper protocol (http/https)
- Automatically adds `/v1` suffix for OpenAI compatibility
- Provides clear error messages for invalid URLs

## Testing

You can test your configuration by checking the loaded URL:

```bash
python -c "from config import OPENAI_BASE_URL; print('Using base URL:', OPENAI_BASE_URL)"
```

## Troubleshooting

### Common Issues

1. **Invalid URL format**: Ensure your URL starts with `http://` or `https://`
2. **Missing /v1 suffix**: The system automatically adds this, but ensure your endpoint supports OpenAI v1 API format
3. **Network connectivity**: Verify your custom endpoint is accessible from your environment

### Error Messages

- `"OpenAI base URL must start with http:// or https://"`: Fix the URL protocol
- Connection errors: Check network connectivity to your custom endpoint

## Security Considerations

- Use HTTPS endpoints in production
- Ensure your custom endpoint properly handles authentication
- Validate that your proxy/mirror maintains API compatibility