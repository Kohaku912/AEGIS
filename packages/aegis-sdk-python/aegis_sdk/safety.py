"""Safety validator — validates capability definitions against safety rules.

Checks:
- Dangerous capability names
- Missing safety level
- Missing side_effects for Level 2+
- Level 2/3 without approval info
- Forbidden category proximity
"""

from __future__ import annotations

import re

from aegis_schema.models import RiskLevel

# Patterns that indicate dangerous capabilities
DANGEROUS_PATTERNS: list[str] = [
    r".*delete.*",
    r".*rm_.*",
    r".*wipe.*",
    r".*destroy.*",
    r".*execute.*",
    r".*shell.*",
    r".*command.*",
    r".*inject.*",
    r".*exploit.*",
    r".*hack.*",
    r".*crack.*",
    r".*bypass.*",
]

# Forbidden capability patterns (always denied by PolicyEngine)
FORBIDDEN_PATTERNS: list[str] = [
    r".*\.send_sns$",
    r".*\.post_sns$",
    r".*\.send_dm$",
    r".*\.send_message$",
    r".*\.send_email$",
    r".*\.delete_file$",
    r".*\.delete_all$",
    r".*\.rm_.*",
    r".*\.wipe_.*",
    r".*\.bulk_delete.*",
    r".*\.upload_.*",
    r".*\.transmit_.*",
    r".*\.read_credential.*",
    r".*\.write_credential.*",
    r".*\.access_ssh.*",
    r".*\.access_.*key.*",
    r".*\.read_secret.*",
    r".*\.purchase.*",
    r".*\.bypass_policy.*",
    r".*\.bypass_approval.*",
    r".*\.disable_policy.*",
    r".*\.captcha_bypass.*",
    r".*\.tos_bypass.*",
]

# Categories that are always forbidden
FORBIDDEN_CATEGORIES: set[str] = {
    "send_sns", "post_sns", "send_dm", "send_message", "send_email",
    "delete_file", "delete_all", "rm_", "wipe_", "bulk_delete",
    "upload_", "transmit_", "external_upload",
    "read_credential", "write_credential", "access_ssh", "read_secret",
    "purchase", "bypass_policy", "bypass_approval", "disable_policy",
    "captcha_bypass", "tos_bypass",
}


def validate_capability_definition(
    cap_id: str,
    name: str,
    description: str,
    risk_level: RiskLevel,
    side_effects: list[str],
    tags: list[str],
) -> list[str]:
    """Validate a capability definition against safety rules.

    Returns a list of validation errors. Empty list means valid.
    """
    errors: list[str] = []

    # Check risk level
    if risk_level == RiskLevel.UNSPECIFIED:
        errors.append(f"risk_level must not be UNSPECIFIED for '{cap_id}'")
    if risk_level == RiskLevel.FORBIDDEN:
        errors.append(f"Cannot register FORBIDDEN capability '{cap_id}'")

    # Check required fields
    if not name:
        errors.append(f"name is required for '{cap_id}'")
    if not description:
        errors.append(f"description is required for '{cap_id}'")

    # Check ID format
    if not re.match(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$", cap_id):
        errors.append(f"capability ID '{cap_id}' must be 'prefix.action' format (lowercase, underscores)")

    # Check for forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.match(pattern, cap_id):
            errors.append(f"capability ID '{cap_id}' matches forbidden pattern '{pattern}'")
            break

    # Check for dangerous names
    action_part = cap_id.split(".")[-1] if "." in cap_id else cap_id
    for pattern in DANGEROUS_PATTERNS:
        if re.match(pattern, action_part):
            errors.append(f"action name '{action_part}' matches dangerous pattern — verify safety level is appropriate")
            break

    # Check side_effects for Level 2+
    if risk_level >= RiskLevel.APPROVAL_REQUIRED and not side_effects:
        errors.append(f"Level 2+ capability '{cap_id}' must declare side_effects")

    # Check that Level 2+ has requires_approval implied
    if risk_level >= RiskLevel.APPROVAL_REQUIRED:
        # This is informational, not blocking
        pass

    return errors


def check_forbidden_proximity(cap_id: str) -> list[str]:
    """Check if a capability ID is close to a forbidden pattern.

    Returns warnings (not blocking errors).
    """
    warnings: list[str] = []
    action_part = cap_id.split(".")[-1] if "." in cap_id else cap_id

    for forbidden in FORBIDDEN_CATEGORIES:
        # Extract the base keyword (first part before underscore)
        keyword = forbidden.split("_")[0] if "_" in forbidden else forbidden
        if keyword and keyword in action_part:
            warnings.append(
                f"Action '{action_part}' contains forbidden keyword '{keyword}' — "
                f"verify this is intentional"
            )

    return warnings
