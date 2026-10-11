# Vector store

Chapter notes (folder `12_RAG_Retrieval_Augmented_Generation`).

**Read order:** `6` of `8` — best after [`3_lm_types_and_embeddings.md`](./3_lm_types_and_embeddings.md) (what embeddings are) and [`cosine_similarity.md`](./cosine_similarity.md) (how “closest” is scored); ties to [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md) retrieve phase. Evaluation continues in notes **5**, then **7–8**.

Related: [`6_indexes_loaders_retrievers_vector_stores.md`](../13_LANGCHAIN/6_indexes_loaders_retrievers_vector_stores.md) · [`4_langchain_vs_langgraph.md`](../13_LANGCHAIN/4_langchain_vs_langgraph.md)

---

A **vector store** is a database or system that stores **embeddings** and finds items that are **semantically similar** efficiently.

It is one of the core components of **RAG (Retrieval-Augmented Generation)**.

---

## Simple example

Suppose you have these documents:

```text
doc1: "Red Hat OpenShift is a Kubernetes platform."
doc2: "Kubernetes manages containerized workloads."
doc3: "Bangalore is the capital of Karnataka."
```

An embedding model converts them into vectors:

```text
doc1 → [0.21, -0.43, 0.87, ...]
doc2 → [0.19, -0.39, 0.82, ...]
doc3 → [-0.72, 0.15, -0.31, ...]
```

You store those vectors in a **vector store**.

The user asks:

> What does OpenShift use to manage containers?

The question is also converted into an embedding:

```text
Question → [0.20, -0.41, 0.84, ...]
```

The vector store searches for vectors **closest** (most similar) to the question embedding. It might retrieve **doc1** and **doc2**.

Then the LLM gets those documents as context:

```text
Question
   +
Retrieved documents
   ↓
   LLM
   ↓
Answer
```

That retrieval step is the heart of **RAG**.

---

## Vector store vs normal database

A traditional database might search:

```sql
WHERE keyword = 'OpenShift'
```

A vector store searches by **meaning**.

For example, the question:

> What technology does OpenShift use for containers?

can retrieve:

> Kubernetes manages containerized workloads.

even when the exact words do not match.

---

## Popular vector stores

You will often see:

| Name | Notes |
|------|--------|
| **FAISS** | Meta; popular for local experimentation |
| **Chroma** | Common for local RAG projects |
| **Pinecone** | Managed vector database |
| **Milvus** | Open-source vector database |
| **Weaviate** | Vector database with tooling |
| **Qdrant** | Open-source vector search |
| **pgvector** | Vector search inside PostgreSQL |
| **Elasticsearch** | Traditional search + vector search |

Pick based on scale, ops burden (managed vs self-hosted), and how you already store data.

---

## Complete GenAI / RAG picture

Worth remembering end-to-end:

```text
                 Documents
                     ↓
              Chunking
                     ↓
             Embedding Model
                     ↓
                Vector Store
                     ↑
                     │
User Question → Embedding
                     ↓
              Similarity Search
                     ↓
              Relevant chunks
                     ↓
                   LLM
                     ↓
                  Answer
```

| Piece | Role |
|-------|------|
| **Embedding** | Converts text → vectors |
| **Vector store** | Stores and searches those vectors |
| **RAG** | Retrieves relevant information and gives it to the LLM |

**LangGraph** (optional) can sit above this stack to orchestrate richer agent workflows — retrieve, re-query, call tools, loop — while the vector store still holds your knowledge.
