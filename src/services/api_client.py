"""
Z.AI API client for challenge evaluation.
Uses httpx for HTTP requests with OpenAI-compatible format.
"""
import os
from typing import List, Optional

import httpx

from src.models.evaluation import Message


class APIError(Exception):
    """Custom exception for API-related errors."""

    pass


class ZAIClient:
    """
    Client for Z.AI GLM-4.7 model API.
    OpenAI-compatible format: POST /chat/completions
    """

    BASE_URLS = {
        "default": "https://api.z.ai/api/paas/v4",
        "coding": "https://api.z.ai/api/coding/paas/v4",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "default",
        timeout: float = 60.0,
    ):
        """
        Initialize the Z.AI API client.

        Args:
            api_key: API key for authentication. If not provided,
                     reads from ZAI_API_KEY environment variable.
            base_url: Which base URL to use ("default" or "coding").
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        if not self.api_key:
            raise APIError(
                "API key not found. Set ZAI_API_KEY environment variable."
            )

        self.base_url = self.BASE_URLS.get(base_url, base_url)
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def chat_completion(
        self,
        messages: List[Message],
        model: str = "glm-4.7",
        temperature: float = 0.7,
    ) -> str:
        """
        Send messages to the API and get completion response.

        Args:
            messages: List of Message objects for conversation history
            model: Model identifier
            temperature: Sampling temperature

        Returns:
            Assistant's response content

        Raises:
            APIError: On API communication failure
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
        }

        try:
            response = self._client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            raise APIError(
                f"API request failed: {e.response.status_code} - "
                f"{e.response.text}"
            )
        except httpx.RequestError as e:
            raise APIError(f"Network error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise APIError(f"Unexpected API response format: {str(e)}")

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "ZAIClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.close()
