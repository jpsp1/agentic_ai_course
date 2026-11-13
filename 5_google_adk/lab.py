#From Edward Donner's 2026 course: AI Engineer Agentic Track: The Complete Agent & MCP Course 
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from quiet import silence
import asyncio
import board

silence()  # turn down some noisy library logging so the agent's trace is easy to read

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
load_dotenv(override=True)

MODEL = "gemini-3.1-flash-lite"

agent = LlmAgent(
    model=MODEL,
    name="assistant",
    instruction="You are a concise, friendly assistant. Reply in a single short sentence.",
)



board.reset_board()
board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt.")
board.list_todos()

board.show_board()

async def main():    
    result = await InMemoryRunner(agent=agent).run_debug("Say hello in spanish.", verbose=True)

if __name__ == "__main__":
    asyncio.run(main())