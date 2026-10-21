from agents import Agent, WebSearchTool, trace, Runner, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
from IPython.display import display, Markdown
from messenger import send_email, push
import sys

load_dotenv(override=True)

# Constants 

MODEL_NAME = "gpt-5.4-mini"
USE_EMAIL = False
#HOW_MANY_SEARCHES = 5
HOW_MANY_SEARCHES = 2

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


INSTRUCTIONS = """
You are a research assistant. Given a search term, you search the web for that term and 
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 words.
Capture the main points and be succinct. Reply only with the summary.
"""
task = "Most popular AI Agent frameworks in 2026"

settings = ModelSettings(tool_choice="required")
tools = [WebSearchTool()]

search_agent = Agent(name="Search Agent", instructions=INSTRUCTIONS, tools=tools, model=MODEL_NAME, model_settings=settings)

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

print(WebSearchPlan.model_json_schema())
# See note above about cost of WebSearchTool

INSTRUCTIONS = f"""
You are a research assistant. Given a user query, come up with a set of web searches
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.
"""

planner_agent = Agent(name="Planner Agent", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=WebSearchPlan)


INSTRUCTIONS = """
You are a senior researcher tasked with writing a cohesive report for a research query.
You will be provided with the original query, and some research.
Generate a comprehensive report based on the research and the query.
The final output should be in markdown format, and it should be lengthy and detailed. Aim 
for 5-10 pages of content, at least 1000 words.
"""


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(name="Writer Agent", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=ReportData)

USE_EMAIL=False

@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
    """
    Send out an email with the given subject and body to all sales prospects
    
    Args:
        subject: The subject of the email
        text_body: The body of the email as plain text
        html_body: The HTML body of the email
    """
    if USE_EMAIL:
        send_email(subject, text_body, html_body)
    else:
        push(f"Subject: {subject}\n\n{text_body}")
    return "Email sent successfully"

INSTRUCTIONS = """
You are provided with a detailed report. Use your tool to send an email, converting the report into
a clean, well presented HTML email with an appropriate subject line.
"""

email_agent = Agent(name="Email Agent", instructions=INSTRUCTIONS, tools=[send_email_tool], model=MODEL_NAME)


async def run_searches(query: str):
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    searches = result.final_output.searches
    print(f"Will perform {len(searches)} searches")
    tasks = [search(item) for item in searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results


async def search(item: WebSearchItem):
    input_message = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input_message)
    return result.final_output


async def write_report(query: str, search_results: list[str]):
    print("Thinking about report...")
    input_message = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input_message)
    print("Finished writing report")
    return result.final_output

async def send_report_email(report: ReportData):
    print("Writing email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("Email sent")
    return result.final_output

# incomplete... see course notes for next steps. The idea is to run the search, then write the report, then send the email.

async def main():    
    
    result = await Runner.run(planner_agent, task)
    print(result.final_output)
    sys.exit(0)  # Exit after printing the schema to avoid running the rest of the code 

    try:
        result = await Runner.run(search_agent, task)       
    except Exception as e:
        print(f"An error occurred: {e}")
    else:
        display(Markdown(result.final_output))
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

