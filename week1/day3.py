
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
# from IPython.display import Markdown, display   # notebook only, so we use print instead

load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Print the key prefixes to check that .env is loading (never print the full key)
print("Google key loaded:", bool(google_api_key))
print("Groq key loaded:", bool(groq_api_key))
print()

print("Akanksha Singh")

# All of these providers have an OpenAI compatible endpoint, so we use the OpenAI class
ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")


# Step 1: ask one model to create a question
request = """
Please come up with a challenging, nuanced question with a succinct answer,
that I can ask a number of LLMs to evaluate their intelligence.
Not a mathematical puzzle, but more of a thought-provoking question that requires intelligent insight.
Include in your question that the answer must be short.
"""
request += "Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]

response = ollama.chat.completions.create(model="llama3.2", messages=messages)
question = response.choices[0].message.content

print("QUESTION:")
print(question)
print()


# Step 2: ask the same question to each model and save the answers
competitors = []
answers = []
messages = [{"role": "user", "content": question}]


def record(model_name, answer):
    competitors.append(model_name)
    answers.append(answer)
    print(f"--- {model_name} ---")
    print(answer)
    print()


def run_competitor(client, model_name):
    # If one model fails (wrong name, no key, rate limit), we skip it instead of stopping the script
    try:
        response = client.chat.completions.create(model=model_name, messages=messages)
        answer = response.choices[0].message.content
        if "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()
        record(model_name, answer)
        # record(model_name, answer)
    except Exception as e:
        print(f"--- {model_name} FAILED: {e}")
        print()


run_competitor(ollama, "llama3.2:latest")
run_competitor(ollama, "llama3.2:1b")
run_competitor(ollama, "deepseek-r1:1.5b")
run_competitor(gemini, "gemini-3.1-flash-lite")
run_competitor(groq, "openai/gpt-oss-120b")

if len(answers) < 2:
    raise SystemExit("Need at least 2 answers to judge. Check the errors above.")


# Step 3: join all answers into one text for the judge
together = ""
for index, answer in enumerate(answers):
    together += f"# Response from competitor {index+1}\n\n"
    together += answer + "\n\n"


# Step 4: build the judge prompt
judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

judge_messages = [{"role": "user", "content": judge}]


# Step 5: judge time (Groq follows the JSON format better than a small local model)
response = groq.chat.completions.create(model="openai/gpt-oss-120b", messages=judge_messages)
results = response.choices[0].message.content
print("JUDGE OUTPUT:")
print(results)
print()


# Step 6: turn the judge's JSON into a ranking
# Sometimes the judge adds extra words, so we keep only the part from { to }
start = results.find("{")
end = results.rfind("}") + 1
results_dict = json.loads(results[start:end])
ranks = results_dict["results"]

for index, result in enumerate(ranks):
    competitor = competitors[int(result) - 1]
    print(f"Rank {index+1}: {competitor}")