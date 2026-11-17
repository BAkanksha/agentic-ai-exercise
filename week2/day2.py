
import sys
from dotenv import load_dotenv
import requests
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, ModelSettings, OpenAIChatCompletionsModel,  set_tracing_export_api_key
import os
import asyncio
import smtplib
from email.message import EmailMessage
load_dotenv(override=True)
# from agents import Agent, Runner, trace, function_tool, ModelSettings, OpenAIChatCompletionsModel, set_tracing_disabled, set_tracing_export_api_key

# Gemini model instead of gpt-5.4-mini\
gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite", openai_client=gemini_client)
# set_tracing_disabled(True)
set_tracing_export_api_key(os.getenv("OPENAI_API_KEY"))
sys.stdout.reconfigure(encoding="utf-8")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

USE_EMAIL = EMAIL_ADDRESS and EMAIL_SMTP_SERVER and EMAIL_APP_PASSWORD

if USE_EMAIL:
    print("Email is set up and we will try using it")
else:
    print("Email is not set up; we will send push notifications instead")

# Here we go

def send_email(subject, text_body, html_body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = "akanksha78si@gmail.com"
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)

### If email doesn't work, uncomment the below so that we don't use emails
# USE_EMAIL = False

### Our fallback strategy - send a push
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

def send_message(subject, text_body, html_body):
    if USE_EMAIL:
        send_email(subject, text_body, html_body)
    else:
        push(f"Subject: {subject}\n\n{text_body}")

### OK Now everything should work!
send_message("Big news", "Communications are a go!", "<html><body>Communications are a <strong>go!</strong></body></html>")



async def main():
    ## Part 2: Orchestrating by Code

    intro = """
    You are a sales agent working for ComplAI, 
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
    You write emails.
    """

    instructions1 = intro + "Your email style is professional, serious, with gravitas and credibility."
    instructions2 = intro + "Your email style is witty, engaging, and humorous."
    instructions3 = intro + "Your email style is concise, to the point, in the style of a busy senior executive."
    sales_agent1 = Agent(name="Professional Sales Agent", instructions=instructions1, model=MODEL_NAME)
    sales_agent2 = Agent(name="Humorous Sales Agent", instructions=instructions2, model=MODEL_NAME)
    sales_agent3 = Agent(name="Executive Sales Agent", instructions=instructions3, model=MODEL_NAME)

    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    message = "Write a cold sales email"

    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )

    outputs = [result.final_output for result in results]

    for output in outputs:
        print(output + "\n\n")

    decision = """
    You pick the best cold sales email from the given options.
    Imagine you are a customer and pick the one you are most likely to respond to.
    Do not give an explanation; reply with the selected email only.
    """

    sales_picker = Agent(name="Sales_picker", instructions=decision, model=MODEL_NAME)

    message = "Write a cold sales email"

    with trace("Sales selection workflow"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
        outputs = [result.final_output for result in results]

        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")

    ### Now we will add a tool to the mix.
    @function_tool
    def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
        """
        Send out an email with the given subject and body to all sales prospects
    
        Args:
            subject: The subject of the email
            text_body: The body of the email as plain text
            html_body: The HTML body of the email
        """
        send_message(subject, text_body, html_body)
        return "Email sent successfully"

    decision = """
    You pick the best cold sales email from the given options.
    Imagine you are a customer and pick the one you are most likely to respond to.
    Then use your tool to send the email.
    """

    require_tool = ModelSettings(tool_choice="required")

    sales_sender = Agent(name="Sales Sender", instructions=decision, model=MODEL_NAME, tools=[send_email_tool], model_settings=require_tool)

    message = "Write a cold sales email"

    with trace("Sales selection workflow with sending"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
        outputs = [result.final_output for result in results]

        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        response = await Runner.run(sales_sender, emails)

        print(f"Final response:\n{response.final_output}")

    ## Part 3: Orchestrating by LLMs

    ### 3a: via Tools

    description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

    tool1 = sales_agent1.as_tool(tool_name="sales_email_writer_1", tool_description=description)
    tool2 = sales_agent2.as_tool(tool_name="sales_email_writer_2", tool_description=description)
    tool3 = sales_agent3.as_tool(tool_name="sales_email_writer_3", tool_description=description)

    tools = [tool1, tool2, tool3, send_email_tool]

    ## And now it's time for our Sales Manager - our planning agent
    instructions = """
    You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_writer tools.
    """

    task = """
    Follow these steps:

    1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
    Just instruct each to write a sales email; no further details are needed.
    Do not proceed until all three drafts are ready, one from each tool.
 
    2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
    3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.
    """

    sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model=MODEL_NAME)

    with trace("Sales manager"):
        result = await Runner.run(sales_manager, task)
    print(result.final_output)

    ### 3b: via Handoffs

    instructions = """
    You are a Sales Manager at ComplAI. You get your sales team to draft emails, then send them all to a sales picker.
    """

    task = """
    Follow these steps:

    1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
    Just instruct each to write a sales email; no further details are needed.
    Do not proceed until all three drafts are ready, one from each tool.
 
    2. Handoff to the sales sender to choose and send the best email.
    """

    tools = [tool1, tool2, tool3]
    handoffs = [sales_sender]

    sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, handoffs=handoffs, model=MODEL_NAME)

    with trace("Sales manager"):
        result = await Runner.run(sales_manager, task)
    print(result.final_output)


asyncio.run(main())