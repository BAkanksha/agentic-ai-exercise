# The imports

import os
import asyncio
import requests
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, set_tracing_export_api_key, trace, function_tool, SQLiteSession, OpenAIChatCompletionsModel , set_tracing_export_api_key
# from agents import..., set_tracing_export_api_key
load_dotenv(override=True)



gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite", openai_client=gemini_client)
set_tracing_export_api_key(os.getenv("OPENAI_API_KEY"))


pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


@function_tool
def push_tool(message: str) -> str:
    """ Send the given message to the user as a push notification """
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    result = requests.post(pushover_url, data=payload).status_code
    return f"Push sent with API status code {result}"


async def main():
    

    # agent = Agent(name="Jokester", instructions="You are a joke teller", model=gemini_model)
    agent = Agent(name="Jokester", instructions="You are a joke teller", model=gemini_model)

    

    result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)

   

    print(result.to_input_list())

    ## Adding Observability with a trace
    with trace("Telling a joke"):
        result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)

    # Streaming

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes about AI Agents.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print()

    ## Part 2: Adding a tool

    push("HEY!!")

    notifier = Agent(name="Notifier", model=gemini_model, instructions="You notify the user upon request", tools=[push_tool])
    with trace("Pizza has arrived"):
        result = await Runner.run(notifier, "Notify the user that the pizza is here")

    print(result.final_output)

    ## Part 3: Sessions (memory)

    agent = Agent(name="Assistant", model=gemini_model)
    response = await Runner.run(agent, "Hi there. My name is Akanksha.")
    print(response.final_output)
    response = await Runner.run(agent, "What's my name?")
    print(response.final_output)

    ## Memory approach 1 - just manually pass in the list of dicts
    response = await Runner.run(agent, "Hi there. My name is Akanksha.")
    print(response.final_output)
    next_input = response.to_input_list() + [{"role": "user", "content": "What's my name?"}]
    response = await Runner.run(agent, next_input)
    print(response.final_output)

    ## Another approach - use OpenAI Agents SDK built in SQLLite session
    session = SQLiteSession("12346")
    response = await Runner.run(agent, "Hi there. My name is Akanksha.", session=session)
    print(response.final_output)
    response = await Runner.run(agent, "What's my name?", session=session)
    print(response.final_output)


asyncio.run(main())