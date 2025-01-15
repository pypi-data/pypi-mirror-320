import logging
import requests
from typing import Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class KonvoError(Exception):
    """Base exception for all Konvotech API errors"""
    pass

class APIError(KonvoError):
    """Exception for API response errors"""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class System:
    """Endpoints related to system operations and health checks."""
    
    def __init__(self, client: 'KonvoClient'):
        self._client = client

    def check_health(self) -> Dict[str, str]:
        """Check the health status of the Konvotech API.
        
        Returns:
            Dictionary containing the health status, typically {"status": "healthy"}
            
        Raises:
            APIError: If the API request fails
        """
        self._client.logger.debug("Checking API health")
        try:
            response = self._client.session.get(
                "https://api.konvotech.com/health",
                timeout=self._client.timeout
            )
            response.raise_for_status()
            self._client.logger.debug("Health check successful")
            return response.json()
        except requests.exceptions.RequestException as e:
            self._client.logger.error("Health check failed: %s", str(e))
            status_code = e.response.status_code if e.response else None
            raise APIError(f"API request failed: {str(e)}", status_code) from e

class KonvoClient:
    """Client for interacting with the Konvotech API."""

    BASE_URL = "https://api.konvotech.com/v1"
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(self, api_key: str, max_retries: int = 3, log_level: str = "WARNING", timeout: int = None):
        """Initialize the client with an API key.
        
        Args:
            api_key: Your Konvotech API key
            max_retries: Maximum number of retries for failed requests
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            timeout: Timeout in seconds for API requests (default: 30)
        """
        # Configure logging
        self.logger = logging.getLogger("konvo")
        self.logger.setLevel(log_level)
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        # Configure session
        self.api_key = api_key
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.system = System(self)
        self.logger.debug("KonvoClient initialized with max_retries=%d, timeout=%d", max_retries, self.timeout)
