# Imports and environment first, all in one place

from dotenv import load_dotenv
from IPython.display import Image, display
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv(override=True)

if False:
    agent = create_agent(
        model="openai:gpt-5.4-mini",
        system_prompt="You are a helpful assistant who answers concisely.",
    )
if False:
    result = agent.invoke({"messages": [{"role": "user", "content": "What is the Model Context Protocol, in two sentences?"}]})
    print(result["messages"][-1].content)


@tool
def get_weather(city: str) -> str:
    """Return today's weather for a city."""
    pretend = {"London": "rainy, 14 degrees", "Rome": "sunny, 27 degrees"}
    return pretend.get(city, "clear, 20 degrees")

@tool
def get_population(city: str) -> str:
    """Return the population of a city."""
    pretend = {"London": "8.9 million", "Rome": "2.8 million"}
    return pretend.get(city, "unknown")

if False:
    agent = create_agent(
        model="openai:gpt-5.4-mini",
        tools=[get_weather, get_population],
        system_prompt="You are a travel assistant. Use your tools to answer questions about cities.",
    )

    display(Image(agent.get_graph().draw_mermaid_png()))

if False:
    memory_agent = create_agent(
        model="openai:gpt-5.4-mini",
        tools=[get_weather],
        checkpointer=MemorySaver(),
    )

class CityReport(BaseModel):
    city: str = Field(description="The city name")
    weather: str = Field(description="A short weather description")
    population: str = Field(description="The population")

if False:
    report_agent = create_agent(
        model="openai:gpt-5.4-mini",
        tools=[get_weather, get_population],
        response_format=CityReport,
    )

@wrap_tool_call
def log_tool_calls(request, handler):
    call = request.tool_call
    print(f"  [middleware] calling {call['name']} with {call['args']}")
    return handler(request)

watched_agent = create_agent(
    model="openai:gpt-5.4-mini",
    tools=[get_weather, get_population],
    system_prompt="You are a travel assistant. Use your tools.",
    middleware=[log_tool_calls],
)


async def main():    
    if False:
        result = await agent.ainvoke({"messages": [{"role": "user", "content": "In one sentence: why does async code suit agents so well?"}]})
        print(result["messages"][-1].content)

    if False:
        result = agent.invoke({"messages": [{"role": "user", "content": "What is the weather and population of Rome?"}]})
        print(result["messages"][-1].content)

    if False:
        config = {"configurable": {"thread_id": "trip-planning"}}
        memory_agent.invoke({"messages": [{"role": "user", "content": "I am planning a trip to London."}]}, config=config)
        result = memory_agent.invoke({"messages": [{"role": "user", "content": "What is the weather like where I am going on my trip?"}]}, config=config)
        print(result["messages"][-1].content)

    if False:
        result = report_agent.invoke({"messages": [{"role": "user", "content": "Give me a report on London."}]})
        report = result["structured_response"]
        print(report)
        print("Just the weather:", report.weather)

    result = watched_agent.invoke({"messages": [{"role": "user", "content": "Weather and population of London and Rome?"}]})
    print("\nFinal answer:", result["messages"][-1].content)

# Executa a função assíncrona

if __name__ == "__main__":
    asyncio.run(main())