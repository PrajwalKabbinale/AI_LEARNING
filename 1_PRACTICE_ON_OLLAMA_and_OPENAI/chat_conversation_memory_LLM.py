from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

MODEL_NAME = "gpt-4.1-nano"

openai_api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)
messages = []
i = 1

while True:
    print("iteration :  ", i)

    print("\n---------- Conversation History ----------")

    for message in messages:
        print(message)

    print("------------------------------------------")

    user_input = input("\nYou : ")
    # Save the user's message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", MODEL_NAME),
        messages=messages,
    )

    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    # Save the AI's reply
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )

    i += 1
