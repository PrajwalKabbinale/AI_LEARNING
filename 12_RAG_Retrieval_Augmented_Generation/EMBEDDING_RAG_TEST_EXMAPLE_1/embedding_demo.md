# `embedding_demo.py` — every step explained

Walkthrough of `[embedding_demo.py](./embedding_demo.py)`, in the **same order** as the file (top → bottom).

Concepts: `[text_embedding_3_small.md](./text_embedding_3_small.md)` · theory: `[3_lm_types_and_embeddings.md](./3_lm_types_and_embeddings.md)`

File header: first OpenAI embedding with `text-embedding-3-small`; needs `OPENAI_API_KEY` in `.env`.

---

## What this script does (one sentence)

Loads your OpenAI API key, sends one short sentence to `text-embedding-3-small`, and prints the vector length (1,536) plus the first five floats.

---

## How to run

From the folder that contains `embedding_demo.py` (or with `OPENAI_API_KEY` already in the environment / a discoverable `.env`):

```bash
pip install openai python-dotenv
python3 embedding_demo.py
```

### `.env`


| Key              | Used in file                               |
| ---------------- | ------------------------------------------ |
| `OPENAI_API_KEY` | `OpenAI()` (and the early exit if missing) |


```env
OPENAI_API_KEY=your-key-here
```

`load_dotenv(override=True)` loads a `.env` from the **current working directory** (typical dotenv behavior). Put the key there, or export it in the shell before running.

---

## Execution order (what runs when)

1. Imports
2. `load_dotenv(override=True)`
3. Exit if `OPENAI_API_KEY` missing
4. `client = OpenAI()`
5. `client.embeddings.create(...)` with one string
6. Take `response.data[0].embedding`
7. Print dimension count and first 5 values

---

## Step 1 — Imports

```python
import os

from dotenv import load_dotenv
from openai import OpenAI
```


| Import        | Role in this file              |
| ------------- | ------------------------------ |
| `os`          | `getenv` for the API key check |
| `load_dotenv` | Load key into the environment  |
| `OpenAI`      | Embeddings API client          |


No Gradio, no chat model, no `MODEL_NAME` — this file only calls the **embeddings** endpoint.

---

## Step 2 — Load `.env`

```python
load_dotenv(override=True)
```


| Piece              | Meaning                                                       |
| ------------------ | ------------------------------------------------------------- |
| `load_dotenv(...)` | Read `.env` into process environment                          |
| `override=True`    | Values from `.env` replace existing env vars of the same name |


Unlike `[keyword_rag_gradio_chat.py](./keyword_rag_gradio_chat.py)`, this script does **not** `os.chdir` — it only needs the API key, not relative paths like `knowledge-base/`.

---

## Step 3 — Require the API key

```python
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY not set — add it to .env")
```

Fails fast with a clear message instead of a vague OpenAI auth error later.

---

## Step 4 — Create the client

```python
client = OpenAI()
```

`OpenAI()` reads `OPENAI_API_KEY` from the environment (already loaded by dotenv). Same client family as chat completions — different method below.

---

## Step 5 — Call the embeddings API

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Kubernetes automatically restarts failed containers.",
)
```

This is the **only network call** in the script. Everything before it only prepared the client; everything after it only **reads** what came back.

### 5a — What this line does (plain English)

You hand OpenAI:

1. **Which embedding model** to use (`text-embedding-3-small`).  
2. **Which text** to represent (one Kubernetes sentence).

OpenAI runs that text through the embedding model and returns a **vector** — a long list of floats that stands for the sentence’s meaning. Your variable `response` holds the full API reply object; the actual list of numbers is dug out in Step 6.

```text
Python process                          OpenAI
─────────────                          ──────
client.embeddings.create( ... )
        │
        │  HTTPS POST  (model + input text + your API key)
        ▼
                                   text-embedding-3-small
                                   turns the sentence into
                                   ~1536 floats
        │
        │  JSON reply (embedding + metadata)
        ▼
response  =  that whole reply object
```

Nothing here generates a chat answer. No “assistant message,” no tokens of prose — only numbers for similarity search later.

### 5b — Read the call left to right

| Piece | Meaning |
|-------|---------|
| `client` | The `OpenAI()` object from Step 4 — knows your key and how to talk to the API |
| `.embeddings` | Namespace for **embedding** endpoints (sibling of `.chat` used in keyword RAG) |
| `.create(...)` | “Create an embedding for this input” — the request that actually runs |
| `response = ...` | Store the full reply so Step 6 can pick out `.data[0].embedding` |

So:

- Chat scripts: `client.chat.completions.create(...)`  
- This script: `client.embeddings.create(...)`  

Same `client`, **different product surface**.

### 5c — Compare to chat completions (what you already know)

In [`keyword_rag_gradio_chat.py`](../keyword_rag_gradio_chat.py) you call something like:

```python
openai.chat.completions.create(model=MODEL_NAME, messages=messages)
```

| | Chat (`chat.completions.create`) | Embeddings (`embeddings.create`) |
|--|----------------------------------|----------------------------------|
| Typical model | `gpt-4.1-nano` (`MODEL_NAME`) | `text-embedding-3-small` |
| Main input | `messages=[...]` (roles + text) | `input="..."` or `input=["...", "..."]` |
| Job | Continue the conversation / answer | Turn text into a vector |
| Useful output | `response.choices[0].message.content` (string) | `response.data[0].embedding` (list of floats) |
| Used in RAG for | Final answer after retrieval | Index chunks + embed the user question |

If you used a chat model here, you would get **words**, not a stable embedding space a vector DB can search.

### 5d — Argument `model=`

```python
model="text-embedding-3-small",
```

| Point | Detail |
|-------|--------|
| What it selects | OpenAI’s small embedding model (default **1536** dimensions) |
| What it is **not** | Not `gpt-4.1-nano`, not any chat/completions model |
| Why hard-coded | This demo always embeds; there is no `MODEL_NAME` for chat |
| Consistency rule | In a real RAG index, **every** chunk and **every** query must use this same model string (or you rebuild the index) |

Wrong model name → API error. Chat model name here → wrong endpoint / wrong kind of result.

### 5e — Argument `input=`

```python
input="Kubernetes automatically restarts failed containers.",
```

| Point | Detail |
|-------|--------|
| Type here | One Python `str` — one sentence → one vector |
| What gets embedded | The **entire** string as one unit (not split into words by you) |
| Why this sentence | Dummy “document chunk” about Kubernetes — enough to see a real 1536-d vector |
| Token limit | Model accepts up to **8,192 tokens** per input item (docs can change; check OpenAI if you embed huge blobs) |
| Cost | You pay for embedding **input** tokens (cheap vs chat); no “output tokens” of prose |

**Batch form** (not in this file, but same API):

```python
client.embeddings.create(
    model="text-embedding-3-small",
    input=[
        "Kubernetes restarts failed containers.",
        "Python is a popular programming language.",
    ],
)
```

Then `response.data` has **two** items — `data[0].embedding`, `data[1].embedding` — same order as the list. RAG ingest almost always uses this pattern over many chunks.

### 5f — What `response` is (before Step 6)

After `.create` returns, `response` is an SDK object roughly shaped like:

```text
response
├── data          → list of embedding results (length = number of inputs)
│   └── [0]
│       ├── embedding  → [float, float, ...]   ← what we want
│       ├── index      → 0
│       └── object     → "embedding"
├── model         → "text-embedding-3-small" (echo / version info)
└── usage         → token counts for this call
```

This script does **not** print `response` itself. Step 6 only pulls `response.data[0].embedding`.

### 5g — What this step does **not** do

- Does **not** call a chat model or return an answer to a question.  
- Does **not** search a vector database (no Chroma/FAISS yet).  
- Does **not** compare two texts (need two embeddings + a similarity score).  
- Does **not** need `messages`, `system` prompts, or Gradio history.

It only answers: **“What is the embedding vector for this one string?”**

### 5h — Common mistakes

| Mistake | What goes wrong |
|---------|-----------------|
| Using `chat.completions.create` with an embedding model | Wrong API; you expect prose, embeddings expect vectors |
| Using `gpt-4.1-nano` as `model=` here | Chat model ≠ embedding model |
| Forgetting `OPENAI_API_KEY` | Auth error (Step 3 should have caught it) |
| Assuming the printed floats are “the answer” | They are coordinates for similarity, not readable text |
| Later: embedding docs with model A and queries with model B | Similarity search becomes meaningless |

---

## Step 6 — Extract and print the vector

```python
embedding = response.data[0].embedding
print("Number of dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
```


| Piece            | Meaning                                          |
| ---------------- | ------------------------------------------------ |
| `response.data`  | List of embedding results (one per input string) |
| `[0]`            | First (only) input                               |
| `.embedding`     | Python `list` of floats                          |
| `len(embedding)` | Default **1536** for `text-embedding-3-small`    |
| `embedding[:5]`  | Peek at the start; full list is long             |


Example shape of output (values change every call):

```text
Number of dimensions: 1536

First 5 values: [0.0123, -0.0456, ...]
```

---

## How this connects to RAG

```text
This script:  one sentence  →  one vector  →  print
Full RAG:     many chunks   →  many vectors →  store in vector DB
              user question →  one vector   →  nearest chunks → chat model
```

You already use the same embedding model from LangChain as `OpenAIEmbeddings(model="text-embedding-3-small")` in `[13_LANGCHAIN/](../13_LANGCHAIN/)`. This demo is the raw OpenAI SDK equivalent of “make one embedding.”

---

## Checklist

- [ ] `OPENAI_API_KEY` set in `.env` (or the environment)  
- [ ] `pip install openai python-dotenv`  
- [ ] `python3 embedding_demo.py` prints `1536` and five floats  
- [ ] You know this model is for **vectors**, not chat answers  

**Next:** `[text_embedding_3_small.md](./text_embedding_3_small.md)` (concepts) · `[6_vector_store.md](./6_vector_store.md)` (where vectors are stored)