#From Edward Donner's 2026 course: AI Engineer Agentic Track: The Complete Agent & MCP Course 

# Imports and environment first

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

load_dotenv(override=True)

search = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())

sandbox = os.path.abspath("sandbox")
os.makedirs(sandbox, exist_ok=True)

model = ChatOpenAI(model="gpt-5.4-mini")

researcher = create_deep_agent(
    model=model,
    tools=[search],
    system_prompt=(
        "You are a research analyst. Plan your work with your todo tool, "
        "research with the search tool, and write your findings as a tidy markdown briefing to a file."
    ),
    backend=FilesystemBackend(root_dir=sandbox, virtual_mode=True),
)

brief = """
Our company is planning to move its sales fleet to electric vehicles.
Research the public EV charging landscape in Portugal: find out roughly how many public charging points there are,
and pick out two major charging networks a fleet could rely on.
Write a one page markdown briefing, with a heading and a short section for each, to the file charging.md.
"""

result = researcher.invoke({"messages": [{"role": "user", "content": brief}]})
print(result["messages"][-1].content)
