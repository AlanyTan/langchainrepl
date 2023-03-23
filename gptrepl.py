#from typing import Dict, Optional
import os
import re
import dotenv
import requests
import html
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

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return html.unescape(re.sub(clean, '', text))

def stack_exchange (search_term):
    site = 'stackoverflow'
    api_key = os.getenv("STACKEXCHANGE_API_KEY")
    base_url = 'https://api.stackexchange.com/2.3'
    search_url = f'{base_url}/search/advanced?order=desc&tagged=python&sort=relevance&site={site}&key={api_key}&q={search_term}'

    search_response = requests.get(search_url)
    search_json = search_response.json()
    if len(search_json['items']) > 0: 
        question_id = search_json['items'][0]['question_id']

        url = f'{base_url}/questions/{question_id}/answers?order=desc&sort=activity&site={site}&filter=withbody&key={api_key}'

        response = requests.get(url)
        json_data = response.json()

        # Get the body of the first answer
        answer_body = json_data['items'][0]['body']

        return remove_html_tags(answer_body) + '\n'
    else :
        return 'Can not find an answer\n'

def manual_input(prompt): 
    return input(f"\n ==> Dear Human: {prompt} ")

tools = load_tools(["google-search",])
tools.append ( PythonREPLTool(name="Python REPL", description="Execute Python code") )
tools.append ( Tool("ask the human", manual_input, "A tool that prompts the user for input.") )
# docstore=DocstoreExplorer(Wikipedia())
# tools.append ( Tool(
#     name="Lookup Wikipedia",
#     func=docstore.search,
#     description="Search for a concept in the wikipedia site.",
#   ))
# tools.append (
#   Tool(
#     name="Retrieve a Wikipedia article",
#     func=docstore.lookup,
#     description="Retrieve a document from the wikipedia the docstore.",
#   ))
tools.append ( Tool("search Stack Overflow", stack_exchange, "A tool that looks up stack overflow for potential answers with samples.") )
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True) # type: ignore

#question = "look up for SPC study in manufacturing, and write a python code that calculates cpk of a series of 20 numbers that were randomly generated"
#question = "Learn how to calculate sigma using C4 constant in SPC study in manufacturing, which is different than numpy standard deviation, then write python code to calcuate sigma of a set of 30 random numbers."
question = "lookup how to use redis and write a python code that subscribe to redis stream to wait for incoming data and calculate standard deviation once receive 20 numbers."
#question = "lookup how to use redis and write a python code that publish 40 random numbers to redis stream <rstream>."
#question = "search google what is an openfeature provider, and write a LaunchDarkly python-client-sdk based openfeature provider in python"
#question = "Research how to calculate SPC study in manufacturing and write python code to calculate cp, cpk, and pp, ppk using D2 constant"
agent.run(question)

