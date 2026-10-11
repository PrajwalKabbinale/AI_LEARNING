# `cosine_similarity_test.py` — every step explained

Walkthrough of [`cosine_similarity_test.py`](./cosine_similarity_test.py), in the **same order** as the file (top → bottom).

Concepts: [`../cosine_similarity.md`](../cosine_similarity.md) · embeddings: [`../text_embedding_3_small.md`](../text_embedding_3_small.md) · API demo: [`../embedding_demo.md`](../embedding_demo.md)

What this file proves: embed three short sentences with `text-embedding-3-small`, show related pairs score **higher** than unrelated ones, and that a vector compared to **itself** scores ≈ **1.0**.

---

## What this script does (one sentence)

Embeds three strings with OpenAI, computes cosine for each pair (plus `embedding1` vs itself), and prints lengths and scores: Python–Python high, Python–Pizza low, self-compare ≈ 1.

---

## How to run

```bash
python cosine_similarity_test.py
```

```bash
pip install openai python-dotenv numpy
```

### Example output

```text
embedding1
1536
embedding2
1536
embedding3
1536
score1
0.6553905504622973
score2
0.2523612373308963
score3
0.16632411209633624
score4
1.0000000000000002
```

| Line | Meaning |
|------|---------|
| `1536` (three times) | Each embedding is a vector with **1536** numbers — see [Why all lengths are the same](#why-all-embedding-lengths-are-the-same-1536) |
| `score1 ≈ 0.66` | text1 ↔ text2 (both Python) — high |
| `score2 ≈ 0.25` | text1 ↔ text3 (Python ↔ pizza) — lower |
| `score3 ≈ 0.17` | text2 ↔ text3 (Python ↔ pizza) — lower |
| `score4 ≈ 1.0` | embedding1 ↔ **itself** — maximum similarity (angle 0°) |

Exact floats for score1–3 can change slightly across API versions; the **ranking** and **score4 ≈ 1** are the lesson.

### `.env`

| Key | Used in file |
|-----|----------------|
| `OPENAI_API_KEY` | `OpenAI()` reads it from the environment |

```env
OPENAI_API_KEY=your-key-here
```

`load_dotenv(override=True)` loads `.env` into the environment.

**Important:** this script does **not** use `MODEL_NAME` from `.env` (`gpt-4.1-nano` is a **chat** model). Embedding model is hard-coded as `text-embedding-3-small`.

---

## Execution order (what runs when)

1. Imports  
2. Define `cosine_similarity(vector1, vector2)` (not called yet)  
3. `load_dotenv`, read `OPENAI_API_KEY` into a variable (client still uses env)  
4. Set `MODEL_NAME = "text-embedding-3-small"`  
5. `client = OpenAI()`  
6. Define `text1`, `text2`, `text3`  
7. Three `client.embeddings.create(...)` calls → `embedding1/2/3`  
8. Print each embedding’s length  
9. Four cosine calls → `score1/2/3` + `score4` (embedding1 vs itself)  
10. Print the four scores  

---

## Step 1 — Imports

```python
from dotenv import load_dotenv
from openai import OpenAI
import os
import numpy as np
```

| Import | Role in this file |
|--------|-------------------|
| `load_dotenv` | Load `.env` into the process environment |
| `OpenAI` | Embeddings API client |
| `os` | `getenv("OPENAI_API_KEY")` |
| `numpy` (`np`) | Arrays, `dot`, `linalg.norm` for cosine |

No Gradio, no chat completions — only **embeddings** + math.

---

## Step 2 — Define `cosine_similarity`

```python
def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

### Why this function exists

OpenAI gives you **vectors** (lists of floats). It does **not** tell you “these two sentences are related.”  
**You** (or a vector DB) must compare two vectors with a formula. That formula is **cosine similarity**.

Without this function you would only have three separate lists of 1536 numbers — no way to say which pair is closer in meaning.

```text
embedding1  ──┐
              ├──►  cosine_similarity  ──►  one float (how similar?)
embedding2  ──┘
```

### Why not just print the embeddings?

Printing 1536 floats per sentence does not help a human judge similarity. Cosine collapses two long vectors into **one readable score** between roughly −1 and +1 (here, around 0…1).

### Line by line

| Line | Why |
|------|-----|
| `def cosine_similarity(vector1, vector2):` | Reusable helper — you call it three times for three pairs |
| `v1 = np.array(vector1)` | OpenAI returns a plain Python `list`; NumPy needs an array for `dot` / `norm` |
| `v2 = np.array(vector2)` | Same for the second vector |
| `np.dot(v1, v2)` | Dot product \(A \cdot B\) — how much the vectors “point together” |
| `np.linalg.norm(v1)` / `norm(v2)` | Lengths \(\|A\|\) and \(\|B\|\) |
| Divide | Full cosine: \(\dfrac{A\cdot B}{\|A\|\|B\|}\) — compares **direction**, not raw length |

### Why divide by the lengths?

Two vectors can be long or short. Cosine asks: **do they point the same way?** Dividing by \(\|A\|\|B\|\) removes magnitude so only the **angle / direction** remains. That matches “similar meaning” better than raw distance in many embedding setups.

OpenAI embeddings are **normalized** by default (`\|v\| ≈ 1`), so for those vectors cosine ≈ **dot product alone**. This function still uses the full formula — always correct. Theory: [`../cosine_similarity.md`](../cosine_similarity.md).

### When it runs

Here the function is only **defined**. It runs later:

```python
score1 = cosine_similarity(embedding1, embedding2)
score2 = cosine_similarity(embedding1, embedding3)
score3 = cosine_similarity(embedding2, embedding3)
score4 = cosine_similarity(embedding1, embedding1)  # same vector twice
```

---

## Step 3 — Load env and read the API key

```python
load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")
```

| Piece | Meaning |
|-------|---------|
| `load_dotenv(override=True)` | Put `.env` values into `os.environ` (override existing) |
| `openai_api_key = ...` | Stored in a variable — **not** passed into `OpenAI()` below |

`OpenAI()` still picks up `OPENAI_API_KEY` from the environment after dotenv. The local variable is unused for the client (fine for learning / debugging; you could `print` a prefix if you want).

Unlike [`../embedding_demo.py`](../embedding_demo.py), this script does **not** exit early if the key is missing — you’d get an OpenAI auth error on the first embed call instead.

---

## Step 4 — Embedding model name (not chat `MODEL_NAME`)

```python
MODEL_NAME = "text-embedding-3-small"
client = OpenAI()
```

| Piece | Meaning |
|-------|---------|
| `MODEL_NAME = "text-embedding-3-small"` | Hard-coded **embedding** model for all three API calls |
| `client = OpenAI()` | Client uses env `OPENAI_API_KEY` |

**Do not** set this from `.env`’s `MODEL_NAME=gpt-4.1-nano`. That env var is for **chat**. Embedding and chat are different jobs:

| Env / constant | Typical value | Used for |
|----------------|---------------|----------|
| `.env` `MODEL_NAME` | `gpt-4.1-nano` | Chat answers (keyword RAG, Gradio) |
| This file’s `MODEL_NAME` | `text-embedding-3-small` | Vectors for cosine |

Wrong model on OpenAI’s embeddings endpoint → 404 / invalid model (e.g. `nomic-embed-text` is Ollama, not OpenAI).

---

## Step 5 — Three example texts

```python
text1 = "Python is a programming language."
text2 = "Python is used for software development."
text3 = "Pizza is a delicious food."
```

| Variable | Role in the demo |
|----------|------------------|
| `text1` | About Python (language) |
| `text2` | Also about Python (development) — **related** to text1 |
| `text3` | About pizza — **unrelated** to Python |

Expected pattern after scoring:

- `score1` (text1 ↔ text2) — **high**  
- `score2` (text1 ↔ text3) — **lower**  
- `score3` (text2 ↔ text3) — **lower**  
- `score4` (embedding1 ↔ embedding1) — **≈ 1.0** (identical vectors)

Exact floats for score1–3 change with the model/version; the **ranking** plus self-score ≈ 1 is what matters for learning.

---

## Step 6 — Call the embeddings API (three times)

```python
embedding1 = client.embeddings.create(
    model=MODEL_NAME,
    input=text1
).data[0].embedding

embedding2 = client.embeddings.create(
    model=MODEL_NAME,
    input=text2
).data[0].embedding

embedding3 = client.embeddings.create(
    model=MODEL_NAME,
    input=text3
).data[0].embedding
```

### 6a — What each call does

Same pattern as [`../embedding_demo.md`](../embedding_demo.md) Step 5:

1. Send `model` + one `input` string to OpenAI.  
2. Get back a reply object.  
3. Take `.data[0].embedding` — the list of floats (default **1536** dims for `text-embedding-3-small`).

```text
text1  →  text-embedding-3-small  →  embedding1  (1536 floats)
text2  →  text-embedding-3-small  →  embedding2
text3  →  text-embedding-3-small  →  embedding3
```

### 6b — Why the same `MODEL_NAME` for all three

Cosine only makes sense when all vectors live in the **same** embedding space. Mixing models (or mixing OpenAI with Ollama `nomic-embed-text` without pointing the client at Ollama) breaks comparison.

### 6c — Chained `.data[0].embedding`

| Piece | Meaning |
|-------|---------|
| `client.embeddings.create(...)` | HTTPS call; returns a response object |
| `.data` | List of results (one per input string) |
| `[0]` | First (only) input in this call |
| `.embedding` | The vector as a Python `list` |

You could batch all three strings in **one** API call with `input=[text1, text2, text3]` and then `data[0]`, `data[1]`, `data[2]`. This script uses three separate calls for clarity.

### 6d — Not chat

This is **not** `client.chat.completions.create(...)`. No messages, no assistant reply — only vectors.

---

## Step 7 — Print embedding lengths

```python
print("embedding1")
print(len(embedding1))
print("embedding2")
print(len(embedding2))
print("embedding3")
print(len(embedding3))
```

Example:

```text
embedding1
1536
embedding2
1536
embedding3
1536
```

### Why all embedding lengths are the same (1536)

| Question | Answer |
|----------|--------|
| Why **1536**? | That is the **default output size** of `text-embedding-3-small`. Every embedding from this model is a list of **1536 floats**. |
| Why the **same** for text1, text2, and text3? | The model always maps **any** input text into a vector of that fixed size. Short sentence, long sentence — still 1536 numbers (unless you change dimensions via API options). |
| Does same length mean same meaning? | **No.** Length = shape of the vector. Meaning lives in the **values** of those 1536 numbers (which direction the vector points). |
| Why must lengths match for cosine? | Cosine / dot product needs two vectors of the **same dimension**. Same model ⇒ same dimension ⇒ comparison is valid. |

```text
"Python is a programming language."     →  [f1, f2, ..., f1536]
"Python is used for software development." →  [g1, g2, ..., g1536]
"Pizza is a delicious food."            →  [h1, h2, ..., h1536]

Same length (1536). Different directions → different cosine scores.
```

If you used a different embedding model, you might get a different length (e.g. 768). Mixing 1536 with 768 in one cosine call would be wrong.

---

## Step 8 — Compute the pairwise scores (+ self)

```python
score1 = cosine_similarity(embedding1, embedding2)  # Python ↔ Python
score2 = cosine_similarity(embedding1, embedding3)  # Python ↔ Pizza
score3 = cosine_similarity(embedding2, embedding3)  # Python ↔ Pizza

score4 = cosine_similarity(embedding1, embedding1)  # same vector vs itself
```

Then:

```python
print("score1")
print(score1)
print("score2")
print(score2)
print("score3")
print(score3)
print("score4")
print(score4)
```

Example:

```text
score1
0.6553905504622973
score2
0.2523612373308963
score3
0.16632411209633624
score4
1.0000000000000002
```

### Why the scores are different

The **lengths** are equal; the **meanings** (and pairs) are not. Cosine looks at direction (semantic closeness).

| Score | Pair | Texts | Why that score |
|-------|------|-------|----------------|
| `score1 ≈ 0.66` | embedding1 ↔ embedding2 | Python language ↔ Python development | Both about **Python / programming**. Similar direction → **high**. |
| `score2 ≈ 0.25` | embedding1 ↔ embedding3 | Python language ↔ pizza | Different topics → **much lower**. |
| `score3 ≈ 0.17` | embedding2 ↔ embedding3 | Python development ↔ pizza | Unrelated → **low**. |
| `score4 ≈ 1.0` | embedding1 ↔ embedding1 | Same vector twice | Angle between a vector and itself is **0°** → cosine = **1** (max). |

```text
text1 (Python) ════ high (~0.66) ════ text2 (Python)
   │                                    │
   │ low (~0.25)                        │ low (~0.17)
   │                                    │
   └──────────── text3 (Pizza) ─────────┘

text1 ↔ text1  →  score4 ≈ 1.0  (perfect match to itself)
```

### Why `score4` is (almost) 1.0

Mathematically:

```text
cosine(A, A) = (A · A) / (||A|| ||A||) = ||A||² / ||A||² = 1
```

So comparing a vector to **itself** must be **1**. That is the ceiling: nothing can score higher than “identical embedding.”

**Why print `1.0000000000000002` instead of exactly `1.0`?**  
Floating-point rounding in `dot` / `norm` / divide. Treat it as **1**. Not a bug in your idea — just IEEE float noise.

### Why `score1` is not 1.0

text1 and text2 are **related**, not **identical**. Different wording → different vectors → cosine below 1. Only the same vector (or the same string embedded the same way) hits ≈ 1 — that is what `score4` shows.

**What the numbers are not**

- Not a percent (“66% correct”).  
- Not proof that pizza and Python are “25% the same.”  
- Only: **relative** closeness in this model’s space. Rank with them (keep text2 over text3 for a Python query).

**RAG takeaway:** when a user asks about Python, retrieve chunks with high cosine to the query (like text1/text2), not pizza (text3). A chunk that is an exact duplicate of the query embedding would score ~1 like `score4`.

---

## How this connects to RAG

```text
This script:  3 sentences → 3 vectors → pairwise cosine → print
Full RAG:     many chunks → store vectors → embed query → top-k by cosine → chat model
```

Same building blocks: **embed** with one model, **compare** with cosine (or equiv. distance / inner product in a vector DB). Next store/search: [`../6_vector_store.md`](../6_vector_store.md).

---

## Common mistakes (from this exercise)

| Mistake | What goes wrong |
|---------|-----------------|
| `model="nomic-embed-text"` with `OpenAI()` (default OpenAI cloud) | 404 — model not on OpenAI |
| Using `.env` `MODEL_NAME=gpt-4.1-nano` for embeddings | Chat model ≠ embedding model |
| Different embedding models for different texts | Cosine meaningless |
| Sorting scores the wrong way | “Best” match is usually the **highest** cosine |

---

## Checklist

- [ ] `OPENAI_API_KEY` available after `load_dotenv`  
- [ ] `MODEL_NAME` in this file is `text-embedding-3-small`  
- [ ] Lengths print as `1536`  
- [ ] `score1` > `score2` and `score1` > `score3` (typical)  
- [ ] `score4` ≈ `1.0` (self-compare)

**Next:** [`../cosine_similarity.md`](../cosine_similarity.md) · [`../6_vector_store.md`](../6_vector_store.md)
