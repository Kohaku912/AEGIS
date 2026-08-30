# Chat UI — Web-based Chat Interface

> **Status**: Implemented
> **Related**: `docs/interaction-hub.md`

## Overview

The Chat UI provides a web-based chat interface for interacting with AEGIS.

## Features

- Message input and response display
- Conversation history
- Session management
- Source/citation display
- Pending approval links
- Localhost only

## Access

```
http://localhost:8090/chat
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | GET | Chat interface (SPA) |
| `/api/chat/send` | POST | Send message |
| `/api/chat/history` | GET | Get conversation history |
| `/health` | GET | Health check |

## Security

- Served by the Dashboard on port 8090
- Auth follows Dashboard passkey/session settings
- Requests go through PolicyEngine
- Tool requests redirect to Approval UI
