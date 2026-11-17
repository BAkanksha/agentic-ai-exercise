import os
import json
from rich.console import Console
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL = "gemini-3.1-flash-lite"


def show(text):
    Console().print(text)


checklist = []
completed = []


def get_checklist_report() -> str:
    result = ""
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result


def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_checklist_report()


def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return "No checklist at this index."
    show(completion_notes)
    return get_checklist_report()


create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {"descriptions": {"type": "array", "items": {"type": "string"}}},
        "required": ["descriptions"],
        "additionalProperties": False,
    },
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "index": {"type": "integer", "description": "The 1-based index of the checklist item"},
            "completion_notes": {"type": "string", "description": "Notes about how you completed it, in rich console markup"},
        },
        "required": ["index", "completion_notes"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": create_checklist_json},
    {"type": "function", "function": mark_complete_json},
]


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results


def loop(messages):
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    while response.choices[0].message.tool_calls:
        message = response.choices[0].message
        results = handle_tool_calls(message.tool_calls)
        messages.append(message)
        messages.extend(results)
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    show(response.choices[0].message.content)


system_message = """
You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
Now create a plan, set the checklist, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""

user_message = """
The 100 Prisoners and the Boxes

100 prisoners are numbered 1 to 100. In a room there are 100 boxes, also numbered 1 to 100. Inside each box is a slip with a prisoner’s number on it, shuffled randomly, so each number appears exactly once.

The rules:

One by one, each prisoner enters the room and may open at most 50 boxes.
Their goal is to find the slip with their own number.
After each prisoner finishes, the room is reset exactly as it was. No communication is possible once the process starts.
All 100 prisoners must find their own number, or everyone is executed.

Before it starts, the prisoners can sit together and agree on a strategy.

If every prisoner just opens 50 random boxes, each has a 50% chance, so the group’s chance of survival is (1/2)^100, which is basically zero.

The question: Is there a strategy that gives the group a survival chance of around 30%? If so, what is it?
"""

messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
checklist, completed = [], []
loop(messages)