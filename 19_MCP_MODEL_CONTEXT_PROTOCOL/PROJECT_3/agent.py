import asyncio
import os

from dotenv import load_dotenv
from openai import OpenAI

from planner import *

from mcp_client import *

# Load configuration
load_dotenv()
# Create AI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL=os.getenv("OPENAI_MODEL")

def answer_user(user_request, tool_output):
    prompt = f"""
    The user asked:
    {user_request}
    The tool returned:
    {tool_output}
    Answer the user naturally. Use only what the tool returned.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

async def main():
    mcp = await connect()
    tools = await discover_tools(mcp)
    print()
    print("Available Tools")
    print("----------------")
    for tool in tools:
        print(tool.name)
    print()
    user_request = input("User : ")
    tool_name = choose_tool(user_request, tools)
    print()
    print("Planner Selected:", tool_name)
    result = await execute_tool(mcp, tool_name)
    tool_output = result.content[0].text
    print("Tool output:", tool_output)
    print()
    reply = answer_user(user_request, tool_output)
    print("AI :", reply)
    await disconnect(mcp)

if __name__ == "__main__":
    asyncio.run(main())
