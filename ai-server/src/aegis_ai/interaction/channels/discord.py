"""Discord Channel (inbound) — not implemented.

Nothing receives Discord messages, and nothing routes them into the Interaction Hub.

*Outbound* Discord sending **is** implemented, in
``aegis_ai/notification/channels/discord.py``, and it goes through the egress permission
check (``aegis_ai/egress/``) — user information may only leave with the user's permission.
This module is the inbound side, which does not exist; it is not a stub of the outbound
path.
"""
