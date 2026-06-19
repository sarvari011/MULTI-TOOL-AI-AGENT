from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
import wikipedia
import math

load_dotenv()

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

# ---------------- TOOLS ---------------- #

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url)

        if response.status_code == 200:
            return f"The weather in {city} is {response.text}"

        return "Weather information unavailable."

    except Exception as e:
        return str(e)


def wiki_search(query):
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=3)

    except Exception as e:
        return str(e)


def calculator(expression):
    try:
        allowed = {
            "__builtins__": {},
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs
        }

        return str(eval(expression, allowed))

    except Exception as e:
        return str(e)


available_tools = {
    "get_weather": get_weather,
    "wiki_search": wiki_search,
    "calculator": calculator
}

# ---------------- PROMPT ---------------- #

SYSTEM_PROMPT = """
You are a helpful AI Assistant.

You work in:
1. plan
2. action
3. output

Rules:
- Return ONLY valid JSON.
- Use tools whenever needed.
- Wait for tool result before final answer.
- Only one final output.

JSON Format:

{
    "step":"plan/action/output",
    "content":"text",
    "function":"tool_name",
    "input":"tool_input"
}

Available Tools:

get_weather:
Returns weather of a city.

wiki_search:
Returns wikipedia summary.

calculator:
Evaluates mathematical expressions.
"""

# ---------------- AGENT ---------------- #

def run_agent(query):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]

    while True:

        response = client.chat.completions.create(
            model="qwen2.5:3b",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_response = json.loads(
            response.choices[0].message.content
        )

        step = parsed_response.get("step")

        if step == "action":

            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            if tool_name in available_tools:

                output = available_tools[tool_name](tool_input)

                messages.append({
                    "role": "user",
                    "content": json.dumps({
                        "step": "observe",
                        "output": output
                    })
                })

                continue

            return "Unknown tool requested."

        elif step == "output":

            return parsed_response.get("content")

        else:

            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })