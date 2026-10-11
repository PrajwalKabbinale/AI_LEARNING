# Cosine similarity (for RAG embeddings)

Companion note after [`text_embedding_3_small.md`](./text_embedding_3_small.md) and [`3_lm_types_and_embeddings.md`](./3_lm_types_and_embeddings.md). Folder `12_RAG_Retrieval_Augmented_Generation`.

One of the most important ideas when you learn AI, RAG, and embeddings: **cosine similarity** helps a system decide whether two pieces of text have **similar meanings** by comparing the **direction** of their vectors.

**Next:** [`6_vector_store.md`](./6_vector_store.md) (stores vectors and runs similarity search at scale)

Related: [`embedding_demo.py`](./embedding_demo.py) · [`embedding_demo.md`](./embedding_demo.md) · practice: [`COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.py`](./COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.py) · [`COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.md`](./COSINE_SIMILARITY_TEST_EXMAPLE_1/cosine_similarity_test.md) · mini RAG: [`MULTI_DOCS_FULL_REAL_RAG_EXAMPLE/rag.py`](./MULTI_DOCS_FULL_REAL_RAG_EXAMPLE/rag.py) · [`MULTI_DOCS_FULL_REAL_RAG_EXAMPLE/rag.md`](./MULTI_DOCS_FULL_REAL_RAG_EXAMPLE/rag.md) · [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md) (retrieve phase)

---

## Index

| # | Topic |
|---|--------|
| 1 | [Why we need a similarity score](#1-why-we-need-a-similarity-score) |
| 2 | [Intuition: angle between two arrows](#2-intuition-angle-between-two-arrows) |
| 3 | [The formula](#3-the-formula) |
| 4 | [What the score means](#4-what-the-score-means) |
| 5 | [How this works with AI embeddings (example)](#5-how-this-works-with-ai-embeddings-example) |
| 6 | [Cosine similarity vs cosine distance](#6-cosine-similarity-vs-cosine-distance) |
| 7 | [Dot product and normalized embeddings](#7-dot-product-and-normalized-embeddings) |
| 8 | [Tiny Python example](#8-tiny-python-example) |
| 9 | [How OpenAI fits in](#9-how-openai-fits-in) |
| 10 | [How RAG uses this](#10-how-rag-uses-this) |
| 11 | [Common mistakes](#11-common-mistakes) |
| 12 | [Check your understanding](#12-check-your-understanding) |

---

## 1. Why we need a similarity score

An embedding model turns text into a **vector** (list of numbers). For RAG you usually have:

- Many **document chunk** vectors (already stored).  
- One **query** vector (just computed from the user’s question).

You need a number that answers:

> How related is this chunk to this question?

That number is a **similarity score**. **Cosine similarity** is one of the most common choices for text embeddings.

Keyword RAG (your [`keyword_rag_gradio_chat.py`](./keyword_rag_gradio_chat.py)) skips this: it matches words to dict keys. Vector RAG ranks by **math in embedding space**.

---

## 2. Intuition: angle between two arrows

Think of each vector as an **arrow** from the origin in a high-dimensional space (you can only draw 2D, but the idea is the same).

Cosine similarity measures similarity in **direction** between two vectors, largely **regardless of their magnitudes** (lengths).

```text
        ↑
        │     B  (query)
        │    /
        │   /
        │  /  θ  ← angle between A and B
        │ /
        │/________→
       A (document chunk)
```

| Situation | Angle θ | Cosine similarity (idea) |
|-----------|---------|---------------------------|
| Same direction | ~0° | Near **1** — very similar |
| Somewhat related | medium | Between 0 and 1 |
| Orthogonal (unrelated axes) | ~90° | Near **0** |
| Opposite direction | ~180° | Near **−1** — opposite |

**Key idea:** cosine cares about **direction** (orientation), not how long the arrows are. Two texts with the same meaning point roughly the same way even if their vector lengths differ.

For embeddings, “same direction” ≈ “similar meaning.”

---

## 3. The formula

For vectors **A** and **B**:

```text
                    A · B
cosine(A, B)  =  ─────────────
                 ||A||  ||B||
```

| Symbol | Meaning |
|--------|---------|
| `A · B` | **Dot product** — multiply matching components, then sum |
| `\|\|A\|\|` | **L2 norm** (length) of A — √(sum of squares of components) |
| `\|\|B\|\|` | Length of B |

### Worked example — both vectors length 1

Suppose:

```text
A = [1, 0]
B = [0.8, 0.6]
```

Dot product:

```text
A · B = (1 × 0.8) + (0 × 0.6) = 0.8
```

Both have magnitude **1**, so:

```text
similarity = 0.8 / (1 × 1) = 0.8
```

### Dot product in 2D (lengths not 1)

```text
A = [1, 2]
B = [2, 3]

A · B = (1)(2) + (2)(3) = 2 + 6 = 8

||A|| = √(1² + 2²) = √5  ≈ 2.236
||B|| = √(2² + 3²) = √13 ≈ 3.606

cosine = 8 / (√5 × √13) ≈ 8 / 8.062 ≈ 0.992
```

Very high → A and B point almost the same way.

In RAG you do the same with **1536** numbers instead of 2 — formula unchanged, just more terms in the sums.

---

## 4. What the score means

Mathematically cosine ranges from **−1** to **+1**. For many practical text-embedding comparisons you mostly see values between **0** and **1**, but the full range is still the definition.

| Cosine similarity | Rough reading |
|-------------------|---------------|
| **~1.0** (+1) | Same direction — maximum similarity / very similar meaning |
| **~0.0** | Perpendicular — little directional similarity in that space |
| **~−1.0** | Opposite direction (less common in many embedding setups; you often see mostly positive scores) |

Important limits:

- The score is a **ranking signal**, not a probability that the chunk answers the question.  
- There is **no universal cutoff** like “> 0.8 means relevant” that works for every corpus and model.  
- You usually **sort** chunks by score and take **top-k** (and maybe apply a threshold you tune yourself).

---

## 5. How this works with AI embeddings (example)

Imagine semantic search / RAG with two support docs:

| | Text |
|--|------|
| **Document 1** | "How do I reset my password?" |
| **Document 2** | "How can I change my account password?" |

Wording differs; meaning is closely related.

```text
Document 1  →  embedding model  →  Vector A  [0.21, 0.73, ...]   (illustrative)
Document 2  →  embedding model  →  Vector B  [0.24, 0.69, ...]   (illustrative)
                                      ↓
                            cosine similarity(A, B)
                                      ↓
                         high score  →  treat as related
```

Exact scores depend on the model and real vectors — the floats above are **not** measured output.

This is how RAG retrieves relevant documents even when the user’s question does **not** share the same keywords as the stored text.

---

## 6. Cosine similarity vs cosine distance

Libraries and vector DBs sometimes talk about **distance** instead of similarity.

A common definition:

```text
cosine_distance(A, B)  =  1 − cosine_similarity(A, B)
```

| Measure | “Better” match means |
|---------|----------------------|
| **Cosine similarity** | **Higher** score |
| **Cosine distance** | **Lower** score |

Same geometry; flipped scale. When you read Chroma / FAISS / docs, check whether they return similarity or distance so you don’t sort the wrong way.

---

## 7. Dot product and normalized embeddings

**Normalized** means each vector is scaled so its length `||v|| = 1` (unit vector).

If both A and B are unit length:

```text
||A|| = 1,  ||B|| = 1

cosine(A, B)  =  (A · B) / (1 × 1)  =  A · B
```

So for **unit-normalized** embeddings, **dot product = cosine similarity**. Ranking by `np.dot(query, doc)` is enough.

OpenAI’s embedding API returns vectors that are **normalized by default**. That is why many tutorials (and your notes) say: for OpenAI embeddings, **dot product ranks like cosine**.

| Situation | What to compute |
|-----------|-----------------|
| OpenAI embeddings (default, normalized) | Dot product is fine for ranking |
| Vectors that may not be unit length | Full cosine: divide by `||A|| ||B||` |
| Mixing models / custom vectors | Do not assume normalization — check docs or compute norms |

---

## 8. Tiny Python example

These examples use **hand-made** 2D vectors — not real text embeddings. Goal: see the number **0.8** from section 3.

### Option A — NumPy

```bash
pip install numpy
```

```python
import numpy as np

def cosine_similarity(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

A = [1.0, 0.0]
B = [0.8, 0.6]
print(cosine_similarity(A, B))   # 0.8

doc = [1.0, 2.0]
query_close = [2.0, 3.0]
query_far = [-2.0, -1.0]
print("close:", round(cosine_similarity(doc, query_close), 4))
print("far:  ", round(cosine_similarity(doc, query_far), 4))
```

Expected idea: `close` near **1**, `far` much lower (here negative / opposite-ish direction).

### Option B — scikit-learn

```bash
pip install scikit-learn
```

```python
from sklearn.metrics.pairwise import cosine_similarity

A = [[1, 0]]
B = [[0.8, 0.6]]
score = cosine_similarity(A, B)
print(score[0][0])   # 0.8
```

`sklearn` expects **2D** arrays: one row per vector — that is why you write `[[1, 0]]` not `[1, 0]`.

### Already unit-normalized

```python
def cosine_via_dot_unit(a, b):
    return float(np.dot(a, b))  # only valid when ||a|| ≈ ||b|| ≈ 1
```

### With real OpenAI vectors

From [`embedding_demo.py`](./embedding_demo.py) you already know how to get one embedding. Embed two strings with the **same** model, then:

```python
score = float(np.dot(np.array(vec_a), np.array(vec_b)))  # ≈ cosine if normalized
```

---

## 9. How OpenAI fits in

You are learning OpenAI embeddings (`text-embedding-3-small`). Cosine similarity is what you (or a vector DB) use **after** you have vectors.

| Step | Action |
|------|--------|
| **1. Embed** | `client.embeddings.create(model="text-embedding-3-small", input=...)` — see [`embedding_demo.md`](./embedding_demo.md) |
| **2. Store** | Keep vectors in a vector DB (Chroma, FAISS, …) — [`6_vector_store.md`](./6_vector_store.md) |
| **3. Compare** | Cosine similarity (or equiv. inner product / distance) to find relevant content |

| Model | Job |
|-------|-----|
| `text-embedding-3-small` | Produce vectors |
| Cosine similarity | Compare those vectors |
| `gpt-4.1-nano` (chat) | Generate the final answer **after** retrieval |

**Remember:** embeddings represent text **numerically**; cosine similarity compares the **direction** of those numerical representations. GPT-nano does not replace the embedding model for this step.

---

## 10. How RAG uses this

```text
1. Embed each chunk        →  store vectors (vector DB)
2. Embed user question     →  query vector
3. Score every candidate   →  cosine (or equiv. distance / inner product)
4. Keep top-k chunks       →  highest similarity (or lowest distance)
5. Stuff chunks into prompt →  chat model answers
```

| Piece | Role |
|-------|------|
| Embedding model | Builds the vectors |
| Cosine (or equiv.) | Decides **which** chunks are nearest |
| Vector store | Stores vectors and runs this search efficiently (ANN indexes, not always brute-force) |
| Chat model | Writes the answer from retrieved text |

At small scale you can brute-force: loop all docs, compute cosine, sort. At large scale, Chroma/FAISS/etc. approximate nearest neighbors — same **idea**, faster **implementation**.

---

## 11. Common mistakes

| Mistake | Why it hurts |
|---------|----------------|
| Comparing vectors from **different** embedding models | Spaces don’t align; scores are meaningless |
| Treating cosine as “% correct” | It only ranks geometric closeness |
| Sorting **distance** as if it were **similarity** | Best match ends up at the wrong end of the list |
| Forgetting normalization when vectors are not unit length | Dot product alone can prefer longer vectors |
| Expecting a fixed global threshold | Thresholds are corpus- and model-specific; start with top-k |
| Using a **chat** model to “make embeddings” | Use `text-embedding-3-small` (or similar), then cosine |

---

## 12. Check your understanding

**Q1:** Cosine similarity between two embeddings is closest to measuring…

- A. How many words they share  
- B. How similar their **directions** are in vector space  
- C. How many tokens the chat model will generate  

**Q2:** For unit-normalized OpenAI embeddings, ranking by **dot product**…

- A. Is unrelated to cosine  
- B. Gives the **same ranking** as cosine similarity  
- C. Always equals exactly 0  

**Q3:** In a RAG app, what produces the vectors that cosine compares?

- A. `gpt-4.1-nano` alone  
- B. An **embedding** model such as `text-embedding-3-small`  
- C. Cosine similarity itself  

<details>
<summary>Answers</summary>

**Q1 → B.** Cosine is about angle / direction (semantic orientation), not keyword overlap.

**Q2 → B.** When `||A|| = ||B|| = 1`, cosine equals the dot product, so ranking matches.

**Q3 → B.** Embeddings create vectors; cosine only **compares** them; the chat model answers after retrieval.

</details>

**Next:** [`6_vector_store.md`](./6_vector_store.md) — where these scores are computed over a whole index.
