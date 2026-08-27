# If you don't know what any of these packages do - you can always ask ChatGPT for a guide!

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from IPython.display import Markdown, display
import gradio as gr
import json


#not used anymore:
def chat_v1(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages)
    return response.choices[0].message.content

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
         
    if response.choices[0].finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_call = message.tool_calls[0]
            email = json.loads(tool_call.function.arguments).get("email")
            record_email_tool(email)
            messages.append(message)
            messages.append({"role": "tool", "content": "Email recorded", "tool_call_id": tool_call.id})
            response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
            
    return response.choices[0].message.content

    
def record_email_tool(email):
    print(f"Tool called to record an email: {email}")
    with open("emails.txt", "a", encoding="utf-8") as f:
        f.write(email + "\n")
    return "Email received"

############
load_dotenv(override=True)
openai = OpenAI()
##########
reader = PdfReader("twin/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text
##########
print(linkedin)
##########
with open("twin/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()
########
print(summary)
#########
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hi, my name is Joao"}
]
#######
response = openai.chat.completions.create(model="gpt-5.4-nano", messages=messages)
print(response.choices[0].message.content)
############
messages = [
    {"role": "system", "content": "You are a snarky, witty assistant"},
    {"role": "user", "content": "Hi, my name is Joao"}
]
###########
messages = [
    {"role": "system", "content": "You are a snarky, witty assistant"},
    {"role": "user", "content": "What's my name?"}
]
#######
response = openai.chat.completions.create(model="gpt-5.4-nano", messages=messages)
print(response.choices[0].message.content)
######
messages = [
    {"role": "system", "content": "You are a snarky, witty assistant"},
    {"role": "user", "content": "Hi, my name is João"},
    {"role": "assistant", "content": "Well hi there, João. It's nice to meet you."},
    {"role": "user", "content": "What's my name?"}
]
response = openai.chat.completions.create(model="gpt-5.4-nano", messages=messages)
print(response.choices[0].message.content)
##############
system_prompt = f"""

# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's LinkedIn profile so that you can answer questions:

{linkedin}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
"""

##########
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Hi - please tell me about yourself"},
]
response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages)
display(Markdown(response.choices[0].message.content))
print(response.choices[0].message.content)



chat("Please summarize who you are", [])

print("will open a chat interface in your browser. You can ask questions about the person whose digital twin you are talking to. ")

# To create a public link, set `share=True` in `launch()`.
#gr.ChatInterface(chat).launch(inbrowser=True)

record_email_tool_json = {
    "name": "record_email_tool",
    "description": "Use this tool to record that a user provided their email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_email_tool_json}]