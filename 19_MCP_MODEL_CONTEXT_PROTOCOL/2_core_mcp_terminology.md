# Core MCP terminology

Chapter notes (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

Read first: [`1_introduction.md`](./1_introduction.md).  
Read next: [`3_communication_flow.md`](./3_communication_flow.md).

MCP is a standard like **HTTP** or **USB-C**: defined roles and messages. Like HTTP’s client/server, MCP has **host**, **client**, and **server**.

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [Big picture diagram](#1-big-picture-diagram) |
| 2 | [Host](#2-host) |
| 3 | [Client](#3-client) |
| 4 | [Server](#4-server) |
| 5 | [Quick comparison](#5-quick-comparison) |

---

## 1. Big picture diagram

```text
┌───────────────────────────────────────────── Host ─────────────────────────────────────────────┐
│  User-facing AI app (Claude Desktop, Cursor, ChatGPT, your LangChain app, …)                   │
│                                                                                              │
│   ┌─────────────┐  1:1   ┌─────────────┐  1:1   ┌─────────────┐                             │
│   │ MCP Client  │◄──────►│ MCP Server  │        │ MCP Server  │  …                          │
│   └─────────────┘        └─────────────┘        └─────────────┘                             │
│         │                      │                      │                                      │
└─────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────┘
          │                      │                      │
          │                 local or remote              │
          │                      ▼                      ▼
          │                 tools, resources, prompts, data APIs
          │
     LLM + orchestration inside Host
```

---

## 2. Host

The **overall application** where the user chats or works with an agent **equipped with external capabilities**.

Examples:

- AI chat apps — OpenAI **ChatGPT**, Anthropic **Claude Desktop**  
- AI-enhanced IDEs — **Cursor**, **Continue.dev**  
- Custom agents — apps built with **LangChain**, **smolagents**, Hugging Face SDK, etc.

The **host** is what **end users** open and interact with directly.

**Host responsibilities**

- Managing user interactions and **permissions**  
- Initiating connections to MCP servers via **MCP clients**  
- Orchestrating the flow: user request → LLM → external tools → result  
- Rendering results back to the user in a coherent format  

---

## 3. Client

The MCP **client** is a component **inside the host** — like a small plugin — that manages communication with **one** MCP server.

| Property | Meaning |
|----------|---------|
| **1:1** | One client ↔ one server. Three servers in Claude Desktop ⇒ three clients inside the host. |
| Protocol layer | Handles JSON-RPC and MCP method details (discovery, `tools/call`, …) |
| Bridge | Between the host’s logic and that server’s capabilities |

If you use Claude Desktop with multiple MCP servers, you have **one client per server**, all living inside the same host.

---

## 4. Server

The MCP **server** is the program that **exposes** tools, context, and prompt templates to the agent (via the client).

| Property | Meaning |
|----------|---------|
| Provides | **Tools**, **resources**, **prompts** (per spec) |
| Often | Lightweight wrapper around an API, database, filesystem, or script |
| Runs | **Locally** (same machine as host) or **remotely** (over the network) |
| Discovery | Exposes capabilities in a **standard** format the client can list |

Servers are gateways: they let the model reach the right data or action — databases, repos, APIs — in a controlled way.

**Topic 18 analogy:** `get_current_time()` in [`tools.py`](../18_AI_AGENTS_INTRO/tools.py) lived inside your project. An **MCP server** packages similar capabilities so **any** MCP host can use them the same way.

---

## 5. Quick comparison

| Term | One-line role | Lives where |
|------|---------------|-------------|
| **Host** | The AI app the user sees | Your laptop, IDE, browser app, … |
| **Client** | Talks MCP to **one** server | Inside the host |
| **Server** | Offers tools / resources / prompts | Subprocess, local service, or remote service |

---

## Next

[`3_communication_flow.md`](./3_communication_flow.md) — how host, client, and server work together step by step.
