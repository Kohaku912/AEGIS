"""Small helpers for passkey bootstrap operations."""

from __future__ import annotations

import secrets


def generate_bootstrap_token() -> str:
    """Generate a one-time bootstrap token for the admin passkey setup flow."""
    return secrets.token_urlsafe(32)


def main() -> None:
    print(generate_bootstrap_token())


if __name__ == "__main__":
    main()
