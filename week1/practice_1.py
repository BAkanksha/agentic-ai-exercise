import os
from dotenv import load_dotenv
from openai import OpenAI
# from IPython.display import Markdown, display

load_dotenv(override=True)

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
MODEL = "llama3.2"


def ask(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def main():
    # Call 1: pick a business area
    p1 = (
        "Pick one business area that might be worth exploring for an Agentic AI opportunity. "
        "Answer with just the name of the area. No explanation, no punctuation."
    )
    business_area = ask(p1).strip()

    # Call 2: pain-point in that area
    p2 = f"Present one specific pain-point in the {business_area} industry, something challenging that is ripe for an Agentic AI solution. Keep it short."
    pain_point = ask(p2)

    # Call 3: propose the solution
    p3 = (
        f"Industry: {business_area}\n"
        f"Pain-point: {pain_point}\n\n"
        "Propose an Agentic AI solution for this pain-point. Explain what the agents would do and how they would work together."
    )
    solution = ask(p3)

    # display(Markdown(f"**Business area:** {business_area}\n\n**Pain-point:** {pain_point}\n\n**Solution:** {solution}"))
    print(f"Business area: {business_area}\n")
    print(f"Pain-point: {pain_point}\n")
    print(f"Solution: {solution}")


if __name__ == "__main__":
    main()