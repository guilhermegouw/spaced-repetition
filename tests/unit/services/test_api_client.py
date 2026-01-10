"""Tests for Z.AI API client."""
import os
from unittest.mock import Mock, patch

import httpx
import pytest

from src.models.evaluation import Message
from src.services.api_client import APIError, ZAIClient


class TestZAIClientInit:
    """Tests for ZAIClient initialization."""

    def test_init_without_api_key_raises_error(self):
        """Should raise APIError if no API key provided."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(APIError, match="API key not found"):
                ZAIClient()

    def test_init_with_env_api_key(self):
        """Should use API key from environment."""
        with patch.dict(os.environ, {"ZAI_API_KEY": "test-key"}):
            client = ZAIClient()
            assert client.api_key == "test-key"
            client.close()

    def test_init_with_explicit_api_key(self):
        """Should use explicitly provided API key."""
        client = ZAIClient(api_key="explicit-key")
        assert client.api_key == "explicit-key"
        client.close()

    def test_default_base_url(self):
        """Should use default base URL."""
        client = ZAIClient(api_key="key")
        assert client.base_url == ZAIClient.BASE_URLS["default"]
        client.close()

    def test_coding_base_url(self):
        """Should use coding base URL when specified."""
        client = ZAIClient(api_key="key", base_url="coding")
        assert client.base_url == ZAIClient.BASE_URLS["coding"]
        client.close()

    def test_custom_base_url(self):
        """Should use custom base URL if not a preset."""
        client = ZAIClient(api_key="key", base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"
        client.close()


class TestZAIClientChatCompletion:
    """Tests for chat completion API calls."""

    @pytest.fixture
    def client(self):
        """Create client with test key."""
        client = ZAIClient(api_key="test-key")
        yield client
        client.close()

    @pytest.fixture
    def messages(self):
        """Create test messages."""
        return [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hello"),
        ]

    def test_chat_completion_success(self, client, messages):
        """Should return assistant message on success."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status = Mock()

        with patch.object(client._client, "post", return_value=mock_response):
            result = client.chat_completion(messages)

        assert result == "Test response"

    def test_chat_completion_sends_correct_payload(self, client, messages):
        """Should send correctly formatted payload."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_response.raise_for_status = Mock()

        with patch.object(
            client._client, "post", return_value=mock_response
        ) as mock_post:
            client.chat_completion(messages, model="glm-4.7", temperature=0.5)

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["model"] == "glm-4.7"
        assert payload["temperature"] == 0.5
        assert len(payload["messages"]) == 2

    def test_chat_completion_http_error(self, client, messages):
        """Should raise APIError on HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        error = httpx.HTTPStatusError(
            "Error", request=Mock(), response=mock_response
        )

        with patch.object(client._client, "post", side_effect=error):
            with pytest.raises(APIError, match="API request failed"):
                client.chat_completion(messages)

    def test_chat_completion_network_error(self, client, messages):
        """Should raise APIError on network error."""
        with patch.object(
            client._client,
            "post",
            side_effect=httpx.RequestError("Connection failed"),
        ):
            with pytest.raises(APIError, match="Network error"):
                client.chat_completion(messages)

    def test_chat_completion_invalid_response_format(self, client, messages):
        """Should raise APIError on unexpected response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "format"}
        mock_response.raise_for_status = Mock()

        with patch.object(client._client, "post", return_value=mock_response):
            with pytest.raises(APIError, match="Unexpected API response"):
                client.chat_completion(messages)


class TestZAIClientContextManager:
    """Tests for context manager support."""

    def test_context_manager(self):
        """Should work as context manager."""
        with ZAIClient(api_key="key") as client:
            assert client.api_key == "key"

    def test_context_manager_closes_client(self):
        """Should close client on exit."""
        client = ZAIClient(api_key="key")
        with patch.object(client._client, "close") as mock_close:
            with client:
                pass
            mock_close.assert_called_once()
