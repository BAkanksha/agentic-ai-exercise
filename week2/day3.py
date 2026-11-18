
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from agents import (
    Agent,
    Runner,
    trace,
    function_tool,
    OpenAIChatCompletionsModel,
    output_guardrail,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    set_tracing_disabled,
)

from messenger import send_email, push

load_dotenv(override=True)

# Tracing uploads to OpenAI and needs an OpenAI key, so it is turned off
set_tracing_disabled(True)

google_api_key = os.getenv("GOOGLE_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set")

if openrouter_api_key:
    print(f"OpenRouter API Key exists and begins {openrouter_api_key[:6]}")
else:
    print("OpenRouter API Key not set")

if groq_api_key:
    print(f"Groq API Key exists and begins {groq_api_key[:4]}")
else:
    print("Groq API Key not set")


# ---------------------------------------------------------------------------
# Part 1: Different models (OpenAI compatible endpoints)
# ---------------------------------------------------------------------------

instructions = """
You are a sales agent working for ComplAI,
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
You write compelling sales emails that are likely to get a response.
"""

# STEP 1: OpenAI compatible base URLs
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

# STEP 2: Async client instances
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
openrouter_client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key)
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

# STEP 3: Model objects (all free)
gemini_model = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite", openai_client=gemini_client)
oss_model = OpenAIChatCompletionsModel(model="openai/gpt-oss-120b", openai_client=groq_client)

# Free OpenRouter model (check openrouter.ai/models and filter by "free" for current names)
free_openrouter_model = OpenAIChatCompletionsModel(model="openai/gpt-oss-20b:free", openai_client=openrouter_client)

# Alternative: local Ollama (no key, no limits)
# free_openrouter_model = OpenAIChatCompletionsModel(model="llama3.2", openai_client=ollama_client)

sales_agent1 = Agent(name="Gemini Sales Agent", instructions=instructions, model=gemini_model)
sales_agent2 = Agent(name="OpenRouter Free Sales Agent", instructions=instructions, model=free_openrouter_model)
sales_agent3 = Agent(name="GPT-OSS Sales Agent", instructions=instructions, model=oss_model)

description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

USE_EMAIL = True


def send_message(subject, text_body, html_body):
    if USE_EMAIL:
        send_email(subject, text_body, html_body)
    else:
        push(f"Subject: {subject}\n\n{text_body}")


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


tools = [tool1, tool2, tool3, send_email_tool]

manager_instructions = """
You are a Sales Manager at OneMinus. Your goal is to find the single best cold sales email using the sales_agent tools.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_agent tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.

2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.

3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.
"""

sales_manager = Agent(
    name="Sales Manager",
    instructions=manager_instructions,
    tools=tools,
    model=gemini_model,  # was "gpt-5.4-mini"
)


async def part1_different_models():
    send_message("Yet another test", "Hooray!", "<html><body><h1>Hooray!</h1></body></html>")

    with trace("Sales Manager across different models"):
        result = await Runner.run(sales_manager, task)
    print(result.final_output)


# ---------------------------------------------------------------------------
# Part 2: Structured Outputs
# ---------------------------------------------------------------------------

class EmailReview(BaseModel):
    is_professional: bool = Field(description="Whether the email is professional and appropriate")
    number_of_sentences: int = Field(
        description="The number of sentences in the body of the email, not including the greeting and signature"
    )
    contains_placeholders: bool = Field(description="Whether the email contains placeholders for personalization")


checker = Agent(
    name="Checker",
    instructions="You review potential sales emails",
    model=gemini_model,  # was "gpt-5.4-mini"
    output_type=EmailReview,
)

sample_email = """
Hi Sir/madam,

I'm hitting you up to see if you'd like to buy our product. It's really great. You'll miss out if you don't buy it.

Laters.

Akanksha
"""


async def part2_structured_outputs():
    print(EmailReview.model_json_schema())

    result = await Runner.run(checker, sample_email)
    review = result.final_output
    print(review)
    print(review.is_professional)


# ---------------------------------------------------------------------------
# Part 3: Guardrails
# ---------------------------------------------------------------------------

@output_guardrail
async def email_guardrail(ctx, agent, message):
    result = await Runner.run(checker, message, context=ctx.context)
    review = result.final_output
    is_problem = review.contains_placeholders or not review.is_professional
    return GuardrailFunctionOutput(output_info={"review": review}, tripwire_triggered=is_problem)


cowboy_instructions = instructions + "\nSpeak like a San"

sales_agent_cowboy = Agent(
    name="san",
    instructions=cowboy_instructions,
    model=gemini_model,
    output_guardrails=[email_guardrail],
)

simple_cowboy = Agent(name="Simple san", instructions=cowboy_instructions, model=gemini_model)


async def part3_guardrails():
    # Framework guardrail
    try:
        result = await Runner.run(sales_agent_cowboy, "Write a cold sales email")
        print(result.final_output)
    except OutputGuardrailTripwireTriggered as e:
        print("Output guardrail tripped:", e)

    # The simpler approach: explicit checks, works in any framework
    result = await Runner.run(simple_cowboy, "Write a cold sales email")
    email = result.final_output
    print(email)

    result = await Runner.run(checker, email)
    review = result.final_output
    if not review.is_professional or review.contains_placeholders:
        print("The email is not professional or has placeholders and will not be sent")
    else:
        print("Email is good")


# Exercise ideas:
# - Try different models
# - Add more input and output guardrails
# - Use structured outputs for the email generation


# ---------------------------------------------------------------------------
# OPTIONAL EXTRA: Sandbox Agents (Windows + WSL2, Mac or Linux)
# May still depend on OpenAI-specific support, so test it before relying on it.
# ---------------------------------------------------------------------------

async def optional_sandbox_agent():
    from agents.run import RunConfig
    from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig, SandboxPathGrant
    from agents.sandbox.capabilities import Capabilities
    from agents.sandbox.entries import LocalDir
    from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

    CODE_DIR = Path("code").resolve()
    OUTPUT_DIR = Path("output").resolve()
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir()

    sandbox_instructions = f"""
You are a software engineer that fixes bugs.
Review files in the sandbox code directory.

Write the fixed version of the file to this host output directory:
{OUTPUT_DIR}

Use full file paths when writing output.
Respond with a summary of what you did.
"""

    manifest = Manifest(
        entries={"code": LocalDir(src=CODE_DIR)},
        extra_path_grants=[SandboxPathGrant(path=str(OUTPUT_DIR))],
    )
    capabilities = Capabilities.default()
    run_config = RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
        workflow_name="Sandbox coding example",
    )
    agent = SandboxAgent(
        name="Engineer",
        instructions=sandbox_instructions,
        model=gemini_model,  # was "gpt-5.4-mini"
        default_manifest=manifest,
        capabilities=capabilities,
    )
    result = await Runner.run(agent, "Fix the bug in the code", run_config=run_config)
    print(result.final_output)


# ---------------------------------------------------------------------------
# OPTIONAL EXTRA: MCP teaser
# ---------------------------------------------------------------------------

async def optional_mcp_teaser():
    from agents.mcp import MCPServerStreamableHttp

    mcp_task = """
In the new SandboxAgents feature in the OpenAI Agents SDK as of May 2026, what is the role of the Manifest object?
Always be accurate. If you don't know the answer, say so.
"""

    # Without MCP
    agent = Agent(name="Expert", instructions="Answer the question", model=gemini_model)  # was "gpt-4o-mini"
    result = await Runner.run(agent, mcp_task)
    print(result.final_output)

    # With Context7 MCP server
    params = {"url": "https://mcp.context7.com/mcp", "timeout": 60}
    async with MCPServerStreamableHttp(name="Context7", params=params) as server:
        agent = Agent(
            name="Expert",
            instructions="Use Context7 to answer the question",
            mcp_servers=[server],
            model=gemini_model,  # was "gpt-4o-mini"
        )
        result = await Runner.run(agent, mcp_task)

    print(result.final_output)


# ---------------------------------------------------------------------------

async def main():
    await part1_different_models()
    await part2_structured_outputs()
    await part3_guardrails()

    # Optional extras - uncomment to run
    # await optional_sandbox_agent()
    # await optional_mcp_teaser()


if __name__ == "__main__":
    asyncio.run(main())