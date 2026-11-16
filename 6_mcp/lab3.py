from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio, create_static_tool_filter
import os
from pathlib import Path
from datetime import datetime
from IPython.display import Markdown, display
import functools
import subprocess
import agents.mcp.server
import asyncio
import json

load_dotenv(override=True)

# On Windows, a stdio MCP server started from a Jupyter kernel writes to a stderr stream with no
# real file descriptor and crashes with io.UnsupportedOperation: fileno. We send the server's
# stderr to the null device so it always has somewhere real to write, which lets every cell below
# use MCPServerStdio exactly as the OpenAI Agents SDK documents it. Mac and Linux are unaffected.


agents.mcp.server.stdio_client = functools.partial(agents.mcp.server.stdio_client, errlog=subprocess.DEVNULL)

memory_path = os.path.abspath("memory/memory.json")
memory_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"], "env": {"MEMORY_FILE_PATH": memory_path}}

instructions = "You use your entity tools as a persistent memory to store and recall information about your conversations."
request = "My name's Ed. I'm an LLM engineer. I'm teaching a course about AI Agents, including the incredible MCP protocol. MCP is a protocol for connecting agents with tools, resources and prompt templates, and makes it easy to integrate AI agents with capabilities."
model = "gpt-5.4-mini"


async def main():      
    # async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=60) as server:
    #     memory_tools = await server.list_tools()

    # print(memory_tools)

    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=30) as mcp_server:
        agent = Agent(name="agent", instructions=instructions, model=model, mcp_servers=[mcp_server])
        with trace("conversation"):
            result = await Runner.run(agent, request)
        print(result.final_output)

    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=30) as mcp_server:
        agent = Agent(name="agent", instructions=instructions, model=model, mcp_servers=[mcp_server])
        with trace("conversation"):
            result = await Runner.run(agent, "My name's Ed. What do you know about me?")
        print(result.final_output)
        

if __name__ == "__main__":
    asyncio.run(main())


