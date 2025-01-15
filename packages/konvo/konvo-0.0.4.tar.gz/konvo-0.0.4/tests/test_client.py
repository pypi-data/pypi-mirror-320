import pytest
import logging
import requests
from unittest.mock import Mock, patch
from konvo import KonvoClient, APIError, __version__

@pytest.fixture
def mock_client():
    client = KonvoClient(api_key="test-key", log_level="DEBUG", timeout=10)
    client.session = Mock()
    return client

def test_system_health_check(mock_client):
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"status": "healthy"}
    mock_response.raise_for_status.return_value = None
    mock_client.system._client.session.get.return_value = mock_response

    # Call the method
    result = mock_client.system.check_health()

    # Assertions
    mock_client.system._client.session.get.assert_called_once_with(
        "https://api.konvotech.com/health",
        timeout=mock_client.timeout
    )
    assert result == {"status": "healthy"}

def test_client_initialization():
    client = KonvoClient(
        api_key="test-key",
        timeout=10,
        max_retries=5,
        log_level="DEBUG"
    )
    
    # Verify headers are set correctly
    assert client.session.headers["Authorization"] == "Bearer test-key"
    assert client.session.headers["Content-Type"] == "application/json"
    assert client.session.headers["Accept"] == "application/json"
    
    # Verify system endpoint is available
    assert hasattr(client, "system")
    
    # Verify timeout
    assert client.timeout == 10
    
    # Verify logging
    assert client.logger.level == logging.DEBUG

def test_health_check_failure(mock_client):
    # Setup mock to raise exception
    mock_client.system._client.session.get.side_effect = requests.exceptions.RequestException("Test error")
    
    with pytest.raises(APIError) as exc_info:
        mock_client.system.check_health()
    
    assert "Test error" in str(exc_info.value)

def test_retry_logic():
    client = KonvoClient(api_key="test-key", max_retries=3)
    adapter = client.session.get_adapter("https://")
    assert adapter.max_retries.total == 3

def test_logging(caplog):
    client = KonvoClient(api_key="test-key", log_level="DEBUG")
    with caplog.at_level(logging.DEBUG):
        client.system.check_health()
        assert "KonvoClient initialized" in caplog.text

def test_version():
    """Test that __version__ matches the package version"""
    assert __version__ == "0.0.3"
