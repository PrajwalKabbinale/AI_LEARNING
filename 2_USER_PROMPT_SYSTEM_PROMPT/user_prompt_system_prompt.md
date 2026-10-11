# User Prompt & System Prompt — Website Summarizer

Explains [`user_prompt_system_prompt.py`](./user_prompt_system_prompt.py): a small learning script that scrapes a webpage, then asks an OpenAI model for a snarky markdown summary.

For **`role`** (`system` / `user` / `assistant`) in the Chat API, see [`../1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_message_roles.md`](../1_PRACTICE_ON_OLLAMA_and_OPENAI/chat_message_roles.md).

## What this script teaches

1. Loading secrets from a `.env` file (`OPENAI_API_KEY`, `MODEL_NAME`)
2. Fetching and cleaning webpage text (no LLM yet)
3. Building a **system prompt** vs **user prompt**
4. Calling the OpenAI Chat Completions API with those messages

## Prerequisites

- Conda env with packages installed (`openai`, `python-dotenv`, `beautifulsoup4`, `requests`)
- A `.env` file in the parent folder (`AI_LEARNING/`) with:

```env
OPENAI_API_KEY=sk-proj-...
MODEL_NAME=gpt-4.1-mini
```

Run from the folder that contains `.env` so `load_dotenv()` finds it:

```bash
cd /path/to/AI_LEARNING
python 2_USER_PROMPT_SYSTEM_PROMPT/user_prompt_system_prompt.py
```

## How the script flows

```
.env (API key + model)
        │
        ▼
┌───────────────────────────────┐
│ Part 1 — NO LLM               │
│ fetch_website_contents(url)   │
│ print raw title + body text   │
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│ Part 2 — LLM CALL             │
│ system_prompt + user_prompt   │
│ → messages_for(website)       │
│ → summarize(url) → OpenAI     │
│ print markdown summary        │
└───────────────────────────────┘
```

### Part 1 — scrape only (no LLM)

**Why Part 1 exists:** Before calling an LLM, we want to *see* the raw website text ourselves — and to check that **`fetch_website_contents` works** and that **BeautifulSoup is parsing/cleaning HTML correctly**. If the scrape is messy (nav junk, empty body, wrong page), the summary will be bad — and we would wrongly blame the model. Part 1 proves the pipeline works with **zero API cost**: fetch → clean → print.

`fetch_website_contents(url)`:

1. `GET`s the URL with a browser-like `User-Agent` (`requests`)
2. Parses HTML with BeautifulSoup
3. Removes noisy tags (`script`, `style`, `img`, `input`)
4. Returns `title + body text`, truncated to **2,000 characters**

The Harry Potter homepage is printed so you can see the raw input the model will later receive.

### Part 2 — system prompt + user prompt + LLM

**Why Part 2 exists:** Now that we trust the scraped text, we hand it to the model. Part 2 is where **system prompt** (personality + format) and **user prompt** (task + website contents) come together, get wrapped into OpenAI `messages`, and produce the snarky markdown summary. Separating it from Part 1 makes it clear what is “just scraping” vs “actual LLM work.”

| Piece | Role |
|--------|------|
| **System prompt** | Sets *who* the model is and *how* it should answer (snarky, short, markdown, ignore nav junk) |
| **User prompt** | Gives the *task* + the website text to summarize |
| **`messages_for(website)`** | Builds the OpenAI `messages` list: `[{system}, {user}]` |
| **`summarize(url)`** | Scrapes again, calls Chat Completions with `MODEL_NAME`, returns the reply |

The script prints the messages payload, then the model’s markdown summary.

## About BeautifulSoup (`bs4`)

**BeautifulSoup** turns raw HTML (a big messy string) into a tree you can query — titles, body text, tags to remove, etc.

In this script it is used like this:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.content, "html.parser")
title = soup.title.string if soup.title else "No title found"
# drop noisy tags, then pull readable text from <body>
for irrelevant in soup.body(["script", "style", "img", "input"]):
    irrelevant.decompose()
text = soup.body.get_text(separator="\n", strip=True)
```

| Piece | Role |
|--------|------|
| **`BeautifulSoup(html, "html.parser")`** | Parse the downloaded page into a searchable soup object |
| **`soup.title`** | Grab the page `<title>` |
| **`decompose()`** | Delete tags we do not want (scripts, styles, images, inputs) |
| **`get_text(...)`** | Flatten the remaining body into plain text for the LLM |

Install name vs import name:

- Install: `pip install beautifulsoup4` (or conda equivalent)
- Import: `from bs4 import BeautifulSoup`

`requests` fetches the bytes; BeautifulSoup **understands** the HTML. Without it you would be stuck regex-ing markup.

## System prompt vs user prompt (quick mental model)

- **System** = standing instructions / personality / format rules  
- **User** = this turn’s input (here: “summarize this site” + scraped text)

Together they become the chat `messages` array sent to the API.

## Key functions

| Function | What it does |
|----------|----------------|
| `fetch_website_contents(url)` | Scrape + clean + truncate page text |
| `messages_for(website)` | Wrap system + user prompts into API message format |
| `summarize(url)` | Scrape → messages → OpenAI → summary string |

## Things to experiment with

- Change the last line of the system prompt (e.g. respond in Spanish)
- Point `summarize(...)` at a different URL
- Swap `MODEL_NAME` in `.env` and compare tone / cost / quality
- Shorten or expand the 2,000-character scrape limit

## Note

The Harry Potter URL is fetched twice on purpose (once in Part 1 for display, once inside `summarize`). That is fine for learning; in production you would scrape once and reuse the text.
