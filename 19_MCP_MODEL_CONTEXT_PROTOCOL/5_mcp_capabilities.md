# MCP capabilities

Chapter notes (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

Read first: [`4_the_communication_protocol.md`](./4_the_communication_protocol.md).  
Chapter start: [`1_introduction.md`](./1_introduction.md) · index: [`README.md`](./README.md).

MCP servers expose several kinds of **capabilities**. **Tools** are the main focus for most builders; **resources** and **prompts** are also part of the standard.

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [Tools](#1-tools) |
| 2 | [Resources](#2-resources) |
| 3 | [Prompts](#3-prompts) |
| 4 | [Sampling](#4-sampling) |
| 5 | [Summary table](#5-summary-table) |

---

## 1. Tools

**Tools** are executable functions or actions the AI model can invoke through MCP.

| Aspect | Notes |
|--------|--------|
| **Control** | Usually **model-controlled** — the LLM decides when to call, based on user request and context |
| **Safety** | Tools can have **side effects** (send email, delete file). Hosts often require **explicit user approval** |
| **Use cases** | Send messages, create tickets, query APIs, run calculations |

**Example** (conceptual server-side Python):

```python
def get_weather(location: str) -> dict:
    """Get the current weather for a specified location."""
    # Connect to weather API and fetch data
    return {
        "temperature": 72,
        "conditions": "Sunny",
        "humidity": 45,
    }
```

Compare **Topic 18:** `roll_dice()` in [`tools.py`](../18_AI_AGENTS_INTRO/tools.py) — same *idea*, but exposed via MCP so hosts like Cursor or Claude Desktop can call it without your custom `assistant.py`.

---

## 2. Resources

**Resources** provide **read-only** access to data — context for the model without running arbitrary “action” logic on every read.

| Use cases | File contents, database records, configuration |
|-----------|-----------------------------------------------|

**Example:**

```python
def read_file(file_path: str) -> str:
    """Read the contents of a file at the specified path."""
    with open(file_path, "r") as f:
        return f.read()
```

Popular for sharing **RAG**-style corpora: one MCP server exposes documents; many hosts can attach the same resource surface.

---

## 3. Prompts

**Prompts** are predefined **templates** or workflows on the server — guided interactions between user, model, and server capabilities.

| Use cases | Common workflows, task templates, specialized review flows |
|-----------|--------------------------------------------------------------|

**Example idea** — a `code_review` prompt that returns chat messages for the host’s LLM:

```python
def code_review(code: str, language: str) -> list:
    """Generate a code review for the provided code snippet."""
    return [
        {
            "role": "system",
            "content": (
                f"You are a code reviewer examining {language} code. "
                "Highlight best practices, issues, and improvements."
            ),
        },
        {
            "role": "user",
            "content": f"Please review this {language} code:\n\n```{language}\n{code}\n```",
        },
    ]
```

**Adoption:** prompts are part of the spec but **less common** in the wild than tools and resources.

---

## 4. Sampling

**Sampling** lets a **server** ask the **client** (host) to run an **LLM completion** — reverse direction from the usual “host asks server for a tool.”

| Use cases | Multi-step tasks, server-driven analysis using the host’s model |
|-----------|----------------------------------------------------------------|

**Example shape** (conceptual):

```python
def request_sampling(messages, system_prompt=None, include_context="none"):
    """Request LLM sampling from the client."""
    # Real MCP: server sends a sampling request; host runs the model and returns text
    return {
        "role": "assistant",
        "content": "Analysis of the provided data...",
    }
```

Treat sampling as **advanced** — learn tools and resources first.

---

## 5. Summary table

| Capability | Read / write | Who drives it | Typical excitement |
|------------|--------------|---------------|-------------------|
| **Tools** | Actions (often write side effects) | Model + host approval | Highest |
| **Resources** | Read-only data | Host / model retrieval | High (RAG sharing) |
| **Prompts** | Template messages | Server provides pattern | Medium |
| **Sampling** | LLM call via host | Server requests | Advanced |

---

## Next

- FastMCP (Python servers): [`6_fastmcp.md`](./6_fastmcp.md)  
- Hands-on server: [`PROJECT_1/weather.py`](./PROJECT_1/weather.py) · [`PROJECT_1/7_weather_py.md`](./PROJECT_1/7_weather_py.md)  
- Official spec: [modelcontextprotocol.io](https://modelcontextprotocol.io)
