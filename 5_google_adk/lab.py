import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from quiet import silence
silence()  # turn down some noisy library logging so the agent's trace is easy to read

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
load_dotenv(override=True)
