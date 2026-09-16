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


async def main_v3():
    agent = Agent(name="Jokester", instructions="You are a joke teller", model="gpt-5.4-mini")    
    # Streaming
    result = Runner.run_streamed(agent, input="Please tell me 5 jokes about AI Agents.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
 
async def main_v4():
    #look at the trace
    #https://platform.openai.com/traces
    with trace("Pizza has arrived"):
        result = await Runner.run(notifier, "Notify the user that the pizza is here")
    print(result.final_output)

async def main_v5():
    #history. memory. conversation. context. whatever you want to call it.
    agent = Agent(name="agent name", model="gpt-5.4-mini")
    response = await Runner.run(agent, "Hi there. My name is Joao.")
    print(response.final_output)
    next_input = response.to_input_list() + [{"role": "user", "content": "What's my name?"}]
    response = await Runner.run(agent, next_input)
    print(response.final_output)      

def push_v1(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

# Now this:

@function_tool
def push_tool(message: str) -> str:
    """ Send the given message to the user as a push notification """
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    result = requests.post(pushover_url, data=payload).status_code
    return f"Push sent with API status code {result}"

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

#print(push_tool)
#FunctionTool(name='push_tool', 
#description='Send the given message to the user as a push notification',
# params_json_schema={'properties': {'message':
# {'title': 'Message', 'type': 'string'}},
# 'required': ['message'], 'title': 'push_tool_args', ...

#push_tool.description
#push("HEY!!")




#notifier = Agent(name="Notifier", model="gpt-5.4-mini", 
#    instructions="You notify the user upon request", 
#    tools=[push_tool])

async def main():
    session = SQLiteSession("12346")
    #history. memory. conversation. context. whatever you want to call it.
    agent = Agent(name="agent name", model="gpt-5.4-mini")
    response = await Runner.run(agent, "Hi there. My name is Joao.",session=session)
    print(response.final_output)
    response = await Runner.run(agent, "What's my name?", session=session)    
    print(response.final_output)      


# Executa a função assíncrona

if __name__ == "__main__":
    asyncio.run(main())

