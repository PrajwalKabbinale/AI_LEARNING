# `helper_functions.py` & `demo_helper_functions.py`

**Step 1** in this chapter: write normal **Python functions** your code can call.  
**Step 2** (later in this folder): teach an LLM to *request* those kinds of functions via OpenAI **tools** — see [`tool_functions_1.md`](./tool_functions_1.md).

Why not name the module `tools.py`? In AI docs, **“tools”** usually means **function calling** on the API. These files are **plain Python** first so the reader separates “a function I wrote” from “the model asked me to run it.”

---

## Requirements

No extra packages — only the Python standard library (`datetime`, `random`, `secrets`, `string`).

---

## How to run

From the folder that contains the scripts:

```bash
python demo_helper_functions.py
```

That imports and prints results from `helper_functions.py`. You do **not** need an API key for this step.

---

## What these files teach

| File | Role |
|------|------|
| [`helper_functions.py`](./helper_functions.py) | Defines three small functions (time, dice, password) |
| [`demo_helper_functions.py`](./demo_helper_functions.py) | **Runner** — imports them and prints one line each |

Same pattern as Modal’s `hello.py` (definition) + `TEST_MODAL.py` (runner): one module holds logic, the other script is what you execute to try it.

---

## Full source — `helper_functions.py`

```python
"""Plain Python functions — practice before wiring them to an LLM as OpenAI tools."""

from datetime import datetime
import random
import secrets
import string


def get_current_time():
    """Return the current date and time."""
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


def roll_dice():
    """Return a random number between 1 and 6."""
    return random.randint(1, 6)


def generate_password(length=12):
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ""
    for _ in range(length):
        password += secrets.choice(characters)
    return password
```

### Line-by-line (`helper_functions.py`)

| Piece | Meaning |
|-------|---------|
| Module docstring | These are **not** OpenAI tools yet — just Python. |
| `get_current_time()` | Formats **now** as `DD-MM-YYYY HH:MM:SS AM/PM`. |
| `roll_dice()` | `random.randint(1, 6)` — one die roll. |
| `generate_password(length=12)` | Builds a string from letters, digits, and punctuation using `secrets` (safer than `random` for passwords). |

---

## Full source — `demo_helper_functions.py`

```python
"""Smoke test: call each function in helper_functions.py (no LLM)."""

from helper_functions import generate_password, get_current_time, roll_dice

print(get_current_time())
print(roll_dice())
print(generate_password())
```

### Line-by-line (`demo_helper_functions.py`)

| Line | Meaning |
|------|---------|
| `from helper_functions import ...` | Import the three functions from the module in the **same folder**. |
| Three `print(...)` calls | Run each function once and show output in the terminal. |

No `if __name__ == "__main__"` here — the whole file is the demo. That is fine for a tiny learning script.

---

## Sample output

```bash
python demo_helper_functions.py
```

```text
10-10-2026 07:54:20 PM
1
VX#f-43{edZZ
```

- **Line 1** — current time when you ran the script (always changes).  
- **Line 2** — dice roll between 1 and 6 (changes each run).  
- **Line 3** — random 12-character password (changes each run).

---

## How this connects to real “AI tools”

```text
Today (these files):
  Your code  →  helper_functions.py  →  print result

Next (tool_functions_1.py):
  User chat  →  LLM  →  "please run get_ticket_price(...)"
         →  your Python  →  result back to LLM  →  final answer
```

The LLM does not run `roll_dice()` by itself. **You** run Python. Tools are how the model **asks** you to run the right function.

---

## File names in this folder (reading order)

| Order | Files | What to call them mentally |
|-------|--------|----------------------------|
| 1 | `helper_functions.py` + `demo_helper_functions.py` | Practice **Python** helpers (this note) |
| 2 | `tool_functions_1.py` + `tool_functions_1.md` | **OpenAI tools** + Gradio FlightAI chat |

A clearer name for step 2 would be something like `flightai_tool_calling_gradio.py`; the repo keeps `tool_functions_1` so older links in [`README.md`](./README.md) and the root index still work. New readers: start with **helper** → then **tool_functions_1**.
