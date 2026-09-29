"""Safety validator — validates capability definitions against safety rules.

Checks:
- Dangerous capability names
- Missing safety level
- Missing side_effects for Level 2+
- Level 2/3 without approval info
- Forbidden category proximity
- Capability id shape, against the schema's own pattern
"""

from __future__ import annotations

import re

from aegis_schema.models import CAPABILITY_ID_PATTERN, RiskLevel, ServerType
from aegis_schema.roster import PREFIXES_BY_TYPE_WITH_RETIRED

#: Every prefix a capability id may start with: the roster's short and canonical spellings for
#: the live servers, plus the retired ones that are still reachable. **Derived** from the roster
#: rather than re-spelled, so the SDK cannot drift from the schema's allowlist (B-15).
ALLOWED_SERVER_PREFIXES: tuple[str, ...] = tuple(
    prefix for prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.values() for prefix in prefixes
)

#: ``prefix -> ServerType``, the same direction. ``define_capability`` derives ``server_type``
#: from this, so a caller never restates what the prefix already says. Before 2026-09-29 the
#: default was ``ServerType.DEV``, which made the SDK build out of the box only for the server
#: deleted in Phase 9 — and made every other prefix fail with a message naming a ``server_type``
#: the caller had not chosen (B-14).
SERVER_TYPE_BY_PREFIX: dict[str, ServerType] = {
    prefix: server_type
    for server_type, prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.items()
    for prefix in prefixes
}

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

    # Check ID format. The pattern is the *schema's own*, imported rather than re-spelled: this
    # module used to carry an open-class regex (``^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$``) that
    # admitted any prefix, which is how the SDK came to document third-party ids the schema
    # refuses (B-14). One id space, one rule.
    if not re.match(CAPABILITY_ID_PATTERN, cap_id):
        prefix = cap_id.split(".")[0]
        if prefix not in ALLOWED_SERVER_PREFIXES:
            errors.append(
                f"capability ID '{cap_id}' is not in AEGIS's id space: '{prefix}' is not an "
                f"AEGIS server. A capability id is namespaced by the server that hosts it, so "
                f"the prefix must be one of {ALLOWED_SERVER_PREFIXES}; use the segments after "
                f"the first for your own namespace (e.g. 'room-server.myapp.do_thing')"
            )
        else:
            errors.append(
                f"capability ID '{cap_id}' must be '<server>.<action>' or "
                f"'<server>.<app>.<action>', with lowercase [a-z0-9_] segments"
            )

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
