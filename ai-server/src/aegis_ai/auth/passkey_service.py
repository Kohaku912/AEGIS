"""WebAuthn/Passkey registration and authentication service."""

from __future__ import annotations

import base64
import os
import secrets
import uuid
from dataclasses import dataclass
from typing import Any

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from aegis_ai.auth.models import AuthChallenge, AuthEvent, AuthUser, PasskeyCredential
from aegis_ai.auth.passkey_store import PasskeyStore, now_ms


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class PasskeyConfig:
    rp_id: str
    rp_name: str
    origins: list[str]
    production: bool = False
    challenge_ttl_ms: int = 5 * 60 * 1000

    @classmethod
    def from_env(cls) -> "PasskeyConfig":
        runtime_mode = os.getenv("AEGIS_RUNTIME_MODE", "development").strip().lower()
        production = runtime_mode == "production"
        rp_id = os.getenv("AEGIS_WEBAUTHN_RP_ID", "").strip()
        if not rp_id:
            rp_id = "localhost" if not production else "kawahara.pp.ua"
        rp_name = os.getenv("AEGIS_WEBAUTHN_RP_NAME", "AEGIS Dashboard").strip() or "AEGIS Dashboard"
        origins = _split_csv(os.getenv("AEGIS_WEBAUTHN_ORIGINS", ""))
        if not origins and not production:
            origins = [
                "http://localhost:8090",
                "http://127.0.0.1:8090",
                "http://localhost:8091",
                "http://127.0.0.1:8091",
            ]
        if not origins and production:
            origins = [f"https://{rp_id}"]
        return cls(rp_id=rp_id, rp_name=rp_name, origins=origins, production=production)


class PasskeyService:
    """High-level passkey service."""

    def __init__(self, store: PasskeyStore, config: PasskeyConfig | None = None) -> None:
        self.store = store
        self.config = config or PasskeyConfig.from_env()

    def bootstrap_allowed(self, token: str = "") -> bool:
        if self.store.has_users():
            return False
        configured = os.getenv("AEGIS_AUTH_BOOTSTRAP_TOKEN", "").strip()
        legacy = os.getenv("AEGIS_DASHBOARD_ACCESS_TOKEN", "").strip()
        if configured:
            return secrets.compare_digest(token, configured)
        if legacy and token:
            return secrets.compare_digest(token, legacy)
        return not self.config.production

    def bootstrap_status(self) -> dict[str, Any]:
        return {
            "allowed": not self.store.has_users(),
            "has_users": self.store.has_users(),
            "bootstrap_token_configured": bool(os.getenv("AEGIS_AUTH_BOOTSTRAP_TOKEN", "").strip()),
            "legacy_token_configured": bool(os.getenv("AEGIS_DASHBOARD_ACCESS_TOKEN", "").strip()),
            "rp_id": self.config.rp_id,
            "origins": self.config.origins,
        }

    def registration_options(
        self,
        *,
        username: str,
        display_name: str,
        bootstrap_token: str = "",
        session_user_id: str = "",
    ) -> dict[str, Any]:
        username = username.strip() or "admin"
        display_name = display_name.strip() or username
        user = self.store.get_user_by_name(username)
        bootstrap = False
        if user is None:
            if not self.bootstrap_allowed(bootstrap_token):
                raise PermissionError("Passkey bootstrap token is required for the first admin registration.")
            bootstrap = True
            user_id = b64url_encode(uuid.uuid4().bytes)
        else:
            if session_user_id != user.user_id:
                raise PermissionError("Authenticated session is required to register another passkey.")
            user_id = user.user_id

        challenge = secrets.token_bytes(32)
        exclude = [
            PublicKeyCredentialDescriptor(id=b64url_decode(credential.credential_id))
            for credential in self.store.list_credentials(user_id)
        ]
        options = generate_registration_options(
            rp_id=self.config.rp_id,
            rp_name=self.config.rp_name,
            user_name=username,
            user_id=user_id.encode("utf-8"),
            user_display_name=display_name,
            challenge=challenge,
            timeout=60_000,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                require_resident_key=True,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            exclude_credentials=exclude,
        )
        challenge_id = secrets.token_urlsafe(18)
        self.store.add_challenge(
            AuthChallenge(
                challenge_id=challenge_id,
                challenge=b64url_encode(challenge),
                kind="registration",
                user_id=user_id,
                username=username,
                display_name=display_name,
                created_at=now_ms(),
                expires_at=now_ms() + self.config.challenge_ttl_ms,
                bootstrap=bootstrap,
            )
        )
        payload = _json_options(options)
        payload["challenge_id"] = challenge_id
        return payload

    def verify_registration(self, *, challenge_id: str, credential: dict[str, Any], origin: str) -> dict[str, Any]:
        self._assert_origin(origin)
        challenge = self.store.consume_challenge(challenge_id, "registration")
        if challenge is None:
            raise PermissionError("Registration challenge is invalid, expired, or already used.")
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=b64url_decode(challenge.challenge),
            expected_rp_id=self.config.rp_id,
            expected_origin=self.config.origins,
            require_user_verification=True,
        )
        user = self.store.get_user(challenge.user_id)
        if user is None:
            user = AuthUser(
                user_id=challenge.user_id,
                username=challenge.username,
                display_name=challenge.display_name or challenge.username,
                role="admin",
                created_at=now_ms(),
            )
            self.store.add_user(user)
        credential_id = b64url_encode(verified.credential_id)
        passkey = PasskeyCredential(
            credential_id=credential_id,
            user_id=user.user_id,
            public_key=b64url_encode(verified.credential_public_key),
            sign_count=verified.sign_count,
            nickname=credential.get("nickname") or "Passkey",
            aaguid=str(verified.aaguid),
            device_type=str(getattr(verified.credential_device_type, "value", verified.credential_device_type)),
            backed_up=bool(verified.credential_backed_up),
            created_at=now_ms(),
        )
        self.store.add_credential(passkey)
        self._event("passkey.registered", user.user_id, {"credential_id": credential_id, "bootstrap": challenge.bootstrap})
        return {"user": user.to_dict(), "credential": _public_credential(passkey)}

    def authentication_options(self) -> dict[str, Any]:
        challenge = secrets.token_bytes(32)
        options = generate_authentication_options(
            rp_id=self.config.rp_id,
            challenge=challenge,
            timeout=60_000,
            allow_credentials=None,
            user_verification=UserVerificationRequirement.REQUIRED,
        )
        challenge_id = secrets.token_urlsafe(18)
        self.store.add_challenge(
            AuthChallenge(
                challenge_id=challenge_id,
                challenge=b64url_encode(challenge),
                kind="authentication",
                created_at=now_ms(),
                expires_at=now_ms() + self.config.challenge_ttl_ms,
            )
        )
        payload = _json_options(options)
        payload["challenge_id"] = challenge_id
        return payload

    def verify_authentication(self, *, challenge_id: str, credential: dict[str, Any], origin: str) -> dict[str, Any]:
        self._assert_origin(origin)
        challenge = self.store.consume_challenge(challenge_id, "authentication")
        if challenge is None:
            raise PermissionError("Authentication challenge is invalid, expired, or already used.")
        raw_id = credential.get("rawId") or credential.get("id") or ""
        credential_id = raw_id if isinstance(raw_id, str) else ""
        stored = self.store.get_credential(credential_id)
        if stored is None:
            raise PermissionError("Passkey is not registered for this AEGIS instance.")
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=b64url_decode(challenge.challenge),
            expected_rp_id=self.config.rp_id,
            expected_origin=self.config.origins,
            credential_public_key=b64url_decode(stored.public_key),
            credential_current_sign_count=stored.sign_count,
            require_user_verification=True,
        )
        stored.sign_count = verified.new_sign_count
        stored.last_used_at = now_ms()
        stored.device_type = str(getattr(verified.credential_device_type, "value", verified.credential_device_type))
        stored.backed_up = bool(verified.credential_backed_up)
        self.store.update_credential(stored)
        user = self.store.get_user(stored.user_id)
        if user is None:
            raise PermissionError("Passkey user is missing.")
        self._event("passkey.login", user.user_id, {"credential_id": stored.credential_id})
        return {"user": user.to_dict(), "credential": _public_credential(stored)}

    def list_passkeys(self, user_id: str) -> list[dict[str, Any]]:
        return [_public_credential(item) for item in self.store.list_credentials(user_id)]

    def rename_passkey(self, credential_id: str, user_id: str, nickname: str) -> dict[str, Any]:
        credential = self.store.get_credential(credential_id)
        if credential is None or credential.user_id != user_id:
            raise KeyError("Passkey not found.")
        credential.nickname = nickname.strip()[:80] or "Passkey"
        self.store.update_credential(credential)
        self._event("passkey.renamed", user_id, {"credential_id": credential_id})
        return _public_credential(credential)

    def delete_passkey(self, credential_id: str, user_id: str) -> bool:
        credentials = self.store.list_credentials(user_id)
        if len(credentials) <= 1:
            raise PermissionError("Cannot delete the last passkey.")
        ok = self.store.delete_credential(credential_id, user_id)
        if ok:
            self._event("passkey.deleted", user_id, {"credential_id": credential_id})
        return ok

    def _assert_origin(self, origin: str) -> None:
        if not origin:
            raise PermissionError("Origin header is required.")
        if origin not in self.config.origins:
            raise PermissionError("Origin is not allowed for this relying party.")
        if self.config.production and origin.startswith("http://"):
            raise PermissionError("HTTPS origin is required in production.")

    def _event(self, event_type: str, user_id: str, detail: dict[str, Any]) -> None:
        self.store.add_event(
            AuthEvent(
                event_id=f"auth_{uuid.uuid4().hex[:10]}",
                event_type=event_type,
                user_id=user_id,
                detail=detail,
                created_at=now_ms(),
            )
        )


def _json_options(options: Any) -> dict[str, Any]:
    import json

    return json.loads(options_to_json(options))


def _public_credential(credential: PasskeyCredential) -> dict[str, Any]:
    return {
        "credential_id": credential.credential_id,
        "nickname": credential.nickname,
        "aaguid": credential.aaguid,
        "device_type": credential.device_type,
        "backed_up": credential.backed_up,
        "created_at": credential.created_at,
        "last_used_at": credential.last_used_at,
    }
