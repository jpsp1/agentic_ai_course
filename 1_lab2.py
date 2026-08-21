# https://github.com/ed-donner/agents/blob/main/1_foundations/2_lab2.ipynb
# Start with imports - ask the Cursor Agent to explain any package that you don't know

import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display
import requests

def record(model_name, answer):
    competitors.append(model_name)
    answers.append(answer)
    print(answer)
    display(Markdown(answer))


bash_path = "/c/jpsp/agentic_AI/agents/.env"
# Convert "/c/users/..." to "C:/users/..." if on Windows
if bash_path.startswith("/") and bash_path[2] == "/":
    drive_letter = bash_path[1].upper()
    standard_path = f"{drive_letter}:{bash_path[2:]}"
else:
    standard_path = bash_path

#load_dotenv(dotenv_path=standard_path,override=True)
load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
grok_api_key = os.getenv('GROK_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set (and this is optional)")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")

if deepseek_api_key:
    print(f"DeepSeek API Key exists and begins {deepseek_api_key[:3]}")
else:
    print("DeepSeek API Key not set (and this is optional)")

if groq_api_key:
    print(f"Groq API Key exists and begins {groq_api_key[:4]}")
else:
    print("Groq API Key not set (and this is optional)")

if grok_api_key:
    print(f"Grok API Key exists and begins {grok_api_key[:4]}")
else:
    print("Grok API Key not set (and this is optional)")

if openrouter_api_key:
    print(f"OpenRouter API Key exists and begins {openrouter_api_key[:6]}") 
else:
    print("OpenRouter API Key not set (and this is optional)")

input("Press Enter to continue...")

#####################
request = """
Please come up with a challenging, nuanced question with a succinct answer,
that I can ask a number of LLMs to evaluate their intelligence.
Not a mathematical puzzle, but more of a thought-provoking question that requires intelligent insight.
Include in your question that the answer must be short.
"""
request += "Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]

messages

openai = OpenAI()

response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages)
question = response.choices[0].message.content
print(question)
display(Markdown(question))

input("Press Enter to continue...")

# OpenAI Compatible URLs

#ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1/"
#DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
#GROQ_BASE_URL = "https://api.groq.com/openai/v1"
#GROK_BASE_URL = "https://api.x.ai/v1"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"



# OpenAI client libraries with the right base_url and key
# If this surprises you, please see Guide 9 in the Guides folder!

#anthropic = OpenAI(api_key=anthropic_api_key, base_url=ANTHROPIC_BASE_URL)
#deepseek = OpenAI(api_key=deepseek_api_key, base_url=DEEPSEEK_BASE_URL)
gemini = OpenAI(api_key=google_api_key, base_url=GEMINI_BASE_URL)
#groq = OpenAI(api_key=groq_api_key, base_url=GROQ_BASE_URL)
#grok = OpenAI(api_key=grok_api_key, base_url=GROK_BASE_URL)
openrouter = OpenAI(api_key=openrouter_api_key, base_url=OPENROUTER_BASE_URL)
ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")



competitors = []
answers = []
messages = [{"role": "user", "content": question}]


# The API we know well
# Reasoning effort can be none, low, medium, high, or xhigh

model_name = "gpt-5.4-nano"
print(model_name)
response = openai.chat.completions.create(model=model_name, messages=messages, reasoning_effort="none")
answer = response.choices[0].message.content

record(model_name, answer)

model_name = "gemini-3.1-flash-lite"
print(model_name)

response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

record(model_name, answer)

#model_name = "moonshotai/kimi-k2.6"
model_name = "nvidia/nemotron-3-ultra-550b-a55b:free"
print(model_name)
response = openrouter.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

record(model_name, answer)

if 0==0:
    ##################ollama
    requests.get('http://localhost:11434').content


    models = requests.get('http://localhost:11434/v1/models').json()
    for model in models.get("data"):
        print(model.get("id"))

    #model_name = "llama3.2:1b"
    model_name = "llama3.2:latest"
    print(model_name)
    response = ollama.chat.completions.create(model=model_name, messages=messages)
    answer = response.choices[0].message.content

    record(model_name, answer)


input("Press Enter to continue...")
# So where are we?

print(len(competitors))
print(competitors)
print(answers)

input("Press Enter to continue...")

# It's nice to know how to use "zip"
for competitor, answer in zip(competitors, answers):
    print(f"Competitor: {competitor}\n\n{answer}")

# Let's bring this together - note the use of "enumerate"

input("Press Enter to continue...")

together = ""
for index, answer in enumerate(answers):
    together += f"# Response from competitor {index+1}\n\n"
    together += answer + "\n\n"

print(together)

judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

judge_messages = [{"role": "user", "content": judge}]


#####################
# Judgement time!



response = openai.chat.completions.create(model="gpt-5.4-mini", messages=judge_messages)
response = response.choices[0].message.content
answer = response.choices[0].message.content
print(answer)


