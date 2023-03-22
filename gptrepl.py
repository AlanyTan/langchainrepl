#from typing import Dict, Optional
import os
import dotenv
from dotenv import load_dotenv
load_dotenv()
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents.tools import Tool
from langchain.agents.react.base import DocstoreExplorer
from langchain.docstore.wikipedia import Wikipedia
from langchain.llms.openai import OpenAI
from langchain.tools.python.tool import PythonREPLTool
from langchain.utilities import GoogleSearchAPIWrapper

from googleapiclient.discovery import build

llm = OpenAI(model_name="text-davinci-003",temperature=0.00) # type: ignore

def google_search(search_term, google_api_key, google_cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=google_api_key)
        res = service.cse().list(q=search_term, cx=google_cse_id, **kwargs).execute()
        return res['items']

def manual_input(prompt): 
    return input(prompt)

tools = load_tools(["google-search"])
docstore=DocstoreExplorer(Wikipedia())
tools.append ( Tool(
    name="Search Wikipedia",
    func=docstore.search,
    description="Search for a term in the docstore.",
  ))
tools.append (
  Tool(
    name="Lookup a Wikipedia article",
    func=docstore.lookup,
    description="Lookup a term in the docstore.",
  ))
tools.append ( PythonREPLTool(name="Python REPL", description="Execute Python code") )
tools.append ( Tool("ask the human", manual_input, "A tool that prompts the user for input.") )
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True) # type: ignore

#question = "look up for SPC study in manufacturing, and write a python code that calculates cpk of a series of 20 numbers that were randomly generated"
#question = "Learn how to calculate sigma using C4 constant in SPC study in manufacturing, which is different than numpy standard deviation, then write python code to calcuate sigma of a set of 30 random numbers."
#question = "lookup how to use redis and write a python code that subscribe to redis stream to wait for incoming data and calculate standard deviation once receive 20 numbers."
#question = "write a python code that publish 40 random numbers to redis stream."
question = "write a code to use .env files to configure the application in Python."
agent.run(question)

