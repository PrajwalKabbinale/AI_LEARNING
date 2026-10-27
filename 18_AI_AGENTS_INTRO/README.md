# AI Agents intro

Chapter notes for **Souvik’s** AI learning journey (folder `18_AI_AGENTS_INTRO`).

Hands-on mini agent: an LLM **plans** which tool to use, Python **runs** that tool, then another LLM call **answers** the user.

Read in order:

1. **What is an AI Agent?** — [`1_what_is_ai_agent.md`](./1_what_is_ai_agent.md)  
2. **Code walkthrough** — [`tools.py`](./tools.py) · [`planner.py`](./planner.py) · [`assistant.py`](./assistant.py) · notes [`2_assistant_planner_tools.md`](./2_assistant_planner_tools.md)

Related earlier chapters:

- **Topic 5** — [`5_TOOLS_FUNCTIONS/README.md`](../5_TOOLS_FUNCTIONS/README.md): step **2** = keyword assistant ([`tool_functions_2.py`](../5_TOOLS_FUNCTIONS/tool_functions_2.py) — we compare to that in Topic 18); step **3** = OpenAI `tools=`  
- **Topic 6** — [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md): theory (workflows, frameworks)

---

## Quick start

```bash
pip install openai python-dotenv
```

`.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-nano
```

```bash
python assistant.py
```

Type `time`, `dice`, `password`, a normal question, then `quit` to exit.

---

## Files

| File | Role |
|------|------|
| [`1_what_is_ai_agent.md`](./1_what_is_ai_agent.md) | Theory — chatbot vs agent, brain + body |
| [`tools.py`](./tools.py) | Body — local helpers |
| [`planner.py`](./planner.py) | Brain (plan) — `choose_tool` |
| [`assistant.py`](./assistant.py) | Loop — entry point |
| [`2_assistant_planner_tools.md`](./2_assistant_planner_tools.md) | Full explanation + your sample session |
