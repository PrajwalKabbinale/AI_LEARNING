# FastMCP — build MCP servers in Python

Chapter notes (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

**FastMCP** is a **high-level, Pythonic** library for building **MCP servers**. You write normal Python functions; FastMCP handles much of the **JSON-RPC**, schema, and server wiring so you do not have to implement the protocol by hand.

Think of it like **FastAPI for MCP**: decorators + type hints instead of writing every low-level message yourself.

Read first: notes **`1_` → `5_`** in [`README.md`](./README.md) (what MCP is, host/client/server, protocol, capabilities).  
Official MCP spec: [modelcontextprotocol.io](https://modelcontextprotocol.io).  
FastMCP project docs: [gofastmcp.com](https://gofastmcp.com) (install, API, CLI).

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [What FastMCP is (and is not)](#1-what-fastmcp-is-and-is-not) |
| 2 | [Why people mention “agent framework”](#2-why-people-mention-agent-framework) |
| 3 | [Core features](#3-core-features) |
| 4 | [Requirements and install](#4-requirements-and-install) |
| 5 | [Minimal server — one tool](#5-minimal-server--one-tool) |
| 6 | [CLI — `mcp dev`, inspect, install](#6-cli--mcp-dev-inspect-install) |
| 7 | [Connect a host (e.g. Claude Desktop)](#7-connect-a-host-eg-claude-desktop) |
| 8 | [End-to-end mental model](#8-end-to-end-mental-model) |
| 9 | [Compare to Topic 18](#9-compare-to-topic-18) |

---

## 1. What FastMCP is (and is not)

| | **MCP (protocol)** | **FastMCP (library)** |
|--|-------------------|------------------------|
| Layer | **Standard** — how host client and server talk | **Python toolkit** — helps you **implement** a server |
| You write | JSON-RPC methods, capability lists, transports | Functions with `@mcp.tool()`, `@mcp.resource()`, etc. |
| Analogy | USB-C **spec** | A **factory** that builds USB-C devices faster |

| FastMCP is **not** | Meaning |
|--------------------|---------|
| The MCP **protocol** itself | That is the open standard ([`4_the_communication_protocol.md`](./4_the_communication_protocol.md)) |
| An **agent framework** like LangChain | It does not replace your agent loop; it **exposes tools** to hosts |
| The **host** | Claude Desktop, Cursor, etc. remain the host; your script is usually the **server** |

FastMCP **is** a practical way to ship an **MCP server** from Python with less boilerplate.

---

## 2. Why people mention “agent framework”

MCP is often discussed next to **agents** because it gives the LLM **real tools** (read, write, call APIs). The word **agent** still means: **LLM + goal + actions**.

```text
User: "What is the weather in New York?"
        │
        ▼
   Host (Claude Desktop / Cursor)  ── MCP client ──►  Your FastMCP server
        │                                                    │
        │◄── tool result: forecast / "sunny" ─────────────────┘
        ▼
   LLM answers in natural language
```

In the UI you may see something like **“Ran get_forecast_weather”** — that is the host calling your **tool** over MCP, not magic inside the model.

| Piece | Role |
|-------|------|
| **MCP** | Wire format + lifecycle ([`3_communication_flow.md`](./3_communication_flow.md)) |
| **MCP server** (FastMCP app) | Tools, resources, prompts you define |
| **MCP client** | Inside the **host**; one client per server connection |
| **Host** | App the user chats in |
| **“Agent” in conversation** | Often means **host + LLM + tools** working together — FastMCP builds the **server** side |

---

## 3. Core features

Typical FastMCP selling points (high level):

| Feature | Benefit |
|---------|---------|
| **Decorators** | `@mcp.tool()` registers a function as an MCP tool |
| **Type hints** | Arguments / return types map toward JSON Schema for the host |
| **Validation** | Often via **Pydantic** — clearer errors when params are wrong |
| **Sync and async** | Handlers can be normal `def` or `async def` |
| **Resources & prompts** | Same server can expose more than tools ([`5_mcp_capabilities.md`](./5_mcp_capabilities.md)) |
| **CLI (`mcp`)** | Dev server, inspector, install into Claude Desktop |

You focus on **what** the tool does; FastMCP helps with **how** it is advertised and invoked over MCP.

---

## 4. Requirements and install

```bash
pip install fastmcp
```

Use the same Python environment as your other AI learning scripts (e.g. `my-proj` in the IDE).

Optional (for some hosts): **Claude Desktop** or another MCP **host** to attach the server — see [§7](#7-connect-a-host-eg-claude-desktop).

---

## 5. Minimal server — one tool

Smallest pattern: create a server object, decorate a function, run.

```python
from fastmcp import FastMCP

# Name shown in host / logs (like an app title)
mcp = FastMCP("My Server")


@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    # Demo only — replace with a real API in production
    return f"The weather in {location} is sunny."


if __name__ == "__main__":
    mcp.run()
```

| Line | Meaning |
|------|---------|
| `FastMCP("My Server")` | Creates the server instance (display name for humans) |
| `@mcp.tool()` | Registers the function as an MCP **tool** the host can list and call |
| Docstring | Becomes the tool **description** the model reads when choosing tools |
| Type hints | `a: int`, `location: str` → schema for arguments (e.g. `location` string property) |
| `mcp.run()` | Starts the server (often **stdio** transport for local hosts) |

**Weather-style tool schema (conceptual)** — what the host sees for `get_weather`:

```json
{
  "name": "get_weather",
  "description": "Get the weather for a location.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": { "type": "string" }
    },
    "required": ["location"]
  }
}
```

FastMCP generates this style of metadata from your Python signature instead of you hand-writing JSON for every tool.

---

## 6. CLI — `mcp dev`, inspect, install

FastMCP ships a **`mcp`** command-line tool for development.

```text
mcp [OPTIONS] COMMAND [ARGS]...

Development commands:
  dev       Run a MCP server with the MCP Inspector
  install   Install a MCP server in the Claude desktop app
  (version) Show version / help via --version
```

| Command | What it is for |
|---------|----------------|
| **`mcp dev`** | Run your server locally with the **MCP Inspector** — test list/call tools without a full host UI |
| **Inspector (browser)** | Debug discovery, send `tools/call`, see JSON-RPC traffic |
| **`mcp install`** | Wire the server into **Claude Desktop** config so Claude can use it as a custom MCP server |

Exact flags change between FastMCP versions — run `mcp --help` and `mcp dev --help` after install.

**Typical local dev loop**

1. Write `my_mcp_server.py` with `@mcp.tool()` functions.  
2. `mcp dev my_mcp_server.py` (or the path your version expects).  
3. Use the inspector to call `get_weather` with `location: "New York"`.  
4. When happy, `mcp install` (or manual host config) for Claude Desktop.

---

## 7. Connect a host (Cursor, Claude Desktop, …)

### Cursor — `~/.cursor/mcp.json`

Add under `mcpServers` (see full walkthrough + chat examples in [`7_weather_py.md`](./PROJECT_1/7_weather_py.md#connect-in-cursor-mcpjson)):

```json
"weather": {
  "command": "/path/to/your/env/bin/python3",
  "args": ["/path/to/19_MCP_MODEL_CONTEXT_PROTOCOL/PROJECT_1/weather.py"]
}
```

Use your real **`my-proj`** Python and the absolute path to [`PROJECT_1/weather.py`](./PROJECT_1/weather.py). Reload MCP in Cursor Settings after saving.

### Claude Desktop

Hosts expose **MCP settings** where you enable **custom servers** (names like `weather-server`).

```text
Claude Desktop  →  Settings  →  MCP / Connectors  →  toggle server ON
```

After the server is installed and enabled:

1. User asks: *“What is the weather of New York?”*  
2. Host LLM chooses tool `get_weather` or `get_forecast_weather` (your registered name).  
3. UI may show: **Getting the current weather forecast for New York** and **Ran get_forecast_weather**.  
4. Server returns text/JSON; host LLM replies in chat.

**Cursor** and other IDEs use the same idea: MCP servers in config, tools available to the in-IDE agent.

Security: only enable servers you trust; tools can read files or call APIs ([`5_mcp_capabilities.md`](./5_mcp_capabilities.md) — approvals on the host).

---

## 8. End-to-end mental model

```text
┌────────────── Host (Claude Desktop, Cursor, …) ──────────────┐
│  User chat  →  LLM  →  MCP Client  ──stdio/HTTP──►           │
└──────────────────────────────────────────────────│───────────┘
                                                   │
┌────────────── Your machine ──────────────────────▼───────────┐
│  FastMCP server (my_mcp_server.py)                            │
│    @mcp.tool get_weather  →  real API or demo string          │
└──────────────────────────────────────────────────────────────┘
```

| Step | Topic 19 note |
|------|----------------|
| Protocol on the wire | [`4_the_communication_protocol.md`](./4_the_communication_protocol.md) |
| Who is host / client / server | [`2_core_mcp_terminology.md`](./2_core_mcp_terminology.md) |
| Seven-step flow | [`3_communication_flow.md`](./3_communication_flow.md) |

---

## 9. Compare to Topic 18

| | **Topic 18** (`assistant.py` + `tools.py`) | **FastMCP server** |
|--|-------------------------------------------|---------------------|
| Where tools live | Same Python project as the chat loop | Separate **server** process |
| Who calls tools | Your `if tool == ...` or planner LLM in **your** script | **Host’s** LLM via MCP |
| Who can use the tools | Only your script | Any MCP **host** that connects |
| Best for learning | Agent loop, planner, two LLM calls | Standard **plug-in** tools for real apps |

Topic 18 taught **brain + body in one repo**. FastMCP teaches **body as a shareable MCP server** any host can plug in.

---

## How to run (when you add a script)

After you save a server file in this folder (e.g. `my_mcp_server.py`):

```bash
pip install fastmcp
python my_mcp_server.py
```

For interactive debugging, prefer:

```bash
mcp dev my_mcp_server.py
```

(Use the exact subcommand your installed `mcp` version documents.)

---

## Quick recap

1. **MCP** = protocol; **FastMCP** = Python helper to **build servers**.  
2. **`@mcp.tool()`** + type hints ≈ register tools with schema and descriptions.  
3. **`mcp dev`** + inspector = test without Claude; **`mcp install`** = Claude Desktop integration.  
4. The **host** runs the LLM and MCP **client**; your FastMCP app is usually the **server**.  
5. Hands-on in this repo: [`PROJECT_1/weather.py`](./PROJECT_1/weather.py) · [`PROJECT_1/7_weather_py.md`](./PROJECT_1/7_weather_py.md).

---

## Next

- Lab walkthrough: [`PROJECT_1/7_weather_py.md`](./PROJECT_1/7_weather_py.md)  
- Chapter index: [`README.md`](./README.md)  
- Capabilities deep dive: [`5_mcp_capabilities.md`](./5_mcp_capabilities.md)  
- Prior agent hands-on: [`18_AI_AGENTS_INTRO/`](../18_AI_AGENTS_INTRO/)  
- Write your own MCP client: [`PROJECT_2/8_mcp_client_lab.md`](./PROJECT_2/8_mcp_client_lab.md)
