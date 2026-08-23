# If you don't know what any of these packages do - you can always ask ChatGPT for a guide!

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from IPython.display import Markdown, display
import gradio as gr
import json
############
load_dotenv(override=True)
openai = OpenAI()