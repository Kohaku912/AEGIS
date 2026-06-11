"""Settings — AEGIS configuration management.

Provides:
- AEGISSettings: Pydantic models for all configuration
- SettingsStore: JSON-based persistence with audit logging
- SettingsPermissionGuard: Integration with PolicyEngine
- Validation: Safety rules for settings changes
"""

from aegis_ai.settings.defaults import create_default_settings  # noqa: F401
from aegis_ai.settings.models import (  # noqa: F401
    AEGISSettings,
    AutonomousSettings,
    CapabilityPermission,
    CapabilityPermissions,
    MemorySettings,
    NotificationSettings,
    PrivacySettings,
    ServerSettings,
)
from aegis_ai.settings.permissions import SettingsPermissionGuard  # noqa: F401
from aegis_ai.settings.store import SettingsStore  # noqa: F401
from aegis_ai.settings.validation import validate_settings_change  # noqa: F401
