
import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

from context import system_prompt
from tools import tools, handle_tool_calls
# from styles import TITLE, DESCRIPTION, EXAMPLES, THEME
from styles import EXAMPLES, CSS, JS

load_dotenv(override=True)

# The clients. "not-set" stops the script from crashing if a key is missing
ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
gemini = OpenAI(api_key=os.getenv("GOOGLE_API_KEY", "not-set"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
deepseek = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY", "not-set"), base_url="https://api.deepseek.com/v1")

# Pick ONE pair by removing the # from its two lines (and adding # to the others)
# client = ollama
# MODEL = "llama3.2"
client = gemini
MODEL = "gemini-3.1-flash-lite"
# client = deepseek
# MODEL = "deepseek-v4-flash"


def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    # keep looping while the LLM asks for a tool
    while response.choices[0].message.tool_calls:
        message = response.choices[0].message
        results = handle_tool_calls(message.tool_calls)
        messages.append(message)
        messages.extend(results)
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    return response.choices[0].message.content

# gr.ChatInterface(
#     chat,
#     title=TITLE,
#     description=DESCRIPTION,
#     examples=EXAMPLES,
# ).launch(inbrowser=True, theme=THEME)

gr.ChatInterface(
    chat,
    title="Akanksha Singh",
    description="Digital Twin · Python, Airflow & Data Engineering",
    examples=EXAMPLES,
).launch(inbrowser=True, css=CSS, js=JS)