"""External integrations — registry, webhooks, and speech services."""

from aegis_ai.integrations.models import (  # noqa: F401
    IntegrationConfig,
    IntegrationDirection,
    IntegrationStatus,
    IntegrationType,
)
from aegis_ai.integrations.registry import IntegrationRegistry  # noqa: F401
from aegis_ai.integrations.stt_service import SpeechToTextService, STTRequest, STTResult  # noqa: F401
from aegis_ai.integrations.tts_service import TextToSpeechService, TTSRequest, TTSResult  # noqa: F401
from aegis_ai.integrations.webhook_sender import WebhookRequest, WebhookResponse, WebhookSender  # noqa: F401
