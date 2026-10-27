# Communication flow

Chapter notes (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

Read first: [`2_core_mcp_terminology.md`](./2_core_mcp_terminology.md).  
Read next: [`4_the_communication_protocol.md`](./4_the_communication_protocol.md).

This note describes **how** the host, client, and server interact in a typical MCP workflow — before diving into JSON-RPC and transports in the next file.

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [Seven-step workflow](#1-seven-step-workflow) |
| 2 | [Why modularity matters](#2-why-modularity-matters) |
| 3 | [M×N reminder](#3-mn-reminder) |

---

## 1. Seven-step workflow

1. **User interaction** — The user interacts with the **host** (question, command, or task).  
2. **Host processing** — The host processes input, often with an **LLM**, to understand intent and whether external help is needed.  
3. **Client connection** — The host uses its **MCP client(s)** to reach the right **server(s)**.  
4. **Capability discovery** — The client asks the server what it offers (**tools**, **resources**, **prompts**).  
5. **Capability invocation** — Based on the user or LLM, the host instructs the client to call a specific capability (e.g. `tools/call`).  
6. **Server execution** — The server runs the action or returns data to the client.  
7. **Result integration** — The client returns results to the host; the host feeds the LLM and/or shows the user.

```text
User
  │
  ▼
Host (+ LLM) ──► MCP Client ──► MCP Server ──► external API / files / DB
  │                    │              │
  │                    └──── result ───┘
  ▼
User sees answer
```

---

## 2. Why modularity matters

| Benefit | Meaning |
|---------|---------|
| **Many servers** | One host can connect to several servers at once (one client each). |
| **Add without breaking** | New servers can join the ecosystem without changing existing hosts. |
| **Compose** | Combine capabilities from different servers in one session. |

This architecture is what makes the **M+N** integration story practical (see [`1_introduction.md`](./1_introduction.md)).

---

## 3. M×N reminder

Without MCP, each AI app might integrate with each tool **individually** (M×N custom glue). With MCP, each host implements the **client** side once and each provider implements the **server** side once — **M + N** standard implementations.

---

## Next

[`4_the_communication_protocol.md`](./4_the_communication_protocol.md) — JSON-RPC messages, transport (stdio / HTTP), and the interaction lifecycle.
