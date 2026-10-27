# `weather.py` — FastMCP server (US weather via NWS API)

Hands-on **MCP server**: two async tools call the free **U.S. National Weather Service (NWS)** API. A **host** (Claude Desktop, Cursor, MCP Inspector) connects over **stdio**; the LLM in the host chooses when to call `get_alerts` or `get_forecast`.

This file is **not** a chatbot. There is **no** OpenAI call inside `weather.py` — only HTTP to `api.weather.gov` when a host invokes a tool.

Folder: **`19_MCP_MODEL_CONTEXT_PROTOCOL/PROJECT_1/`** (weather lab).

Read first: [`6_fastmcp.md`](../6_fastmcp.md) · MCP basics [`1_introduction.md`](../1_introduction.md) → [`5_mcp_capabilities.md`](../5_mcp_capabilities.md).  
Script: [`weather.py`](./weather.py).

---

## Requirements

```bash
pip install mcp httpx
```

| Package | Used for |
|---------|----------|
| `mcp` | `FastMCP` server (`from mcp.server.fastmcp import FastMCP`) |
| `httpx` | Async HTTP client for NWS API |

**Note:** [`6_fastmcp.md`](../6_fastmcp.md) shows `from fastmcp import FastMCP` in some tutorials. **This repo** uses the **official MCP Python SDK** import path that matches [`weather.py`](./weather.py).

**Data scope:** NWS covers **United States** locations. Forecast needs **latitude/longitude**; alerts need a **two-letter US state code** (e.g. `NY`, `CA`).

No API key for NWS — but you must send a **`User-Agent`** header (your script does).

---

## How to run

| Goal | What to do |
|------|------------|
| **Use weather in chat** | Configure [`mcp.json`](#connect-in-cursor-mcpjson) and ask the **Cursor Agent** (e.g. “weather for California”) — **do not** type cities into `python weather.py` |
| **Test tools without Cursor** | `mcp dev weather.py` (Inspector UI) |
| **See the server start (debug only)** | `python weather.py` — leave terminal **empty**; Cursor/MCP client sends JSON on stdin |

### Wrong: typing `california` after `python weather.py`

This is **not** like Topic 18’s `assistant.py` (terminal chat). `weather.py` is an **MCP server** on **stdio**: it expects **JSON-RPC** messages on stdin from a **host** (Cursor, Inspector), not plain English.

If you run:

```bash
python weather.py
california
```

you may see:

```text
ERROR    Received exception from stream: 1 validation error for JSONRPCMessage
         Invalid JSON: expected value at line 1 column 1
         input_value='california\n'
```

| What you did | What the server expected |
|--------------|---------------------------|
| Typed `california` + Enter | A JSON line like `{"jsonrpc":"2.0","id":1,"method":"tools/call",...}` |

The server tried to parse your text as JSON → **validation error**. That is normal; you did not break the script.

```text
Topic 18 assistant.py          weather.py (MCP server)
──────────────────────          ────────────────────────
You : california    ✅          stdin: california      ❌ (not JSON-RPC)
AI : (LLM reply)                ERROR Invalid JSON

Cursor Agent : california  ✅  →  host sends proper JSON  →  get_forecast / get_alerts  ✅
```

**Correct ways to get California weather**

1. **Cursor** — `mcp.json` weather server enabled → Agent chat: *“use MCP weather for California”*.  
2. **Inspector** — `mcp dev weather.py` → pick `get_alerts` with `state: CA` or `get_forecast` with lat/long.  
3. **Do not** use the `python weather.py` terminal as a chat UI.

### `python weather.py` alone

From **`PROJECT_1`** (folder that contains `weather.py`):

```bash
cd PROJECT_1
python weather.py
```

The process **blocks** waiting for MCP protocol on stdin. That is correct. **Do not type** questions there unless you are manually sending JSON-RPC (you are not, in normal use).

**Development (recommended):**

```bash
mcp dev weather.py
```

Opens the **MCP Inspector** so you can list tools and call `get_forecast` / `get_alerts` with a form UI.

**Claude Desktop:** after testing, use `mcp install` (see [`6_fastmcp.md`](../6_fastmcp.md)) or add the server in host MCP settings.

---

## Connect in Cursor (`mcp.json`)

Cursor is an **MCP host**: it starts your server as a subprocess and exposes `get_forecast` / `get_alerts` to the **chat Agent**.

### Where the file lives

| OS | Typical path |
|----|----------------|
| Linux / WSL | `~/.cursor/mcp.json` |
| macOS | `~/.cursor/mcp.json` |
| Windows | `%USERPROFILE%\.cursor\mcp.json` |

Open **Cursor Settings → MCP** (or edit the JSON directly). Servers live under the top-level key **`mcpServers`**.

### Entry added for this lab

Inside `mcpServers`, add a server named **`weather`** (the name is up to you; Cursor shows it in MCP tools):

```json
"weather": {
  "command": "/home/soudas/miniforge3/envs/my-proj/bin/python3",
  "args": [
    "/home/soudas/PERSONAL/AI_LEARNING/AI_LEARNING/19_MCP_MODEL_CONTEXT_PROTOCOL/PROJECT_1/weather.py"
  ]
}
```

| Field | Meaning |
|-------|---------|
| **`"weather"`** | Server **id** in Cursor (label in MCP list / tool namespace) |
| **`command`** | Interpreter that runs the server — use the same env where you `pip install mcp httpx` (**`my-proj`** here) |
| **`args`** | Script path — must be the full path to [`weather.py`](./weather.py) on your machine |

**Shape (mental model):**

```text
Cursor Agent  →  spawns:  command + args[0]
                         = python3 weather.py
              →  stdio JSON-RPC  ↔  FastMCP tools
```

No `url` field — this is a **local stdio** server (not HTTP/SSE like some other entries in a big `mcp.json`).

### After you save

1. **Save** `mcp.json`.  
2. **Reload MCP** in Cursor (Settings → MCP → refresh / restart servers) or restart Cursor.  
3. Confirm the **weather** server shows **connected** (green / no error).  
4. If it fails: check `command` exists, `mcp` and `httpx` are installed in that env, and `args` points at **`PROJECT_1/weather.py`** (update `~/.cursor/mcp.json` if you moved the file).

### How the Agent uses it

You do **not** call `get_forecast` yourself in Python during chat. You ask in **natural language**; the Agent may invoke MCP tools when needed.

```text
You (Cursor chat)  →  Agent (LLM)  →  MCP tool: get_forecast / get_alerts
                                              │
                                              ▼
                                        weather.py  →  NWS API
                                              │
You  ←  Agent summarizes tool output  ←────────┘
```

In the UI you may see tool use (e.g. calling **`get_forecast`** or **`get_alerts`**) before the final answer.

---

## Cursor Agent examples — Kolkata vs California

Real prompts from this learning session (same setup as above).

### Example A — Kolkata (outside NWS)

**You asked (paraphrase):** use the MCP tool and get weather for **Kolkata**.

**What the Agent did:**

| Step | Action |
|------|--------|
| 1 | Chose tool **`get_forecast`** (needs latitude / longitude) |
| 2 | Used Kolkata-ish coordinates: **22.5726**, **88.3639** |
| 3 | MCP server ran [`weather.py`](./weather.py) → NWS `/points/22.5726,88.3639` |

**Tool result:**

```text
Unable to fetch forecast data for this location.
```

**Why:** NWS ([`api.weather.gov`](https://api.weather.gov)) is **United States only**. Kolkata is in India — the points lookup fails; your server returns that string by design ([`make_nws_request`](./weather.py) → `None`).

**Lesson:** MCP worked (host → server → HTTP). The **data source** does not cover that place. For global cities you need a different API in the server, not a different MCP wire format.

---

### Example B — California (works with NWS)

**You asked (paraphrase):** weather for **California**.

California is a **state**, so the Agent can use **two** tools:

#### 1) Statewide alerts — `get_alerts`

| Argument | Value |
|----------|--------|
| `state` | `"CA"` |

**Sample outcome:** active NWS alerts (e.g. **Freeze Watch** in Trinity / Mendocino / Lake areas; **Lake Wind Advisory** for Greater Lake Tahoe with east winds and rough waves). Text is long; the Agent summarizes for chat.

#### 2) Forecast — `get_forecast` (needs a point inside CA)

NWS has no “whole state” forecast in one call. The Agent picks a **lat/long** inside California — e.g. **Los Angeles** **34.0522**, **-118.2437**.

**Sample periods returned (abbreviated):**

| Period | Temp | Conditions (summary) |
|--------|------|----------------------|
| Today | High ~72°F | Mostly sunny, light SSW wind |
| Tonight | Low ~55°F | Mostly clear |
| Saturday | High ~76°F | Sunny |
| Saturday night | Low ~58°F | Mostly clear |
| Sunday | High ~78°F | Sunny |

The Agent turns that tool string into a readable reply. You can also ask explicitly: *“forecast for San Francisco”* → Agent should call `get_forecast` with **~37.77, -122.42**.

### Compare the two asks

| You said | Tool(s) typically used | Works with this `weather.py`? |
|----------|------------------------|-------------------------------|
| Kolkata weather | `get_forecast(lat, lon)` | **No** — outside US NWS grid |
| California weather | `get_alerts("CA")` + often `get_forecast` for a CA city | **Yes** |

---

## What this file teaches

| Piece | In `weather.py` |
|-------|-----------------|
| **MCP server** | `mcp = FastMCP("weather")` + `mcp.run(transport="stdio")` |
| **Tools** | `@mcp.tool()` → `get_alerts`, `get_forecast` |
| **Real HTTP** | `httpx` + `make_nws_request` |
| **Host / LLM** | **Outside** this file — host’s model picks tools |

### Compared to Topic 18

| | Topic 18 `assistant.py` | `weather.py` |
|--|-------------------------|--------------|
| Who runs tools | Your Python loop + planner LLM | **Host** MCP client |
| Network | OpenAI API | **NWS** `api.weather.gov` |
| User UI | Terminal `You :` / `AI :` | Claude / Cursor / Inspector |

---

## Main idea — who does what?

| Component | Runs `weather.py`? | Calls NWS? | Calls OpenAI? |
|-----------|-------------------|------------|---------------|
| **`weather.py` (server)** | Yes (subprocess) | **Yes**, when a tool runs | **No** |
| **Host + LLM** | No (starts server) | No | **Yes** (in the host app) |

When the user asks *“What’s the weather in New York?”* in Claude:

1. **Host LLM** decides to call `get_forecast` (with lat/long) or another tool.  
2. **MCP client** sends `tools/call` over stdio.  
3. **`get_forecast`** in this file runs → two NWS HTTP requests → returns a **string**.  
4. **Host LLM** reads that string and answers in natural language.

```text
User  →  Host (LLM)  →  MCP client  →  stdio  →  weather.py tools
                                                      │
                                                      ▼
                                                 NWS HTTP API
                                                      │
User  ←  Host (LLM)  ←  tool result string  ←────────┘
```

---

## Where is the MCP client? (not in `weather.py`)

**You will not find client code in this repo file.** That is normal.

| Piece | Where it lives | In this lab |
|-------|----------------|-------------|
| **MCP server** | [`weather.py`](./weather.py) | `FastMCP` + `@mcp.tool()` + `mcp.run(transport="stdio")` |
| **MCP client** | **Inside the host app** | **Cursor** (when `mcp.json` runs this script) |
| **Host** | Same app as the client | Cursor chat + Agent + LLM |

```text
┌──────────────────────────── Cursor (HOST) ────────────────────────────┐
│  You chat  →  Agent / LLM  →  MCP CLIENT  ──stdin/stdout JSON-RPC──┐  │
└────────────────────────────────────────────────────────────────────│──┘
                                                                     │
┌──────────────────────── weather.py (SERVER) ───────────────────────▼──┐
│  FastMCP reads JSON-RPC  →  runs get_forecast / get_alerts  →  NWS    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Who is the client for you?**

| How you run | Host | MCP client |
|-------------|------|------------|
| **`mcp.json` + Cursor Agent** | Cursor | Built into Cursor; spawns `python3 weather.py` and talks on stdio |
| **`mcp dev weather.py`** | MCP Inspector | Dev UI + client bundled with the `mcp` CLI |
| **`python weather.py` alone** | *Nobody* | No client connected — only type JSON-RPC if you are debugging protocol by hand |

Topic **18** put planner + tools + chat loop **in one project** (`assistant.py` + `planner.py`). Topic **19** splits roles: **you author the server**; **the host ships the client**.

You do **not** need to write `MCPClient(...)` in Python for Cursor to use your tools — configuring `mcp.json` is how you attach your server to Cursor’s existing client.

See also: [`2_core_mcp_terminology.md`](../2_core_mcp_terminology.md) (host / client / server).

---

## Tool summary

| Tool | Arguments | NWS path (idea) | Returns |
|------|-----------|-----------------|---------|
| `get_alerts` | `state: str` (2-letter) | `/alerts/active/area/{state}` | Formatted alert text or message |
| `get_forecast` | `latitude`, `longitude` | `/points/{lat},{lon}` then forecast URL from response | Next **5** forecast periods as text |

---

## Full source — `weather.py`

```python
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

---

## Line-by-line walkthrough

### Imports and server object

| Lines | Code | Meaning |
|-------|------|---------|
| `typing.Any` | Type hint for JSON-like dicts from NWS | |
| `httpx` | Modern async HTTP library (like `requests`, but async-friendly) | |
| `FastMCP` from `mcp.server.fastmcp` | Server helper from the **official MCP Python SDK** | |
| `mcp = FastMCP("weather")` | Server display name `"weather"` — shows up in host logs / tool namespace | |
| `NWS_API_BASE` | Base URL for all NWS calls | |
| `USER_AGENT` | NWS requires a identifiable User-Agent string | |

### `make_nws_request(url)`

| Piece | Meaning |
|-------|---------|
| `async def` | Tool handlers are async; HTTP should not block the event loop |
| `Accept: application/geo+json` | NWS GeoJSON format |
| `httpx.AsyncClient()` | One client per request (simple; fine for a demo) |
| `timeout=30.0` | Avoid hanging forever on bad network |
| `raise_for_status()` | Turn HTTP 4xx/5xx into exceptions |
| `except Exception: return None` | Any failure → `None` so tools return friendly strings instead of crashing the server |

### `format_alert(feature)`

NWS alerts are **GeoJSON** `features`. Each `feature` has a `properties` dict with event name, area, severity, etc. This function turns one feature into readable text for the LLM.

### `get_alerts(state)` — tool 1

| Step | What happens |
|------|----------------|
| 1 | Build URL `/alerts/active/area/{state}` (e.g. `NY`) |
| 2 | `make_nws_request` → JSON with `features` list |
| 3 | Empty or missing data → user-facing error string |
| 4 | No features → `"No active alerts for this state."` |
| 5 | Else format each feature, join with `\n---\n` |

The **docstring** and **`Args:`** block help the host’s LLM know `state` must be a two-letter code.

### `get_forecast(latitude, longitude)` — tool 2

NWS uses a **two-step** forecast flow:

```text
GET /points/{lat},{lon}     →  JSON with properties.forecast (URL)
GET {forecast URL}          →  JSON with properties.periods[]
```

| Step | Code | Meaning |
|------|------|---------|
| 1 | `points_url = .../points/{latitude},{longitude}` | Resolve grid point for coordinates |
| 2 | Read `points_data["properties"]["forecast"]` | NWS gives the **next** URL — not the forecast inline |
| 3 | Second `make_nws_request(forecast_url)` | Fetch detailed periods |
| 4 | `periods[:5]` | Only first **5** periods (keeps tool output smaller for the LLM) |
| 5 | Join formatted blocks | Single string returned to MCP host |

**Why lat/long?** NWS API is grid-based. The host LLM often geocodes “New York” to coordinates before calling the tool.

### `main()` and `mcp.run(transport="stdio")`

| Piece | Meaning |
|-------|---------|
| `transport="stdio"` | Host talks to this process via **stdin/stdout** ([`4_the_communication_protocol.md`](../4_the_communication_protocol.md)) |
| `if __name__ == "__main__"` | Running `python weather.py` starts the server entry point |

---

## Picture: `get_forecast` data flow

```text
Host calls get_forecast(40.71, -74.01)
        │
        ▼
make_nws_request("/points/40.71,-74.01")
        │
        ▼
forecast_url from properties.forecast
        │
        ▼
make_nws_request(forecast_url)
        │
        ▼
format periods[0:5]  →  one big str  →  MCP result  →  Host LLM  →  user
```

---

## Trying tools in MCP Inspector (example)

After `mcp dev weather.py`:

| Tool | Example arguments | What you should see |
|------|-------------------|---------------------|
| `get_alerts` | `state`: `"CA"` | Alert text blocks or “No active alerts…” |
| `get_forecast` | `latitude`: `37.77`, `longitude`: `-122.42` | Several periods with temperature and `detailedForecast` |

If forecast fails, coordinates may be outside US coverage or NWS may be temporarily unavailable (`None` from `make_nws_request`).

---

## What this file does **not** do

| Not included | Why |
|--------------|-----|
| Geocoding city names | Host LLM or another tool must supply lat/long |
| Non-US weather | NWS is US-only |
| Caching | Every tool call hits the network |
| Detailed MCP logging | Add if you debug protocol issues |

---

## Quick recap

1. **`weather.py`** is an **MCP server** with two **tools**, not a standalone chat app.  
2. **`@mcp.tool()`** + **async** functions expose capabilities to any MCP host.  
3. **`make_nws_request`** centralizes HTTP + errors for the NWS API.  
4. **`get_forecast`** uses NWS **points → forecast URL → periods** (two HTTP calls).  
5. **`mcp.run(transport="stdio")`** — Cursor runs it via **`~/.cursor/mcp.json`** (`command` + `args`).  
6. **Do not** type city names into the `python weather.py` terminal — stdin must be **JSON-RPC**, not chat.  
7. **Cursor Agent** — you chat there; Agent calls **`get_forecast`** / **`get_alerts`** (CA yes, Kolkata no with NWS).

---

## Files in this chapter (MCP + labs)

| # | Item |
|---|------|
| `1_` … `5_` | Theory (chapter root) — [`README.md`](../README.md) |
| [`6_fastmcp.md`](../6_fastmcp.md) | FastMCP concepts |
| **`PROJECT_1/`** | [`weather.py`](./weather.py) + **this note** — NWS MCP server |
| **`PROJECT_2/`** | [`8_mcp_client_lab.md`](../PROJECT_2/8_mcp_client_lab.md) — `server.py` + `mcp_client.py` + `test_client.py` |
