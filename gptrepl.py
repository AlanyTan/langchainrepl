#from typing import Dict, Optional
import os
import re
import json
#import dotenv
import redis
import requests
import html
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents.tools import Tool
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.tools.python.tool import PythonREPLTool
from langchain.memory import ConversationBufferMemory
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
#from langchain.utilities import GoogleSearchAPIWrapper
#from langchain.docstore.wikipedia import Wikipedia
#from langchain.agents.react.base import DocstoreExplorer

from googleapiclient.discovery import build

from bs4 import BeautifulSoup

if (v := os.getenv('REDIS_HOST')) is not None:
    redis_host = v
else:
    redis_host = None
if (v := os.getenv('REDIS_PORT')) is not None:
    redis_port = int(v)
else:
    redis_port = 6379
if redis_host is not None:
    r = redis.Redis(host=redis_host, port=redis_port, db=0)
current_stackexchange_count=0

llm = OpenAI(model_name="text-davinci-003",temperature=0.00,max_retries=10) # type: ignore

def retrieve_webpage (input):
    url_pattern = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    match = re.findall(url_pattern,input)
    print(f'match:{match}')
    contents = ''
    if match:
        for url in match: # type: ignore
            print (f'url:{url[0]}')
            response = requests.get(url[0])
            if response.status_code == 200:
                webpage_content = BeautifulSoup(response.content, 'html.parser')
                contents = contents + " " + webpage_content.get_text()
            else:
                contents = contents + f'the url {url} cannot be retrieved. '
            return contents[0:2000]
    else :
        return 'you did not provide a url in your ask, I can only give you an answer if you give me a url.'

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return html.unescape(re.sub(clean, '', text))

def stack_exchange (search_term):
    global current_stackexchange_count
    site = 'stackoverflow'
    if (v := os.getenv('STACKEXCHANGE_API_KEY')) is not None:
        api_key_parm = f'&key={v}'
    else: 
        api_key_parm = r''
    base_url = 'https://api.stackexchange.com/2.3'
    try :
        search_json = json.loads(r.get(search_term) ) # type: ignore
    except: 
        search_json = None
    if search_json is None:
        search_url = f'{base_url}/search/advanced?answers=1&order=desc&tagged=python&sort=relevance&site={site}{api_key_parm}&q={search_term}'
        search_response = requests.get(search_url)
        search_json = search_response.json()
        r.set(search_term, json.dumps(search_json))
    if len(search_json['items'] or []) > current_stackexchange_count: 
        question_id = search_json['items'][current_stackexchange_count]['question_id']

        question_title = search_json['items'][current_stackexchange_count]['title']

        url = f'{base_url}/questions/{question_id}/answers?order=desc&sort=activity&site={site}&filter=withbody{api_key_parm}'
        response = requests.get(url)
        json_data = response.json()
        current_stackexchange_count = current_stackexchange_count + 1   
 
        # Get the body of the first answer
        answer_body = "I can not find an answer for your question."
        answer_item_bodys = [json.dumps(sub_item['body']) for sub_item in json_data['items']]
        if len(answer_item_bodys) > 0:
            answer_body = ".".join(answer_item_bodys) + "."


        return remove_html_tags(question_title + ": " + answer_body) + '\n'
    else :
        return 'Can not find an answer\n'

def manual_input(prompt): 
     return input(f"\n ==> Dear Human: {prompt} :")

default_tool_list = ["google-search","wikipedia"]
if (v := os.getenv('WOLFRAM_ALPHA_APPID')) is not None:
    default_tool_list.append("wolfram-alpha")
tools = load_tools(default_tool_list)
tools.append ( PythonREPLTool(name="Python REPL", description="Used to Execute Python code") )
tools.append ( Tool("ask the human", manual_input, "Ask human for help when search cannot find answer, or prompts the user for input.") )
tools.append ( Tool("retrieve URL", retrieve_webpage, "https and http url used as .") ) # type: ignore
tools.append ( Tool("search Stack Overflow", stack_exchange, "Search stack overflow for potential answers, especially if run into exceptions and errors") )
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True, memory=memory) # type: ignore

#question = "calculate the 10th fibonacci number"
#question = "look up for SPC study in manufacturing, and write a python code that calculates cpk of a series of 20 numbers that were randomly generated"
#question = "Learn how to calculate sigma using C4 constant in SPC study in manufacturing, which is different than numpy standard deviation, then write python code to calcuate sigma of a set of 30 random numbers."
#question = "write a python script that subscribe to redis stream to wait for incoming data and calculate standard deviation once receive 20 numbers."
question = "lookup how to use redis and write a python code that emit 40 random numbers to redis stream <rstream>."
#question = "search google what is an openfeature provider, and write a LaunchDarkly python-client-sdk based openfeature provider in python"
#question = "learn how to calculate SPC study in manufacturing, especially how to use D2 to calculate sigma, ppk and cpk, using AIAG guidelines. Then write python program to perform XBar analysis with a subgroup size of 5, and calculate XBar, range, cp, cpk, and pp, ppk, check with me for each calculation result."
question = "write a python code that calculate 100 digit of PI. Make sure you can calculate 100 digits of PI, most code you found on the internet are unable to calculate that many digits"
agent.run(question)

