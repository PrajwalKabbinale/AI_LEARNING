# `server.py` & `mcp_client.py` & `planner.py` & `agent.py`

Hands-on **MCP + LLM agent**: tools live on an MCP **server** (like PROJECT_2), but **you** no longer hard-code `"roll_dice"`. An LLM **planner** picks the tool after **discovery**; MCP runs it; a second LLM call answers the user in natural language.

**PROJECT_2** ([`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md)) = MCP client only — **no** API keys.  
**Topic 18** ([`2_assistant_planner_tools.md`](../../18_AI_AGENTS_INTRO/2_assistant_planner_tools.md)) = planner + tools in **`tools.py`** (same process).  
**PROJECT_3** (this folder) = Topic 18 **pattern**, but tools execute via **MCP** on **`server.py`** in a subprocess.

Read first: [`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md) (async, `list_tools`, stdio) · Topic 18 planner idea · [`README.md`](../README.md).

| File | Role |
|------|------|
| [`server.py`](./server.py) | MCP **server** — `current_time`, `roll_dice`, `generate_password` |
| [`mcp_client.py`](./mcp_client.py) | MCP **client** helpers — same shape as PROJECT_2 |
| [`planner.py`](./planner.py) | **LLM #1** — `choose_tool(user_request, tools)` (same name as Topic 18; `tools` from MCP) |
| [`agent.py`](./agent.py) | **Entry point** — orchestrates MCP + `choose_tool` + **LLM #2** |

MCP-only smoke test (no LLM): **[`PROJECT_2/test_client.py`](../PROJECT_2/test_client.py)**.

**Read this first for the call chain:** [Who calls whom — files and functions](#who-calls-whom--files-and-functions).

---

## Who calls whom — files and functions

### Entry point (what you run)

| You run | Starts in | Never imports |
|---------|-----------|----------------|
| `python agent.py` | [`agent.py`](./agent.py) → `asyncio.run(main())` | **`server.py` is not imported** as a Python module |

The server is started by **`mcp_client.connect()`** → `Client(SERVER_SCRIPT)` → FastMCP spawns **`server.py`**.

### Import map (Python `import` only)

```text
agent.py
    │
    ├── from mcp_client import connect, disconnect, discover_tools, execute_tool
    │         │
    │         └── from fastmcp import Client
    │
    ├── from planner import choose_tool
    │         │
    │         └── OpenAI in planner.py   (LLM #1)
    │
    └── from openai import OpenAI          (LLM #2 in answer_user)

server.py
    │
    └── from fastmcp import FastMCP
    └── @mcp.tool() → current_time, roll_dice, generate_password
```

**Important:** `agent.py` never does `from server import roll_dice`. The planner may return the string `roll_dice`, but **`execute_tool`** sends MCP **`tools/call`** to the **server process**.

### Master table — who calls what (simplified)

Think in **six phases**. Phases **E–F** are new vs PROJECT_2 (the LLM steps).

| Phase | You run / call (your code) | What happens next (plain English) |
|-------|----------------------------|----------------------------------|
| **A — Start** | `agent.py` → `asyncio.run(main())` → `main()` | `load_dotenv()`, `client = OpenAI(...)`, `MODEL` (same as Topic 18). |
| **B — Connect** | `main()` → `await connect()` in **`mcp_client.py`** | Spawns **`server.py`** subprocess; MCP session open. |
| **C — Discover** | `main()` → `await discover_tools(mcp)` | `list_tools()` → names + **descriptions** from server (for the planner prompt). |
| **D — Ask user** | `main()` → `input("User : ")` | Your question in the terminal (e.g. “what time is it”). |
| **E — Plan (LLM #1)** | `main()` → `choose_tool(user_request, tools)` in **`planner.py`** | Builds prompt from **MCP tool metadata** + user line → **OpenAI** → returns **tool name only** (e.g. `current_time`). |
| **F — Run tool (MCP)** | `main()` → `await execute_tool(mcp, tool_name)` | **`call_tool`** → **`server.py`** runs the matching `@mcp.tool` function. |
| **G — Speak (LLM #2)** | `main()` → `answer_user(user_request, tool_output)` | Second OpenAI call: user question + tool text → natural **`AI :`** reply. |
| **H — Stop** | `main()` → `await disconnect(mcp)` | Close MCP; server subprocess exits. |

**Key idea:** PROJECT_2 **you** chose `"roll_dice"`. PROJECT_3 **LLM #1** chooses the name; **MCP** still runs the tool in the **server process** (same as PROJECT_2).

#### Four layers (same story, different view)

| Layer | Files | Job in this lab |
|-------|--------|-----------------|
| **1 — Agent** | `agent.py` | User I/O, MCP orchestration, **LLM #2**, connect/disconnect. |
| **1b — Planner** | `planner.py` | **LLM #1** — `choose_tool` (Topic 18 same function name). |
| **2 — Client API** | `mcp_client.py` | `connect`, `discover_tools`, `execute_tool`, `disconnect`. |
| **3 — Library + server** | `fastmcp` + `server.py` | MCP wire + tool implementations. |
| **4 — OpenAI** | `planner.py` + `agent.py` | **LLM #1** and **LLM #2** — not part of MCP. |

```text
Phase A–H in agent.main()
        │
        ├─► mcp_client.py ──► fastmcp.Client ──stdio──► server.py
        │
        ├─► planner.py :: choose_tool()  (LLM #1)
        └─► agent.py :: answer_user()  (LLM #2)
```

#### Detail table (file + function names)

| Step | From | Function | To | Function / effect |
|------|------|----------|-----|-------------------|
| 1 | `agent.py` | `main()` | `mcp_client.py` | `connect()` |
| 2 | `mcp_client.py` | `connect()` | fastmcp | spawn **`server.py`**, `__aenter__()` |
| 3 | `agent.py` | `main()` | `mcp_client.py` | `discover_tools()` → `list_tools()` |
| 4 | `agent.py` | `main()` | stdin | `input()` → `user_request` |
| 5 | `planner.py` | `choose_tool()` | OpenAI API | tool name string |
| 6 | `agent.py` | `main()` | `mcp_client.py` | `execute_tool(mcp, tool_name)` → `call_tool` |
| 7 | `server.py` | `@mcp.tool` handler | — | e.g. `current_time()` |
| 8 | `agent.py` | `answer_user()` | OpenAI API | final natural language |
| 9 | `agent.py` | `main()` | `mcp_client.py` | `disconnect()` |

### LLM #1 vs LLM #2 (Topic 18, same names)

| Label | Function | File | Input | Output |
|-------|----------|------|-------|--------|
| **LLM #1** | `choose_tool(user_request, tools)` | `planner.py` | User line + **MCP tool list** | Single tool name, e.g. `roll_dice` |
| **LLM #2** | `answer_user(...)` | `agent.py` | User line + **MCP tool result text** | Sentence for `AI :` |

#### `choose_tool(user_request, tools)` — parameters

| Parameter | Type (conceptually) | Meaning |
|-----------|---------------------|---------|
| **`user_request`** | `str` | What you typed after `User :` |
| **`tools`** | list from `discover_tools()` | MCP tool objects (`name`, `description`, …) — **not** Python functions from `server.py` |

Topic 18: `choose_tool(user_request)` only — tools are **hard-coded** in the prompt inside `planner.py`.  
PROJECT_3: same function name, but **`tools`** is passed in from **`discover_tools(mcp)`** so the planner always matches what the server actually exposes.

#### `answer_user(user_request, tool_output)` — parameters

| Parameter | Meaning |
|-----------|---------|
| **`user_request`** | Same string you passed to `choose_tool` |
| **`tool_output`** | `result.content[0].text` from **`execute_tool`** — facts come from MCP, not from the model guessing |

Topic 18 puts this prompt **inline** in `assistant.py` (no separate function). PROJECT_3 wraps it in **`answer_user`** so `main()` stays short: plan → MCP → speak.

Topic 18’s **`tools.py`** functions are called **in-process** after LLM #1. Here, after LLM #1, **`execute_tool`** is the “body” step — still **no** `import server`.

### Server tools — who can call them?

| Tool in `server.py` | Called from `agent.py` directly? | How it runs |
|---------------------|-----------------------------------|-------------|
| `current_time()` | **No** | MCP after planner returns `current_time` |
| `roll_dice()` | **No** | MCP after planner returns `roll_dice` |
| `generate_password(...)` | **No** | MCP; planner may return `generate_password` (default length 12 if no args) |

Tool **names** in MCP match Python function names because of `@mcp.tool()`.

### One-line summary

**`agent.py`** → **`mcp_client.py`** + **OpenAI (×2)** → **`fastmcp.Client`** → (stdio) → **`server.py`** tool functions.

---

## Requirements

```bash
pip install fastmcp openai python-dotenv
```

| Package | Used for |
|---------|----------|
| `fastmcp` | `FastMCP` on server, `Client` on client (same as PROJECT_2) |
| `openai` | Planner + answer in [`agent.py`](./agent.py) |
| `python-dotenv` | Load `OPENAI_API_KEY` and model from `.env` |

`.env` example (same as Topic 18 — folder you run from, or a parent folder `load_dotenv()` can find):

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

| Variable | Used for |
|----------|----------|
| `OPENAI_API_KEY` | `OpenAI(api_key=...)` in [`agent.py`](./agent.py) |
| `OPENAI_MODEL` | `MODEL=os.getenv("OPENAI_MODEL")` — same model for **planner** and **answer** |

Use a **current** model id from [OpenAI models](https://platform.openai.com/docs/models). Retired ids (e.g. old `gpt-4.1-nano`) return **404 `model_not_found`**.

---

## How to run

From **`PROJECT_3`**:

```bash
python agent.py
```

You do **not** start `server.py` in a second terminal.

**Sample output** (`python agent.py`, `User : time`) — saved from a real run. **Debug prints** are in [`planner.py`](./planner.py). FastMCP startup banner + `INFO ... stdio` lines are normal (omitted below in full ASCII; you still see them in the terminal).

```text
Connected to MCP Server.

Available Tools
----------------
current_time
roll_dice
generate_password

User : time
tool.name
current_time
--------------------------------
description
Return the current date and time.
--------------------------------
tool.name
roll_dice
--------------------------------
description
Roll a six-sided dice.
--------------------------------
tool.name
generate_password
--------------------------------
description
Generate a secure password.
--------------------------------
tool_list
1. current_time
   Return the current date and time.

2. roll_dice
   Roll a six-sided dice.

3. generate_password
   Generate a secure password.
--------------------------------
user_request
time
--------------------------------
planner_prompt

    You are an AI planner.
    Available tools:
    1. current_time
   Return the current date and time.

2. roll_dice
   Roll a six-sided dice.

3. generate_password
   Generate a secure password.
    Return ONLY the tool name.
    User Request:
    time

--------------------------------

Planner Selected: current_time
Tool output: 27-10-2026 11:31:12

AI : The current time is 27-10-2026 11:31:12.
```

| Debug block | Where | What you learn |
|-------------|--------|----------------|
| `tool.name` / `description` | `build_tool_descriptions()` loop | One loop iteration **per tool** from `discover_tools()` — **next section below:** [Debug line explained](#debug-line-explained) |
| `tool_list` | after `build_tool_descriptions` | String pasted into the planner prompt |
| `user_request` | `choose_tool` | Your terminal input |
| `planner_prompt` | before OpenAI call | Full **LLM #1** message body |

#### Debug line explained

**Table row above:** “one loop per tool” + docstrings from `server.py`.

When you run `python agent.py`, **`discover_tools(mcp)`** already finished **before** the debug loop runs. It called MCP **`tools/list`** and gave `planner.py` a Python **list** of tool objects (three items for this lab).

The debug prints in **`build_tool_descriptions(tools)`** walk that list **once per tool**. You are not reading `server.py` as a file in the planner; you are printing fields that **already arrived** from the server over MCP.

**Match your console to `server.py`:**

| What you printed | Example value | Where you wrote it in [`server.py`](./server.py) |
|------------------|---------------|--------------------------------------------------|
| `tool.name` | `roll_dice` | The **function name** under `@mcp.tool()` |
| `description` | `Roll a six-sided dice.` | The **docstring** directly under `def roll_dice():` |

Concrete pair:

```python
@mcp.tool()
def roll_dice():
    """Roll a six-sided dice."""
    return random.randint(1, 6)
```

FastMCP on the **server** registers: name = `roll_dice`, description = docstring text. After **`discover_tools()`**, the **client** exposes that as `tool.name` and `tool.description`. Your loop only **prints** and **formats** them; it does not parse `server.py` source.

**Order of operations:**

```text
1. agent.py     await discover_tools(mcp)     →  list of 3 tools (name + description each)
2. planner.py   choose_tool(..., tools)       →  passes that list in
3. planner.py   build_tool_descriptions(tools) →  for each tool: print name/description, build text
4. planner.py   {tool_list} in prompt         →  LLM reads the same words you saw in debug
```

So the sentence means: **the `description` line in the terminal is the docstring you typed in `server.py`, copied into MCP by FastMCP, then copied again into `tool.description` when the client discovers tools.** If you change a docstring, restart the run so a new server subprocess picks it up.

FastMCP banner lines at startup are normal. Remove the `print(...)` lines in `planner.py` when you no longer need the trace.

(Timestamps and AI wording change each run.)

---

## PROJECT_2 vs PROJECT_3 vs Topic 18

| | **PROJECT_2** | **PROJECT_3** | **Topic 18** |
|--|---------------|---------------|--------------|
| **Entry** | `test_client.py` | `agent.py` | `assistant.py` |
| **Who picks the tool?** | You (hard-coded `"roll_dice"`) | **LLM #1** `choose_tool()` in `planner.py` | **LLM #1** `choose_tool()` (static tool list in prompt) |
| **Where tools run** | MCP `server.py` subprocess | MCP `server.py` subprocess | Local `tools.py` |
| **Discovery** | `list_tools()` | `list_tools()` → descriptions in planner prompt | Tools listed in planner prompt (static) |
| **Natural reply** | None | **LLM #2** `answer_user()` | **LLM #2** in assistant loop |
| **API keys** | No | Yes | Yes |

```text
PROJECT_2:
  test_client.py  →  mcp_client  ──stdio──►  server.py

PROJECT_3:
  agent.py  →  mcp_client  ──stdio──►  server.py
         └─►  OpenAI (planner + answer)

Topic 18:
  assistant.py  →  tools.py (same process)
             └─►  OpenAI (planner + answer)
```

---

## Main idea — agent lifecycle

| Step | Code | MCP / LLM |
|------|------|-----------|
| 1 | `connect()` | MCP session + server subprocess |
| 2 | `discover_tools(mcp)` | **Discovery** — `tools/list` ([`4_the_communication_protocol.md`](../4_the_communication_protocol.md)) |
| 3 | `input(...)` | User question |
| 4 | `choose_tool(...)` in `planner.py` | **LLM #1** — pick tool name from discovered metadata |
| 5 | `execute_tool(mcp, tool_name)` | **Execution** — `tools/call` on server |
| 6 | `answer_user(...)` | **LLM #2** — phrase the answer |
| 7 | `disconnect(mcp)` | Close session |

---

## Full source — `server.py`

Same tools as PROJECT_2. Full walkthrough of `@mcp.tool` and `mcp.run()` is in [`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md#full-source--serverpy).

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
| `FastMCP("Souvik MCP Server")` | Server label in logs (same name as PROJECT_2) |
| `@mcp.tool()` | Registers each function for MCP `tools/list` and `tools/call` |
| Docstrings on each tool | Become **tool descriptions** — `build_tool_descriptions()` in `planner.py` feeds them to **LLM #1** |
| `mcp.run()` | stdio transport when spawned by `Client(SERVER_SCRIPT)` |

---

## Full source — `mcp_client.py`

Same pattern as PROJECT_2 ([`mcp_client.py`](../PROJECT_2/mcp_client.py)). See [`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md#full-source--mcp_clientpy) for `list_tools`, `__aenter__`, and `SERVER_SCRIPT`.

```python
from pathlib import Path

from fastmcp import Client

SERVER_SCRIPT = Path(__file__).resolve().parent / "server.py"


async def connect():

    client = Client(SERVER_SCRIPT)

    await client.__aenter__()

    print("Connected to MCP Server.")

    return client


async def disconnect(client):

    await client.__aexit__(
        None,
        None,
        None
    )


async def discover_tools(client):

    tools = await client.list_tools()

    return tools


async def execute_tool(
    client,
    tool_name,
    arguments=None
):

    if arguments is None:

        arguments = {}

    result = await client.call_tool(

        tool_name,

        arguments

    )

    return result
```

In PROJECT_3, **`discover_tools`** matters for the **agent**: the planner prompt is built from `tool.name` and `tool.description` returned by the server — not from a hard-coded list in Python.

### `async def execute_tool(client, tool_name, arguments=None)` — explain

**Job:** Run **one** tool on the MCP **server** subprocess. This is the PROJECT_3 equivalent of Topic 18 calling `roll_dice()` in `tools.py` — except the code runs in **`server.py`**, not in `agent.py`.

| Parameter | What you pass | Example in this lab |
|-----------|----------------|---------------------|
| **`client`** | The MCP session from **`await connect()`** — in `agent.py` this variable is named **`mcp`** | Same object you passed to `discover_tools(mcp)` |
| **`tool_name`** | String from **`choose_tool()`** — must match MCP **`tool.name`** | `"current_time"`, `"roll_dice"` |
| **`arguments`** | Optional **dict** of parameters for the tool | Omitted → `{}` (dice needs nothing; `generate_password` could use `{"length": 8}`) |

**Why `async def`?** Same as PROJECT_2: **`await client.call_tool(...)`** talks over stdio and must be awaited inside **`async def main()`**.

**What happens inside:**

```text
agent.py:  await execute_tool(mcp, "current_time")
                │
mcp_client.py:  await client.call_tool("current_time", {})
                │
fastmcp:        MCP message  tools/call  over stdio
                │
server.py:      current_time() runs  →  returns time string
                │
agent.py:       result.content[0].text  →  tool_output for answer_user
```

| Piece | Where it lives |
|-------|----------------|
| **`execute_tool`** | Your wrapper in [`mcp_client.py`](./mcp_client.py) |
| **`call_tool`** | **fastmcp** `Client` — you do not implement it |
| **`current_time()` / `roll_dice()`** | **`server.py`** — only runs when MCP delivers `tools/call` |

**Not** `from server import roll_dice; roll_dice()`. Two processes, one protocol.

---

## Full source — `planner.py`

Same role as Topic 18 [`planner.py`](../../18_AI_AGENTS_INTRO/planner.py), with one extra argument: **`tools`** from MCP discovery.

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("OPENAI_MODEL")


def build_tool_descriptions(tools):

    """
    Turn MCP list_tools() results into planner text (like Topic 18's numbered list).
    """

    lines = []

    for index, tool in enumerate(tools, start=1):

        description = (tool.description or "No description.").strip()

        lines.append(f"{index}. {tool.name}\n   {description}")

    return "\n\n".join(lines)


def choose_tool(user_request, tools):

    """
    LLM #1: pick one MCP tool name from the discovered tool list.

    user_request — what the user typed in the terminal.
    tools        — list from discover_tools() (MCP metadata: name + description).
    """

    tool_list = build_tool_descriptions(tools)

    planner_prompt = f"""
Available tools:

{tool_list}

Pick the tool that best fits the user request.
Return ONLY the tool name (example: roll_dice). Do not explain.

User request:

{user_request}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an AI planner.",
            },
            {
                "role": "user",
                "content": planner_prompt,
            },
        ],
    )

    return response.choices[0].message.content.strip()
```

### Line-by-line (`planner.py`)

| Piece | Meaning |
|-------|---------|
| `build_tool_descriptions(tools)` | Formats MCP `tools/list` for the prompt |
| `choose_tool(user_request, tools)` | **LLM #1** — returns one tool **name** string |
| Second argument `tools` | **PROJECT_3 only** — Topic 18 embeds tool names in the prompt file instead |

### `build_tool_descriptions(tools)` — what and why

**Job:** Turn the Python list from `discover_tools(mcp)` into **one string** the planner LLM can read (numbered list like Topic 18).

| Step in code | What it does |
|--------------|----------------|
| `tools` argument | Same list `agent.py` got from `await discover_tools(mcp)` |
| `tool.name` | MCP tool id string — must match what `execute_tool` will call (e.g. `roll_dice`) |
| `tool.description` | Short text telling the LLM what the tool is for — see below |
| `return "\n\n".join(lines)` | One block pasted into `choose_tool` as `{tool_list}` |

You do **not** write this string by hand in PROJECT_3. Topic 18 types tool names and hints directly inside `planner_prompt`; here the server is the source of truth.

### What is `tool.description`? Where does it come from?

`tool` is **not** a function in `server.py`. It is an **object** returned by the **fastmcp** client after MCP **`tools/list`**.

```text
server.py                          MCP (stdio)                    your machine
──────────                         ───────────                    ────────────
@mcp.tool()                        tools/list JSON-RPC            discover_tools()
def roll_dice():        ───────►   name: "roll_dice"      ───────►  tool.name
    """Roll a six-..."""           description: "Roll..."         tool.description
```

| Field | Origin in **your** code | Who sends it on the wire |
|-------|-------------------------|---------------------------|
| **`tool.name`** | Python function name on `@mcp.tool()` (`roll_dice`, `current_time`, …) | FastMCP **server** registers it; client reads it from **`tools/list`** |
| **`tool.description`** | The function’s **docstring** (triple-quoted text under `def`) | FastMCP copies that docstring into the MCP tool **description** field |

**Example from [`server.py`](./server.py):**

```python
@mcp.tool()
def roll_dice():

    """Roll a six-sided dice."""

    return random.randint(1, 6)
```

After `discover_tools(mcp)`:

- `tool.name` → `"roll_dice"`
- `tool.description` → `"Roll a six-sided dice."` (from the docstring)

`build_tool_descriptions` turns that into prompt text:

```text
2. roll_dice
   Roll a six-sided dice.
```

**`(tool.description or "No description.").strip()`** — if a tool had no docstring, MCP might send an empty description; the lab substitutes `"No description."` so the prompt still works.

**Important:** The LLM only sees **`name` + `description`** in the planner prompt. It does **not** see your Python source file. If you change a docstring in `server.py`, restart the run (new server subprocess) so discovery picks up the new text.

### `tool.name` vs `tool.description` (quick)

| | `tool.name` | `tool.description` |
|--|-------------|----------------------|
| **Purpose** | Exact id for **`call_tool`** | Helps LLM **choose** the right tool |
| **Planner must return** | This string exactly | *(not returned — only read in the prompt)* |
| **You edit in** | Function name in `server.py` | Docstring under that function |

---

## Full source — `agent.py`

### Async in this lab

MCP steps use **`async` / `await`** because **fastmcp.Client** is async-only (same as PROJECT_2). **`choose_tool`** and **`answer_user`** are normal **`def`** — synchronous OpenAI HTTP calls.

| Part | File | Async? |
|------|------|--------|
| `main()` | `agent.py` | `async def` — `await` MCP helpers |
| `choose_tool` | `planner.py` | sync |
| `answer_user` | `agent.py` | sync |
| Entry | `agent.py` | `asyncio.run(main())` |

Deep dive: [What is async / asyncio?](../PROJECT_2/8_mcp_client_lab.md#what-is-async--asyncio-why-does-python-have-it) in PROJECT_2.

```python
"""MCP + LLM agent: discover tools on server, planner picks tool, MCP runs it, LLM answers."""

import asyncio
import os

from dotenv import load_dotenv
from openai import OpenAI

from mcp_client import connect, disconnect, discover_tools, execute_tool
from planner import choose_tool

# Load configuration
load_dotenv()
# Create AI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("OPENAI_MODEL")


def answer_user(user_request, tool_output):

    """
    LLM #2: phrase the final reply (same job as the second call in Topic 18 assistant.py).

    user_request — what the user typed.
    tool_output  — text from execute_tool() / MCP (the real tool result).
    """

    answer_prompt = f"""
The user asked:
{user_request}

The tool returned:
{tool_output}

Answer the user naturally. Use only what the tool returned.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": answer_prompt}],
    )

    return response.choices[0].message.content


async def main():

    mcp = await connect()

    tools = await discover_tools(mcp)

    print()
    print("Available Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    print()

    user_request = input("User : ")

    tool_name = choose_tool(user_request, tools)

    print()
    print("Planner Selected:", tool_name)

    result = await execute_tool(mcp, tool_name)
    tool_output = result.content[0].text

    print("Tool output:", tool_output)
    print()

    reply = answer_user(user_request, tool_output)
    print("AI :", reply)

    await disconnect(mcp)


if __name__ == "__main__":

    asyncio.run(main())
```

### Line-by-line (`agent.py`)

| Order | Code | What happens |
|-------|------|----------------|
| 1 | `from planner import choose_tool` | **LLM #1** lives in `planner.py` (Topic 18 style) |
| 2 | `mcp = await connect()` | Server subprocess + session |
| 3 | `tools = await discover_tools(mcp)` | List passed into `choose_tool(user_request, tools)` |
| 4 | `choose_tool(user_request, tools)` | **LLM #1** in `planner.py` |
| 5 | `await execute_tool(mcp, tool_name)` | **MCP** runs tool on server |
| 6 | `answer_user(user_request, tool_output)` | **LLM #2** — wording only; facts from MCP text |
| 7 | `asyncio.run(main())` | Run `python agent.py` |

### Line-by-line (`answer_user`)

| Piece | Meaning |
|-------|---------|
| `tool_output` | Always from MCP in this lab — not `None` (unlike Topic 18 when planner returns `none`) |
| `answer_prompt` | Same shape as Topic 18 second `chat.completions.create` |
| Return value | Printed as `AI :` in `main()` |

### How `build_tool_descriptions` links MCP to the planner

```text
server.py @mcp.tool docstrings
        │
        ▼
MCP tools/list  →  tool.name, tool.description
        │
        ▼
build_tool_descriptions()  →  numbered list in planner prompt
        │
        ▼
LLM #1  →  "roll_dice" / "current_time" / ...
```

**Example string** passed into the planner (from this server):

```text
1. current_time
   Return the current date and time.

2. roll_dice
   Roll a six-sided dice.

3. generate_password
   Generate a secure password.
```

If you add a new `@mcp.tool` on the server, **restart the run** — discovery picks it up automatically; you do not edit a static tool list in `agent.py` (unlike Topic 18’s prompt that names tools in code).

### Try other prompts (experiments)

| User says (examples) | Planner often picks | MCP runs |
|----------------------|---------------------|----------|
| what time is it | `current_time` | clock on server machine |
| roll a dice | `roll_dice` | random 1–6 |
| make me a password | `generate_password` | default length 12 |

**Limitation (this lab):** LLM #1 returns **only the tool name**, not JSON arguments. `generate_password` always uses server default length unless you extend the planner to return arguments and pass them to `execute_tool(mcp, name, {"length": 8})`.

---

## Picture: one run of `agent.py`

```text
agent.py :: main()
      │
      ├─► mcp_client :: connect()
      │         └─► fastmcp.Client(SERVER_SCRIPT)  ──spawns──►  server.py
      │
      ├─► mcp_client :: discover_tools()  ──► list_tools()
      │
      ├─► input("User : ")
      │
      ├─► planner.py :: choose_tool()  ──► OpenAI  (LLM #1)  ──► tool_name
      │
      ├─► mcp_client :: execute_tool(tool_name)  ──► call_tool()
      │         └─► (MCP)  ──►  server.py :: e.g. current_time()
      │
      ├─► answer_user()  ──► OpenAI  (LLM #2)  ──► print "AI :"
      │
      └─► mcp_client :: disconnect()
```

---

## Common mistakes

| Mistake | What happens |
|---------|----------------|
| Missing or wrong `OPENAI_API_KEY` | OpenAI auth error |
| Deprecated / invalid `OPENAI_MODEL` | **404 `model_not_found`** from OpenAI |
| Planner returns extra text (`"Use roll_dice"`) | `call_tool` may fail — prompt says reply **only** tool name |
| Planner typo vs MCP name (`get_current_time` vs `current_time`) | MCP error — names must match `@mcp.tool` function names |
| Run `server.py` and type questions in terminal | stdin expects **JSON-RPC**, not chat (same as PROJECT_1/2) |
| Forget `await` on MCP helpers | Coroutine never runs — see PROJECT_2 async table |

**FastMCP 4.x:** `Client(pathlib.Path(...))` via `SERVER_SCRIPT` — see PROJECT_2 notes.

---

## Quick recap

1. **Run:** `python agent.py` — entry is **`agent.py` → `main()`**.  
2. **Discovery** from MCP feeds **LLM #1** — tools are not imported from `server.py`.  
3. **Execution** is always **`execute_tool`** → subprocess **`server.py`**.  
4. **LLM #2** only phrases the answer; facts for tool turns come from MCP tool output.  
5. **PROJECT_2** = same MCP client, no LLM. **Topic 18** = same two LLM roles, local `tools.py`.  
6. Full MCP caller → callee detail: [`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md#who-calls-whom--files-and-functions).

---

## Next

- Cursor as host: [`PROJECT_1/7_weather_py.md`](../PROJECT_1/7_weather_py.md)  
- Official **tools / function calling** on the API: Topic 5 [`tool_functions_1.md`](../../5_TOOLS_FUNCTIONS/tool_functions_1.md)  
- Chapter theory: [`3_communication_flow.md`](../3_communication_flow.md)
