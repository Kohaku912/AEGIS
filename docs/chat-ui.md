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
http://0.0.0.0:8091/chat
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | GET | Chat interface |
| `/chat/send` | POST | Send message (JSON: `{text, user_id, session_id}`) |
| `/chat/history` | GET | Get conversation history |
| `/chat/sessions` | GET | List sessions |
| `/health` | GET | Health check |

## Security

- Localhost only (0.0.0.0)
- No external exposure
- Requests go through PolicyEngine
- Tool requests redirect to Approval UI
