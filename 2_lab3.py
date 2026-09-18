from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, output_guardrail, GuardrailFunctionOutput
import os
from pydantic import BaseModel, Field
import requests
import asyncio


USE_EMAIL=False


def send_email(subject, text_body, html_body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)    


def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


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

class EmailReview(BaseModel):
    is_professional: bool = Field(description="Whether the email is professional and appropriate")
    number_of_sentences: int = Field(description="The number of sentences in the body of the email, not including the greeting and signature")
    contains_placeholders: bool = Field(description="Whether the email contains placeholders for personalization")

    
load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")

if  openrouter_api_key:
    print(f"OpenRouter API Key exists and begins {openrouter_api_key[:6]}")
else:
    print("OpenRouter API Key not set (and this is optional)")

if groq_api_key:
    print(f"Groq API Key exists and begins {groq_api_key[:4]}")
else:
    print("Groq API Key not set (and this is optional)")

instructions = """
You are a sales agent working for ComplAI, 
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
You write compelling sales emails that are likely to get a response.
"""
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
openrouter_client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key)
#groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=None)

gemini_model = OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite", openai_client=gemini_client)
model_name = "nvidia/nemotron-3-ultra-550b-a55b:free"
#kimi_model = OpenAIChatCompletionsModel(model="moonshotai/kimi-k2.6", openai_client=openrouter_client)
kimi_model = OpenAIChatCompletionsModel(model=model_name, openai_client=openrouter_client)
#oss_model = OpenAIChatCompletionsModel(model="openai/gpt-oss-120b", openai_client=groq_client)
model_name = "llama3.2:latest"
ollama_model = OpenAIChatCompletionsModel(model=model_name, openai_client=ollama_client)


sales_agent1 = Agent(name="Gemini Sales Agent", instructions=instructions, model=gemini_model)
sales_agent2 = Agent(name="Kimi Sales Agent", instructions=instructions, model=kimi_model)
sales_agent3 = Agent(name="Ollama Sales Agent", instructions=instructions, model=ollama_model)

#sales_agent3 = Agent(name="GPT-OSS Sales Agent",instructions=instructions, model=oss_model)

description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

#tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_user:
    if pushover_user.startswith("u"):
        print("Pushover user found and looks good")
    else:
        print("Pushover user found but doesn't start with u")
else:
    print("Pushover user not found")

if pushover_token:
    if pushover_token.startswith("a"):
        print("Pushover token found and looks good")
    else:
        print("Pushover token found but doesn't start with a")
else:
    print("Pushover token not found")

send_message("Yet another test", "Hooray!", "<html><body><h1>Hooray!</h1></body></html>")

#tools = [tool1, tool2, tool3, send_email_tool]
tools = [tool1, tool2, tool3, send_email_tool]


instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_agent tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.
"""

sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model="gpt-5.4-mini")


async def main():
    with trace("Sales Manager across different models"):
        result = await Runner.run(sales_manager, task)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

