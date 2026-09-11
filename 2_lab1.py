# The imports
import os
import requests
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
import sys

async def mai_v1():
    agent = Agent(name="Jokester", instructions="You are a joke teller", model="gpt-5.4-mini")    
    # O 'await' agora funciona porque está dentro de uma função 'async'
    result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)
    # Here is the detail of the LLM calls
    print(result.to_input_list())


async def main_v2():
    agent = Agent(name="Jokester", instructions="You are a joke teller", model="gpt-5.4-mini")    
    with trace("Telling a joke"):
        result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(result.final_output)    
    print(result.to_input_list())


async def main():
    agent = Agent(name="Jokester", instructions="You are a joke teller", model="gpt-5.4-mini")    
    # Streaming
    result = Runner.run_streamed(agent, input="Please tell me 5 jokes about AI Agents.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
# Remember this?

def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

load_dotenv(override=True)
# o comando await só pode ser usado dentro de funções assíncronas
# (definidas com async def) ou diretamente em ambientes interativos 
#que já suportam isso por padrão (como notebooks Jupyter)


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

push("HEY!!")

sys.exit(0)

# Executa a função assíncrona

if __name__ == "__main__":
    asyncio.run(main())

