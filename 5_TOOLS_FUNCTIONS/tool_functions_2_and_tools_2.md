# `tools_2.py` & `tool_functions_2.py`

Terminal assistant with a **system persona** (teacher, Python expert, etc.), **chat memory** (`messages` list), and **keyword shortcuts** that run Python from [`tools_2.py`](./tools_2.py) **without** calling the LLM.

This is **not** OpenAI **tools / function calling** yet (no `tools=` on the API). Your code checks the user text for words like `time` or `dice` and runs functions directly. Compare:

| Step | Files | How “tools” work |
|------|--------|------------------|
| 1 | [`helper_functions_and_demo.md`](./helper_functions_and_demo.md) | Plain `print()` demo |
| 2 | **This note** | Keywords → Python functions; else → Chat API |
| 3 | [`tool_functions_1.md`](./tool_functions_1.md) | LLM chooses tools via `tools=` + `tool_calls` |

Related: [`chat_message_roles.md`](../1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_message_roles.md) (`system` / `user` / `assistant`).

---

## Requirements

```bash
pip install openai python-dotenv
```

`.env` example (same folder you run from):

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1-nano
```

The script also sets a default `MODEL_NAME = "gpt-4.1-nano"` in code; `.env` overrides it when `load_dotenv()` runs before the API call.

---

## How to run

```bash
python tool_functions_2.py
```

1. Pick assistant **1–5** (or any other key → default helpful assistant).  
2. Chat in the terminal.  
3. Messages containing **`time`** or **`dice`** (anywhere in the text, case-insensitive) skip the API and use `tools_2.py`.  
4. Type **`quit`** to exit.

---

## What these files teach

| File | Role |
|------|------|
| [`tools_2.py`](./tools_2.py) | Local helpers: `get_current_time`, `roll_dice` (step 1’s [`helper_functions.py`](./helper_functions.py) also has `generate_password`; this demo does not) |
| [`tool_functions_2.py`](./tool_functions_2.py) | Menu of **system** prompts + loop: keywords → local functions; otherwise → `chat.completions.create` + memory |

---

## Main idea — when is the LLM called vs only Python?

Every time you type something and press Enter, `tool_functions_2.py` does **one** of three things. Only **one** of them talks to OpenAI.

| What you typed | Who answers? | Is `client.chat.completions.create(...)` called? | Functions in `tools_2.py`? | Added to `messages` list? |
|----------------|--------------|--------------------------------------------------|------------------------------|---------------------------|
| Contains **`time`** (e.g. `what time is it?`) | **Your PC** — `get_current_time()` | **No** | Yes | **No** — loop hits `continue` before `messages.append` |
| Contains **`dice`** (e.g. `dice roll`) | **Your PC** — `roll_dice()` | **No** | Yes | **No** |
| **`quit`** | **Your script** — fixed goodbye string | **No** | No | User line **yes** (`quit` appended), then `break` — still **no** API |
| Anything else (e.g. `capital of france ?`) | **OpenAI LLM** over the internet | **Yes** | No | **Yes** — user line, then assistant reply after API returns |

**LLM** here means: send `messages` to OpenAI, wait for the model, read `response.choices[0].message.content`.

**Python tool functions** here means: run code from `tools_2.py` on your machine, `print` the result, **never** send that user line to OpenAI for that turn.

The UI label `AI :` is printed for **both** paths. That is only formatting — for `time` / `dice` the text is **not** from the model.

---

### Picture: one loop iteration

```text
                    user_input
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    "time" in text   "dice" in text   neither
         │               │               │
         ▼               ▼               ▼
  get_current_time()  roll_dice()   messages.append(user)
         │               │               │
         ▼               ▼          quit? ──yes──► print goodbye, exit
      print "AI :"    print "AI :"              │
         │               │                    no │
         └─────── continue ────────┘              ▼
              (back to input)          chat.completions.create(...)
                                              │
                                              ▼
                                    print real LLM reply
                                    messages.append(assistant)
```

`continue` means: **skip everything below** in the loop (no append for keywords, no API).

---

### Walkthrough: your sample session (choice = Teacher)

**After you pick `1`**, `messages` is:

```python
[
  {"role": "system", "content": "You are a friendly school teacher. ..."}
]
```

Nothing has been sent to OpenAI yet. The system message is only stored locally until the first **LLM** turn.

| Step | You type | Path | Network / API? | `messages` after this step |
|------|----------|------|----------------|----------------------------|
| 1 | `time now ?` | Python (`time` in text) | No | Still **only** `system` |
| 2 | `roll dice ?` | Python (`dice` in text) | No | Still **only** `system` |
| 3 | `capital of france ?` | LLM | **Yes** — one API call | `system` + `user: capital of france ?` + `assistant: <teacher answer about Paris>` |
| 4 | `quit` | Script | No | Appends `user: quit` then exits — **no** API on quit |

The model **never sees** `time now ?` or `roll dice ?`. If you later asked “what time did I ask for?” on an LLM turn, it would **not** know — those lines were never appended to `messages`.

---

### Code order matters (`tool_functions_2.py`)

The keyword checks come **before** `messages.append`:

```python
if "time" in user_input.lower():
    print("\nAI :", get_current_time())
    continue   # ← jump to next "You : " — LLM block never runs

if "dice" in user_input.lower():
    print("\nAI : You rolled", roll_dice())
    continue

messages.append({"role": "user", "content": user_input})  # only non-keyword lines reach here
```

| Line / block | LLM? | Why |
|--------------|------|-----|
| `get_current_time()` / `roll_dice()` | No | Normal Python functions; same idea as step 1 `demo_helper_functions.py`. |
| `continue` | No | Ends this iteration; does not run `chat.completions.create`. |
| `chat.completions.create(...)` | **Yes** | Only path that uses the LLM. Sends full `messages` (system + prior user/assistant). |
| `print("\nAI  : Goodbye!...")` on `quit` | No | Hard-coded in your script, not generated by the model. |

---

### What the LLM receives on an LLM turn

When you type `capital of france ?` (Teacher chosen), the API gets roughly:

```python
[
  {"role": "system", "content": "<teacher instructions>"},
  {"role": "user", "content": "capital of france ?"},
]
```

OpenAI returns a new **assistant** message; your code prints it and appends it to `messages` for the **next** LLM turn.

On a **dice** turn, the API is **not** called — so the model is not asked anything and does not generate tokens for that line.

---

### Do you need `OPENAI_API_KEY`?

| Session style | API key needed? |
|---------------|-----------------|
| Only `time` / `dice`, then `quit` | **No** |
| Any normal question (LLM path) | **Yes** |

---

## Full source — `tools_2.py`

```python
"""Local helper functions used by tool_functions_2.py (keyword shortcuts, no OpenAI tools API yet)."""

from datetime import datetime
import random


def get_current_time():
    """Return the current date and time."""
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


def roll_dice():
    """Return a random number between 1 and 6."""
    return random.randint(1, 6)
```

### Line-by-line (`tools_2.py`)

**Module docstring**

| Line | Meaning |
|------|---------|
| `"""Local helper functions..."""` | These run in **your** Python process when `tool_functions_2.py` detects keywords. Still **not** the OpenAI `tools=` API — the main script calls them with `get_current_time()` etc. directly. |

**Imports**

| Import | Used for |
|--------|----------|
| `datetime` | `datetime.now()` inside `get_current_time()`. |
| `random` | `random.randint` for dice. |

**`get_current_time()`**

| Piece | Meaning |
|-------|---------|
| `datetime.now()` | Current local date/time on the machine running the script. |
| `.strftime("%d-%m-%Y %I:%M:%S %p")` | Format as day-month-year, 12-hour clock with AM/PM (e.g. `10-10-2026 08:13:18 PM`). |
| Return value | A **string** printed by `tool_functions_2.py` when the user message contains `"time"`. |

**`roll_dice()`**

| Piece | Meaning |
|-------|---------|
| `random.randint(1, 6)` | Inclusive range — simulates one fair six-sided die. |
| Return value | Integer `1`–`6`; main script prints `You rolled <n>`. |
| Trigger in main app | Any user text with substring **`dice`** (e.g. `dice roll`). |

**Why a separate file from `helper_functions.py`?**

Step 1 includes **`generate_password`**; this step only needs **time** and **dice**. `tools_2.py` keeps the step-2 demo small and imports only what `tool_functions_2.py` uses.

---

## Full source — `tool_functions_2.py`

```python
from dotenv import load_dotenv
import os

from openai import OpenAI

from tools_2 import get_current_time, roll_dice

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-4.1-nano"

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

roles = {
    "1": "You are a friendly school teacher. ...",
    "2": "You are a senior Python developer. ...",
    "3": "You are an experienced travel guide. ...",
    "4": "You are a motivational coach. ...",
    "5": "You are a professional interviewer. ...",
}

# ... menu prints 1–5, choice = input(...)

messages = [{"role": "system", "content": roles.get(choice, "You are a helpful AI assistant.")}]

while True:
    user_input = input("\nYou : ")

    if "time" in user_input.lower():
        print("\nAI :", get_current_time())
        continue
    if "dice" in user_input.lower():
        print("\nAI : You rolled", roll_dice())
        continue

    messages.append({"role": "user", "content": user_input})

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=messages,
    )
    ai_reply = response.choices[0].message.content
    print("\nAI :", ai_reply)
    messages.append({"role": "assistant", "content": ai_reply})
```

(The repo file has the full `roles` strings and menu prints — not abbreviated in the real `.py`.)

---

## Line-by-line (`tool_functions_2.py`)

### Setup (before the loop)

#### `from tools_2 import get_current_time, roll_dice`

This Python import statement:

```python
from tools_2 import get_current_time, roll_dice
```

means you're importing two functions, `get_current_time` and `roll_dice`, from a Python module named `tools_2` (the file [`tools_2.py`](./tools_2.py)).

- **`get_current_time`** — returns the current date and time as a formatted string (uses `datetime.now()` on your machine).
- **`roll_dice`** — returns a random integer from 1 to 6 (simulates one die roll).
- **`tools_2`** — the module that defines these functions; usually the file `tools_2.py` in the same folder as `tool_functions_2.py`.

Example usage (same names work in `tool_functions_2.py` after the import):

```python
from tools_2 import get_current_time, roll_dice

print(get_current_time())
print(roll_dice())
```

Important: Both functions must be defined in `tools_2.py`, and Python must be able to find that module (run from the `5_TOOLS_FUNCTIONS` folder with `python tool_functions_2.py`, or have that folder on `PYTHONPATH`).

In **this** project (step 2), your script calls these functions directly when the user types keywords like `time` or `dice`. That is **not** OpenAI tool calling yet — the model does not choose or invoke them. For registering functions so the **model** can call them via `tools=` + `tool_calls`, see [`tool_functions_1.md`](./tool_functions_1.md).

| Code | LLM called? | Meaning |
|------|-------------|---------|
| `from tools_2 import get_current_time, roll_dice` | No | Import **local** functions only (see above). |
| `client = OpenAI(...)` | No | Create client object; no request until `.create(...)`. |
| `choice = input(...)` | No | Pick persona; builds **system** text in memory. |
| `messages = [{"role": "system", ...}]` | No | Chat history list; starts with persona. Not sent until first `.create()`. |

### Inside `while True:` — each user line

| Order in file | Code | LLM? | What happens |
|---------------|------|------|----------------|
| 1 | `user_input = input(...)` | No | Read one line from terminal. |
| 2 | `if "time" in ...` → `get_current_time()` → `continue` | **No** | Python only; print; next prompt. |
| 3 | `if "dice" in ...` → `roll_dice()` → `continue` | **No** | Python only; print; next prompt. |
| 4 | `messages.append(user)` | No | Only reached if **not** time/dice keyword. |
| 5 | `if quit` → print goodbye → `break` | **No** | Exit loop; no `.create()`. |
| 6 | `client.chat.completions.create(...)` | **Yes** | **Only here** the LLM runs. |
| 7 | `print(ai_reply)` + `messages.append(assistant)` | No (after LLM returns) | Show and store model text for future LLM turns. |

Substring traps (by design):

- `time now ?` → **time** path (LLM never sees it).
- `roll dice ?` → **dice** path (LLM never sees it).
- A message like `summarize downtime reports` contains **`time`** → clock path, not the LLM — keyword routing is dumb, not intelligent.

---

## Sample output

```bash
python tool_functions_2.py
```

Example session: assistant **1 (Teacher)**, two **keyword** turns (`time`, `dice`), one **LLM** turn, then **`quit`**. Clock time, dice value, and model wording can change each run; structure is the same.

```text
========================================
      My AI Assistant
========================================

Choose Your Assistant

1. Teacher
2. Python Expert
3. Travel Guide
4. Motivational Coach
5. Interviewer

Enter your choice : 1

You : time now ?

AI : 10-10-2026 08:22:31 PM

You : roll dice ?

AI : You rolled 4

You : capital of france ?

AI : Hello! The capital of France is Paris. Think of Paris as the main city or the "big boss" city of France. It's like the head of the country where many important things happen, such as government work, famous landmarks like the Eiffel Tower, and lots of delicious food. So, when someone says "the capital of France," they are talking about Paris!

You : quit

AI  : Goodbye! Have a great day.
```

**What to notice (LLM vs Python vs script)**

| Line you typed | Path | LLM API? |
|----------------|------|----------|
| `time now ?` | `get_current_time()` in `tools_2.py` | **No** |
| `roll dice ?` | `roll_dice()` in `tools_2.py` | **No** |
| `capital of france ?` | `chat.completions.create` (teacher **system** + question) | **Yes** |
| `quit` | `print` goodbye in Python | **No** |

See **Main idea — when is the LLM called vs only Python?** above for the `messages` list after each step.

Keyword-only session (no `OPENAI_API_KEY`): only `time` or `dice`, then `quit` — every answer line is from **Python**, never the LLM.

---

## Keyword shortcuts vs OpenAI tools

| | This project (`tool_functions_2`) | `tool_functions_1` |
|--|-----------------------------------|----------------------|
| Who decides to run a function? | **Your** `if "dice" in ...` | **Model** (`tool_calls`) |
| API parameter | `messages` only | `messages` + `tools=` |
| Role for function result | N/A (you `print` directly) | `role: "tool"` in `messages` |

Keyword routing is easy to learn; production apps usually let the model pick tools when the user’s intent is varied.

---

## Files in this chapter (order)

1. `helper_functions.py` + `demo_helper_functions.py`  
2. `tools_2.py` + `tool_functions_2.py` — **this note**  
3. `tool_functions_1.py` — Gradio + real tool calling  
