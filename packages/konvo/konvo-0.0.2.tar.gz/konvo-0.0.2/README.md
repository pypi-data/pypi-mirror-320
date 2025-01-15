# Konvo Python SDK

The official Python SDK for the Konvotech API.

## Installation

```bash
pip install konvo
```

## Usage

### Basic Setup

```python
from konvo import KonvoClient

# Initialize client with your API key
client = KonvoClient(api_key="your_api_key_here")

# Check API health
health_status = client.system.check_health()
print(health_status)  # {"status": "healthy"}
```

### Configuration Options

The `KonvoClient` accepts several configuration options:

```python
client = KonvoClient(
    api_key="your_api_key_here",
    max_retries=3,          # Number of retries for failed requests
    log_level="WARNING",    # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    timeout=30              # Request timeout in seconds
)
```

## Error Handling

The SDK raises custom exceptions:

- `KonvoError`: Base exception for all Konvotech API errors
- `APIError`: Raised when API requests fail, includes status_code

```python
try:
    client.system.check_health()
except APIError as e:
    print(f"API request failed with status {e.status_code}: {str(e)}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

[MIT License](LICENSE)
