"""Tests for Webhook, STT, and TTS integrations."""

from __future__ import annotations

import shutil
import tempfile

import pytest

from aegis_ai.integrations.stt_service import SpeechToTextService, STTRequest
from aegis_ai.integrations.tts_service import TextToSpeechService, TTSRequest
from aegis_ai.integrations.webhook_sender import (
    WebhookRequest,
    WebhookSender,
    _mask_headers,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestWebhookSender:
    def test_send_no_url(self):
        sender = WebhookSender()
        req = WebhookRequest(url="", payload={"test": True})
        resp = sender.send(req)
        assert resp.success is False
        assert "No URL" in resp.error

    def test_send_invalid_url(self):
        sender = WebhookSender()
        req = WebhookRequest(
            url="http://localhost:1",
            payload={"test": True},
            timeout_seconds=2,
            max_retries=0,
        )
        resp = sender.send(req)
        assert resp.success is False
        assert resp.attempts >= 1

    def test_webhook_id_generated(self):
        sender = WebhookSender()
        req = WebhookRequest(url="http://localhost:1", payload={})
        resp = sender.send(req)
        assert resp.webhook_id

    def test_mask_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret123",
            "X-Api-Key": "sk-abcdef1234567890abcdef1234567890",
        }
        masked = _mask_headers(headers)
        assert masked["Content-Type"] == "application/json"
        assert masked["Authorization"] == "***MASKED***"
        assert masked["X-Api-Key"] == "***MASKED***"

    def test_request_to_dict(self):
        req = WebhookRequest(
            webhook_id="wh1",
            url="https://example.com",
            method="POST",
            payload={"key": "value"},
        )
        assert req.webhook_id == "wh1"
        assert req.method == "POST"


class TestSpeechToTextService:
    def test_transcribe_no_file(self):
        svc = SpeechToTextService()
        req = STTRequest(audio_path="/nonexistent/file.wav")
        result = svc.transcribe(req)
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_transcribe_no_path(self):
        svc = SpeechToTextService()
        req = STTRequest(audio_path="")
        result = svc.transcribe(req)
        assert result.success is False

    def test_stt_id_generated(self):
        svc = SpeechToTextService()
        req = STTRequest(audio_path="/nonexistent")
        result = svc.transcribe(req)
        assert result.stt_id

    def test_stt_request_defaults(self):
        req = STTRequest()
        assert req.language == "ja"
        assert req.model_size == "base"


class TestTextToSpeechService:
    def test_synthesize_no_text(self):
        svc = TextToSpeechService()
        req = TTSRequest(text="")
        result = svc.synthesize(req)
        assert result.success is False
        assert "No text" in result.error

    def test_tts_id_generated(self):
        svc = TextToSpeechService()
        req = TTSRequest(text="hello")
        result = svc.synthesize(req)
        assert result.tts_id

    def test_tts_request_defaults(self):
        req = TTSRequest()
        assert req.voice == "ja-JP-NanamiNeural"
        assert req.rate == "+0%"


class TestIntegrationExports:
    def test_webhook_sender_importable(self):
        from aegis_ai.integrations import WebhookRequest, WebhookResponse, WebhookSender
        assert WebhookSender is not None
        assert WebhookRequest is not None
        assert WebhookResponse is not None

    def test_stt_importable(self):
        from aegis_ai.integrations import SpeechToTextService, STTRequest, STTResult
        assert SpeechToTextService is not None
        assert STTRequest is not None
        assert STTResult is not None

    def test_tts_importable(self):
        from aegis_ai.integrations import TextToSpeechService, TTSRequest, TTSResult
        assert TextToSpeechService is not None
        assert TTSRequest is not None
        assert TTSResult is not None

    def test_stubs_still_importable(self):
        from aegis_ai.integrations import DiscordStub, EmailStub, LINEStub, WebhookStub
        assert WebhookStub is not None
        assert LINEStub is not None
        assert DiscordStub is not None
        assert EmailStub is not None
