"""
Binance Futures Testnet API client.

Handles authentication (HMAC-SHA256 signing), request construction,
and low-level HTTP communication with the Binance Futures Testnet API.
"""

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot")

# ── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"
REQUEST_TIMEOUT = 15  # seconds


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, error_code: int, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(
            f"Binance API Error [{status_code}] (code {error_code}): {message}"
        )


class BinanceClient:
    """
    Low-level client for Binance Futures Testnet API.

    Handles request signing, authentication headers, and HTTP communication.
    All API interactions go through this client.
    """

    def __init__(self, api_key: str, api_secret: str):
        """
        Initialise the Binance client.

        Args:
            api_key: Binance Futures Testnet API key.
            api_secret: Binance Futures Testnet API secret.

        Raises:
            ValueError: If API key or secret is missing.
        """
        if not api_key or not api_secret:
            raise ValueError(
                "API key and secret are required. "
                "Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in your .env file."
            )

        self._api_key = api_key
        self._api_secret = api_secret
        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self._api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

        logger.info("BinanceClient initialized (testnet: %s)", BASE_URL)

    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC-SHA256 signature for a query string.

        Args:
            query_string: URL-encoded query string to sign.

        Returns:
            Hex-encoded HMAC-SHA256 signature.
        """
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        logger.debug("Signature generated for query string.")
        return signature

    def _get_timestamp(self) -> int:
        """Return current Unix timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _build_signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add timestamp and HMAC signature to request parameters.

        Args:
            params: Request parameters dictionary.

        Returns:
            Parameters dictionary with timestamp and signature appended.
        """
        params["timestamp"] = self._get_timestamp()
        query_string = urlencode(params)
        params["signature"] = self._generate_signature(query_string)
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request to the Binance API.

        Args:
            method: HTTP method ('GET' or 'POST').
            endpoint: API endpoint path.
            params: Request parameters.
            signed: Whether to sign the request with HMAC.

        Returns:
            Parsed JSON response dictionary.

        Raises:
            BinanceAPIError: If the API returns an error.
            requests.RequestException: On network failures.
        """
        url = f"{BASE_URL}{endpoint}"
        params = params or {}

        if signed:
            params = self._build_signed_params(params)

        logger.debug(
            "API Request: %s %s | params: %s",
            method,
            endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            if method.upper() == "GET":
                response = self._session.get(
                    url, params=params, timeout=REQUEST_TIMEOUT
                )
            elif method.upper() == "POST":
                response = self._session.post(
                    url, data=params, timeout=REQUEST_TIMEOUT
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(
                "API Response: %s %s | status: %d",
                method,
                endpoint,
                response.status_code,
            )

            data = response.json()

            # Check for API error response
            if response.status_code >= 400:
                error_code = data.get("code", -1)
                error_msg = data.get("msg", "Unknown error")
                logger.error(
                    "API error: status=%d code=%d msg=%s",
                    response.status_code,
                    error_code,
                    error_msg,
                )
                raise BinanceAPIError(
                    status_code=response.status_code,
                    error_code=error_code,
                    message=error_msg,
                )

            logger.debug("API Response body: %s", data)
            return data

        except requests.ConnectionError as e:
            logger.error("Connection error: %s", e)
            raise requests.ConnectionError(
                f"Failed to connect to Binance API ({BASE_URL}). "
                "Check your internet connection."
            ) from e

        except requests.Timeout as e:
            logger.error("Request timed out after %ds", REQUEST_TIMEOUT)
            raise requests.Timeout(
                f"Request to Binance API timed out after {REQUEST_TIMEOUT}s."
            ) from e

        except requests.RequestException as e:
            logger.error("Request failed: %s", e)
            raise

    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order on Binance Futures Testnet.

        Args:
            params: Order parameters (symbol, side, type, quantity, etc.).

        Returns:
            Order response dictionary from the API.
        """
        logger.info("Sending order request to Binance API...")
        return self._request("POST", ORDER_ENDPOINT, params=params)

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Fetch exchange information (available symbols, filters, etc.).

        Returns:
            Exchange information dictionary.
        """
        return self._request("GET", EXCHANGE_INFO_ENDPOINT, signed=False)
