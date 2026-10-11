# Introduction to RAG

**R**etrieval-**A**ugmented **G**eneration — chapter notes for **Souvik’s** AI learning journey (folder `12_RAG_Retrieval_Augmented_Generation`).

Related: [`what_is_an_llm.md`](../3_LLMs_and_TOKENS/what_is_an_llm.md) · [`README_LLM_STATELESS_NO_MEMORY.md`](../3_LLMs_and_TOKENS/README_LLM_STATELESS_NO_MEMORY.md) · [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md)

**Read in order:** `1_` → `8_` (this file is **1**). Note **6** fits best right after **3** (embeddings). Notes **7–8** continue retrieval metrics after **5**.

| # | Note | Topics |
|---|------|--------|
| 1 | **This file** | What an **FM** is, what RAG is, limits, vs fine-tuning |
| 2 | [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md) | Ingestion, retrieve, augment, generate; 6-step query flow |
| 3 | [`3_lm_types_and_embeddings.md`](./3_lm_types_and_embeddings.md) | Autoregressive vs autoencoding; embedding models for RAG |
| — | [`text_embedding_3_small.md`](./text_embedding_3_small.md) | Hands-on: OpenAI embeddings API + tiny semantic search (after note 3) |
| — | [`cosine_similarity.md`](./cosine_similarity.md) | How two embedding vectors are compared for ranking (before / with note 6) |
| 4 | [`4_building_rag_challenges.md`](./4_building_rag_challenges.md) | Operational challenges (freshness, scale, relevance, bias, metrics) |
| 5 | [`5_ragas_evaluation.md`](./5_ragas_evaluation.md) | RAGAS metrics: faithfulness, relevancy, context recall/precision |
| 6 | [`6_vector_store.md`](./6_vector_store.md) | What a vector store is, similarity search, popular tools, full RAG diagram |
| 7 | [`7_mrr_mean_reciprocal_rank.md`](./7_mrr_mean_reciprocal_rank.md) | MRR — how high the first relevant result ranks |
| 8 | [`8_recall_precision_at_k.md`](./8_recall_precision_at_k.md) | Recall@K & Precision@K — coverage vs relevance in top K |

---

## Index

| # | Topic |
|---|--------|
| 1 | [What is a foundation model (FM)?](#1-what-is-a-foundation-model-fm) |
| 2 | [What is RAG?](#2-what-is-rag) |
| 3 | [Foundation models and the knowledge gap](#3-foundation-models-and-the-knowledge-gap) |
| 4 | [What RAG does (enterprise view)](#4-what-rag-does-enterprise-view) |
| 5 | [In plain English](#5-in-plain-english) |
| 6 | [RAG vs fine-tuning](#6-rag-vs-fine-tuning) |
| 7 | [Important limits](#7-important-limits) |
| 8 | [Interview one-liner](#8-interview-one-liner) |

---

## 1. What is a foundation model (FM)?

If you have only used **ChatGPT** or **Gemini**, you may not have seen the term **FM** yet. In RAG docs (AWS, enterprise AI, this course), **FM** means **foundation model**.

### Plain English

A **foundation model** is a **large AI model trained once on a huge amount of data** so it learns general patterns (language, reasoning, sometimes images or audio). Teams then **reuse** that same model for many products — chatbots, copilots, classifiers — instead of training a brand-new model from scratch for every app.

**“Foundation”** = it is the **base layer**. You build on top with prompts, RAG, fine-tuning, or agents.

You do **not** retrain the FM every time a user asks a question. At runtime you usually **send a prompt** (via an API or local server) and the FM **generates** a reply using what it already learned in training.

### FM vs LLM vs GenAI (quick map)

| Term | One-line meaning |
|------|------------------|
| **Foundation model (FM)** | Broad, pretrained base model reused across tasks and apps |
| **LLM** | FM focused on **language** (text/code in, text out) — what most chat apps use |
| **Generative AI (GenAI)** | AI that **creates** new content; many GenAI apps sit **on top of** an LLM-style FM |

Most RAG tutorials use an **LLM as the FM** that writes the final answer. The **embedding** model used for search is often a **smaller** FM (encoder-style) — see [`3_lm_types_and_embeddings.md`](./3_lm_types_and_embeddings.md).

Deeper background: [`what_is_an_llm.md`](../3_LLMs_and_TOKENS/what_is_an_llm.md) · [`10_generative_ai_and_inference.md`](../0_WHAT_IS_AI/10_generative_ai_and_inference.md)

### Examples you may already know

| Product / model family | Role as an FM |
|------------------------|----------------|
| **GPT-4** (OpenAI) | Text/chat foundation behind many apps |
| **Claude** (Anthropic) | Same idea — general-purpose language FM |
| **Gemini** (Google) | Multimodal FM (text and more) |
| **Llama** (Meta) | Open-weight FM you can run or host yourself |
| **DALL·E**, **Stable Diffusion** | FMs for **images** (not the usual RAG chat path, but still “foundation” models) |

**Layman:** the FM is the **engine**; ChatGPT is a **car** built around that engine. **RAG** adds a **GPS + document folder** so the engine answers using **your** maps, not only what it memorized in driving school (pretraining).

### What the FM “knows”

Whatever was in its **training data** (public web, books, licensed corpora, etc.) up to a **training cutoff**. It does **not** automatically know your private wiki, today’s stock price, or this morning’s incident ticket unless you **give** that information in the prompt (RAG does that for you at scale).

---

## 2. What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that **enhances a foundation model** by pulling in knowledge from **external sources** before the FM writes an answer.

RAG **does not retrain** the whole FM. It **retrieves** relevant text at query time, **augments** the prompt with that context, then **generates** a response — so output can be more **relevant, accurate, and appropriate** to the situation.

---

## 3. Foundation models and the knowledge gap

| FM strength | FM limitation |
|-------------|----------------|
| General language, reasoning patterns | Training data can be **limited or outdated** for your use case |
| Strong at many tasks out of the box | No built-in access to **internal** wikis, tickets, or live databases |
| Fast to deploy via API | **Hallucination** when it guesses facts it never saw |

RAG bridges the gap: the FM stays the **generator**; **authoritative** content lives in sources **you** control (APIs, databases, document repos, vector stores).

---

## 4. What RAG does (enterprise view)

1. A **retriever** finds relevant passages from an **external data store** (often a **vector database** filled with your enterprise data).
2. Retrieved text becomes **context** combined with the user’s prompt → an **expanded prompt**.
3. The **language model** generates an answer that can incorporate that **enterprise knowledge**.

Benefits often cited in production:

- **Cost-effective** way to tailor FMs to a **domain** or **internal knowledge base** without full retraining.
- **Trust** — answers can be grounded in **pre-determined, authoritative** sources (when retrieval is good).
- **Freshness** — when data changes, you **update the index**; the FM weights can stay **static** while retrieval uses newer embedded content.

For architecture detail, see [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md).

---

## 5. In plain English

The **FM / LLM** alone is like a **very well-read person with no access to your company folder**.

**RAG** = before the model answers:

1. **Search** your knowledge (docs, HR policies, product catalog, …)
2. **Paste** the best matching pieces into the prompt
3. **Generate** an answer using that context

Facts come from **retrieval** + **generation**, not from hoping the model memorized your handbook.

---

## 6. RAG vs fine-tuning

| | **RAG** | **Fine-tuning** |
|---|---------|-----------------|
| **When** | Facts change often; many documents | Stable style, format, or behavior in weights |
| **Update path** | Re-ingest / re-embed documents | New training run |
| **Cost** | Often cheaper for changing knowledge | Higher for repeated full fine-tunes |
| **Typical combo** | RAG for knowledge + prompts | Both together in real products |

**Layman:** RAG = “look it up, then answer.” Fine-tuning = “memorize the handbook in the weights.”

---

## 7. Important limits

1. **Retrieval scope** — search is only over what you **embedded into the vector store** at ingest time (not the whole internet unless you wired that in).
2. **Static generator** — the FM weights are unchanged; quality depends on **retrieval + prompting**.
3. **Latency** — large retrieved context + big context windows can **slow** responses and increase cost (more tokens per request).
4. **Wrong retrieval** — if the retriever misses or picks bad chunks, the FM can still sound confident but be wrong (see [`4_building_rag_challenges.md`](./4_building_rag_challenges.md) and [`5_ragas_evaluation.md`](./5_ragas_evaluation.md)).

RAG is **versatile** anywhere you need **context-specific, well-informed** outputs (support, legal, HR, engineering runbooks, e-commerce catalogs, etc.).

---

## 7. Interview one-liner

> **“RAG augments a foundation model with retrieved context from external knowledge — retrieve, augment the prompt, then generate — so answers can use private or up-to-date data without retraining the whole model.”**

---

## References

- Lewis et al., [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
