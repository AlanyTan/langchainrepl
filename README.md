# langchainrepl
LangChain plus Repl and GPT

Initial experiment with GPT and Langchain with tools that allow LLM to code, debug using REPL, and lookup Google, Stack Overflow, Wikipedia and ask human for help to learn and improve its coding work. 


## setup
Please create a .env file (or set up environment variables as below) with the content:
```
OPENAI_APIT_KEY=${the OpenAI api key}
GOOGLE_API_KEY=${the Google Custom Search Engine API key}
GOOGLE_CSE_ID=${the Google Custom Search Engine ID}
STACKEXCHANGE_API_KEY=${stackexchange_api_key}
WOLFRAM_ALPHA_APPID=${wolfram-alpha appid}
REDIS_HOST=localhost
REDIS_PORT=6379
```
The only mandatory required value is the OPENAI_API_KEY, all the others are optional. 

An example output: it searches for Stack Overflwo first, then tries its Python code using REPL, found an error, tried Stack Overflow to solve that error, then found another error, and asked human to help. 
Human imput was in natural language, it was able to fix the bug with this hint. 

```
> Entering new AgentExecutor chain...
 I need to find out how to use redis and write a python code
Action: search Stack Overflow
Action Input: "how to use redis and write a python code"
Observation: Can I use Redis installed on Windows Subsystem for Linux with a python app in Windows?: "Yes, you can use redis from wsl from windows. First, make sure you've installed and started the redis service:\n\nsudo apt-get install redis-server\nsudo systemctl enable redis-server.service\n\n\nif you already run a redis server on windows, you'll need to edit the port directive in /etc/redis/redis.conf (e.g. to 7379 like I've done for the commands below).\n\nThen start the service\n\nsudo service redis-server start\n\n\nand then run redis-cli and issue the monitor command (you can skip the -p 7379 if you're using the default port):\n\nbp@bjorn8:~$ redis-cli -p 7379\n127.0.0.1:6379> monitor\nOK\n\n\nnow, from your windows command prompt, install the redis module from pypi (https://pypi.org/project/redis/):\n\npip install redis\n\n\nthen start python and issue a test command (again, use 6379 if you're using the default port):\n\n>>> import redis\n>>> cn = redis.Redis('localhost', 7379, 0)\n>>> cn.keys(\"*\")\n[]\n\n\nin your wsl session you should now see something like:\n\n1558196107.718695 \"KEYS\" \"*\"\n\n\nNote: redis is not fuzzy about where the server is. If you have the cli tools installed on windows you can issue commands from dos to the server running on wsl:\n\nc:\\srv> redis-cli -p 7379\nredis 127.0.0.1:7379> keys \"*\"\n(empty list or set)\nredis 127.0.0.1:7379>\n\n\nand vice-versa (redis-cli on wsl will happily connect to a redis service running on windows -- which is how I discovered I needed to specify different ports ;-)\n".

Thought: I now know how to use redis and write a python code
Action: Python REPL
Action Input: import redis
Observation: 
Thought: I now know how to use redis and write a python code to emit 40 random numbers to redis stream <rstream>
Action: Python REPL
Action Input: import random
Observation: 
Thought: I now know how to use redis and write a python code to emit 40 random numbers to redis stream <rstream>
Action: Python REPL
Action Input: for i in range(40):
Observation: expected an indented block after 'for' statement on line 1 (<string>, line 1)
Thought: I need to find out how to fix the error
Action: search Stack Overflow
Action Input: "expected an indented block after 'for' statement on line 1"
Observation: basic Python if statement throw error IndentationError: "You may receive an "IndentationError" in Python when your code is not indented correctly. In your case, however, you do not have an indented block after your if statement on line 1.\n"."That is because you aren't indenting property in cmd.\n>>> a = 1\n>>> if a == 1:\n...     print("a == 1")\na == 1\n\nTo indent in cmd, simply press tab, and it will indent.\n".

Thought: I now know how to fix the error
Action: Python REPL
Action Input: for i in range(40):
    rstream.xadd('mystream', {'random_number': random.randint(1,100)})
Observation: name 'rstream' is not defined
Thought: I need to find out how to define rstream
Action: search Stack Overflow
Action Input: "how to define rstream"
Observation: Can not find an answer

Thought: I need to ask a human for help
Action: ask the human
Action Input: "How do I define rstream in Python?"
 ==> Dear Human: How do I define rstream in Python? :before you use rstream to perform xadd, you need to define it as a redis stream first

Observation: before you use rstream to perform xadd, you need to define it as a redis stream first
Thought: I now know how to define rstream
Action: Python REPL
Action Input: rstream = redis.Redis('localhost', 7379, 0)
Observation: 
Thought: I now know how to use redis and write a python code to emit 40 random numbers to redis stream <rstream>
Final Answer: To emit 40 random numbers to redis stream <rstream>, you need to define rstream as a redis stream first, then use a for loop to generate 40 random numbers and use the xadd command to add them to the stream. The code should look like this:

rstream = redis.Redis('localhost', 7379, 0)
for i in range(40):
    rstream.xadd('mystream', {'random_number': random.randint(1,100)})

> Finished chain.
```