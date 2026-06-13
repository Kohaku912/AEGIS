"""Tests for WebhookSender and integration stubs."""

from __future__ import annotations

import json
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from aegis_ai.integrations.webhook_sender import (
    WebhookRequest,
    WebhookResponse,
    WebhookSender,
    _mask_headers,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestWebhookRequest:
    def test_create_request(self):
        req = WebhookRequest(url="https://example.com/hook", payload={"event": "test"})
        assert req.url == "https://example.com/hook"
        assert req.method == "POST"
        assert req.max_retries == 3

    def test_defaults(self):
        req = WebhookRequest()
        assert req.url == ""
        assert req.timeout_seconds == 30.0
        assert req.retry_count == 0


class TestWebhookResponse:
    def test_create_response(self):
        resp = WebhookResponse(success=True, status_code=200)
        assert resp.success is True
        assert resp.status_code == 200

    def test_error_response(self):
        resp = WebhookResponse(success=False, error="Timeout")
        assert resp.success is False
        assert resp.error == "Timeout"


class TestMaskHeaders:
    def test_masks_sensitive_headers(self):
        headers = {
            "Authorization": "Bearer token123",
            "X-Api-Key": "secret",
            "Content-Type": "application/json",
        }
        masked = _mask_headers(headers)
        assert masked["Authorization"] == "***MASKED***"
        assert masked["X-Api-Key"] == "***MASKED***"
        assert masked["Content-Type"] == "application/json"

    def test_no_sensitive_headers(self):
        headers = {"Content-Type": "application/json", "Accept": "text/plain"}
        masked = _mask_headers(headers)
        assert masked == headers


class TestWebhookSender:
    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_success(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok": true}'
        mock_client = MagicMock()
        mock_client.request.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(url="https://example.com/hook", payload={"event": "test"})
        resp = sender.send(req)
        assert resp.success is True
        assert resp.status_code == 200
        assert resp.attempts == 1

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_failure_4xx(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = '{"error": "bad request"}'
        mock_client = MagicMock()
        mock_client.request.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(url="https://example.com/hook", payload={"event": "test"})
        resp = sender.send(req)
        assert resp.success is False
        assert resp.status_code == 400

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_timeout_retries(self, mock_client_cls):
        import httpx as httpx_mod
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx_mod.TimeoutException("timeout")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(
            url="https://example.com/hook",
            payload={"event": "test"},
            max_retries=2,
        )
        resp = sender.send(req)
        assert resp.success is False
        assert "Timeout" in resp.error
        assert resp.attempts == 3

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_with_secret_signs_payload(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok": true}'
        mock_client = MagicMock()
        mock_client.request.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(
            url="https://example.com/hook",
            payload={"event": "test"},
            secret="my_secret_key",
        )
        resp = sender.send(req)
        assert resp.success is True
        call_headers = mock_client.request.call_args[1]["headers"]
        assert "X-Signature-256" in call_headers
        assert call_headers["X-Signature-256"].startswith("sha256=")

    def test_send_no_url_returns_error(self):
        sender = WebhookSender()
        req = WebhookRequest(url="", payload={"event": "test"})
        resp = sender.send(req)
        assert resp.success is False
        assert "No URL" in resp.error

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_generates_webhook_id(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok": true}'
        mock_client = MagicMock()
        mock_client.request.return_value = mock_resp
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(url="https://example.com/hook", payload={})
        resp = sender.send(req)
        assert resp.webhook_id.startswith("wh_")

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_success_2xx_range(self, mock_client_cls):
        for code in [200, 201, 204]:
            mock_resp = MagicMock()
            mock_resp.status_code = code
            mock_resp.text = ""
            mock_client = MagicMock()
            mock_client.request.return_value = mock_resp
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            sender = WebhookSender()
            req = WebhookRequest(url="https://example.com/hook", payload={})
            resp = sender.send(req)
            assert resp.success is True, f"Expected success for {code}"

    @patch("aegis_ai.integrations.webhook_sender.httpx.Client")
    def test_send_request_error_retries(self, mock_client_cls):
        import httpx as httpx_mod
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx_mod.ConnectError("connection refused")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        sender = WebhookSender()
        req = WebhookRequest(
            url="https://example.com/hook",
            payload={},
            max_retries=1,
        )
        resp = sender.send(req)
        assert resp.success is False
        assert resp.attempts == 2
