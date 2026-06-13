"""Service Permission Scope types — fine-grained access control for external services."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Service(Enum):
    GMAIL = "gmail"
    CALENDAR = "calendar"
    GITHUB = "github"
    BROWSER = "browser"
    CLOUD_STORAGE = "cloud_storage"
    SNS = "sns"
    DISCORD = "discord"
    SLACK = "slack"
    X_TWITTER = "x_twitter"
    NOTION = "notion"
    FILE_SYSTEM = "file_system"
    EXTERNAL_API = "external_api"
    PC = "pc"
    ANDROID = "android"
    CUSTOM = "custom"


class Operation(Enum):
    READ = "read"
    SEARCH = "search"
    SUMMARIZE = "summarize"
    DRAFT = "draft"
    EDIT_DRAFT = "edit_draft"
    CREATE = "create"
    UPDATE = "update"
    SEND = "send"
    PUBLISH = "publish"
    DELETE = "delete"
    ARCHIVE = "archive"
    MOVE = "move"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    SHARE = "share"
    CHANGE_PERMISSION = "change_permission"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    LOGIN = "login"
    LOGOUT = "logout"
    CREDENTIAL_ACCESS = "credential_access"
    ADMIN = "admin"


class OperationCategory(Enum):
    SAFE_READ = "safe_read"
    LOW_RISK_WRITE = "low_risk_write"
    MEDIUM_RISK_WRITE = "medium_risk_write"
    HIGH_RISK_EXTERNAL_EFFECT = "high_risk_external_effect"
    DESTRUCTIVE = "destructive"
    FINANCIAL_OR_LEGAL = "financial_or_legal"


_OPERATION_CATEGORIES: dict[Operation, OperationCategory] = {
    Operation.READ: OperationCategory.SAFE_READ,
    Operation.SEARCH: OperationCategory.SAFE_READ,
    Operation.SUMMARIZE: OperationCategory.SAFE_READ,
    Operation.DRAFT: OperationCategory.LOW_RISK_WRITE,
    Operation.EDIT_DRAFT: OperationCategory.LOW_RISK_WRITE,
    Operation.CREATE: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.UPDATE: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.MOVE: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.ARCHIVE: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.SEND: OperationCategory.HIGH_RISK_EXTERNAL_EFFECT,
    Operation.PUBLISH: OperationCategory.HIGH_RISK_EXTERNAL_EFFECT,
    Operation.SHARE: OperationCategory.HIGH_RISK_EXTERNAL_EFFECT,
    Operation.DOWNLOAD: OperationCategory.SAFE_READ,
    Operation.UPLOAD: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.DELETE: OperationCategory.DESTRUCTIVE,
    Operation.CHANGE_PERMISSION: OperationCategory.DESTRUCTIVE,
    Operation.PURCHASE: OperationCategory.FINANCIAL_OR_LEGAL,
    Operation.PAYMENT: OperationCategory.FINANCIAL_OR_LEGAL,
    Operation.LOGIN: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.LOGOUT: OperationCategory.MEDIUM_RISK_WRITE,
    Operation.CREDENTIAL_ACCESS: OperationCategory.DESTRUCTIVE,
    Operation.ADMIN: OperationCategory.DESTRUCTIVE,
}


def get_operation_category(operation: Operation) -> OperationCategory:
    return _OPERATION_CATEGORIES.get(operation, OperationCategory.MEDIUM_RISK_WRITE)


_CATEGORY_DEFAULT_DECISION: dict[OperationCategory, str] = {
    OperationCategory.SAFE_READ: "allow",
    OperationCategory.LOW_RISK_WRITE: "allow",
    OperationCategory.MEDIUM_RISK_WRITE: "ask_approval",
    OperationCategory.HIGH_RISK_EXTERNAL_EFFECT: "ask_approval",
    OperationCategory.DESTRUCTIVE: "ask_approval",
    OperationCategory.FINANCIAL_OR_LEGAL: "deny",
}


@dataclass
class ServicePermissionScope:
    scope_id: str = ""
    service: str = ""
    operation: str = ""
    resource_pattern: str = "*"
    allowed: bool = True
    requires_approval: bool = False
    risk_level: str = "low"
    allowed_sources: list[str] = field(default_factory=lambda: [
        "user_explicit", "scheduled", "event_driven", "desire_driven",
    ])
    requires_fresh_world_state: bool = False
    requires_verification: bool = True
    requires_user_present: bool = False
    cooldown_seconds: int = 0
    expires_at: int = 0
    created_at: int = 0
    updated_at: int = 0
    reason: str = ""

    def is_expired(self, now_ms: int | None = None) -> bool:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        return self.expires_at > 0 and now > self.expires_at

    def matches(self, service: str, operation: str, resource: str = "*") -> bool:
        if self.service != service:
            return False
        if self.operation != operation and self.operation != "*":
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "service": self.service,
            "operation": self.operation,
            "resource_pattern": self.resource_pattern,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "risk_level": self.risk_level,
            "allowed_sources": self.allowed_sources,
            "requires_fresh_world_state": self.requires_fresh_world_state,
            "requires_verification": self.requires_verification,
            "requires_user_present": self.requires_user_present,
            "cooldown_seconds": self.cooldown_seconds,
            "expires_at": self.expires_at,
            "reason": self.reason,
        }


@dataclass
class OAuthScopeMapping:
    service: str = ""
    oauth_scope: str = ""
    internal_scopes: list[str] = field(default_factory=list)
    risk_level: str = "low"
    description: str = ""
    requires_user_explanation: bool = False


_BROWSER_HIGH_RISK_KEYWORDS = {
    "send", "submit", "post", "delete", "share", "purchase",
    "pay", "buy", "publish", "tweet", "dm", "email",
}

_SERVICE_DOMAIN_MAP: dict[str, str] = {
    "mail.google.com": "gmail",
    "calendar.google.com": "calendar",
    "github.com": "github",
    "twitter.com": "x_twitter",
    "x.com": "x_twitter",
    "discord.com": "discord",
    "slack.com": "slack",
    "notion.so": "notion",
    "notion.site": "notion",
    "drive.google.com": "cloud_storage",
    "dropbox.com": "cloud_storage",
    "onedrive.live.com": "cloud_storage",
}


def infer_service_from_url(url: str) -> str:
    for domain, service in _SERVICE_DOMAIN_MAP.items():
        if domain in url:
            return service
    return "browser"


def infer_operation_from_element(label: str) -> str:
    label_lower = label.lower().strip()
    if any(kw in label_lower for kw in ("send", "送信")):
        return "send"
    if any(kw in label_lower for kw in ("submit", "提出", "送信")):
        return "publish"
    if any(kw in label_lower for kw in ("post", "投稿")):
        return "publish"
    if any(kw in label_lower for kw in ("delete", "削除")):
        return "delete"
    if any(kw in label_lower for kw in ("share", "共有")):
        return "share"
    if any(kw in label_lower for kw in ("purchase", "buy", "購入", "支払")):
        return "purchase"
    if any(kw in label_lower for kw in ("draft", "下書き")):
        return "draft"
    if any(kw in label_lower for kw in ("save", "保存")):
        return "create"
    if any(kw in label_lower for kw in ("edit", "編集")):
        return "update"
    if any(kw in label_lower for kw in ("read", "読む", "表示")):
        return "read"
    return "read"
