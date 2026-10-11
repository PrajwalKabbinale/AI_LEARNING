# Welcome to the learning journey with **Souvik**

This is **Souvik’s** personal AI learning space — notes, practice scripts, and small experiments while exploring LLMs, prompts, Gradio, and more.

---

## Why people should read this

If you are new to AI and feel lost in big words, this journey is for you.

**Souvik** is learning AI the practical way — not only theory, but small programs you can run, break, and understand. Each folder builds on the last:

- start with *what AI even is*
- make your first real LLM calls (cloud + local)
- learn how prompts work
- understand tokens and how chat “memory” really works
- build simple Gradio UIs and chatbots
- teach the LLM to use **tools** (real Python functions) for accurate answers
- understand **AI Agents** — brain (LLM) + body (tools) working toward a goal
- explore **Hugging Face** — open models, Hub, transformers, Spaces
- use **Google Colab** — cloud notebooks + GPUs for heavier model experiments
- learn **quantization** — load big models with fewer bits (8-bit / 4-bit)
- try **audio transcription** — free HF Whisper vs paid OpenAI API
- use **RAG** — ground LLM answers in your own documents (retrieval + generation)
- learn **LangChain** — models, prompts, indexes, memory, chains, and agents
- understand **datasets** — what they are, train/val/test, Kaggle, and RAG evaluation
- practice **model fine-tuning** — specialize a pre-trained LLM on a small task dataset
- learn **LoRA** — efficient fine-tuning with small adapter weights (and **QLoRA** with quantization)
- use **Modal** — run Python and GPU workloads in the cloud from your code

These notes are written in plain language, with step-by-step explanations, so beginners can follow along without fear.  
If **Souvik** can learn it this way, you can too.

---

## Index

| # | Topic | What’s inside |
|---|--------|----------------|
| 0 | [`0_WHAT_IS_AI`](0_WHAT_IS_AI/) | Basics — what AI / ML / DL / generative AI mean |
| 1 | [`1_PRACTICE_ON_OLLAMA_and_OPENAI`](1_PRACTICE_ON_OLLAMA_and_OPENAI/) | First API calls — OpenAI cloud + local Ollama; chat `role`s + memory |
| 2 | [`2_USER_PROMPT_SYSTEM_PROMPT`](2_USER_PROMPT_SYSTEM_PROMPT/) | System prompt vs user prompt |
| 3 | [`3_LLMs_and_TOKENS`](3_LLMs_and_TOKENS/) | What an LLM is, features, tokens, stateless calls |
| 4 | [`4_GRADIO`](4_GRADIO/) | Gradio UIs + chatbot with chat history |
| 5 | [`5_TOOLS_FUNCTIONS`](5_TOOLS_FUNCTIONS/) | LLM tools / function calling (FlightAI ticket price) |
| 6 | [`6_AGENTS_AND_TOOLS`](6_AGENTS_AND_TOOLS/) | AI Agents, workflow patterns, frameworks, tools theory |
| 7 | [`7_HUGGING_FACE`](7_HUGGING_FACE/) | Hugging Face — Hub, pipelines, Spaces |
| 8 | [`8_GOOGLE_COLAB`](8_GOOGLE_COLAB/) | Google Colab — cloud notebooks, GPUs, secrets |
| 9 | [`9_QUANTIZATION`](9_QUANTIZATION/) | Quantization — 8-bit / 4-bit, BitsAndBytes |
| 10 | [`10_AUDIO_TRANSCRIPTION`](10_AUDIO_TRANSCRIPTION/) | Audio → text — free HF Whisper vs paid OpenAI |
| 11 | [`11_PYTHON_CPP_CODE_CONVERSION`](11_PYTHON_CPP_CODE_CONVERSION/) | LLM ports Python → C++ (prompt + save `.cpp`) |
| 12 | [`12_RAG_Retrieval_Augmented_Generation`](12_RAG_Retrieval_Augmented_Generation/) | RAG — read `1_` … `8_` (start [`1_introduction_to_rag.md`](12_RAG_Retrieval_Augmented_Generation/1_introduction_to_rag.md)) |
| 13 | [`13_LANGCHAIN`](13_LANGCHAIN/) | LangChain — read `1_` … `10_` (start [`1_introduction_to_langchain.md`](13_LANGCHAIN/1_introduction_to_langchain.md)) |
| 14 | [`14_DATASETS`](14_DATASETS/) | Datasets — start [`1_what_is_a_dataset.md`](14_DATASETS/1_what_is_a_dataset.md) |
| 15 | [`15_MODEL_FINE_TUNING`](15_MODEL_FINE_TUNING/) | Fine-tuning — start [`1_fine_tuning_in_llm.md`](15_MODEL_FINE_TUNING/1_fine_tuning_in_llm.md) |
| 16 | [`16_LORA`](16_LORA/) | LoRA / QLoRA — read `1_` … `3_` in [`16_LORA/`](16_LORA/) |
| 17 | [`17_MODAL`](17_MODAL/) | Modal — start [`1_what_is_modal.md`](17_MODAL/1_what_is_modal.md) |

### Topic 1 highlight

- Notes: [`chat_message_roles.md`](1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_message_roles.md) — `system` / `user` / `assistant` in the Chat API  
- Scripts: [`Test_OPENAI_LLM_with_openAI.py`](1_PRACTICE_ON_OLLAMA_and_OPENAI/Test_OPENAI_LLM_with_openAI.py) · [`Test_ollama_with_OPENAI.py`](1_PRACTICE_ON_OLLAMA_and_OPENAI/Test_ollama_with_OPENAI.py) · [`chat_conversation_memory_LLM.py`](1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_conversation_memory_LLM.py)  

### Topic 5 highlight

- Chapter intro: [`5_TOOLS_FUNCTIONS/README.md`](5_TOOLS_FUNCTIONS/README.md) — what tools mean in AI  
- Step 1: [`helper_functions_and_demo.md`](5_TOOLS_FUNCTIONS/helper_functions_and_demo.md) — plain Python helpers + `demo_helper_functions.py`  
- Step 2: [`tool_functions_2_and_tools_2.md`](5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) — personas, chat memory, keyword → `tools_2.py`  
- Step 3: [`tool_functions_1.py`](5_TOOLS_FUNCTIONS/tool_functions_1.py) · [`tool_functions_1.md`](5_TOOLS_FUNCTIONS/tool_functions_1.md) — OpenAI `tools=`, Gradio FlightAI  

### Topic 6 highlight

- Notes: [`agents_and_tools.md`](6_AGENTS_AND_TOOLS/agents_and_tools.md) — what is an Agent, workflow vs agent patterns, frameworks, LLM brain, tools theory  

### Topic 7 highlight

- Notes: [`what_is_huggingface.md`](7_HUGGING_FACE/what_is_huggingface.md) — Hugging Face Hub, `pipeline`, Spaces, inference APIs, create `HF_TOKEN`  
- Scripts: [`test_hugging_face_using_huggingFaceHUB.py`](7_HUGGING_FACE/test_hugging_face_using_huggingFaceHUB.py) · [`test_hugging_face_using_OPENAI.py`](7_HUGGING_FACE/test_hugging_face_using_OPENAI.py)  
- Script notes: [`test_hugging_face_using_huggingFaceHUB.md`](7_HUGGING_FACE/test_hugging_face_using_huggingFaceHUB.md) · [`test_hugging_face_using_OPENAI.md`](7_HUGGING_FACE/test_hugging_face_using_OPENAI.md)  
- Practice: [`colab_pipelines_explained.ipynb`](7_HUGGING_FACE/colab_pipelines_explained.ipynb) · [`colab_tokenizers_explained.ipynb`](7_HUGGING_FACE/colab_tokenizers_explained.ipynb)  

### Topic 8 highlight

- Notes: [`what_is_google_colab.md`](8_GOOGLE_COLAB/what_is_google_colab.md) — free tier limits, how to check GPU/usage, Colab vs local  
- Practice: [`colab_openai_and_hf.ipynb`](8_GOOGLE_COLAB/colab_openai_and_hf.ipynb) — OpenAI cloud vs Hugging Face router (same `openai` package)  

### Topic 9 highlight

- Notes: [`what_is_quantization.md`](9_QUANTIZATION/what_is_quantization.md) — fewer bits per weight, BitsAndBytesConfig, double quant, path to QLoRA  
- Practice: [`colab_quantization_explained.ipynb`](9_QUANTIZATION/colab_quantization_explained.ipynb) — Colab GPU 4-bit load + generate  

### Topic 10 highlight

- Practice: [`colab_audio_transcription.ipynb`](10_AUDIO_TRANSCRIPTION/colab_audio_transcription.ipynb) — free HF Whisper vs paid `gpt-4o-mini-transcribe`  

### Topic 11 highlight

- Script: [`python_code_to_CPP_code_Conversion.py`](11_PYTHON_CPP_CODE_CONVERSION/python_code_to_CPP_code_Conversion.py)  
- Notes: [`python_code_to_CPP_code_Conversion.md`](11_PYTHON_CPP_CODE_CONVERSION/python_code_to_CPP_code_Conversion.md)  

### Topic 12 highlight

- Read in order **`1_` → `8_`** in [`12_RAG_Retrieval_Augmented_Generation/`](12_RAG_Retrieval_Augmented_Generation/)  
- [`1_introduction_to_rag.md`](12_RAG_Retrieval_Augmented_Generation/1_introduction_to_rag.md) — what an **FM** is, what RAG is, knowledge gap, vs fine-tuning  
- Script: [`keyword_rag_gradio_chat.py`](12_RAG_Retrieval_Augmented_Generation/keyword_rag_gradio_chat.py) · Notes: [`keyword_rag_gradio_chat.md`](12_RAG_Retrieval_Augmented_Generation/keyword_rag_gradio_chat.md) — dictionary keyword RAG + Gradio chat  
- [`2_rag_architecture_and_workflow.md`](12_RAG_Retrieval_Augmented_Generation/2_rag_architecture_and_workflow.md) — ingest, retrieve, augment, generate; 6-step query flow  
- [`3_lm_types_and_embeddings.md`](12_RAG_Retrieval_Augmented_Generation/3_lm_types_and_embeddings.md) — autoregressive vs autoencoding; BERT / OpenAI embeddings  
- Hands-on: [`text_embedding_3_small.md`](12_RAG_Retrieval_Augmented_Generation/text_embedding_3_small.md) · [`embedding_demo.py`](12_RAG_Retrieval_Augmented_Generation/embedding_demo.py) · [`embedding_demo.md`](12_RAG_Retrieval_Augmented_Generation/embedding_demo.md) — OpenAI embeddings API first vector  
- [`cosine_similarity.md`](12_RAG_Retrieval_Augmented_Generation/cosine_similarity.md) — compare embedding vectors; cosine vs distance; why dot product works when normalized  
- [`4_building_rag_challenges.md`](12_RAG_Retrieval_Augmented_Generation/4_building_rag_challenges.md) — freshness, scale, relevance, bias, metrics; Bedrock KB note  
- [`5_ragas_evaluation.md`](12_RAG_Retrieval_Augmented_Generation/5_ragas_evaluation.md) — faithfulness, answer relevancy, context recall/precision  
- [`6_vector_store.md`](12_RAG_Retrieval_Augmented_Generation/6_vector_store.md) — embeddings storage, similarity search, popular vector DBs, full RAG diagram  
- [`7_mrr_mean_reciprocal_rank.md`](12_RAG_Retrieval_Augmented_Generation/7_mrr_mean_reciprocal_rank.md) — MRR — rank of first relevant result  
- [`8_recall_precision_at_k.md`](12_RAG_Retrieval_Augmented_Generation/8_recall_precision_at_k.md) — Recall@K & Precision@K  


### Topic 13 highlight

- Read in order **`1_` → `10_`** in [`13_LANGCHAIN/`](13_LANGCHAIN/) — note number matches filename (`5_` = note 5 of 10)
- [`1_introduction_to_langchain.md`](13_LANGCHAIN/1_introduction_to_langchain.md) — what LangChain is, components, chains, LCEL (light touch)
- [`4_langchain_vs_langgraph.md`](13_LANGCHAIN/4_langchain_vs_langgraph.md) — toolbox vs graph orchestration
- [`6_indexes_loaders_retrievers_vector_stores.md`](13_LANGCHAIN/6_indexes_loaders_retrievers_vector_stores.md) — loaders, retrievers, vector stores (RAG path)
- [`9_agents.md`](13_LANGCHAIN/9_agents.md) — agents as reasoning + tools  
- [`10_embeddings_and_vector_store.md`](13_LANGCHAIN/10_embeddings_and_vector_store.md) — chunk → embedding → Chroma
- Practice: [`rag_langchain_chunks_vector_db_visualization.ipynb`](13_LANGCHAIN/rag_langchain_chunks_vector_db_visualization.ipynb) — chunk → embed → Chroma → t-SNE (`13_LANGCHAIN/knowledge-base/`)
- Practice: [`rag_langchain_retriever_qa_gradio.ipynb`](13_LANGCHAIN/rag_langchain_retriever_qa_gradio.ipynb) — retrieve from that Chroma DB → LLM Q&A + Gradio

### Topic 14 highlight

- Notes: [`1_what_is_a_dataset.md`](14_DATASETS/1_what_is_a_dataset.md) — data vs dataset, rows/columns, train/val/test, **data curation**, labeled vs unlabeled, Kaggle, RAG evaluation (Recall@K / Precision@K / MRR)
- Script: [`amazon_appliances_dataset_simple.py`](14_DATASETS/amazon_appliances_dataset_simple.py) — load → filter price → train/val/test
- Script notes: [`2_amazon_appliances_dataset_simple.md`](14_DATASETS/2_amazon_appliances_dataset_simple.md) — line-by-line explanation of that script
- Scripts: [`working_with_DATASET.py`](14_DATASETS/working_with_DATASET.py) + [`items.py`](14_DATASETS/items.py) — HF load → `Item` objects → training/test prompts
- Script notes: [`3_working_with_dataset_and_items.md`](14_DATASETS/3_working_with_dataset_and_items.md) — explain both files together
- Script: [`preprocess_product_with_llm_simple.py`](14_DATASETS/preprocess_product_with_llm_simple.py) — Day 2 idea: rewrite one product with an LLM
- Script notes: [`4_preprocess_product_with_llm_simple.md`](14_DATASETS/4_preprocess_product_with_llm_simple.md) — pre-processing vs training; Ollama/Groq

### Topic 15 highlight

- Notes: [`1_fine_tuning_in_llm.md`](15_MODEL_FINE_TUNING/1_fine_tuning_in_llm.md) — what LLM fine-tuning is; RAG = knowledge at inference, FT = behavior; when to combine them
- Practice: [`simple_finetune.ipynb`](15_MODEL_FINE_TUNING/simple_finetune.ipynb) — products → chat messages → JSONL → optional OpenAI job
- Sample data: [`jsonl_simple/`](15_MODEL_FINE_TUNING/jsonl_simple/)

### Topic 16 highlight

- Notes: [`1_what_is_lora.md`](16_LORA/1_what_is_lora.md) — PEFT, LoRA formula, rank/alpha, when to combine with RAG  
- Notes: [`2_what_is_qlora.md`](16_LORA/2_what_is_qlora.md) — 4-bit base + LoRA adapters, LoRA vs QLoRA, RAG + QLoRA, open models  
- Notes: [`3_hyperparameters.md`](16_LORA/3_hyperparameters.md) — hyperparameters vs parameters; `n_epochs`, `batch_size`, common training knobs  
- Practice: [`prepare_sft_prompt_data.ipynb`](16_LORA/prepare_sft_prompt_data.ipynb) — build prompt/completion pairs for LoRA/SFT (tokenizer, cutoffs, Hub) with line-by-line notes

### Topic 17 highlight

- Notes: [`1_what_is_modal.md`](17_MODAL/1_what_is_modal.md) — what Modal is, install/auth, `.local()` vs `.remote()`, secrets, GPUs, vs Colab  
- Script: [`hello.py`](17_MODAL/hello.py) · Notes: [`2_hello_py.md`](17_MODAL/2_hello_py.md) — Modal `App`, `Image`, `@app.function`  
- Script: [`TEST_MODAL.py`](17_MODAL/TEST_MODAL.py) · Notes: [`3_test_modal_py.md`](17_MODAL/3_test_modal_py.md) — `.env` tokens, `local()` vs `remote()` smoke test  
- Script: [`llama.py`](17_MODAL/llama.py) · Notes: [`4_llama_py.md`](17_MODAL/4_llama_py.md) — easy **Llama 3.2 3B Instruct** Q&A on Modal (no LoRA)  
- Script: [`TEST_MODAL_LLAMA.py`](17_MODAL/TEST_MODAL_LLAMA.py) · Notes: [`5_test_modal_llama_py.md`](17_MODAL/5_test_modal_llama_py.md) — run Llama via `generate.remote()` (see [`4_llama_py.md`](17_MODAL/4_llama_py.md))

### Extra notes

- [`OpenAI_API_vs_ChatGPT_subscription.md`](OpenAI_API_vs_ChatGPT_subscription.md) — API billing vs ChatGPT plans  
- [`Ollama_install_linux.md`](Ollama_install_linux.md) — install and run Ollama on Linux  
- [`3_LLMs/LLM_comparison_overview.md`](3_LLMs/LLM_comparison_overview.md) — closed vs open model families (from remote)  

## Run (this laptop)

```bash
source ~/miniforge3/bin/activate
conda activate my-proj
cd /home/soudas/PERSONAL/AI_LEARNING/AI_LEARNING
```

Keep secrets in `.env` at this repo root (`OPENAI_API_KEY=<your_openai_api_key_here>`). It is gitignored.
