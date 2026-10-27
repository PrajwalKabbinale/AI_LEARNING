# `server.py` & `mcp_client.py` & `test_client.py`

Hands-on **MCP client in Python**: you run a small **server** (`server.py`) and a **client** (`mcp_client.py` + `test_client.py`) in the same folder — no Cursor chat required.

**PROJECT_1** ([`7_weather_py.md`](../PROJECT_1/7_weather_py.md)) = you only wrote the **server**; **Cursor** was the client.  
**PROJECT_2** (this folder) = you write the **client** too, so you see connect → list tools → call tool → disconnect in code.

Read first: [`2_core_mcp_terminology.md`](../2_core_mcp_terminology.md) · [`6_fastmcp.md`](../6_fastmcp.md).  
Chapter index: [`README.md`](../README.md).

| File | Role |
|------|------|
| [`server.py`](./server.py) | MCP **server** — tools: `current_time`, `roll_dice`, `generate_password` |
| [`mcp_client.py`](./mcp_client.py) | MCP **client** helpers — `connect`, `discover_tools`, `execute_tool`, `disconnect` |
| [`test_client.py`](./test_client.py) | **Entry point** — demo script that uses the helpers |

**Read this first for the call chain:** [Who calls whom — files and functions](#who-calls-whom--files-and-functions).

---

## Who calls whom — files and functions

### Entry point (what you run)

| You run | Starts in | Never imports |
|---------|-----------|----------------|
| `python test_client.py` | [`test_client.py`](./test_client.py) → `asyncio.run(main())` | **`server.py` is not imported** as a Python module |

The link to the server is **`SERVER_SCRIPT`** in [`mcp_client.py`](./mcp_client.py) → `Client(SERVER_SCRIPT)` (`pathlib.Path` to `server.py`). FastMCP **spawns a new process** that runs that file.

### Import map (Python `import` only)

```text
test_client.py
    │
    └── import * from  mcp_client.py
              │
              └── from fastmcp import Client   (library — not your server)

server.py
    │
    └── from fastmcp import FastMCP   (library)
    └── @mcp.tool() registers current_time, roll_dice, generate_password
```

**Important:** `test_client.py` never does `import server` or `from server import roll_dice`. Tool code runs **inside the server subprocess** when MCP delivers a `tools/call` message.

### Master table — who calls what (simplified)

Think in **four phases**. Only **your** files are in the first column; FastMCP and `server.py` sit behind the helpers.

| Phase | You run / call (your code) | What happens next (plain English) |
|-------|----------------------------|----------------------------------|
| **A — Start** | `test_client.py` → `asyncio.run(main())` → `main()` | Python enters your demo script. |
| **A — Connect** | `main()` → `await connect()` in **`mcp_client.py`** | Builds `Client(SERVER_SCRIPT)` and opens the session. FastMCP **starts another process** that runs **`server.py`** (stdio). You still have **no** `import server`. |
| **B — Discover** | `main()` → `await discover_tools(client)` in **`mcp_client.py`** | Inside: `await client.list_tools()` (**fastmcp** library). That sends MCP **tools/list** to the server process; you get back names like `roll_dice`. |
| **B — Print** | `main()` → `for tool in tools: print(tool.name)` | Only printing in **`test_client.py`** — no server call. |
| **C — Run tool** | `main()` → `await execute_tool(client, "roll_dice")` in **`mcp_client.py`** | Inside: `await client.call_tool("roll_dice", {})` (**fastmcp**). MCP **tools/call** hits **`server.py`** → **`roll_dice()`** runs there. |
| **C — Print result** | `main()` → `print(result.content[0].text)` | Shows the die value **`test_client.py`** received from the client. |
| **D — Stop** | `main()` → `await disconnect(client)` in **`mcp_client.py`** | Closes the session; **server subprocess exits**. |

**Key idea:** `test_client.py` only talks to **`mcp_client.py`**. It never calls `roll_dice()` directly. The die roll runs in the **server process** because FastMCP forwarded the MCP message.

#### Three layers (same story, different view)

| Layer | Files | Job in this lab |
|-------|--------|-----------------|
| **1 — Demo** | `test_client.py` | Decides *when* to connect, list tools, call `roll_dice`, print, disconnect. |
| **2 — Your client API** | `mcp_client.py` | Thin wrappers: `connect`, `discover_tools`, `execute_tool`, `disconnect`. |
| **3 — Library + server** | `fastmcp` + `server.py` | Real MCP wire (`list_tools`, `call_tool`) and tool code (`roll_dice`, …). |

```text
Phase A–D in test_client.main()
        │
        ▼
   mcp_client.py  (your functions)
        │
        ▼
   fastmcp.Client  (pip package — list_tools, call_tool, …)
        │  stdio JSON-RPC
        ▼
   server.py  (separate process — @mcp.tool functions)
```

#### Detail table (only when you need file + function names)

| Step | From | Function | To | Function / effect |
|------|------|----------|-----|-------------------|
| 1 | `test_client.py` | `main()` | `mcp_client.py` | `connect()` |
| 2 | `mcp_client.py` | `connect()` | fastmcp | `Client(SERVER_SCRIPT)` + `__aenter__()` → spawn **`server.py`** |
| 3 | `test_client.py` | `main()` | `mcp_client.py` | `discover_tools()` → `client.list_tools()` |
| 4 | `test_client.py` | `main()` | `mcp_client.py` | `execute_tool(..., "roll_dice")` → `client.call_tool(...)` |
| 5 | MCP + `server.py` | (protocol) | `server.py` | **`roll_dice()`** |
| 6 | `test_client.py` | `main()` | `mcp_client.py` | `disconnect()` → `__aexit__()` |

This is **not** like `from server import roll_dice; roll_dice()` in one process. Steps 2–5 use **two processes** and MCP messages between them.

### Server tools — who can call them?

| Tool function in `server.py` | Called directly from `test_client.py`? | How it runs |
|------------------------------|----------------------------------------|-------------|
| `current_time()` | **No** | MCP `call_tool("current_time", ...)` |
| `roll_dice()` | **No** | MCP `call_tool("roll_dice", ...)` — **used in demo** |
| `generate_password(...)` | **No** | MCP `call_tool("generate_password", {"length": 12})` |

Tool **names** in MCP match the Python function names because of `@mcp.tool()` on each `def`.

### Optional: running `server.py` alone

| You run | What happens |
|---------|----------------|
| `python server.py` | `main` block → `mcp.run()` — server on stdio, **no** `test_client.py` |
| Caller must be | Another MCP **client** (Cursor, `mcp dev`, or `test_client.py` via `Client`) |

Same idea as [`PROJECT_1/7_weather_py.md`](../PROJECT_1/7_weather_py.md): do not type tool names into the server terminal.

### One-line summary

**`test_client.py`** → **`mcp_client.py`** helpers → **`fastmcp.Client`** → (stdio) → **`server.py`** tool functions.

---

## Requirements

```bash
pip install fastmcp
```

| Package | Used for |
|---------|----------|
| `fastmcp` | `FastMCP` on the server **and** `Client` on the client (`from fastmcp import ...`) |

**Import note:** [`PROJECT_1/weather.py`](../PROJECT_1/weather.py) uses the **official SDK** path `from mcp.server.fastmcp import FastMCP`. **This lab** uses the **`fastmcp`** package API (`from fastmcp import FastMCP, Client`) — same idea, different import style as in [`6_fastmcp.md`](../6_fastmcp.md).

No `.env` and no API keys — tools run locally on your machine.

---

## How to run

From **`PROJECT_2`**:

```bash
python test_client.py
```

You do **not** start `server.py` in a second terminal. `Client(SERVER_SCRIPT)` launches the server as a **subprocess** and talks to it over MCP (stdio).

**Expected output (shape):**

```text
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

Dice Result: 4
```

(Dice number changes each run.)

---

## PROJECT_1 vs PROJECT_2

| | **PROJECT_1** (`weather.py`) | **PROJECT_2** (this folder) |
|--|------------------------------|-----------------------------|
| **Server** | NWS weather tools | Time / dice / password tools |
| **Client** | **Cursor** (`mcp.json`) | **Your** `mcp_client.py` |
| **Entry point** | Host chat or `mcp dev` | `python test_client.py` |
| **Lesson** | Publish tools for any host | Program the client yourself |

```text
PROJECT_1:
  Cursor (host + client)  ──stdio──►  weather.py (server)

PROJECT_2:
  test_client.py  →  mcp_client.Client  ──stdio──►  server.py (server)
```

---

## Main idea — client lifecycle

| Step | Function | MCP idea |
|------|----------|----------|
| 1 | `connect()` | Start server subprocess; open session (`__aenter__`) |
| 2 | `discover_tools(client)` | **Discovery** — `list_tools()` ([`4_the_communication_protocol.md`](../4_the_communication_protocol.md#4-the-interaction-lifecycle)) |
| 3 | `execute_tool(client, "roll_dice")` | **Execution** — `call_tool(name, arguments)` |
| 4 | `disconnect(client)` | Close session (`__aexit__`) |

There is **no LLM** in this lab. `test_client.py` hard-codes the tool name `"roll_dice"`. A real agent would let the model pick the tool after discovery.

---

## Full source — `server.py`

```python
from datetime import datetime

from fastmcp import FastMCP

mcp = FastMCP("Souvik MCP Server")

@mcp.tool()

def current_time():

    """Return the current date and time."""

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


import random

@mcp.tool()

def roll_dice():

    """Roll a six-sided dice."""

    return random.randint(1,6)

import secrets
import string

@mcp.tool()

def generate_password(length: int = 12):

    """
    Generate a secure password.
    """

    alphabet = (
        string.ascii_letters
        + string.digits
        + string.punctuation
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )

if __name__ == "__main__":
    print("Starting MCP server..")
    mcp.run()
```

### Line-by-line (`server.py`)

| Piece | Meaning |
|-------|---------|
| `FastMCP("Souvik MCP Server")` | Server label in FastMCP / logs (not the Python filename) |
| `@mcp.tool()` | Register each function as an MCP tool |
| `current_time` / `roll_dice` / `generate_password` | Same ideas as Topic 18 [`tools.py`](../../18_AI_AGENTS_INTRO/tools.py) — local Python only |
| `generate_password(length: int = 12)` | Default length **12**; client can pass `arguments={"length": 16}` |
| `if __name__ == "__main__"` | Running `python server.py` alone starts server on stdio (like `weather.py` — wait for client, do not type chat) |
| `mcp.run()` | Default transport is stdio for local clients |

---

## Full source — `mcp_client.py`

```python
from pathlib import Path

from fastmcp import Client

SERVER_SCRIPT = Path(__file__).resolve().parent / "server.py"


async def connect():

    """
    Connect to the MCP Server.
    """

    client = Client(SERVER_SCRIPT)

    await client.__aenter__()

    print("Connected to MCP Server.")

    return client


async def disconnect(client):

    """
    Close the MCP connection.
    """

    await client.__aexit__(
        None,
        None,
        None
    )


async def discover_tools(client):

    """
    Retrieve all tools from the server.
    """

    tools = await client.list_tools()

    return tools


async def execute_tool(
    client,
    tool_name,
    arguments=None
):

    """
    Execute a tool.
    """

    if arguments is None:

        arguments = {}

    result = await client.call_tool(

        tool_name,

        arguments

    )

    return result
```

### Line-by-line (`mcp_client.py`)

| Piece | Meaning |
|-------|---------|
| `Client(SERVER_SCRIPT)` | **This is the MCP client.** `Path` next to `mcp_client.py` (FastMCP 4.x+; avoids deprecating bare string `"server.py"`). FastMCP spawns that script and speaks JSON-RPC over stdio |
| `await client.__aenter__()` | Async context manager **enter** — handshake / initialization phase |
| `list_tools()` | See [Where is `list_tools()`?](#where-is-list_tools) below — **not** defined in your repo |
| `call_tool(tool_name, arguments)` | Same library — MCP `tools/call`; runs `roll_dice()` etc. on **`server.py`** |
| `await client.__aexit__(None, None, None)` | Clean shutdown — matches `__aenter__` |

#### Where is `list_tools()`?

It is **not** in `mcp_client.py`, `test_client.py`, or `server.py`. You only **call** it here:

```python
# mcp_client.py — your wrapper
tools = await client.list_tools()
```

| Layer | Where `list_tools` lives | What it does |
|-------|--------------------------|--------------|
| **Your code** | [`mcp_client.py`](./mcp_client.py) → `discover_tools()` | Calls `await client.list_tools()` and returns the list |
| **Library** | `fastmcp` package → `Client.list_tools()` (mixin on `fastmcp.Client`) | Sends MCP **`tools/list`** over stdio to the server |
| **Server** | [`server.py`](./server.py) — FastMCP **server** side | Answers with tools registered by `@mcp.tool()` (`current_time`, `roll_dice`, `generate_password`) |

```text
discover_tools()          list_tools()              tools/list (JSON-RPC)
mcp_client.py      →      fastmcp.Client     →      server.py (Souvik MCP Server)
   (yours)                  (installed pip)            (your subprocess)
```

You do not implement `list_tools` yourself — same as you do not implement `chat.completions.create` when using OpenAI; the SDK + protocol do it.

**Why `__aenter__` / `__aexit__` manually?** The helpers avoid `async with Client(...) as client:` so `test_client.py` reads step-by-step. Same pattern as using a connection you open and close explicitly.

---

## Full source — `test_client.py`

### What is `async` / `asyncio`? Why does Python have it?

**The problem:** Much of your program’s time is spent **waiting** — disk, network, another process (here: MCP messages on stdin/stdout). In plain synchronous code, while you wait, that thread sits idle and cannot do other work.

**What Python added (3.5+):** **`async` / `await`** syntax plus the **`asyncio`** library. You write functions that can **pause** at a wait (`await`) and **resume** when data is ready, on **one thread**, without starting a new thread per connection.

| Term | What it is |
|------|------------|
| **`async def`** | A function that can pause; calling it returns a coroutine (not the final result). |
| **`await`** | Pause *this* function until that step finishes (e.g. read reply from server). |
| **`asyncio.run(...)`** | From a normal script: start the event loop, run your coroutine once, exit. |

**Why people use it in Python:** Web servers handling many clients, APIs, chat, databases, MCP/clients like **fastmcp** — lots of I/O, little CPU. Async lets one process juggle many waits efficiently. It is **not** for speeding up heavy number crunching (use normal loops, multiprocessing, or NumPy for that).

**This lab:** **fastmcp**’s `Client` is async-only, so `mcp_client.py` and `test_client.py` use `async`/`await`. You need `await` on every helper call and `asyncio.run(main())` at the bottom.

### Why async is required *here* — and what breaks without it

In PROJECT_2 the client talks to **`server.py` over stdio** (pipes). Each step — start subprocess, MCP handshake, `tools/list`, `tools/call` — is **send a message, wait for bytes back**. **fastmcp** exposes that as **`await client.__aenter__()`**, **`await client.list_tools()`**, **`await client.call_tool(...)`**. There is no synchronous `client.list_tools()` on this `Client` class.

| If you… | What happens |
|--------|----------------|
| Remove **`asyncio.run(main())`** and only define `async def main()` | **`main()` never runs.** Calling `main()` without a loop returns a coroutine object and exits — no connect, no dice. |
| Call **`connect()`** without **`await`** inside `main()` | **`client` is not a Client** — it is an un-awaited coroutine. Next line (`discover_tools(client)`) errors or behaves wrong. |
| Write **`def main():`** (no `async`) and try **`await connect()`** | **SyntaxError** — `await` is only legal inside `async def`. |
| Skip **`async def`** on `mcp_client.py` helpers and call **`client.list_tools()`** without await | You get a **coroutine object**, not a tool list — `for tool in tools` fails. |
| “Just use sync Python” with this stack | You would need **another client library** (or your own blocking wrapper around the MCP protocol). This lab follows **fastmcp**’s design on purpose. |

**Is async for speed in `test_client.py`?** For this **one** script, **no** — steps are sequential (connect → list → roll once → disconnect). Async is not making the dice roll faster. It is **required because the library and protocol are I/O-wait shaped**, and **fastmcp** chose an async API. A big app with **many** MCP servers or parallel tool calls on **one** loop would be where async pays off; here you mainly learn the same pattern Cursor and other MCP hosts use.

```python
import asyncio

from mcp_client import *

async def main():

    client = await connect()

    tools = await discover_tools(
        client
    )

    print()

    print("Available Tools")

    print("----------------")

    for tool in tools:

        print(tool.name)

    print()

    result = await execute_tool(

        client,

        "roll_dice"

    )

    print("Dice Result:", result.content[0].text)

    await disconnect(
        client
    )


asyncio.run(main())
```

### Line-by-line (`test_client.py`)

| Order | Code | What happens |
|-------|------|----------------|
| 1 | `from mcp_client import *` | Imports `connect`, `discover_tools`, `execute_tool`, `disconnect` (fine for a small lab; in production prefer explicit imports) |
| 2 | `client = await connect()` | Server subprocess up; MCP session ready |
| 3 | `discover_tools(client)` | Prints will list `current_time`, `roll_dice`, `generate_password` |
| 4 | `execute_tool(client, "roll_dice")` | No `arguments` → `{}` — die roll needs no params |
| 5 | `result.content[0].text` | Tool result is structured; this lab reads the **text** part of the first content block |
| 6 | `await disconnect(client)` | Close client and server subprocess |
| 7 | `asyncio.run(main())` | Only line that must run at **module** level: boots the event loop and runs `main()` |

### Try other tools (experiments)

Change the `execute_tool` call:

```python
# Time
result = await execute_tool(client, "current_time")
print(result.content[0].text)

# Password (optional length)
result = await execute_tool(client, "generate_password", {"length": 8})
print(result.content[0].text)
```

---

## Picture: one run of `test_client.py`

Short view — full file/function list is [above](#who-calls-whom--files-and-functions).

```text
test_client.py :: main()
      │
      ├─► mcp_client.py :: connect()
      │         └─► fastmcp.Client("server.py")  ──spawns──►  server.py (subprocess)
      │
      ├─► mcp_client.py :: discover_tools()  ──► client.list_tools()
      │
      ├─► mcp_client.py :: execute_tool("roll_dice")  ──► client.call_tool()
      │         └─► (MCP)  ──►  server.py :: roll_dice()
      │
      └─► mcp_client.py :: disconnect()
```

---

## Common mistakes

| Mistake | What happens |
|---------|----------------|
| Run `server.py` and type `roll_dice` in the terminal | Same as PROJECT_1 — stdin expects **JSON-RPC**, not plain text |
| Run `test_client.py` from the **wrong folder** | Older labs used `Client("server.py")` (cwd-relative). This repo uses **`Path(__file__).parent / "server.py"`** so the server path stays correct |
| Forget `await` on `connect` / `call_tool` | `async` functions must be awaited inside `async def main()` |

**FastMCP 4.x:** use `Client(pathlib.Path(...))` for the server script (see `SERVER_SCRIPT` in `mcp_client.py`). A bare string like `Client("server.py")` still works today but warns and will break in FastMCP 5.

---

## Quick recap

1. **Run:** `python test_client.py` only — entry is **`test_client.py` → `main()`**.  
2. **`mcp_client.py`** — `connect` / `discover_tools` / `execute_tool` / `disconnect` call **`fastmcp.Client`**, not `server.py` directly.  
3. **`server.py`** — runs in a **subprocess**; **`roll_dice()`** (etc.) run when MCP `call_tool` arrives.  
4. **No** `import server` in the client files — only the path to `server.py` via `SERVER_SCRIPT`.  
5. See [Who calls whom](#who-calls-whom--files-and-functions) for the full table.  
6. **PROJECT_1:** Cursor’s client plays the same role as `mcp_client.py` for `weather.py`.

---

## Next

- Weather server + Cursor: [`PROJECT_1/7_weather_py.md`](../PROJECT_1/7_weather_py.md)  
- Terminology: [`2_core_mcp_terminology.md`](../2_core_mcp_terminology.md)  
- Chapter: [`README.md`](../README.md)
