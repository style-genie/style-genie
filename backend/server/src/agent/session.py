import logging
logger = logging.getLogger(__name__)
import litellm
import json
import subprocess
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
import asyncio
from backend.server.src.agent.workflows.advisor1 import Advisor1
from crewai.flow.flow import Flow, listen, start


tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_elements_from_vector_db",
                        "description": "Get the JSON element with the specified ID",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "keywords for the semantic search",
                                },
                                "unit": {"type": "string"},
                            },
                            "required": ["query"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_json_element_by_id",
                        "description": "get json element by id",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Die ID des gesuchten Elements",
                                },
                            },
                            "required": ["id"],
                            "additionalProperties": False,
                        },
                    },
                },
            ]
# the reason i have this function here is that mcp functions can call this too
async def compl_send_await(websocket,mcp,manager,session_id,msg,model_id="open_router_palm2"):
    print(msg)
    question= mcp.mcp_completion(
                    messages=msg,
                    model=model_id,
                )["response"].content
    # tell the user you want something
    print("\nAsking user for responce about:---------------->\n")
    print(question)
    asyncio.create_task(manager.send_personal_message(session_id, {"message": question})) 
    response = await websocket.receive_text()
    print("\nReceived User Response---------------->\n")
    print(response)
    return response  
  
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value
with open("./../../data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
class ModelContextProtocol:
    def error(self,error):
        if(self.manager):
            self.manager.send_personal_message(self.session_id, {"message": f"Error received: {error}"})
            print(f"Error received: {error}")
        #raise ValueError(error)
    def __init__(self,manager,session_id):
        self.models = {}
        self.session_id = session_id
        self.manager = manager
        #   ----------> CHECKING IF PINECONE_API_KEY IS SET <----------
        self.PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
        if(self.PINECONE_API_KEY == ""):
            self.error("PINECONE_API_KEY environment variable not set")
        self.INDEX_HOST = os.environ.get("INDEX_HOST", "" )
        if self.INDEX_HOST == "":
            self.error("INDEX_HOST environment variable not set")

        self.NAMESPACE = os.environ.get("NAMESPACE", "__default__")
        
        #   ----------> CHECKING IF OPENROUTER_API_KEY IS SET <----------
        OPENROUTER_API_KEY=os.environ.get("OPENROUTER_API_KEY","")
        OPENROUTER_API_BASE=os.environ.get("OPENROUTER_API_BASE","https://openrouter.ai/api/v1")
        if OPENROUTER_API_KEY != "" and OPENROUTER_API_KEY is not None:
            self.register_provider("open_router",OPENROUTER_API_BASE,OPENROUTER_API_KEY,"openrouter")

        #   ----------> CHECKING IF OLLAMA_HOST IS SET <----------
        OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
        if OLLAMA_API_KEY != "":
            self.register_provider("ollama_local",OLLAMA_HOST,OLLAMA_API_KEY,"ollama")

        #   ----------> CHECKING IF OPENWEBUI_HOST IS SET <----------
        OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/ollama")
        OPENWEBUI_API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
        if OPENWEBUI_API_KEY != "":
            self.register_provider("openwebui",OPENWEBUI_HOST,OPENWEBUI_API_KEY,"openwebui")
            
        #   ----------> CHECKING IF GEMINI_HOST IS SET <----------
        GEMINI_HOST = os.environ.get("GEMINI_HOST", "")
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "" )
        if GEMINI_API_KEY != "":
            self.register_provider("gemini",GEMINI_HOST,GEMINI_API_KEY,"gemini")
    
    def register_provider(self, host_type, host_url, api_key,provider, arguments={}):
        """Registers a host after the server has started."""
        print(f"Registering {provider} host: {host_url}")
        # registering some models we need later for the agent workflows
        if host_type == "open_router":
            self.models["open_router_gpt35"]={"api_key": api_key, "base_url": host_url, "model":"openrouter/openai/gpt-3.5-turbo", "tools":False,**arguments} 
            self.models["open_router_palm2"]={"api_key": api_key, "base_url": host_url, "model":"openrouter/google/palm-2-chat-bison", "tools":False,**arguments}
        elif host_type == "ollama_local":
            self.models["ollama_local"]={"api_key": api_key, "base_url": host_url, "model":"ollama/gemma3:27b","tools":True, **arguments}
        elif host_type == "openwebui":
            self.models["openwebui"]={"api_key": api_key, "base_url": host_url,"model":"ollama/gemma3:27b","tools":True, **arguments}
        elif host_type == "gemini":
            self.models["gemini"]={"api_key": api_key, "base_url": host_url, "model": "gemini/gemini-2.5-flash-preview-04-17","tools":True,**arguments}
        else:
            raise ValueError("Invalid host type. Must be 'ollama_local', 'gemini' or 'openwebui'.")
        try:
                new_host={f"{host_type}":{
                            "litellm_provider": provider,
                            "max_tokens": 8192,
                            "api_key": api_key,
                                          }}
                print(new_host)
                # we use base_url since api_base seems to be a deprecated argument
                host_type!= "open_router" and litellm.register_model(new_host)
                print(f"Registered host: {host_type}")
        except Exception as e:
            print(f"Failed to register host {provider}: {e}")
            sys.exit(1)
    def fetch_elements_from_vector_db(self, query):
        """Fetches elements from the vector database based on the given query."""
        top_k = 2
        if not query:
            return {"error": "Query must be provided in the request."}
        # Construct the curl command
        curl_command = f"""curl "https://{self.INDEX_HOST}/records/self.NAMESPACEs/{self.NAMESPACE}/search" \
          -H "Accept: application/json" \
          -H "Content-Type: application/json" \
          -H "Api-Key: {self.PINECONE_API_KEY}" \
          -H "X-Pinecone-API-Version: unstable" \
          -d '{{"query": {{"inputs": {{"text": "{query}"}}, "top_k": {top_k} }}, "fields": ["text"] }}'"""
        # Execute the curl command
        process = subprocess.Popen(
            curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        # Check for errors
        if stderr:
            print(f"Curl Error: {stderr.decode()}")
            return {"error": stderr.decode()}
        print(stdout.decode())
        results = json.loads(stdout.decode())
        formatted_results = []
        for match in results["result"]["hits"]:
            index = match["_id"]
            print(index)
            score = match["_score"]
            print(score)
            item = {
                "score": score,
                **(data[int(index)]),
            }
            print(item)
            print("--------------------------")
            formatted_results.append(item)
        return formatted_results
    def get_json_element_by_id(self, id):
        """Gets a JSON element from the file based on the ID."""
        try:
            with open("../data.json", "r") as f:
                data = json.load(f)
            def find_element(obj, target_id):
                if isinstance(obj, dict):
                    if obj.get("id") == target_id:
                        return obj
                    for value in obj.values():
                        result = find_element(value, target_id)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_element(item, target_id)
                        if result:
                            return result
                return None
            return find_element(data, id)
        except FileNotFoundError:
            return {"error": "Datei nicht gefunden"}
        except json.JSONDecodeError:
            return {"error": "Ungültiges JSON"}
    def completion(self, messages, model="open_router_palm2",ignored_tools=[]):
        """Tests parallel function calling."""
        
        try:
            model=self.models[model]['model']
            allow_tools=self.models[model]['tools']
            print("-----------------------------------------")
            print(f"model: {model}")
            
            print(f"baseurl: {self.models[model]['base_url']}")#gemini/gemini-2.0-flash-001
            args={
                "model":model,
                "messages":messages,
                "api_key":self.models[model]["api_key"],
            }
              # Convert to dictionary
            if(model=="open_router"):
                args["base_url"]=self.models[model]["base_url"] if "base_url" in self.models[model] else None
            if(allow_tools):
                args["tools"] = tools
                args["tool_choice"] = "auto"
                #tools=tools,#[tool for tool in tools if tool['function']['name'] not in ignored_tools], # Filter tools here
                #tool_choice="auto",  # auto is default, but we'll be explicit
            response = litellm.completion(**args,)
            response = dict(response)
            try:
                response_message = response["choices"][0].message
                json_response = response_message# json.loads(response_message)    
                print("------------------R-----------------------")
                print("\nLLM Response:\n")
                print(response_message.content)
                print("------------------R----------------------")
            except Exception as e:
                print("------------------E-----------------------")
                print(e)
                print("------------------E-----------------------")
                return {"error": "Unexpected response format from the model."}
            
            # Step 2: check if the model wanted to call a function
            if allow_tools and tool_calls:
                tool_calls =  response_message.tool_calls if allow_tools  else 0
                print("\nLength of tool calls", len(tool_calls))
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                available_functions = {
                    "get_json_element_by_id": self.get_json_element_by_id,
                    "fetch_elements_from_vector_db": self.fetch_elements_from_vector_db,
                }  # only one function in this example, but you can have multiple
                messages.append(response_message)  # extend conversation with assistant's reply
                # Step 4: send the info for each function call and function response to the model
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    if function_name == "get_json_element_by_id":
                        function_response = function_to_call(id=function_args.get("id"))
                    else:
                        function_response = function_to_call(query=function_args.get("query"))
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response
            # json_response["messages"] = messages
            
            # json_response["step"] = step+1
            return {"response":response_message,"messages":messages}
        except Exception as e:
            logger.error(f"Error in inner try: {e}")
            return {"error": str(e)}



class Session():
    def __init__(self, manager,websocket,session_id, max_tokens=150,temperature=0.7,max_recursion_depth=10):
        self.mcp = ModelContextProtocol(manager,session_id)
        self.manager = manager
        self.websocket = websocket
        self.session_id = session_id
        self.models = self.mcp.models
        self.history = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_recursion_depth = max_recursion_depth
        flow = Advisor1(session=self,mcp=self.mcp,websocket=self.websocket,manager=self.manager,session_id=self.session_id)
        result = flow.kickoff()
        print(f"Generated fun fact: {result}")
    def compl_send_await(self,msg):
        resp=compl_send_await(self.websocket,self.mcp,self.manager,self.session_id,msg)
        return resp
