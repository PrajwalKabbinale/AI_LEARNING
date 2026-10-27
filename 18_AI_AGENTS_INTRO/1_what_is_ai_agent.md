# What is an AI Agent?

Chapter notes for **Souvik’s** AI learning journey (folder `18_AI_AGENTS_INTRO`).

An **AI Agent** is a system that uses an AI model (usually an **LLM**) to **reason**, **plan**, and **act** toward a **goal** — not only to write text back to you.

We call it an **agent** because it has **agency**: it can interact with an **environment** (clock, files, APIs, browsers, email, …) through **tools**, instead of only chatting.

Chapter index: [`README.md`](./README.md).  
Hands-on next: [`2_assistant_planner_tools.md`](./2_assistant_planner_tools.md).  
Longer theory + workflows/frameworks: [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md).

---

## Index

| Section | Topic |
|---------|--------|
| 1 | [Chatbot vs Agent](#1-chatbot-vs-agent-plain-english) |
| 2 | [Brain + Body](#2-brain--body) |
| 3 | [Core loop](#3-core-loop-what-agency-looks-like-in-code) |
| 4 | [What can an agent do?](#4-what-can-an-agent-do) |
| 5 | [How this chapter fits your path](#5-how-this-chapter-fits-your-learning-path) |
| 6 | [What this intro agent is not yet](#6-what-this-intro-agent-is-not-yet) |
| 7 | [Mental model](#7-mental-model-one-sentence) |
| 8 | [Next](#8-next) |

---

## 1. Chatbot vs Agent (plain English)

| | **Chatbot / plain LLM** | **AI Agent** |
|--|-------------------------|--------------|
| Main job | Generate text | Reach a **goal** |
| Sees | Your message (+ history) | Message + **what tools can do** + results |
| Acts? | No — words only | Yes — calls **tools** / APIs / code |
| Example | “Paris is the capital of France.” | “Get the time” → run `get_current_time()` → reply with real clock |

```text
Plain LLM:   You → LLM → text answer

Agent:       You → LLM (plan) → Tool (act) → LLM (speak) → text answer
                              ↑_________________|
                         (may loop for harder goals)
```

An LLM **alone** can only produce text. Apps like ChatGPT that “generate an image” or “browse” do that because developers attached **tools** the model can request.

---

## 2. Brain + Body

Think of the agent as two parts:

```text
Agent
├── Brain  → LLM (thinks / plans / decides)
└── Body   → Tools (do things in the world)
```

| Part | Role | In this folder |
|------|------|----------------|
| **Brain** | Reason about the request; choose next action | [`planner.py`](./planner.py) (`choose_tool`) + answer call in [`assistant.py`](./assistant.py) |
| **Body** | Run real actions (time, dice, password, …) | [`tools.py`](./tools.py) |
| **Loop** | Keep going until the goal (or you quit) | `while True` in [`assistant.py`](./assistant.py) |

- **Tool** = one capability (e.g. `roll_dice`)  
- **Agent** = the whole system that decides *when* to use tools and how to answer  

---

## 3. Core loop (what “agency” looks like in code)

Most agents follow some version of:

```text
1. Observe  — read the user request (and maybe prior results)
2. Plan     — decide: which tool, or answer directly?
3. Act      — run the tool / call an API
4. Speak    — turn the result into a natural reply
5. (Optional) Repeat until the goal is done
```

This chapter’s mini agent does **one** plan → act → speak cycle **per message** (simple on purpose). Bigger agents may loop many times, use many tools, or plan multi-step tasks.

Mapped to your code:

| Step | Code |
|------|------|
| Observe | `user_input = input(...)` in `assistant.py` |
| Plan | `choose_tool(user_input)` in `planner.py` |
| Act | `get_current_time()` / `roll_dice()` / `generate_password()` in `tools.py` |
| Speak | second `chat.completions.create(...)` in `assistant.py` |

---

## 4. What can an agent do?

Anything you expose as a **tool**. Examples:

| Goal | Typical tools |
|------|----------------|
| Personal assistant | calendar, email, local files |
| Customer support | FAQ search, ticket system, order API |
| Dev helper | run tests, open PRs, read repo |
| Research | web search, scrape, summarize docs |

Without tools, you only have a **chatbot**. With tools + a decision loop, you have an **agent**.

---

## 5. How this chapter fits your learning path

You already touched **tools** in **Topic 5** ([`5_TOOLS_FUNCTIONS/`](../5_TOOLS_FUNCTIONS/)). Topic 18 is the next step after **step 2** there:

| What we call it in notes | Where it is | Who picks the action? |
|--------------------------|-------------|------------------------|
| **Keyword routing** (Topic 5 **step 2**) | [`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py) + [`tools_2.py`](../5_TOOLS_FUNCTIONS/tools_2.py) — explained in [`tool_functions_2_and_tools_2.md`](../5_TOOLS_FUNCTIONS/tool_functions_2_and_tools_2.md) | **Your Python** — e.g. `if "time" in user_input.lower():` then call `get_current_time()` |
| **Planner mini agent (Topic 18 — here)** | [`2_assistant_planner_tools.md`](./2_assistant_planner_tools.md) | **Planner LLM** returns a tool name like `roll_dice` or `none` |
| **OpenAI tool calling** (Topic 5 **step 3**) | [`tool_functions_1.md`](../5_TOOLS_FUNCTIONS/tool_functions_1.md) | **Chat API** — model sends `tool_calls`; your code runs the function |
| **Agents theory** (Topic 6) | [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md) | Concepts — workflows, frameworks (mostly reading) |

**Why compare to step 2?** Same kind of demo (time, dice, terminal chat), but Topic 18 replaces brittle **keywords** with an LLM **planner** — closer to how people describe “agents.”

This folder is the **intro**: brain (planner) + body (tools) + a small orchestration loop — before frameworks (LangChain agents, etc.).

---

## 6. What this intro agent is *not* (yet)

| Not included | Why it matters later |
|--------------|----------------------|
| Multi-step plans | Hard goals need several tool calls in a row |
| Chat memory across turns | Agent “forgets” earlier messages unless you store them |
| OpenAI `tools=` schema | Production style of registering tools with the API |
| Guardrails / permissions | Real agents need limits on what tools may do |

Those are upgrades on the same idea: **LLM decides → code acts → LLM answers**.

---

## 7. Mental model (one sentence)

**An AI agent = LLM brain + tools body + a loop that uses both to pursue a user goal.**

---

## 8. Next

1. Finish this note.  
2. Run the demo: [`2_assistant_planner_tools.md`](./2_assistant_planner_tools.md) → `python assistant.py`.  
3. Deeper theory when you want it: [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md).  
4. After that: MCP — [`1_introduction.md`](../19_MCP_MODEL_CONTEXT_PROTOCOL/1_introduction.md) (Topic 19, read `1_` … `5_`).  
