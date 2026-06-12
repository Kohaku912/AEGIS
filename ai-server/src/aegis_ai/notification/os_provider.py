"""OS Notification Provider — sends desktop notifications.

Supports:
- Windows: PowerShell BurntToast or System.Windows.Forms
- macOS: osascript
- Linux: notify-send

Usage:
    provider = OsNotificationProvider()
    provider.send("Title", "Message body")
"""

from __future__ import annotations

import logging
import platform
import subprocess
from typing import Any

logger = logging.getLogger("aegis_ai.notification.os_provider")


class OsNotificationProvider:
    """OS-native notification provider.

    Sends desktop notifications using platform-specific methods.
    Falls back to logging if notification fails.
    """

    def __init__(self) -> None:
        self._platform = platform.system().lower()

    def send(self, title: str, body: str, urgency: str = "normal") -> bool:
        """Send a desktop notification.

        Args:
            title: Notification title
            body: Notification body
            urgency: low, normal, critical

        Returns:
            True if notification was sent successfully
        """
        try:
            if self._platform == "windows":
                return self._send_windows(title, body)
            elif self._platform == "darwin":
                return self._send_macos(title, body)
            elif self._platform == "linux":
                return self._send_linux(title, body, urgency)
            else:
                logger.info("Notification [%s]: %s", title, body)
                return True
        except Exception as e:
            logger.warning("Failed to send OS notification: %s", e)
            logger.info("Notification [%s]: %s", title, body)
            return False

    def _send_windows(self, title: str, body: str) -> bool:
        """Send notification on Windows using PowerShell."""
        # Escape quotes
        title_escaped = title.replace('"', '`"')
        body_escaped = body.replace('"', '`"')

        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
        <toast>
            <visual>
                <binding template="ToastGeneric">
                    <text>{title_escaped}</text>
                    <text>{body_escaped}</text>
                </binding>
            </visual>
        </toast>
"@

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AEGIS").Show($toast)
        '''

        try:
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, timeout=10, check=False,
            )
            return True
        except Exception:
            # Fallback to simple message
            try:
                subprocess.run(
                    ["powershell", "-Command", f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("{body_escaped}", "{title_escaped}")'],
                    capture_output=True, timeout=10, check=False,
                )
                return True
            except Exception:
                return False

    def _send_macos(self, title: str, body: str) -> bool:
        """Send notification on macOS using osascript."""
        script = f'display notification "{body}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10, check=False)
        return True

    def _send_linux(self, title: str, body: str, urgency: str = "normal") -> bool:
        """Send notification on Linux using notify-send."""
        subprocess.run(
            ["notify-send", f"--urgency={urgency}", title, body],
            capture_output=True, timeout=10, check=False,
        )
        return True

    def is_available(self) -> bool:
        """Check if OS notifications are available."""
        try:
            if self._platform == "windows":
                result = subprocess.run(
                    ["powershell", "-Command", "Get-Command New-BurntToastNotification -ErrorAction SilentlyContinue"],
                    capture_output=True, timeout=5, check=False,
                )
                return result.returncode == 0
            elif self._platform == "darwin":
                return True
            elif self._platform == "linux":
                result = subprocess.run(["which", "notify-send"], capture_output=True, timeout=5, check=False)
                return result.returncode == 0
        except Exception:
            pass
        return False
