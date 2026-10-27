# `tools.py` & `planner.py` & `assistant.py`

Terminal mini **AI agent**: a **planner** LLM picks a tool name, your Python runs that function from [`tools.py`](./tools.py), then a second LLM call turns the tool result into a natural reply.

This is **not** OpenAI **tools / function calling** yet (no `tools=` on the API). The planner is a normal chat completion that returns text like `get_current_time` or `none`. Your code reads that string and calls the matching function.

### Topic 5 — what we compare to (read this if “keywords / tool_functions_2” is new)

In **Topic 5** ([`5_TOOLS_FUNCTIONS/`](../5_TOOLS_FUNCTIONS/)) you already built helpers and wired them into a terminal chat — in **three steps**. This chapter is **step 2 upgraded into a mini agent**, not a random old file name.

| Topic 5 step | What you ran | Where it lives | How it picks time / dice |
|--------------|--------------|----------------|---------------------------|
| **1** | Plain helpers demo | [`helper_functions_and_demo.md`](../5_TOOLS_FUNCTIONS/helper_functions_and_demo.md) | No chat — just Python |
| **2 — keyword routing** | Terminal assistant | Scripts: [`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py) + [`tools_2.py`](../5_TOOLS_FUNCTIONS/tools_2.py) · Notes: [`tool_functions_2_and_tools_2.md`](../5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) | **Your code** checks substrings, e.g. `if "time" in user_input.lower():` → call `get_current_time()` — **no LLM** on that turn |
| **3** | FlightAI + Gradio | [`tool_functions_1.py`](../5_TOOLS_FUNCTIONS/tool_functions_1.py) · [`tool_functions_1.md`](../5_TOOLS_FUNCTIONS/tool_functions_1.md) | **OpenAI API** `tools=` + `tool_calls` |

**“Keywords”** in these notes means **step 2 only**: dumb but clear string matching in `tool_functions_2.py`, not AI magic.

**Why Topic 18 mentions it:** same idea (time + dice + chat), but **who decides** to run a function changes:

```text
Topic 5 step 2 (tool_functions_2)     Topic 18 (this folder)
─────────────────────────────────     ───────────────────────
You:  if "dice" in text               LLM #1: choose_tool → "roll_dice"
      → roll_dice()                         → roll_dice()
      → print result                    LLM #2: phrase the answer
```

If you skipped Topic 5, read at least [`tool_functions_2_and_tools_2.md`](../5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) once so the tables below make sense.

### Three ways to hook up tools (big picture)

| Step | Files / notes | How “tools” work |
|------|---------------|------------------|
| 1 | Topic 5 step 2 — [`tool_functions_2_and_tools_2.md`](../5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) | **Keywords** in your Python → call `tools_2.py`; else → Chat API |
| 2 | **This note** — folder `18_AI_AGENTS_INTRO` | **Planner LLM** → tool name → `tools.py`; then **answer LLM** |
| 3 | Topic 5 step 3 — [`tool_functions_1.md`](../5_TOOLS_FUNCTIONS/tool_functions_1.md) | **Model** chooses via `tools=` + `tool_calls` |

Read first: [`1_what_is_ai_agent.md`](./1_what_is_ai_agent.md).  
Theory: [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md).  
Chapter index: [`README.md`](./README.md).

---

## Requirements

```bash
pip install openai python-dotenv
```

`.env` example (same folder you run from, or a parent folder `load_dotenv()` can find):

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-nano
```

| Variable | Used for |
|----------|----------|
| `OPENAI_API_KEY` | `OpenAI(api_key=...)` in [`planner.py`](./planner.py) and [`assistant.py`](./assistant.py) |
| `OPENAI_MODEL` | `MODEL=os.getenv("OPENAI_MODEL")` — same model for **planner** and **answer** calls |

---

## How to run

```bash
python assistant.py
```

1. Banner **My AI Assistant** prints.  
2. Chat in the terminal (`time`, `dice`, `password`, normal questions, …).  
3. Type **`quit`** to exit (only `quit` hits the hard-coded exit — `bye` does not).

Each non-`quit` turn makes **up to two** LLM calls (planner + answer). Tool functions in `tools.py` run on your machine and do **not** need the network.

---

## What these files teach

| File | Role |
|------|------|
| [`tools.py`](./tools.py) | Local helpers: `get_current_time`, `roll_dice`, `generate_password` (+ unused `read_text_file`) |
| [`planner.py`](./planner.py) | `choose_tool(user_request)` — LLM returns **only** a tool name or `none` |
| [`assistant.py`](./assistant.py) | Loop: plan → run tool → answer prompt → print |

### Agent pieces (mapped to this code)

| Idea | In this project |
|------|-----------------|
| Brain (plan) | `choose_tool` in `planner.py` |
| Body (tools) | functions in `tools.py` |
| Orchestration loop | `while True` in `assistant.py` |
| Natural reply | second `chat.completions.create` in `assistant.py` |

---

## Main idea — when is the LLM called vs only Python?

This project uses **two different LLM jobs** on almost every line you type (except `quit`). The numbers are just labels in **this** note — not an OpenAI API name.

| Label | Where | Job |
|-------|--------|-----|
| **LLM #1** | [`planner.py`](./planner.py) — `choose_tool()` | **Plan:** return a tool name (`get_current_time`, …) or `none` |
| **LLM #2** | [`assistant.py`](./assistant.py) — second `chat.completions.create` | **Speak:** turn the user line + optional tool result into the line you see as `AI :` |

### Why is there an LLM #2 at all?

Your code **never** does `print(get_current_time())` directly. After Python runs a tool (or skips it), **every** turn still calls LLM #2 with a prompt like “The user asked … The tool returned … Answer naturally.”

So LLM #2 is not “the tool.” It is the **wording** step:

| Turn type | Where the **fact** comes from | What LLM #2 does |
|-----------|------------------------------|------------------|
| `time` / `dice` / `password` | **`tools.py`** (real clock, die, password) | Rephrase that value (`6`, the time string, …) |
| `india's capital` | **LLM #2 only** (model knowledge) — **not** a tool | Answer the question; `result` is `None` |
| `bye` | **LLM #2 only** (chat) — **not** a tool | Say goodbye in natural language |

You *could* skip LLM #2 on tool turns and `print(result)` yourself (like topic 5 keywords). This chapter keeps LLM #2 on purpose so you see **plan → act → speak** every time.

### Normal questions are **not** answered by a tool

For `india's capital`:

1. **LLM #1** runs → returns `none` (no tool fits).  
2. **`tools.py` is not called** → `result = None`.  
3. **LLM #2** runs → “New Delhi” comes from the **model’s training**, not from Python and not from `tools.py`.

So: **tool = live/action data** (time on your PC, random dice, generated password). **General knowledge = LLM**, after the planner says `none`.

`quit` is the only exit with **zero** LLM calls (hard-coded goodbye in Python).

---

### Summary table (one row per thing you type)

| What you typed | LLM #1 planner? | `tools.py`? | LLM #2 answer? | Where the **content** comes from |
|----------------|-----------------|-------------|----------------|----------------------------------|
| `time` (time intent) | Yes → `get_current_time` | **Yes** | Yes | Fact: **Python** clock → LLM #2 phrases it |
| `dice` | Yes → `roll_dice` | **Yes** | Yes | Fact: **Python** die → LLM #2 phrases it |
| `password` | Yes → `generate_password` | **Yes** | Yes | Fact: **Python** password → LLM #2 phrases it |
| Normal Q (e.g. `india's capital`) | Yes → `none` | **No** | Yes | Fact: **LLM #2 only** (no tool) |
| `bye` | Yes → `none` | **No** | Yes | Text: **LLM #2 only** (loop continues) |
| `quit` | No | No | No | Text: **your script** (`break`) |

**LLM** here means: `client.chat.completions.create(...)` and read `response.choices[0].message.content`.

**Python tool** here means: a function in `tools.py` runs on your machine **only** when LLM #1 returns a matching tool name (not `none`).

The UI label `AI :` is used for LLM #2 output. Quit uses `AI  :` (two spaces) from a hard-coded `print` — see your sample session below.

---

### Picture: one loop iteration

```text
                    user_input
                         │
                    quit? ──yes──► print goodbye, break (no LLM)
                         │ no
                         ▼
              choose_tool(user_input)          LLM #1 (planner)
                         │
         ┌───────────────┼───────────────┬────────────────┐
         ▼               ▼               ▼                ▼
  get_current_time   roll_dice   generate_password    else / none
         │               │               │                │
         ▼               ▼               ▼                ▼
      result=str      result=int     result=str      result=None
         │               │               │                │
         └───────────────┴───────────────┴────────────────┘
                         │
                         ▼
         answer prompt + chat.completions.create   LLM #2
                         │
                         ▼
                   print "AI :"
```

---

### Walkthrough: your sample session

**After the banner**, nothing has been sent to OpenAI yet. There is **no** growing `messages` list (unlike **Topic 5 step 2** — [`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py), which keeps chat history for the LLM) — each turn here builds a fresh planner call and a fresh answer call.

| Step | You type | Path | Network / API? | What lands in `result` |
|------|----------|------|----------------|------------------------|
| 1 | `time` | Tool | **2** LLM calls + local clock | e.g. `23-10-2026 05:32:56 PM` |
| 2 | `dice` | Tool | **2** LLM + `roll_dice()` | e.g. `6` |
| 3 | `password` | Tool | **2** LLM + `generate_password()` | e.g. `93d'QZhGa{` |
| 4 | `india's capital` | No tool | **2** LLM (`none`) | `None` |
| 5 | `bye` | No tool | **2** LLM (`none`) | `None` — model says goodbye; **not** exit |
| 6 | `quit` | Script | **No** API | — |

The model **does** see tool results on tool turns, but only inside the **answer** prompt for that turn. Earlier turns are **not** stored for later questions.

---

### Code order matters (`assistant.py`)

```python
user_input = input("\nYou : ")

if user_input.lower() == "quit":
    print("\nAI  : Goodbye! Have a great day.")
    break   # ← exit before planner / answer

tool = choose_tool(user_input)   # LLM #1

if tool == "get_current_time":
    result = get_current_time()
elif tool == "roll_dice":
    result = roll_dice()
elif tool == "generate_password":
    result = generate_password()
else:
    result = None

# then build prompt and LLM #2 …
```

| Line / block | LLM? | Why |
|--------------|------|-----|
| `if ... == "quit"` | No | Ends the loop; planner never runs. |
| `choose_tool(...)` | **Yes (#1)** | Only job: return a tool name string. |
| `get_current_time()` / `roll_dice()` / `generate_password()` | No | Normal Python on your machine. |
| `else: result = None` | No | `none` or unexpected planner text. |
| `chat.completions.create(...)` (answer) | **Yes (#2)** | Phrases the final line you see as `AI :`. |

---

### What each LLM receives

**Planner (`planner.py`)** — system + user prompt listing tools and your line, e.g. for `time`:

```text
system: You are an AI planner.
user:   … Available tools: get_current_time, roll_dice, generate_password …
       … Return ONLY the tool name.
       … User Request: time
```

Expected reply (exact string): `get_current_time` (or `roll_dice` / `generate_password` / `none`).

**Answer (`assistant.py`)** — single user message, e.g. after a successful time tool:

```text
The user asked:
time
The tool returned:
23-10-2026 05:32:56 PM
Answer the user naturally.don't add anything from your side in the answer. if tool is none, then answer it from llm model.
```

When planner returns `none`, `The tool returned: None` and the instruction tells the model to answer from its own knowledge.

---

### Do you need `OPENAI_API_KEY`?

| Session style | API key needed? |
|---------------|-----------------|
| Only `quit` immediately | **No** (no planner/answer calls) |
| Any tool or chat turn (`time`, capital, `bye`, …) | **Yes** |

Unlike **Topic 5 step 2** (keyword routing in [`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py)), even a `time` turn here needs the API — the **planner** must choose the tool.

---

## Full source — `tools.py`

```python
from datetime import datetime

def get_current_time():
    """Return the current date and time."""

    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

import random

def roll_dice():
    """Return a random number between 1 and 6."""

    return random.randint(1, 6)

import secrets
import string

def generate_password(length=12):
    """Generate a secure random password."""

    characters = (
        string.ascii_letters +
        string.digits +
        string.punctuation
    )

    password = ""

    for _ in range(length):
        password += secrets.choice(characters)

    return password

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
| `random` | `random.randint` for dice. |
| `secrets` | Cryptographically stronger picks for passwords. |
| `string` | `ascii_letters`, `digits`, `punctuation` character pools. |

**`get_current_time()`**

| Piece | Meaning |
|-------|---------|
| `datetime.now()` | Current local date/time on the machine running the script. |
| `.strftime("%d-%m-%Y %I:%M:%S %p")` | Day-month-year, 12-hour clock with AM/PM (e.g. `23-10-2026 05:32:56 PM`). |
| Return value | A **string** passed into the answer prompt when planner returns `get_current_time`. |

**`roll_dice()`**

| Piece | Meaning |
|-------|---------|
| `random.randint(1, 6)` | Inclusive range — one fair six-sided die. |
| Return value | Integer `1`–`6`; answer LLM may print just `6` if told not to add fluff. |

**`generate_password(length=12)`**

| Piece | Meaning |
|-------|---------|
| `characters = letters + digits + punctuation` | Pool of allowed symbols. |
| `secrets.choice(characters)` | Prefer `secrets` over `random` for credentials. |
| Loop `length` times | Default **12** characters (assistant never passes another length). |

**`read_text_file(filename)`**

Defined for later practice, but **not** imported in `assistant.py` and **not** listed in the planner prompt — the agent cannot use it yet.

**Why a separate file?** Keeps the **body** (actions) apart from the **brain** (planner) and the **loop** (assistant), same idea as splitting helpers in topic 5.

---

## Full source — `planner.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL=os.getenv("OPENAI_MODEL")

def choose_tool(user_request):

    planner_prompt = f"""
You are an AI planner.

Available tools:

1. get_current_time
   Use when the user asks for the current date or time.

2. roll_dice
   Use when the user asks to roll a dice.

3. generate_password
   Use when the user wants a secure password.

If no tool is required, return:

none

Return ONLY the tool name.

User Request:

{user_request}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role":"system",
                "content":"You are an AI planner."
            },
            {
                "role":"user",
                "content":planner_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
```

### Line-by-line (`planner.py`)

#### Setup (before `choose_tool`)

| Code | LLM? | Meaning |
|------|------|---------|
| `load_dotenv()` | No | Load `.env` into the process environment. |
| `client = OpenAI(api_key=...)` | No | Create client; no request until `.create(...)`. |
| `MODEL=os.getenv("OPENAI_MODEL")` | No | Model id string for later calls. |

#### `choose_tool(user_request)`

| Piece | Meaning |
|-------|---------|
| `planner_prompt` | Lists tools + “Return ONLY the tool name” + the user text. |
| `role: system` | Short role: “You are an AI planner.” |
| `role: user` | The full planner prompt (tools + request). |
| `model=MODEL` | Same env model as the answer call. |
| `.strip()` | Trim whitespace/newlines so `if tool == "get_current_time"` matches cleanly. |

**Expected return values (exact strings):**

- `get_current_time`
- `roll_dice`
- `generate_password`
- `none`

If the model returns extra words (e.g. `` `get_current_time` `` or a sentence), `assistant.py`’s `elif` chain will miss it → `result = None` → answer LLM has no tool data.

---

## Full source — `assistant.py`

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

from planner import choose_tool

from tools import (
    get_current_time,
    roll_dice,
    generate_password
)

# Load configuration
load_dotenv()
# Create AI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL=os.getenv("OPENAI_MODEL")

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
while True:

    user_input = input("\nYou : ")
    if user_input.lower() == "quit":
            print("\nAI  : Goodbye! Have a great day.")
            break

    tool = choose_tool(user_input)

    if tool == "get_current_time":

        result = get_current_time()

    elif tool == "roll_dice":

        result = roll_dice()

    elif tool == "generate_password":

        result = generate_password()

    else:

        result = None

    prompt = f"""
    The user asked:
    {user_input}
    The tool returned:
    {result}
    Answer the user naturally.don't add anything from your side in the answer. if tool is none, then answer it from llm model.
    """

    response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                "role":"user",
                "content":prompt
            }
                ]
                )
    print("\nAI :", response.choices[0].message.content)
```

### Line-by-line (`assistant.py`)

#### Setup (before the loop)

#### `from planner import choose_tool` / `from tools import ...`

```python
from planner import choose_tool
from tools import get_current_time, roll_dice, generate_password
```

- **`choose_tool`** — asks the planner LLM which tool name to use.  
- **`get_current_time` / `roll_dice` / `generate_password`** — local actions from [`tools.py`](./tools.py).  
- Run from this folder (`python assistant.py`) so Python can import sibling modules.

| Code | LLM? | Meaning |
|------|------|---------|
| `load_dotenv()` | No | Load `.env`. |
| `client = OpenAI(...)` | No | Answer-call client (planner has its own client inside `planner.py`). |
| `MODEL=os.getenv("OPENAI_MODEL")` | No | Model for the answer call. |
| Banner `print`s | No | UI only. |

#### Inside `while True:` — each user line

| Order in file | Code | LLM? | What happens |
|---------------|------|------|----------------|
| 1 | `user_input = input(...)` | No | Read one line from terminal. |
| 2 | `if quit` → print goodbye → `break` | **No** | Exit loop; no `.create()`. |
| 3 | `tool = choose_tool(user_input)` | **Yes (#1)** | Planner returns a name string. |
| 4 | `if / elif` → `tools.py` | No | Set `result` from local functions. |
| 5 | `else: result = None` | No | `none` or bad planner output. |
| 6 | Build `prompt` with user + `result` | No | Stuff tool output into answer text. |
| 7 | `client.chat.completions.create(...)` | **Yes (#2)** | Only path that phrases the final answer. |
| 8 | `print("\nAI :", ...)` | No (after LLM returns) | Show model text. |

**No chat memory:** each turn is independent. There is no `messages` list that grows across turns.

**Answer prompt instruction:** “if tool is none, then answer it from llm model” — when `result` is `None`, the second call is normal Q&A (plus that instruction text).

---

## Sample session (explained)

Your real run (clock / dice / password / wording can change next time; the **paths** stay the same):

```bash
python assistant.py
```

```text
========================================
      My AI Assistant
========================================

You : time

AI : The current time is 23-10-2026 05:32:56 PM.

You : dice

AI : 6

You : password

AI : The password is 93d'QZhGa{

You : india's capital

AI : India's capital is New Delhi.

You : bye

AI : Goodbye! Have a great day!

You : quit

AI  : Goodbye! Have a great day.
```

### Turn-by-turn — what actually happened

| You typed | Planner (typical) | Python tool? | Answer came from | Notes |
|-----------|-------------------|--------------|------------------|--------|
| `time` | `get_current_time` | Yes — `get_current_time()` | LLM #2, using tool string | Short word is enough; planner maps intent → tool (not a keyword `if` in your code) |
| `dice` | `roll_dice` | Yes — `roll_dice()` → `6` | LLM #2 | Minimal reply (`6`) matches “don’t add anything from your side” |
| `password` | `generate_password` | Yes — `generate_password()` | LLM #2 | Password from **`secrets`** on your PC; LLM only wraps it |
| `india's capital` | `none` | No (`result = None`) | LLM #2 from model knowledge | No tool fits → normal Q&A |
| `bye` | `none` | No | **LLM #2** goodbye | **Not** the quit handler — script still waiting |
| `quit` | (not called) | No | **Hard-coded** in `assistant.py` | Only this string hits `if ... == "quit"` → `break` |

### Why `bye` and `quit` both say goodbye (but are different)

| | `bye` | `quit` |
|--|-------|--------|
| Hits `if ... == "quit"`? | **No** | **Yes** |
| Planner + answer LLM? | **Yes** (two API calls) | **No** |
| Print label in code | `print("\nAI :", ...)` → `AI :` (one space) | `print("\nAI  : Goodbye!...")` → `AI  :` (two spaces) |
| Loop continues? | Yes | No — `break` exits |

So in your transcript, the first goodbye is the **model** being polite; the second is your **script** exiting.

### API / Python calls for this session

| Line | Planner LLM? | Tool in `tools.py`? | Answer LLM? |
|------|--------------|---------------------|-------------|
| `time` | Yes | `get_current_time` | Yes |
| `dice` | Yes | `roll_dice` | Yes |
| `password` | Yes | `generate_password` | Yes |
| `india's capital` | Yes → `none` | No | Yes |
| `bye` | Yes → `none` | No | Yes |
| `quit` | No | No | No |

**Count:** 5 planner calls + 5 answer calls + 3 local tool runs, then a pure-Python exit on `quit`.

See **Main idea — when is the LLM called vs only Python?** above for the path table.

---

## Planner agent vs keywords vs OpenAI tools

| | **Topic 5 step 2** — keyword assistant ([`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py) + [`tools_2.py`](../5_TOOLS_FUNCTIONS/tools_2.py)) | **Topic 18** — this project ([`assistant.py`](./assistant.py) + [`planner.py`](./planner.py) + [`tools.py`](./tools.py)) | **Topic 5 step 3** — OpenAI tools ([`tool_functions_1.py`](../5_TOOLS_FUNCTIONS/tool_functions_1.py)) |
|--|------------------------------|----------------------------------------|--------------------|
| Who decides to run a function? | **Your** `if "dice" in ...` in Python | **Planner LLM** (tool name text) | **Model** (`tool_calls`) |
| API parameter | `messages` only | `messages` only (twice) | `messages` + `tools=` |
| Role for function result | N/A (you `print` directly) | Stuffed into answer **user** prompt | `role: "tool"` in `messages` |
| LLM calls on a tool turn | **0** | **2** (plan + speak) | Usually **2** (tool request + final) |

Keyword routing (step 2) is the easiest to read in code; Topic 18 adds a real **plan** step; step 3 is what many production apps use (`tools=`).

---

## Mental model

```text
Agent (this folder)
├── Brain (plan)  → planner.choose_tool  → "which tool?"
├── Body          → tools.py             → run action
└── Brain (speak) → assistant prompt     → "tell the user"
```

Still a **teaching** agent: one tool per turn, no multi-step plan, no OpenAI `tools=` schema, no conversation memory.

---

## Quick recap

1. **`tools.py`** — real actions on your machine (time / dice / password).  
2. **`planner.py`** — LLM returns **only** a tool name (or `none`).  
3. **`assistant.py`** — loop: plan → run tool → second LLM → print.  
4. Needs **`.env`**: `OPENAI_API_KEY`, `OPENAI_MODEL`.  
5. Next level up: official **function calling** (`tools=` / `tool_calls`) in topic 5’s `tool_functions_1`.

---

## Files in this chapter (order)

1. [`1_what_is_ai_agent.md`](./1_what_is_ai_agent.md) — what an agent is  
2. [`tools.py`](./tools.py) + [`planner.py`](./planner.py) + [`assistant.py`](./assistant.py) — **this note**  
3. Entry point: `python assistant.py`  
