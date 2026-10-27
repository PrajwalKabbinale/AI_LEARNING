# The communication protocol

Chapter notes (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

Read first: [`3_communication_flow.md`](./3_communication_flow.md).  
Read next: [`5_mcp_capabilities.md`](./5_mcp_capabilities.md).

MCP defines a **standard** way for clients and servers to exchange messages. This note covers:

1. **Message format** — JSON-RPC 2.0  
2. **Transport** — how messages move (stdio, HTTP + SSE / streamable HTTP)  
3. **Interaction lifecycle** — initialize → discover → execute → terminate  

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [JSON-RPC 2.0](#1-json-rpc-20) |
| 2 | [Three message types](#2-three-message-types) |
| 3 | [Transport mechanisms](#3-transport-mechanisms) |
| 4 | [The interaction lifecycle](#4-the-interaction-lifecycle) |

---

## 1. JSON-RPC 2.0

At its core, MCP uses **JSON-RPC 2.0** for all client–server messages.

| Property | Why it matters |
|----------|----------------|
| Human-readable | Easier to debug than binary protocols |
| Language-agnostic | Implement servers/clients in Python, TypeScript, Go, … |
| Well-established | Clear spec, wide adoption |

JSON-RPC is the **envelope**. MCP defines **which methods** exist (`tools/call`, discovery, etc.) inside that envelope.

---

## 2. Three message types

### Requests

Sent from **client → server** to start an operation.

| Field | Role |
|-------|------|
| `id` | Unique id so the response can match |
| `method` | What to run (e.g. `tools/call`) |
| `params` | Arguments for that method |

**Example request** (call a weather tool):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "weather",
    "arguments": {
      "location": "San Francisco"
    }
  }
}
```

### Responses

Sent from **server → client** for a matching `id`.

| Outcome | Body |
|---------|------|
| Success | `"result": { ... }` |
| Failure | `"error": { ... }` |

**Example success response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "temperature": 62,
    "conditions": "Partly cloudy"
  }
}
```

### Notifications

**One-way** messages — no `id`, no response required. Often **server → client** (e.g. progress).

**Example notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "progress",
  "params": {
    "message": "Processing data...",
    "percent": 50
  }
}
```

In practice, SDKs and hosts build these messages for you; knowing the shape helps when you read logs or debug.

---

## 3. Transport mechanisms

JSON-RPC is the **format**. **Transport** is how bytes travel between client and server.

### stdio (standard input / output)

| | |
|--|--|
| **How** | Host **launches** the server as a **subprocess**; client writes to server **stdin**, reads **stdout** |
| **Good for** | Local tools — filesystem, local scripts, dev utilities on your machine |
| **Pros** | Simple; no network setup; OS process isolation |

### HTTP + SSE / streamable HTTP

| | |
|--|--|
| **How** | Communication over **HTTP**; server may use **Server-Sent Events (SSE)** or streamable HTTP for ongoing updates |
| **Good for** | Remote APIs, cloud services, shared team servers, serverless-friendly setups |
| **Pros** | Works across networks; integrates with web infrastructure |

Same MCP **protocol**; different **pipes**. Local dev often uses **stdio**; shared or cloud servers often use **HTTP**.

---

## 4. The interaction lifecycle

Structured phases between client and server:

| Phase | What happens |
|-------|----------------|
| **Initialization** | Client connects; client and server exchange protocol versions and **capabilities**; client sends a notification that init is complete |
| **Discovery** | Client requests available capabilities; server returns lists of **tools**, **resources**, **prompts**, etc. |
| **Execution** | Client invokes capabilities as the host / LLM needs (e.g. `tools/call`) |
| **Termination** | Connection closes gracefully when finished; server acknowledges shutdown |

```text
Initialize  →  Discover  →  Execute (maybe many times)  →  Terminate
```

Think: **handshake → catalog → call → close** — similar to many other APIs, but standardized for MCP.

---

## Next

[`5_mcp_capabilities.md`](./5_mcp_capabilities.md) — Tools, Resources, Prompts, and Sampling.
