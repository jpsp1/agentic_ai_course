from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from IPython.display import display, Markdown
import functools
import subprocess
import agents.mcp.server
from backend.accounts import Account
import asyncio


load_dotenv(override=True)

# On Windows, a stdio MCP server started from a Jupyter kernel writes to a stderr stream with no
# real file descriptor and crashes with io.UnsupportedOperation: fileno. We send the server's
# stderr to the null device so it always has somewhere real to write, which lets every cell below
# use MCPServerStdio exactly as the OpenAI Agents SDK documents it. Mac and Linux are unaffected.


agents.mcp.server.stdio_client = functools.partial(agents.mcp.server.stdio_client, errlog=subprocess.DEVNULL)

account = Account.get("Joao")
account.reset()


account.buy_shares("AMZN", 3, "Because this bookstore website looks promising")

print(account.report())

print(account.list_transactions())

# Now let's use our accounts server as an MCP server

params = {"command": "uv", "args": ["run", "-m", "backend.accounts_server"]}


async def main():      
    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
        mcp_tools = await server.list_tools()
    

if __name__ == "__main__":
    asyncio.run(main())
