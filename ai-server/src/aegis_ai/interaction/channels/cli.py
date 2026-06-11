"""CLI Channel — command-line interface for AEGIS interaction."""

from __future__ import annotations

import time
import uuid

from aegis_ai.interaction.message import Channel, Message
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager


class CLIChannel:
    """Command-line interface for AEGIS.

    Usage:
        cli = CLIChannel(router=router)
        cli.run()  # Starts interactive loop
        # Or:
        response = cli.send("research Python 3.12")
    """

    def __init__(
        self,
        router: InteractionRouter,
        session_manager: SessionManager | None = None,
    ) -> None:
        self._router = router
        self._sessions = session_manager or SessionManager()
        self._session = self._sessions.get_or_create("cli_user", "cli")

    def send(self, text: str) -> str:
        """Send a message and get response text."""
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            channel=Channel.CLI,
            user_id="cli_user",
            session_id=self._session.session_id,
            text=text,
            timestamp_ms=int(time.time() * 1000),
        )

        self._sessions.add_message(self._session.session_id, message)
        response = self._router.route(message)
        self._sessions.add_response(self._session.session_id, response)

        return response.text

    def run(self) -> None:
        """Start interactive CLI loop."""
        print("AEGIS CLI — type 'quit' to exit, 'help' for commands")
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            # Special CLI commands
            if user_input.lower() == "approvals":
                self._show_approvals()
                continue
            if user_input.lower() == "status":
                self._show_status()
                continue
            if user_input.lower().startswith("approve "):
                self._approve(user_input.split(None, 1)[1])
                continue
            if user_input.lower().startswith("reject "):
                self._reject(user_input.split(None, 1)[1])
                continue

            # Normal message — route through interaction router
            response_text = self.send(user_input)
            print(f"\nAEGIS: {response_text}")

    def _show_approvals(self) -> None:
        """Show pending approvals."""
        if hasattr(self._router, '_approval') and self._router._approval:
            pending = self._router._approval.get_pending()
            if pending:
                print(f"\nPending approvals ({len(pending)}):")
                for r in pending:
                    print(f"  [{r.approval_id}] {r.tool_name} — {r.capability_id}")
            else:
                print("\nNo pending approvals.")
        else:
            print("\nApproval store not available.")

    def _show_status(self) -> None:
        """Show system status."""
        print("\nAEGIS Status:")
        print("  Dashboard: http://127.0.0.1:8090")
        print("  Approvals: http://127.0.0.1:8080/approvals")
        print("  Chat: http://127.0.0.1:8091/chat")

    def _approve(self, approval_id: str) -> None:
        """Approve a pending request."""
        if hasattr(self._router, '_approval') and self._router._approval:
            from approval import ApprovalType
            ok = self._router._approval.approve(approval_id, ApprovalType.ONE_TIME)
            if ok:
                print(f"Approved: {approval_id}")
            else:
                print(f"Failed to approve: {approval_id}")

    def _reject(self, approval_id: str) -> None:
        """Reject a pending request."""
        if hasattr(self._router, '_approval') and self._router._approval:
            ok = self._router._approval.reject(approval_id)
            if ok:
                print(f"Rejected: {approval_id}")
            else:
                print(f"Failed to reject: {approval_id}")
