# Imports and environment first, as always

import os
import random
import requests
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langchain_openai import ChatOpenAI
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv(override=True)
#
class State(TypedDict):
    messages: Annotated[list, add_messages]

##############################    
if False:
    nouns = ["Cabbages", "Unicorns", "Toasters", "Penguins", "Bananas", "Eels", "Pickles"]
    adjectives = ["outrageous", "smelly", "pedantic", "existential", "sparkly", "haunted"]

    def silly_node(state: State) -> dict:
        sentence = f"{random.choice(nouns)} are {random.choice(adjectives)}"
        return {"messages": [{"role": "assistant", "content": sentence}]}

    builder = StateGraph(State)
    builder.add_node("silly", silly_node)
    builder.add_edge(START, "silly")
    builder.add_edge("silly", END)
    graph = builder.compile()

    display(Image(graph.get_graph().draw_mermaid_png()))    
    result = graph.invoke({"messages": [{"role": "user", "content": "say something"}]})
    print(result["messages"][-1].content)
##############################

llm = ChatOpenAI(model="gpt-5.4-mini")
if False:
    def chatbot_node(state: State) -> dict:
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot_node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)
    graph = builder.compile()

    display(Image(graph.get_graph().draw_mermaid_png()))

    result = graph.invoke({"messages": [{"role": "user", "content": "What is a directed graph, in one sentence?"}]})
    print(result["messages"][-1].content)

search = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())

@tool
def send_push_notification(text: str) -> str:
    """Send a short push notification to the user's phone."""
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": os.getenv("PUSHOVER_TOKEN"), "user": os.getenv("PUSHOVER_USER"), "message": text},
    )
    return "Notification sent"

tools = [search, send_push_notification]
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

if False:
    builder = StateGraph(State)

    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    graph = builder.compile()

    display(Image(graph.get_graph().draw_mermaid_png()))

    result = graph.invoke({"messages": [{"role": "user", "content": "Use your search tool to tell me the ingredients in banoffee pie and send me a push notification."}]})
    print(result["messages"][-1].content)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    spanish: str

def translator_node(state: State) -> dict:
    last = state["messages"][-1].content
    prompt = f"Translate this into Spanish, replying with the translation only:\n\n{last}"
    return {"spanish": llm.invoke(prompt).content}

builder = StateGraph(State)

builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_node("translator", translator_node)

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END:"translator"})
builder.add_edge("tools", "chatbot")
builder.add_edge("translator", END)
graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

result = graph.invoke({"messages": [{"role": "user", "content": "In one sentence, what is special about a banana?"}]})
print(result["messages"][-1].content)
print(result["spanish"])
