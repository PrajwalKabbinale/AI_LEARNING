# Understanding `chat_conversation_memory_LLM.py`

This note explains a **terminal chat loop** that keeps **conversation memory** by growing a `messages` list and sending the **full history** to OpenAI on every turn.

Related scripts:

- `[Test_OPENAI_LLM_with_openAI.py](Test_OPENAI_LLM_with_openAI.py)` — one-shot question, no memory  
- `[Test_OPENAI_LLM_with_openAI.md](Test_OPENAI_LLM_with_openAI.md)` — same style of line-by-line notes  
- Gradio version with the same idea: `[../4_GRADIO/gradio_chatbot.py](../4_GRADIO/gradio_chatbot.py)`

Concept: LLMs are **stateless** — they do not remember past calls. “Memory” here means **your Python list** of prior `user` / `assistant` messages, resent on each API request. See also `[../3_LLMs_and_TOKENS/README_LLM_STATELESS_NO_MEMORY.md](../3_LLMs_and_TOKENS/README_LLM_STATELESS_NO_MEMORY.md)` and `[chat_message_roles.md](chat_message_roles.md)` (what **`role`** means).

---

## Requirements

```bash
pip install openai python-dotenv
```

`.env` example (same folder you run from, or set variables in your shell):

```env
OPENAI_API_KEY=<your_openai_api_key_here>
```

Optional:

```env
MODEL_NAME=gpt-4.1-nano
```

Keep `.env` out of version control.

---

## How to run

1. Install the packages above.
2. Set `OPENAI_API_KEY` (`.env` or environment).
3. From the folder that contains `chat_conversation_memory_LLM.py`:

```bash
python chat_conversation_memory_LLM.py
```

1. Chat in the terminal. Type `**quit**` to exit. (`bye` is a normal message to the model.)

---

## What this script teaches


| Idea                     | In this file                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| **Chat Completions API** | `client.chat.completions.create(...)`                                                      |
| **Roles**                | `"user"` and `"assistant"` entries in `messages`                                           |
| **Conversation memory**  | Append each turn to `messages`; pass entire list every time                                |
| **Interactive loop**     | `while True` + `input()`; type `**quit`** to exit (other words like `bye` go to the model) |
| **Iteration counter**    | Prints `iteration : N` and history **before** each prompt                                  |


---

## Full script

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

MODEL_NAME = "gpt-4.1-nano"

openai_api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
messages = []
i = 1

while True:
    print("iteration :  ", i)

    print("\n---------- Conversation History ----------")

    for message in messages:
        print(message)

    print("------------------------------------------")

    user_input = input("\nYou : ")
    # Save the user's message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", MODEL_NAME),
        messages=messages,
    )

    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    # Save the AI's reply
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )

    i += 1
```

---

## Line-by-line explanation

### Imports and load secrets

```python
from openai import OpenAI
```

Imports the official OpenAI client class (same package as in `Test_OPENAI_LLM_with_openAI.py`).

```python
from dotenv import load_dotenv
import os
```

- `load_dotenv` — reads a `.env` file into the process environment.  
- `os` — used to read `OPENAI_API_KEY` and `MODEL_NAME` from that environment.

```python
load_dotenv()
```

Loads variables from a `.env` file in the **current working directory** (where you run `python`).  
Unlike the test script, this uses the default `override=False`, so an `OPENAI_API_KEY` already set in your shell is **not** replaced by `.env`.

---

### Model name and API key check

```python
MODEL_NAME = "gpt-4.1-nano"
```

Default model name in code. The API call uses `os.getenv("MODEL_NAME", MODEL_NAME)` — `.env` wins if set; otherwise `gpt-4.1-nano`.

```python
openai_api_key = os.getenv('OPENAI_API_KEY')
```

Reads whether a key is present (after `.env` load). In this script the value is **not** passed into `OpenAI()` — the client still picks up `OPENAI_API_KEY` from the environment automatically, same as `OpenAI()` with no arguments.

```python
client = OpenAI()
```

Creates the cloud OpenAI client. It uses `OPENAI_API_KEY` from the environment; you do not pass `api_key=` manually when `.env` is loaded correctly.

---

### Banner and empty history

```python
print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
```

Prints a simple header (`"=" * 40` repeats the `=` character 40 times).

```python
messages = []
i = 1
```

- `messages` — empty chat history; this list is the “memory” for the whole session.  
- `i` — turn counter printed at the start of each loop.

---

### Main loop — show history, then read input

```python
while True:
```

Runs forever until `break` (when the user types `quit`).

```python
    print("iteration :  ", i)
```

Prints which lap of the loop you are on (`1`, `2`, …). Increments at the **end** of a successful API turn, not when you `quit`.

```python
    print("\n---------- Conversation History ----------")

    for message in messages:
        print(message)

    print("------------------------------------------")
```

**Before** asking for input, prints whatever is in `messages` so far. On iteration 1 the block is empty (only the separator lines). After each assistant reply, the next iteration shows the updated history.

```python
    user_input = input("\nYou : ")
```

Blocks and waits for keyboard input. The prompt shows `You :` on a new line.

```python
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )
```

**Before** calling the model, saves this turn as a Chat Completions message dict:


| Key       | Value                   |
| --------- | ----------------------- |
| `role`    | `"user"`                |
| `content` | whatever the user typed |


So even the word `quit` is appended to `messages` once before exit (harmless for the API because you `break` before calling OpenAI).

---

### Exit command

```python
    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break
```

Case-insensitive exit: only the word `**quit**` (not `bye`).  
No API call on this turn — fixed goodbye from the script, then `break`.

Words like `**bye**` are normal user messages: they are appended to `messages`, sent to the model, and the assistant can reply with a farewell.

---

### Call OpenAI with full history

```python
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", MODEL_NAME),
        messages=messages,
    )
```

Sends **every message so far** (all prior user + assistant turns **including** the latest user line) to the Chat Completions API.

- `model` — `MODEL_NAME` from `.env` if set, else the Python default `gpt-4.1-nano`.  
- `messages` — the growing list; this is what lets the model answer “what is my name?” after you introduced yourself earlier in the chat.

```python
    ai_reply = response.choices[0].message.content
```

Extracts the assistant’s text from the response object (first choice → message → content string).

```python
    print("\nAI :", ai_reply)
```

Prints the model reply in the terminal.

---

### Save assistant reply and advance counter

```python
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )

    i += 1
```

Stores the model’s answer so the **next** `create(...)` call includes it in context.  
`i += 1` runs only after a full user → API → assistant cycle (not when you type `quit`).

---

## Memory flow (one picture)

```text
Turn 1:  messages = [ user₁ ]           → API → assistant₁
Turn 2:  messages = [ user₁, asst₁, user₂ ]  → API → assistant₂
Turn 3:  messages = [ ... all prior ..., user₃ ] → ...
```

The model has no hidden memory — only what you send in `messages` each time.

---

## Sample run (output)

Model replies will vary; the **layout** below is what the script always prints.

```text
========================================
      My AI Assistant
========================================
iteration :   1

---------- Conversation History ----------
------------------------------------------

You : i am souvik

AI : Hello, Souvik! How can I assist you today?
iteration :   2

---------- Conversation History ----------
{'role': 'user', 'content': 'i am souvik'}
{'role': 'assistant', 'content': 'Hello, Souvik! How can I assist you today?'}
------------------------------------------

You : what is my name ? u remember ?

AI : Yes, you mentioned your name is Souvik. How can I assist you further, Souvik?
iteration :   3

---------- Conversation History ----------
{'role': 'user', 'content': 'i am souvik'}
{'role': 'assistant', 'content': 'Hello, Souvik! How can I assist you today?'}
{'role': 'user', 'content': 'what is my name ? u remember ?'}
{'role': 'assistant', 'content': 'Yes, you mentioned your name is Souvik. How can I assist you further, Souvik?'}
------------------------------------------

You : bye

AI : Goodbye, Souvik! Have a great day!
iteration :   4

---------- Conversation History ----------
{'role': 'user', 'content': 'i am souvik'}
{'role': 'assistant', 'content': 'Hello, Souvik! How can I assist you today?'}
{'role': 'user', 'content': 'what is my name ? u remember ?'}
{'role': 'assistant', 'content': 'Yes, you mentioned your name is Souvik. How can I assist you further, Souvik?'}
{'role': 'user', 'content': 'bye'}
{'role': 'assistant', 'content': 'Goodbye, Souvik! Have a great day!'}
------------------------------------------

You : quit

AI  : Goodbye! Have a great day.
```

**What to notice**

- **Iteration 1** — history is empty until after the first reply; then iteration 2 shows both messages.  
- **“what is my name?”** — works because earlier turns are still in `messages`.  
- `**bye**` — handled by the **model**, not the exit logic.  
- `**quit**` — script exit only; no API call on that line.

