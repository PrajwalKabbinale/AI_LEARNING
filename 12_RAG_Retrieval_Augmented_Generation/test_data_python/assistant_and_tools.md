# `tools.py` & `assistant.py`

Terminal assistant with **keyword shortcuts** that call Python from [`tools.py`](./tools.py) **without** the LLM, plus one shortcut (**`summary`**) that **reads a file locally** then calls OpenAI to summarize it.

This is **not** OpenAI **tools / function calling** yet (no `tools=` on the API). Your code checks the user text (`read`, `time`/`date`, `summary`) and runs functions directly—or builds a one-off `messages` list for a single API call. Compare:

| Step | Files | How “tools” work |
|------|--------|------------------|
| Earlier | [`tool_functions_2_and_tools_2.md`](../../5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) | Keywords → `tools_2.py`; else → chat with memory |
| **This note** | `tools.py` + `assistant.py` | Keywords → `tools.py`; **`summary`** → `read_text_file` then **one** `chat.completions.create` |
| Later RAG | [`keyword_rag_gradio_chat.md`](../keyword_rag_gradio_chat.md) | Load knowledge dict → match words → augment system prompt |

Related: [`chat_message_roles.md`](../../1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_message_roles.md) (`system` / `user` / `assistant`).

---

## Requirements

```bash
pip install openai python-dotenv
```

`.env` example (folder where `load_dotenv()` finds it):

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1-nano
```

`MODEL` in code comes from `os.getenv("MODEL_NAME")` after `load_dotenv()`.

---

## How to run

```bash
cd test_data_python
python assistant.py
```

1. Banner lists commands (`time/date`, `read`, `summarize`, `quit`).  
2. **`read`** or **`summary`** — in the **current** code the file is always [`notes.txt`](./notes.txt) (hard-coded); typing `read` or `summary` alone is enough.  
3. **`time`** or **`date`** anywhere in the line → clock, no API.  
4. **`quit`** → exit.

Run from **`test_data_python`** so `read_text_file("notes.txt")` finds the file (path is relative to the **current working directory**).

---

## What these files teach

| File | Role |
|------|------|
| [`tools.py`](./tools.py) | Local helpers: `get_current_time`, `read_text_file` |
| [`assistant.py`](./assistant.py) | Loop: keywords → call `tools.py`; **`summary`** → read file + LLM summarize |
| [`notes.txt`](./notes.txt) | Small document used for **read** and **summary** demos |

---

## Main idea — when is the LLM called vs only Python?

Every time you type something and press Enter, `assistant.py` does **one** of these. Only the **`summary`** branch talks to OpenAI.

| What you typed | Who answers? | Is `client.chat.completions.create(...)` called? | Functions in `tools.py`? | Chat history kept? |
|----------------|--------------|--------------------------------------------------|---------------------------|---------------------|
| Starts with **`read`** (e.g. `read`) | **Your PC** — prints file via `read_text_file` | **No** | Yes | **No** — `continue` |
| Contains **`time`** or **`date`** (e.g. `time`) | **Your PC** — `get_current_time()` | **No** | Yes | **No** |
| Starts with **`summary`** (e.g. `summary`) | **OpenAI** (after you read the file in Python) | **Yes** — one call | Yes (`read_text_file` first) | **No** — `messages` is built only for that API call, then discarded |
| **`quit`** | **Your script** — fixed goodbye | **No** | No | No |
| Anything else | **Your script** — help hint | **No** | No | No |

**LLM** here means: send a `messages` list to OpenAI, wait for the model, read `response.choices[0].message.content`.

**Python tool functions** here means: run code from `tools.py` on your machine. For **read** / **time**, you `print` the result and **never** call the API for that turn.

The label **`AI :`** is printed for local tools and for the model. That is only formatting — for **read** / **time**, the text is **not** from the model.

Unlike `tool_functions_2.py`, this script does **not** keep a growing `messages` list across turns. Only the **summary** path creates `messages` (system + user with the file inside), sends it once, then loops again.

---

### Picture: one loop iteration

```text
                    user_input
                         │
     ┌───────────────────┼───────────────────┬─────────────┐
     │                   │                   │             │
startswith "read"   "time"/"date"      startswith      else
     │                   │              "summary"          │
     ▼                   ▼                   ▼             ▼
read_text_file    get_current_time   read_text_file    quit? ──yes──► goodbye
(notes.txt)              │           (notes.txt)              │
     │                   │                   │             no ▼
     ▼                   ▼                   ▼             hint
 print file          print time      user_prompt + messages[]
     │                   │                   │
     └──────── continue ─┴───────────────────┘
                              │
                              ▼
                 chat.completions.create(...)   [summary only]
                              │
                              ▼
                    print model summary
                              │
                         continue
```

`continue` means: **skip everything below** in the loop (no API on read/time after print).

---

### Walkthrough: your sample session

| Step | You type | Path | Network / API? | What the model saw |
|------|----------|------|----------------|---------------------|
| 1 | `read` | Python — `read_text_file("notes.txt")` | No | Nothing |
| 2 | `time` | Python — `get_current_time()` | No | Nothing |
| 3 | `summary` | Python read, then LLM | **Yes** — one API call | See **The `summary` branch** under `assistant.py` line-by-line |
| 4 | `quit` | Script | No | Nothing |

The model **never saw** `read` or `time`. If you only use those commands, you do not need a working API key for those turns.

---

### Code order matters (`assistant.py`)

Checks run **top to bottom**; first match wins:

```python
if "time" in text or "date" in text:
    print("\nAI :", get_current_time())
    continue

if text.startswith("read"):
    print("\nAI :\n", read_text_file("notes.txt"))
    continue

if text.startswith("summary"):
    file_content = read_text_file("notes.txt")
    user_prompt = f"Summarize the following document.\n\nDocument:\n\n{file_content}"
    # ... messages + client.chat.completions.create(...)
    continue
```

| Line / block | LLM? | Why |
|--------------|------|-----|
| `read_text_file(...)` on **read** | No | Same as opening a file in Python; you print the string. |
| `get_current_time()` | No | Clock on your machine. |
| `read_text_file` then `user_prompt` on **summary** | No for read; **Yes** for `.create` | File load is local; summarization is the API. |
| `continue` | No | Ends this iteration; no fall-through. |
| `chat.completions.create(...)` | **Yes** | **Only** on the **summary** branch. |

Details of `user_prompt`, `messages`, and what OpenAI receives are under **Line-by-line (`assistant.py`)** → **The `summary` branch**.

---

### Do you need `OPENAI_API_KEY`?

| Session style | API key needed? |
|---------------|-----------------|
| Only `read`, `time`, then `quit` | **No** |
| Any **`summary`** turn | **Yes** |

---

## Full source — `tools.py`

```python
from datetime import datetime

def get_current_time():
    """Return the current date and time."""

    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

def read_text_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read()

    except FileNotFoundError:
        return "Error: File not found."
```

### Line-by-line (`tools.py`)

**Imports**

| Import | Used for |
|--------|----------|
| `datetime` | `datetime.now()` inside `get_current_time()`. |

**`get_current_time()`**

| Piece | Meaning |
|-------|---------|
| `datetime.now()` | Current local date/time on the machine running the script. |
| `.strftime("%d-%m-%Y %I:%M:%S %p")` | Format like `11-10-2026 03:09:32 PM`. |
| Return value | **String** printed when the user message contains **`time`** or **`date`**. |

**`read_text_file(filename)`**

| Piece | Meaning |
|-------|---------|
| `open(filename, "r")` | Read text from disk (`filename` relative to cwd unless absolute). |
| `file.read()` | Whole file as one string. |
| `FileNotFoundError` | Return `"Error: File not found."` instead of crashing. |
| Trigger in main app | **`read`** branch (print as-is) and **`summary`** branch (pass into `user_prompt`). |

---

## Full source — `assistant.py`

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import get_current_time, read_text_file

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL_NAME")

SUMMARIZE_SYSTEM = "You are a helpful assistant."

print("Commands: time/date | read <file> | summarize <file> | quit\n")

while True:
    user_input = input("\nYou : ").strip()
    text = user_input.lower()

    if "time" in text or "date" in text:
        print("\nAI :", get_current_time())
        continue

    if text.startswith("read"):
        filename = "notes.txt"
        print("\nAI :\n", read_text_file(filename))
        continue

    if text.startswith("summary"):
        filename = "notes.txt"
        file_content = read_text_file(filename)

        user_prompt = f"Summarize the following document.\n\nDocument:\n\n{file_content}"

        messages = [
            {
                'role': 'system',
                'content': SUMMARIZE_SYSTEM
            },
            {
                'role': 'user',
                'content': user_prompt
            }
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        print("\nAI :", response.choices[0].message.content)
        continue

    if text == "quit":
        print("\nAI : Goodbye!")
        break

    print("\nAI : Try 'what time is it?', 'read notes.txt', 'summarize notes.txt', or 'quit'.")
```

---

## Line-by-line (`assistant.py`)

### Setup (before the loop)

#### `from tools import get_current_time, read_text_file`

This Python import statement:

```python
from tools import get_current_time, read_text_file
```

means you're importing two functions, `get_current_time` and `read_text_file`, from a Python module named `tools` (the file [`tools.py`](./tools.py)).

- **`get_current_time`** — returns the current date and time as a formatted string.
- **`read_text_file`** — returns file contents as a string (or an error message).
- **`tools`** — the module file `tools.py`; **not** an OpenAI `tools=` definition.

Example usage:

```python
from tools import get_current_time, read_text_file

print(get_current_time())
print(read_text_file("notes.txt"))
```

Important: Both functions must be defined in `tools.py`, and you should run `python assistant.py` from **`test_data_python`** so `notes.txt` resolves.

In **this** project, your script calls these functions when keywords match. That is **not** OpenAI tool calling — the model does not choose **read** or **time**. On **summary**, you still call `read_text_file` yourself, then call the API with the text inside `user_prompt`.

| Code | LLM called? | Meaning |
|------|-------------|---------|
| `from tools import get_current_time, read_text_file` | No | Import **local** functions only. |
| `client = OpenAI(...)` | No | Client object; no request until `.create(...)`. |
| `SUMMARIZE_SYSTEM` | No | System text for **summary** API calls only. |

### Inside `while True:` — each user line

| Order in file | Code | LLM? | What happens |
|---------------|------|------|----------------|
| 1 | `user_input = input(...)` | No | Read one line from terminal. |
| 2 | `"time" in text` or `"date" in text` → `get_current_time()` → `continue` | **No** | Python only; print; next prompt. |
| 3 | `startswith("read")` → `read_text_file` → `continue` | **No** | Print full file; no API. |
| 4 | `startswith("summary")` → read file → `user_prompt` → `messages` → `.create(...)` → `continue` | **Yes** | Read locally, then one LLM call. |
| 5 | `quit` → `break` | **No** | Exit; no API. |
| 6 | else → help `print` | **No** | Remind user of commands. |

Substring traps (by design):

- `time` → clock path even if you meant something else (e.g. a long sentence containing “time”).
- **`summary`** is checked **after** **read**; a line starting with `read` never hits **summary**.

### The `summary` branch — `read_text_file`, `user_prompt`, `messages`, API

This block is the **only** place in `assistant.py` that calls the LLM:

```python
    if text.startswith("summary"):
        filename = "notes.txt"
        file_content = read_text_file(filename)

        user_prompt = f"Summarize the following document.\n\nDocument:\n\n{file_content}"

        messages = [
            {
                'role': 'system',
                'content': SUMMARIZE_SYSTEM
            },
            {
                'role': 'user',
                'content': user_prompt
            }
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        print("\nAI :", response.choices[0].message.content)
        continue
```

| Step in code | LLM? | Meaning |
|--------------|------|---------|
| `file_content = read_text_file(filename)` | No | **Retrieve** — load `notes.txt` on your PC (same helper as **read**). |
| `user_prompt = f"..."` | No | Build the **user** message string; see table below. |
| `messages = [...]` | No | Two dicts only for this request (not stored for the next loop turn). |
| `client.chat.completions.create(...)` | **Yes** | Send `messages` to OpenAI; print the returned summary. |
| `continue` | No | Back to `You :` — no chat history appended. |

#### `user_prompt` line

```python
user_prompt = f"Summarize the following document.\n\nDocument:\n\n{file_content}"
```

| Piece | Meaning |
|-------|---------|
| `user_prompt =` | One string for the **user** `content` (keeps `messages` readable). |
| `f"..."` | **f-string** — inserts `{file_content}` from `read_text_file`. |
| `Summarize the following document.` | Instruction to the model. |
| `\n\n` | Blank line in the prompt. |
| `Document:` | Label before the file body. |
| `{file_content}` | Full `notes.txt` text — the model does not open the file; **you** read it and paste it here. |

Without `{file_content}`, the model would only see “summarize” and would **guess**. **Retrieve** with `read_text_file`, **generate** with the chat API (same idea as later RAG).

#### What the LLM receives on this turn

When you type `summary`, `chat.completions.create` sends roughly:

```python
[
  {"role": "system", "content": "You are a helpful assistant."},
  {
    "role": "user",
    "content": "Summarize the following document.\n\nDocument:\n\n<entire notes.txt text>",
  },
]
```

OpenAI returns one **assistant** message; your code prints it with `print("\nAI :", ...)`. That reply is **not** saved for the next turn.

On **read** or **time** turns, this API call **never runs** — the model is not asked anything.

| Line / block | LLM? | Why |
|--------------|------|-----|
| `read_text_file` on **read** / **summary** (before `.create`) | No | Local file I/O. |
| `messages` + `.create` on **summary** | **Yes** | Only path that uses the model. |
| `print` after `.create` | No (after LLM returns) | Show model text; not the same as `messages.append` in `tool_functions_2.py`. |

---

## Sample output

```bash
python assistant.py
```

Example session: **read**, **time**, **summary**, **quit**. Clock time and summary wording can change each run; structure matches your run.

```text
Commands: time/date | read <file> | summarize <file> | quit

You : read

AI :
 Python is one of the most popular programming languages.

It is easy to learn.

Python is widely used in Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.

Python supports object-oriented programming
and has thousands of useful libraries.


You : time

AI : 11-10-2026 03:09:32 PM

You : summary

AI : Python is a popular and easy-to-learn programming language widely used in AI, machine learning, data science, automation, and web development. It supports object-oriented programming and offers numerous libraries to facilitate development.

You : quit

AI : Goodbye!
```

**What to notice (LLM vs Python vs script)**

| Line you typed | Path | LLM API? |
|----------------|------|----------|
| `read` | `read_text_file` in `tools.py` | **No** |
| `time` | `get_current_time()` in `tools.py` | **No** |
| `summary` | `read_text_file` then `chat.completions.create` | **Yes** |
| `quit` | `print` goodbye in Python | **No** |

See **Main idea — when is the LLM called vs only Python?** above for what runs on each step.

Keyword-only session (no `OPENAI_API_KEY`): `read`, `time`, then `quit` — every answer except the help line is from **Python**, never the LLM.

---

## Keyword shortcuts vs OpenAI tools

| | This project (`assistant.py`) | `tool_functions_1` |
|--|-------------------------------|----------------------|
| Who decides to run a function? | **Your** `if` / `startswith` | **Model** (`tool_calls`) |
| API parameter | `messages` only (on summary) | `messages` + `tools=` |
| Role for function result | N/A (you `print` or embed file in user text) | `role: "tool"` in `messages` |

Keyword routing is easy to learn; **summary** here already looks like RAG’s “put context in the prompt” step before you build [`keyword_rag_gradio_chat.py`](../keyword_rag_gradio_chat.py).

---

## Files in this folder (order)

1. [`tools.py`](./tools.py) + [`notes.txt`](./notes.txt)  
2. [`assistant.py`](./assistant.py) — **this note**  
3. Next in chapter: [`keyword_rag_gradio_chat.md`](../keyword_rag_gradio_chat.md)
