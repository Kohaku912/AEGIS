"""Validation rules for settings changes.

Ensures settings changes cannot weaken safety guarantees.
"""

from __future__ import annotations

from aegis_ai.settings.models import AEGISSettings

# Capabilities that can NEVER be enabled by settings
FORBIDDEN_CAPABILITIES: set[str] = {
    "browser.send_sns", "browser.post_sns", "browser.send_dm",
    "browser.send_message", "browser.send_email",
    "browser.purchase_item", "browser.captcha_bypass", "browser.tos_bypass",
    "pc.delete_file", "pc.bulk_delete", "pc.read_secret_file",
    "pc.write_system_config", "pc.run_shell_command", "pc.type_password",
    "pc.click_payment_button", "pc.modify_policy",
    "android.send_sms", "android.send_dm", "android.post_sns",
    "android.access_contacts", "android.make_call",
    "android.type_password", "android.click_payment_button",
    "android.captcha_bypass", "android.tos_bypass",
    "room.move_robot_arm", "room.robot_arm_move", "room.lock_door",
    "room.ac_power_on",
    "dev.merge_to_main", "dev.push_main", "dev.deploy_production",
    "dev.production_deploy", "dev.read_secrets", "dev.delete_repo",
    "dev.mount_docker_socket", "dev.install_system_package",
    "dev.disable_policy_engine", "dev.modify_approval_bypass",
}


def validate_settings_change(
    current: AEGISSettings,
    proposed: AEGISSettings,
) -> list[str]:
    """Validate a proposed settings change.

    Returns a list of validation errors. Empty list means valid.
    """
    errors: list[str] = []

    # Check that forbidden capabilities are not re-enabled
    for cap_id in proposed.capabilities.disabled_capabilities:
        if cap_id in FORBIDDEN_CAPABILITIES:
            # This is fine — forbidden caps should be disabled
            pass

    # Check that no forbidden capability is in allowlist
    for cap_id in proposed.capabilities.allowlist:
        if cap_id in FORBIDDEN_CAPABILITIES:
            errors.append(f"Cannot add forbidden capability '{cap_id}' to allowlist")

    # Check that no forbidden capability is enabled via per_capability
    for cap_id, perm in proposed.capabilities.per_capability.items():
        if cap_id in FORBIDDEN_CAPABILITIES and perm.enabled:
            errors.append(f"Cannot enable forbidden capability '{cap_id}'")

    # Check privacy settings
    if proposed.privacy.camera_snapshot_enabled and not current.privacy.camera_snapshot_enabled:
        errors.append("Enabling camera snapshot requires explicit user confirmation")

    # Check autonomous limits
    if proposed.autonomous.max_autonomous_runs_per_hour > 100:
        errors.append("Max autonomous runs per hour cannot exceed 100")

    return errors
