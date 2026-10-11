# Chat message `role` — system, user, assistant (and more)

Plain guide to the **`role`** field in OpenAI-style chat APIs: what it is, which values are allowed, and why your scripts send a list of `{role, content}` objects.

Related:

- [`Test_OPENAI_LLM_with_openAI.md`](./Test_OPENAI_LLM_with_openAI.md) — first cloud call with a **`user`** message  
- [`chat_conversation_memory_LLM.md`](./chat_conversation_memory_LLM.md) — **`user`** + **`assistant`** history each turn  
- [`Test_ollama_with_OPENAI.md`](./Test_ollama_with_OPENAI.md) — same `messages` shape on local Ollama  
- [`../2_USER_PROMPT_SYSTEM_PROMPT/user_prompt_system_prompt.md`](../2_USER_PROMPT_SYSTEM_PROMPT/user_prompt_system_prompt.md) — **system** vs **user** in a longer script  
- [`../3_LLMs_and_TOKENS/README_LLM_STATELESS_NO_MEMORY.md`](../3_LLMs_and_TOKENS/README_LLM_STATELESS_NO_MEMORY.md) — the model does not remember; **you** resend `messages`  
- [`../4_GRADIO/gradio_chatbot.md`](../4_GRADIO/gradio_chatbot.md) — building the same list in Gradio  

---

## One sentence

**`role` labels who each message is from** so the Chat Completions API (and chat-tuned models) can read a conversation and generate the **next assistant** reply.

---

## Are these roles defined by OpenAI?

**Yes.** For the **Chat Completions** API (`client.chat.completions.create(..., messages=[...])`), each message is an object with at least:

```python
{"role": "<allowed value>", "content": "<text>"}
```

The **`role` names are part of the API contract** — not something you invent in Python. Libraries (LangChain, Gradio) and local servers (Ollama’s OpenAI-compatible API) use the **same** shape so one `messages` list works in many places.

You **cannot** use arbitrary roles like `"customer"` or `"bot"` in standard chat — the API expects the official values below.

---

## The three roles you use most

| `role` | Who it represents | Typical use |
|--------|-------------------|-------------|
| **`system`** | Instructions for the model | Persona, rules, format (“answer in bullet points”, “you are a tutor”) |
| **`user`** | The human using the app | Questions, commands, facts the user types |
| **`assistant`** | The model’s **previous** replies in this chat | Past answers you store and send back on the next turn |

### Example (one turn + memory)

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "I am Alex."},
    {"role": "assistant", "content": "Nice to meet you, Alex!"},
    {"role": "user", "content": "What is my name?"},
]
```

The API returns a **new** assistant message answering the last user line — using earlier turns as context.

Many beginner scripts use only **`user`** (single question) or **`user`** + **`assistant`** (chat loop) without **`system`**. Adding **`system`** once at the start is optional but common in production apps.

---

## What does the model “understand” from `role`?

The model is **not** running separate code per role. It receives **one structured conversation** (tokens built from your `messages` list). The **`role`** tells the model:

- which lines are **instructions** (`system`),
- which lines are **from the human** (`user`),
- which lines are **its own past output** (`assistant`),

so it can continue the pattern: *after user messages, produce the next **assistant** message.*

That is why chat “memory” in scripts like `chat_conversation_memory_LLM.py` works: you **append** `user` and `assistant` dicts and send the **whole list** every time. The model has no hidden memory between HTTP calls — only what you put in `messages`.

```text
Call 1:  [ user₁ ]                          → assistant₁
Call 2:  [ user₁, assistant₁, user₂ ]       → assistant₂
Call 3:  [ user₁, assistant₁, user₂, assistant₂, user₃ ] → assistant₃
```

---

## Why is `role` needed?

| Reason | Explanation |
|--------|-------------|
| **API format** | Chat Completions requires `role` + `content` on each message. |
| **Training** | Chat models are fine-tuned on dialogs labeled system / user / assistant. |
| **Separation** | **System** = how to behave; **user** = what was asked; **assistant** = what was already said. |
| **Multi-turn apps** | Without correct roles, the model cannot reliably tell “what I said before” from “what the user said now.” |

If you put everything in one blob with no roles, or label it all as `user`, answers get worse or the API may error.

---

## All roles in the Chat Completions API (official list)

OpenAI’s type for `role` on input messages is exactly **six** values (see [Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat)):

| `role` | When you use it |
|--------|------------------|
| **`developer`** | High-priority instructions (OpenAI recommends this instead of **`system`** on **o1 and newer** reasoning models) |
| **`system`** | Same idea as developer — behavior rules for the session (still widely used; many models accept both) |
| **`user`** | What the human (or your app) sends |
| **`assistant`** | Past model replies **you** store; can also include **`tool_calls`** when the model asked to run a function |
| **`tool`** | Output of a function **your code** ran, tied to a `tool_call_id` from the assistant message above |
| **`function`** | **Legacy** tool result role; **prefer `tool`** in new code |

There are **no other** standard chat `role` strings (no `"bot"`, `"customer"`, etc.). Optional extra fields on a message (not roles) include e.g. **`name`** on system/user/developer messages to distinguish participants.

### `developer` vs `system`

Both carry “instructions the model should follow.” For newer models, OpenAI’s docs steer you toward **`developer`**; older tutorials and scripts (including many in this repo) still use **`system`**. Do not put both with conflicting instructions unless you know the model’s docs.

### `tool` messages (function calling)

Typical pattern:

```text
user → assistant (with tool_calls) → tool (your function result) → assistant (final answer)
```

Each **`tool`** message needs **`tool_call_id`** matching the assistant’s call. Rules about ordering are strict (tool replies must follow the assistant message that requested them).

Beginner scripts in this repo usually use only **`user`** and **`assistant`** (plus optional **`system`**). **`tool`** / **`function`** appear when you add tools (e.g. [`../5_TOOLS_FUNCTIONS/tool_functions_1.md`](../5_TOOLS_FUNCTIONS/tool_functions_1.md)).

---

## Mental picture

```text
┌─────────────────────────────────────────┐
│  messages (your list in Python)         │
├─────────────────────────────────────────┤
│  system    →  rules for this session    │
│  user      →  human                     │
│  assistant →  model (past turns)        │
│  user      →  human again               │
│  ...                                    │
└─────────────────────────────────────────┘
                    │
                    ▼
         Chat Completions API
                    │
                    ▼
         New message: role = assistant
```

---

## Same roles on Ollama?

If you call **Ollama** with the OpenAI Python client (`base_url=.../v1`), you still send **`system` / `user` / `assistant`** in `messages`. Ollama aims to be **OpenAI-compatible** for that shape even though the model runs locally.

See: [`Test_ollama_with_OPENAI.md`](./Test_ollama_with_OPENAI.md).

---

## Quick reference

| Question | Answer |
|----------|--------|
| Who defines `system`, `user`, `assistant`? | **OpenAI Chat Completions API** (copied by compatible servers and libraries). |
| Do I need all three every time? | No — often just `user`; chats use `user` + `assistant`; add `system` when you want fixed instructions. |
| Is `role` the same as “memory”? | No — **memory** is your list of past messages; **`role`** labels each entry in that list. |
| Can I make up new roles? | No — only **`developer`**, **`system`**, **`user`**, **`assistant`**, **`tool`**, **`function`**. |
| What’s new vs old? | **`developer`** (newer instruction role); **`function`** (legacy; use **`tool`**). |

---

## Official docs (external)

- [OpenAI — Chat Completions](https://platform.openai.com/docs/api-reference/chat) — message object and `role` enum  
- [OpenAI — text generation guide](https://platform.openai.com/docs/guides/text) — how messages fit together  
