# Tools in AI

Chapter notes for **Souvik’s** AI learning journey (folder `5_TOOLS_FUNCTIONS`).  
Hands-on in this folder (read in order):

1. **Plain Python functions** — [`helper_functions.py`](./helper_functions.py) · runner [`demo_helper_functions.py`](./demo_helper_functions.py) · notes [`helper_functions_and_demo.md`](./helper_functions_and_demo.md)  
2. **Personas + keyword shortcuts** — [`tools_2.py`](./tools_2.py) · [`tool_functions_2.py`](./tool_functions_2.py) · notes [`tool_functions_2_and_tools_2.md`](./tool_functions_2_and_tools_2.md)  
3. **LLM + OpenAI tools** — [`tool_functions_1.py`](./tool_functions_1.py) · [`tool_functions_1.md`](./tool_functions_1.md)

---

## What are “tools” in AI?

In everyday chat, an LLM mostly **predicts text**.

A **tool** (also called **function calling**) lets the model say:

> “I need outside help — please run this function with these arguments.”

Then **your code** runs that function (lookup a price, call an API, read a database, etc.) and sends the result back.  
The model uses that result to write the final answer.

So a tool is not magic inside the model.  
It is a **bridge** between the LLM and real-world actions / live data.

```text
User question
     ↓
LLM thinks: "I should use a tool"
     ↓
Your Python runs the tool
     ↓
LLM writes the final answer using the tool result
```

---

## Why tools matter

LLMs are strong at language, but weak at some things on their own:

| Without tools | With tools |
|---------------|------------|
| May **guess** a ticket price | Looks up the **real** price from your data |
| No access to your database / API | Can request your backend function |
| Knowledge can be outdated | Can use live or private information |
| Only talks | Can **act** (search, calculate, book, fetch) |

Example from this chapter:

User asks: `ticket price for paris ?`  
Model does not invent `$899`.  
It asks your tool `get_ticket_price`, your dictionary returns the price, then the model says it politely in chat.

---

## Tools vs normal chat (simple difference)

### Normal chat

```text
User → LLM → text answer
```

One path. Model answers from what it already “knows”.

### Chat with tools

```text
User → LLM → (maybe) tool request
              ↓
         your Python tool
              ↓
         LLM → final text answer
```

Sometimes **two** LLM calls:

1. decide / request tool  
2. write final answer after tool result  

---

## Important: the LLM does not run your Python

This confuses many beginners.

| Piece | What it is |
|-------|------------|
| `def get_ticket_price(...):` | Real Python you wrote and you execute |
| Tool schema (`price_function`) | A **description** so the LLM knows the tool exists |
| `tools=[...]` in the API call | Gives the model permission to **request** that tool |
| `handle_tool_call(...)` | Your glue code: read request → run function → format result |

The model only **asks**.  
You **do** the work.

---

## Everyday analogy

Think of a restaurant:

| Role | In AI tools |
|------|-------------|
| Customer | User |
| Waiter | LLM |
| Menu card | Tool schema (`price_function`) |
| Kitchen | Your Python function |
| Dish brought back | Tool result |
| Waiter presenting the dish | Second LLM reply to the user |

The waiter does not cook.  
The waiter reads the menu, asks the kitchen, then speaks to the customer.

---

## What kinds of tools can you build?

Almost anything your program can do. Here are practical examples:

### Travel / booking (this chapter)

| Tool idea | What it would do |
|-----------|------------------|
| `get_ticket_price(city)` | Look up flight price (your FlightAI demo) |
| `set_ticket_price(city, price)` | Update a price in a database |
| `check_seat_availability(flight_id)` | See if seats are left |
| `book_flight(city, date, name)` | Create a booking record |

### Everyday apps

| Tool idea | What it would do |
|-----------|------------------|
| `get_weather(city)` | Call a weather API |
| `get_current_time(timezone)` | Return accurate local time |
| `convert_currency(amount, from, to)` | Live FX conversion |
| `calculator(expression)` | Exact math (LLMs often miscount) |

### Work / productivity

| Tool idea | What it would do |
|-----------|------------------|
| `search_docs(query)` | Search company documents |
| `create_calendar_event(title, time)` | Add a meeting |
| `send_email(to, subject, body)` | Send a message |
| `create_jira_ticket(summary)` | Open a work item |

### Data / engineering

| Tool idea | What it would do |
|-----------|------------------|
| `run_sql(query)` | Read from a database (carefully!) |
| `fetch_url(url)` | Get webpage or API text |
| `list_files(folder)` | Show files on disk |
| `run_python(code)` | Execute a small code snippet (sandboxed) |

### Multi-tool example (how agents feel)

User: `Book me the cheapest flight to Paris next Friday and email me the price.`

An agent-style app might call tools in order:

1. `get_ticket_price("Paris")`  
2. `send_email(...)` with the result  

Same idea as your chapter — just more than one tool.

> Beginner tip: start with **one safe read-only tool** (like ticket price lookup).  
> Be careful with tools that write data, send email, or run code.

---

## Core vocabulary (chapter 5)

| Term | Plain meaning |
|------|----------------|
| **Tool / function calling** | LLM can request a function during a reply |
| **Tool schema** | JSON-like description of name, purpose, arguments |
| **`tools=`** | Argument you pass into OpenAI so tools are available |
| **`finish_reason='tool_calls'`** | Model wants a tool, not a final answer yet |
| **`role: 'tool'`** | Message that carries the tool’s result back |
| **`tool_call_id`** | Links one tool request to its result |

---

## How this chapter fits **Souvik’s** journey

So far in this repo:

1. What AI is  
2. Call OpenAI / Ollama  
3. System vs user prompts  
4. Tokens + chat memory  
5. Gradio UI  

Now:

6. **Tools** — let the chatbot use real Python for accurate actions/data  

This is a big step toward **agents**: models that can use tools step by step to solve tasks.

---

## Start here in this folder

| File | Purpose |
|------|---------|
| [`README.md`](./README.md) | This page — what tools mean in AI |
| [`tool_functions_1.py`](./tool_functions_1.py) | FlightAI chatbot + ticket price tool |
| [`tool_functions_1.md`](./tool_functions_1.md) | Every bit of the script + real Paris run prints |

Run:

```bash
python tool_functions_1.py
```

Try asking: `ticket price for paris ?`

---

## One-line takeaway

**Tools let an LLM ask your code for help — so answers can be accurate, live, and actionable, not only guessed text.**
