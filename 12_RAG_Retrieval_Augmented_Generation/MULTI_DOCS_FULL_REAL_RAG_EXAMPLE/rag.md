# `rag.py` — every step explained

Walkthrough of [`rag.py`](./rag.py), in the **same order** as the file (top → bottom). Every important line is covered.

This is a **mini real RAG** loop (no vector DB yet):

```text
knowledge/*.txt  →  embed once at startup
user question    →  embed
cosine vs each doc  →  pick best file
best file text + question  →  chat model  →  answer
```

Related: [`../cosine_similarity.md`](../cosine_similarity.md) · [`../embedding_demo.md`](../embedding_demo.md) · [`../COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.md`](../COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.md) · [`../2_rag_architecture_and_workflow.md`](../2_rag_architecture_and_workflow.md) · [`../6_vector_store.md`](../6_vector_store.md)

---

## What this script does (one sentence)

Loads text files from `knowledge/`, embeds them with `text-embedding-3-small`, and for each user message finds the closest file by cosine similarity, then asks a **chat** model to answer using only that file as context.

---

## Index

| # | Topic |
|---|--------|
| 1 | [Line map (`rag.py`)](#line-map-ragpy) |
| 2 | [Execution order](#execution-order-what-runs-when) |
| 3 | [Code — step by step](#step-1--imports) |
| 4 | [Full RAG map](#full-rag-map-for-this-file) |
| 5 | [Limits of this toy RAG](#limits-of-this-toy-rag-on-purpose) |
| 6 | [How to run](#how-to-run) |
| 7 | [Example output](#example-output-with-debug-prints) |
| 8 | [Explain the output](#explain-the-output) |

---

## Line map (`rag.py`)

| Lines | What |
|-------|------|
| 1–5 | Imports |
| 7–8 | `load_dotenv` + read `OPENAI_API_KEY` |
| 10–14 | Embedding vs chat model + `OpenAI()` client |
| 16–19 | `cosine_similarity` |
| 21–28 | `load_documents` |
| 30–35 | `create_embedding` |
| 37–42 | Load docs + embed all files into `document_embeddings` |
| 44–46 | Banner prints |
| 48–52 | Loop start + `quit` |
| 54–68 | Embed question, score docs, pick best, print `RAG_DOC_CONTENT` |
| 70–72 | Build + print `prompt` |
| 74–84 | Chat completion + print answer |

---

## Execution order (what runs when)

1. Imports  
2. `load_dotenv`, read key, set `EMBEDDING_MODEL` / `CHAT_MODEL`, `OpenAI()`  
3. Define `cosine_similarity`, `load_documents`, `create_embedding` (not called yet)  
4. `documents = load_documents()` — reads every `knowledge/*.txt`  
5. Loop: embed each file → `document_embeddings`  
6. Print banner  
7. Forever loop: `input` → quit? → embed question → score all docs → pick best → print `RAG_DOC_CONTENT` → build `prompt` → print `AI_ASSISTANT_PROMPT` → chat → print answer  

---

## Step 1 — Imports

```python
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from pathlib import Path
```

| Line | Role |
|------|------|
| `from openai import OpenAI` | Official OpenAI Python SDK — embeddings **and** chat |
| `from dotenv import load_dotenv` | Load key/model names from a `.env` file |
| `import os` | `os.getenv(...)` to read environment variables |
| `import numpy as np` | Arrays + `dot` + `norm` for cosine |
| `from pathlib import Path` | Clean path / `glob` / `read_text` for `knowledge/` |

No Gradio. No vector DB library. Pure OpenAI + NumPy + files.

---

## Step 2 — Env and two different models

```python
load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Embedding model ≠ chat model

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("MODEL_NAME")
client = OpenAI()
```

| Line | Meaning |
|------|---------|
| `load_dotenv(override=True)` | Read `.env` into `os.environ`. `override=True` means `.env` values replace any already-set env vars of the same name |
| `openai_api_key = os.getenv("OPENAI_API_KEY")` | Pull the key into a Python variable. **Not** passed into `OpenAI()` below — the client still reads the key from the environment itself. (Variable is unused later; harmless / leftover for debugging.) |
| Comment `# Embedding model ≠ chat model` | Reminder: do not reuse one string for both jobs |
| `EMBEDDING_MODEL = "text-embedding-3-small"` | Hard-coded embedding model for **all** `embeddings.create` calls |
| `CHAT_MODEL = os.getenv("MODEL_NAME")` | Chat model from `.env` (e.g. `gpt-4.1-nano`). Used **only** in `chat.completions.create` |
| `client = OpenAI()` | One client object; uses env `OPENAI_API_KEY` for auth |

**Never** put `text-embedding-3-small` into `chat.completions.create` — OpenAI will reject / refuse sampling (403 / not allowed to sample).

If `MODEL_NAME` is missing from `.env`, `CHAT_MODEL` is `None` and the chat call will fail — keep `MODEL_NAME` set.

---

## Step 3 — `cosine_similarity` (line by line)

```python
def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

| Line | Why |
|------|-----|
| `def cosine_similarity(vector1, vector2):` | Helper: two embeddings in → one float out |
| `v1 = np.array(vector1)` | OpenAI returns a Python `list` of floats; NumPy needs an array for `dot` / `norm` |
| `v2 = np.array(vector2)` | Same for the second vector |
| `np.dot(v1, v2)` | Dot product \(A \cdot B\) |
| `np.linalg.norm(v1)` / `norm(v2)` | Lengths \(\|A\|\), \(\|B\|\) |
| Divide | Full cosine \(\dfrac{A\cdot B}{\|A\|\|B\|}\) — compares **direction** |

OpenAI embeddings are normalized by default, so for those vectors cosine ≈ dot product alone. Full formula is always safe. Theory: [`../cosine_similarity.md`](../cosine_similarity.md).

Defined here; **called later** when scoring the question against each document.

---

## Step 4 — `load_documents` (line by line)

```python
def load_documents():
    documents = {}
    folder = Path("knowledge")
    for file in folder.glob("*.txt"):
        documents[file.name] = file.read_text(
            encoding="utf-8"
        )
    return documents
```

| Line | Why |
|------|-----|
| `documents = {}` | Empty dict; will map filename → file text |
| `folder = Path("knowledge")` | Relative folder next to **current working directory** when you run the script |
| `folder.glob("*.txt")` | Only `.txt` files (skips other types) |
| `file.name` | Basename only, e.g. `python.txt` (not full path) — used as dict key and in “Best document” prints |
| `file.read_text(encoding="utf-8")` | Read whole file as one Unicode string |
| `documents[file.name] = ...` | Store text under that filename |
| `return documents` | Hand the filled dict to the caller |

If `knowledge/` is missing or empty, you get `{}` or a crash on missing folder — run from the correct directory with `.txt` files present.

---

## Step 5 — `create_embedding` (line by line)

```python
def create_embedding(content):
    embedding1 = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=content,
    ).data[0].embedding
    return embedding1
```

| Piece | Why |
|-------|-----|
| `def create_embedding(content):` | One helper for “string → vector” (docs and questions) |
| `client.embeddings.create(...)` | HTTPS call to OpenAI embeddings API |
| `model=EMBEDDING_MODEL` | Must be `text-embedding-3-small` (or another **embedding** model) |
| `input=content` | The text to embed (full file, or user message) |
| `.data` | List of embedding results (one per input string) |
| `[0]` | First (only) input in this call |
| `.embedding` | The vector: Python `list` of floats (default **1536** dims) |
| `return embedding1` | Caller stores or compares this list |

Same pattern as [`../embedding_demo.md`](../embedding_demo.md). Used at startup (each file) and each turn (user question).

---

## Step 6 — Index at startup (line by line)

```python
documents = load_documents()

document_embeddings = {}

for filename, content in documents.items():
    document_embeddings[filename] = create_embedding(content)
```

| Line | Why |
|------|-----|
| `documents = load_documents()` | Actually run the loader — now you have text in RAM |
| `document_embeddings = {}` | Second dict: filename → **vector** (not text) |
| `for filename, content in documents.items():` | Unpack each key/value from `documents` |
| `document_embeddings[filename] = create_embedding(content)` | One API embed call per file; store the vector under the same filename |

```text
documents["python.txt"]           = "Python is a high-level..."
document_embeddings["python.txt"] = [0.01, -0.02, ..., ]  (1536 floats)
```

This is the **ingest / index** phase (in memory — not Chroma/FAISS). After this, the chat loop only embeds the **question**, not every file again (saves time/cost).

---

## Step 7 — Banner

```python
print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
```

| Line | Why |
|------|-----|
| `"=" * 40` | String of 40 equals signs — decorative border |
| Middle print | Title line |
| No API | Pure UI before the interactive loop |

---

## Step 8 — Chat loop: retrieve then generate

```python
while True:
    user_input = input("\nYou : ")
```

| Line | Why |
|------|-----|
| `while True:` | Infinite loop until `break` on `quit` |
| `input("\nYou : ")` | Wait for keyboard; `"\nYou : "` is the prompt shown in the terminal |
| `user_input` | Exact string the user typed (this turn) |

### 8a — Quit

```python
if user_input.lower() == "quit":
    print("\nAI  : Goodbye! Have a great day.")
    break
```

| Line | Why |
|------|-----|
| `user_input.lower()` | Case-insensitive (`Quit` / `QUIT` also work) |
| `== "quit"` | Exact word after lowercasing — **not** `bye` |
| `print(...)` | Farewell message |
| `break` | Leave `while True` — script ends |

`bye` is **not** special: it goes through embed → retrieve → chat (usually “I don't know”).

### 8b — Embed the question

```python
question_embedding = create_embedding(user_input)
```

| Line | Why |
|------|-----|
| `create_embedding(user_input)` | Same embedding model as the docs |
| `question_embedding` | Query vector to compare against every `document_embeddings[...]` |

### 8c — Score every document, keep the best

```python
best_score = -1
best_document = None

for filename, embedding in document_embeddings.items():
    score = cosine_similarity(question_embedding, embedding)
    print(f"Score for {filename}: {score}")
    if score > best_score:
        best_score = score
        best_document = filename

print(f"Best document: {best_document}")

RAG_DOC_CONTENT = documents[best_document]
print(f"\nRAG_DOC_CONTENT: {RAG_DOC_CONTENT}")
```

| Line | Why |
|------|-----|
| `best_score = -1` | Cosine is at least −1; starting at −1 means the **first** file always becomes the initial winner |
| `best_document = None` | Placeholder until the loop sets a filename |
| `for filename, embedding in document_embeddings.items():` | Walk every indexed vector |
| `score = cosine_similarity(question_embedding, embedding)` | Similarity of **this question** vs **this file** |
| `print(f"Score for {filename}: {score}")` | Debug: see all scores |
| `if score > best_score:` | Keep a better match (`>` means a **tie** keeps the earlier file) |
| `best_score = score` | Remember the new high score |
| `best_document = filename` | Remember which file won so far |
| `print(f"Best document: {best_document}")` | Local debug — GPT never sees this filename unless you put it in the prompt (you don’t) |
| `RAG_DOC_CONTENT = documents[best_document]` | Look up the **text** (not the vector) for that filename |
| `print(f"\nRAG_DOC_CONTENT: ...")` | Show exactly what will be pasted as context |

No minimum threshold: even `0.09` can win if it’s the highest.  
> **Best document ≠ correct document.** Highest cosine among *your* files only.

### 8d — Augment: build the prompt (and print it)

```python
prompt = f"Use ONLY the Context below to answer.\nIf the user typed a topic or keyword (not a full question), briefly explain what it is using the Context.\nIf the Context truly has nothing relevant, say 'I don't know.'\n\nRAG_Context: {RAG_DOC_CONTENT}\n\nUSER_INPUT: {user_input}"

print(f"\n\nAI_ASSISTANT_PROMPT: {prompt}")
```

| Piece inside `prompt` | Why |
|-----------------------|-----|
| `Use ONLY the Context below...` | Force grounding — don’t invent from world knowledge |
| Keyword / topic instruction | So `"python"` / `"mysql"` get an explanation, not only full questions |
| `say 'I don't know.'` | When Context can’t answer (france, bye) |
| `\n\n` | Blank lines for readability in the printed prompt |
| `RAG_Context: {RAG_DOC_CONTENT}` | **File text injected here** — this is how knowledge reaches GPT |
| `USER_INPUT: {user_input}` | The user’s typed line |
| `print(...AI_ASSISTANT_PROMPT...)` | Proof of what is sent to the API |

`f"..."` builds one string. `{RAG_DOC_CONTENT}` and `{user_input}` are filled in at runtime.

### 8e — Does GPT know about `python.txt` on my laptop?

**No.** GPT-nano never sees your laptop and never opens `knowledge/python.txt`.

**Wrong mental model**

```text
User: "python"
        ↓
GPT somehow finds python.txt on my PC  ❌  (this does NOT happen)
```

**What actually happens**

```text
1. YOUR Python script
   - already loaded files into `documents` at startup
   - cosine picks best filename, e.g. python.txt
   - RAG_DOC_CONTENT = documents["python.txt"]   ← file TEXT copied into a string

2. YOUR Python builds one big prompt string:
   instructions
   + RAG_Context: <that text>
   + USER_INPUT: python

3. YOUR Python sends that string to OpenAI over HTTPS
   client.chat.completions.create(..., messages=[{"content": prompt}])

4. GPT-nano only reads the characters inside `prompt`
   - It never receives a path like knowledge/python.txt
   - It cannot browse your disk
```

| Who | Role |
|-----|------|
| **Your script** | Librarian — finds the right file, **copies its text** into the message |
| **GPT-nano** | Reader — only reads the message you sent; answers from that text |

Filename `python.txt` is used **locally** only to choose which string becomes `{RAG_DOC_CONTENT}`. The API never gets “look at python.txt on Souvik’s PC.”

### 8f — Generate with chat model (line by line)

```python
response = client.chat.completions.create(
    model=CHAT_MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)

print("\nAI :", response.choices[0].message.content)
```

| Piece | Why |
|-------|-----|
| `client.chat.completions.create(...)` | Chat Completions API (not embeddings) |
| `model=CHAT_MODEL` | Must be a **chat** model from `.env` (`gpt-4.1-nano`), not the embedding model |
| `messages=[...]` | Conversation list; here one message |
| `"role": "user"` | This message is from the “user” side (your whole RAG prompt) |
| `"content": prompt` | The full string from Step 8d — instructions + context + question |
| `response` | Full API reply object |
| `response.choices` | List of completion choices (usually one) |
| `[0]` | First choice |
| `.message` | The assistant message object |
| `.content` | The answer text string |
| `print("\nAI :", ...)` | Show the answer in the terminal |

Chat model never searches files itself — it only sees `prompt`.

---

## Full RAG map for this file

| RAG phase | In `rag.py` |
|-----------|-------------|
| **Ingest** | `load_documents` + embed into `document_embeddings` |
| **Retrieve** | Embed question + cosine + `best_document` |
| **Augment** | `RAG_DOC_CONTENT` into `prompt` (`RAG_Context` + `USER_INPUT`) |
| **Generate** | `chat.completions.create` |

Keyword RAG ([`../keyword_rag_gradio_chat.py`](../keyword_rag_gradio_chat.py)) matches dict keys by word. This script matches by **meaning** (embeddings + cosine).

---

## Limits of this toy RAG (on purpose)

| Limit | Effect |
|-------|--------|
| Tiny corpus | No answer for France |
| Always pick top-1 | Weak matches still “win” |
| No score threshold | Off-topic queries still get a “Best document” |
| No chunking | Whole file = one vector |
| No vector DB | Everything in a Python dict in RAM |
| No hybrid keyword search | Pure cosine |
| `openai_api_key` unused | Client reads env directly |
| No empty-corpus guard | Empty `knowledge/` → crash when indexing/scoring |

Next upgrades: [`../6_vector_store.md`](../6_vector_store.md) and LangChain Chroma notebooks in `13_LANGCHAIN/`.

---

## How to run

```bash
python rag.py
```

```bash
pip install openai python-dotenv numpy
```

Needs `OPENAI_API_KEY` and chat `MODEL_NAME` in `.env`. Run from the folder that contains both `rag.py` and `knowledge/` (relative path `knowledge`).

### `.env`

| Key | Used in file |
|-----|----------------|
| `OPENAI_API_KEY` | `OpenAI()` (via environment) |
| `MODEL_NAME` | Chat model only (`CHAT_MODEL`) — e.g. `gpt-4.1-nano` |

```env
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4.1-nano
```

Embedding model is hard-coded as `text-embedding-3-small` — **not** the same as chat `MODEL_NAME`.

---

## Example output (with debug prints)

```text
python rag.py
========================================
      My AI Assistant
========================================

You : capital of france ?
Score for mysql.txt: -0.03659725624667847
Score for weather.txt: 0.0604369286086797
Score for machine_learning.txt: 0.00510959253971092
Score for python.txt: 0.08778214741521417
Best document: python.txt

RAG_DOC_CONTENT: Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.



AI_ASSISTANT_PROMPT: Use ONLY the Context below to answer.
If the user typed a topic or keyword (not a full question), briefly explain what it is using the Context.
If the Context truly has nothing relevant, say 'I don't know.'

RAG_Context: Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.


USER_INPUT: capital of france ?

AI : I don't know.

You : python
Score for mysql.txt: 0.1278897278381381
Score for weather.txt: 0.11145577754908513
Score for machine_learning.txt: 0.12974036466259864
Score for python.txt: 0.432502602755652
Best document: python.txt

RAG_DOC_CONTENT: Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.



AI_ASSISTANT_PROMPT: Use ONLY the Context below to answer.
If the user typed a topic or keyword (not a full question), briefly explain what it is using the Context.
If the Context truly has nothing relevant, say 'I don't know.'

RAG_Context: Python is a high-level programming language.

It is widely used for Artificial Intelligence,
Machine Learning,
Data Science,
Automation,
and Web Development.


USER_INPUT: python

AI : Python is a high-level programming language that is widely used for Artificial Intelligence, Machine Learning, Data Science, Automation, and Web Development.

You : bye
Score for mysql.txt: 0.022630237451596254
Score for weather.txt: 0.04823013356814127
Score for machine_learning.txt: 0.04434897965560738
Score for python.txt: -0.00713711284868845
Best document: weather.txt

RAG_DOC_CONTENT: Weather forecasting predicts future atmospheric conditions.

It uses temperature,
humidity,
wind speed,
and pressure.



AI_ASSISTANT_PROMPT: Use ONLY the Context below to answer.
If the user typed a topic or keyword (not a full question), briefly explain what it is using the Context.
If the Context truly has nothing relevant, say 'I don't know.'

RAG_Context: Weather forecasting predicts future atmospheric conditions.

It uses temperature,
humidity,
wind speed,
and pressure.


USER_INPUT: bye

AI : I don't know.

You : quit

AI  : Goodbye! Have a great day.
```

---

## Explain the output

### What the print labels mean

| Print | What it is | Code that prints it |
|-------|------------|---------------------|
| `Score for …` | Cosine of user message vs each file | `print(f"Score for {filename}: {score}")` |
| `Best document` | Filename that won (local only) | `print(f"Best document: {best_document}")` |
| `RAG_DOC_CONTENT` | Full text of that file | `print(f"\nRAG_DOC_CONTENT: {RAG_DOC_CONTENT}")` |
| `AI_ASSISTANT_PROMPT` | Exact string sent to chat API | `print(f"\n\nAI_ASSISTANT_PROMPT: {prompt}")` |
| `AI :` | Chat model reply | `print("\nAI :", response.choices[0].message.content)` |

GPT only ever sees `AI_ASSISTANT_PROMPT` — not your folder tree.

### Turn-by-turn

#### 1) `capital of france ?` → python.txt → “I don't know.”

| Piece | Meaning |
|-------|---------|
| All scores low (max ~0.09) | No France/Paris doc in `knowledge/` |
| Best = `python.txt` | Always pick highest score — even when weak (“best of a bad set”) |
| `RAG_DOC_CONTENT` | Python language text was copied into the prompt |
| AI: I don't know | Prompt says use **only** Context. That text has no capital of France → refuse |

**Lesson:** Off-topic questions still retrieve *some* file. Without a score threshold, the “winner” can be unrelated. Chat still refuses if Context doesn’t answer.

##### Why Best can be `python.txt` but the answer is still “I don't know”

Because **finding a “best” file** and **answering the question** are two different steps.

**1. Retrieve (your script)**  
Cosine only asks: *which of my 4 files is closest to this question?*  
For `"capital of france ?"`, all scores are tiny. `python.txt` wins at **~0.09** — not because it knows France, but because it’s the least-bad of a bad set.

> **Best document ≠ correct document.**

**2. Generate (GPT-nano)**  
It never sees the filename. It only sees the prompt:

- Instructions: use **ONLY** Context; if nothing relevant → say I don't know  
- `RAG_Context`: text about the **Python programming language**  
- `USER_INPUT`: capital of france ?

That Context has **no Paris / France**. So it correctly says **I don't know**.

```text
Best document: python.txt     ← "closest file among 4" (weak match)
RAG_Context: Python is a...   ← what GPT actually reads
Question: capital of france?  ← not in that text
Answer: I don't know.         ← prompt working as designed
```

If it answered “Paris” from training memory, that would **break** RAG (not grounded in your docs). Refusing here is correct.

#### 2) `python` → python.txt → real answer

| Piece | Meaning |
|-------|---------|
| `python.txt` ~**0.43** | Clear winner |
| Same style of `RAG_DOC_CONTENT` | Now Context **matches** the user topic |
| AI answer | Keyword → “explain from Context” → definition |

#### 3) `bye` → weather.txt → “I don't know.”

| Piece | Meaning |
|-------|---------|
| Scores all very low | Farewell ≠ knowledge topic |
| Best = `weather.txt` | Weak winner again |
| AI: I don't know | Weather doesn’t answer “bye” |
| Not `quit` | Only `quit` exits; `bye` still runs full RAG |

#### 4) `quit` → goodbye, exit

No embed / retrieve / prompt. Loop breaks via `break`.

### Score cheat-sheet from this run

| User | Best file | Best score (approx.) | Why |
|------|-----------|----------------------|-----|
| capital of france ? | python.txt | 0.09 | Off-topic; weak “winner” |
| python | python.txt | 0.43 | On-topic |
| bye | weather.txt | 0.05 | Not a knowledge query; weak “winner” |
| quit | — | — | Exit, no RAG |

Negative scores mean those vectors point somewhat opposite / unrelated — still valid cosine.

---

## Checklist

- [ ] You can map every line in `rag.py` via the [line map](#line-map-ragpy)  
- [ ] You understand Steps 1–8 line by line  
- [ ] `python rag.py` from the folder with `knowledge/`  
- [ ] `.env` has `OPENAI_API_KEY` and chat `MODEL_NAME`  
- [ ] `EMBEDDING_MODEL` ≠ `CHAT_MODEL`  
- [ ] On-topic (`python`) → matching `.txt` + real answer  
- [ ] Off-topic (`capital of france ?`, `bye`) → weak file + “I don't know.”  
- [ ] GPT never opens files on disk — only reads `prompt`  
- [ ] `quit` exits  

**Next:** [`../6_vector_store.md`](../6_vector_store.md) · [`../cosine_similarity.md`](../cosine_similarity.md)
