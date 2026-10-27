from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL=os.getenv("OPENAI_MODEL")

def build_tool_descriptions(tools):
    lines = []
    for index, tool in enumerate(tools, start=1):
        description = (tool.description or "No description.").strip()
        print("tool.name")
        print(tool.name)
        print("--------------------------------")
        print("description")
        print(description)
        print("--------------------------------")
        lines.append(f"{index}. {tool.name}\n   {description}")
    return "\n\n".join(lines)

def choose_tool(user_request, tools):
    tool_list = build_tool_descriptions(tools)
    planner_prompt = f"""
    You are an AI planner.
    Available tools:
    {tool_list}
    Return ONLY the tool name.
    User Request:
    {user_request}
    """
    print("tool_list")
    print(tool_list)
    print("--------------------------------")
    print("user_request")
    print(user_request)
    print("--------------------------------")
    print("planner_prompt")
    print(planner_prompt)
    print("--------------------------------")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role":"system","content":"You are an AI planner."},
            {"role":"user","content":planner_prompt}
        ]
    )
    return response.choices[0].message.content.strip()
