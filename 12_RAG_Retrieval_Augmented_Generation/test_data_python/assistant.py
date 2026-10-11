import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import get_current_time, read_text_file

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL_NAME")

SUMMARIZE_SYSTEM = "You are a helpful assistant."

print("Commands: time/date | read <file> | summarize <file> | quit\n")

while True:
    user_input = input("\nYou : ").strip()
    text = user_input.lower()

    if "time" in text or "date" in text:
        print("\nAI :", get_current_time())
        continue

    if text.startswith("read"):
        filename = "notes.txt"
        print("\nAI :\n", read_text_file(filename))
        continue

    if text.startswith("summary"):
        filename = "notes.txt"
        file_content = read_text_file(filename)

        user_prompt = f"Summarize the following document.\n\nDocument:\n\n{file_content}"

        messages = [
            {
                'role': 'system', 
                'content': SUMMARIZE_SYSTEM
            }, 
            {
                'role': 'user',
                'content': user_prompt
            }
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        print("\nAI :", response.choices[0].message.content)
        continue

    if text == "quit":
        print("\nAI : Goodbye!")
        break

    print("\nAI : Try 'what time is it?', 'read notes.txt', 'summarize notes.txt', or 'quit'.")
