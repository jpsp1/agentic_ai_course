import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

load_dotenv(override=True)

llm = ChatOpenAI(model="gpt-5.4-mini")

message = "In 1 sentence, what does it mean for an AI Agent to be autonomous"

reply = llm.invoke(message)

print(reply.content)
