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
from src.agent.workflows.advisor1 import Advisor1
from src.agent.tools import tools, fetch_elements_from_vector_db, get_json_element_by_id,init_user_database, read_user_data, write_user_data,wiki,internet_search_tool
default_provider="openrouter"
default_model="openrouter_maverick"
# the reason i have this function here is that mcp functions can call this too
async def send(websocket,mcp,manager,session_id,msg,model_id=default_model,args):
    asyncio.create_task(manager.send_personal_message(session_id, {"message": msg})) 
async def compl_send_await(websocket,mcp,manager,session_id,msg,model_id=default_model,args):
    print(msg)
    question= mcp.completion(
                    messages=msg,
                    model_id=model_id,
                )["response"]
    
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
        #   ----------> CHECKING IF POStGRES ENV IS SET <----------
        self.POSTGRES_USER=os.environ.get("POSTGRES_USER","stylegen")
        self.POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD","stylegen")
        self.POSTGRES_DB=os.environ.get("POSTGRES_DB","main")
        if(self.POSTGRES_USER == ""):
            self.error("POSTGRES environment variables not set")
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
            self.models["openrouter_gpt35"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/openai/gpt-3.5-turbo", "tools":False,**arguments} 
            self.models["openrouter_palm2"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/google/palm-2-chat-bison", "tools":False,**arguments}
            self.models["openrouter_llamaguard12b"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/meta-llama/llama-guard-4-12b", "tools":True,**arguments}
            self.models["openrouter_phi4_3"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/microsoft/phi-4-reasoning-plus", "tools":True,**arguments}
            self.models["openrouter_maverick"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/meta-llama/llama-4-maverick", "tools":True,**arguments}
            self.models["openrouter_scout"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/meta-llama/llama-4-scout", "tools":True,**arguments}
            self.models["openrouter_gemini_2.5_pro_p325"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/google/gemini-2.5-pro-preview-03-25", "tools":True,**arguments}
            self.models["openrouter_gemini_2.5_pro_e325"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/google/gemini-2.5-pro-exp-03-25", "tools":True,**arguments}
            self.models["openrouter_claude3.7"]={"api_key": api_key,"provider":"openrouter", "base_url": host_url, "model":"openrouter/anthropic/claude-3.7-sonnet", "tools":True,**arguments}
        elif host_type == "ollama_local":
            self.models["ollama_local"]={"api_key": api_key,"provider":"ollama", "base_url": host_url, "model":"ollama/gemma3:27b","tools":True, **arguments}
        elif host_type == "openwebui":
            self.models["openwebui"]={"api_key": api_key, "provider":"openwebui","base_url": host_url,"model":"ollama/gemma3:27b","tools":True, **arguments}
        elif host_type == "gemini":
            self.models["gemini"]={"api_key": api_key,"provider":"gemini", "base_url": host_url, "model": "gemini/gemini-2.5-flash-preview-04-17","tools":True,**arguments}
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
   
    def completion(self, messages, model_id=default_model,ignored_tools=[]):
        """Tests parallel function calling."""
        print(self.models[model_id])
        model=self.models[model_id]['model']
        provider=self.models[model_id]['provider']
        allow_tools=self.models[model_id]['tools']
        print("-----------------------------------------")
        print(f"model: {model_id}")
        
        print(f"baseurl: {self.models[model_id]['base_url']}")#gemini/gemini-2.0-flash-001
        args={
            "model":model,
            "messages":messages,
            "api_key":self.models[model_id]["api_key"],
        }
            # Convert to dictionary
        if(provider=="open_router"):
            args["base_url"]=self.models[model_id]["base_url"] if "base_url" in self.models[model_id] else None
        if(allow_tools):
            print("------------------TOOOOLS-----------------------")
            args["tools"] = tools
            args["tool_choice"] = "auto"
            #tools=tools,#[tool for tool in tools if tool['function']['name'] not in ignored_tools], # Filter tools here
        response = litellm.completion(**args,)
        response = dict(response)
        try:
            response_message = response["choices"][0]
            print("------------------R-----------------------")
            print("\nLLM Response:\n")
            print(response_message.message.content)
            print("------------------R----------------------")
        except Exception as e:
            print("------------------E-----------------------")
            print(e)
            print("------------------E-----------------------")
            return {"error": "Unexpected response format from the model."}
        
        # Step 2: check if the model wanted to call a function
        tool_calls =  response["choices"][0].message.tool_calls if allow_tools  else 0
        print("\nLength of tool calls", (tool_calls))
        if tool_calls and tool_calls!=0:

            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_json_element_by_id": get_json_element_by_id,
                "fetch_elements_from_vector_db": fetch_elements_from_vector_db,
                "init_user_database":init_user_database, 
                "read_user_data":read_user_data, 
                "write_user_data":write_user_data,
                "wiki":wiki,
                "internet_search_tool":internet_search_tool,
            }  
            messages.append(response_message)  # extend conversation with assistant's reply
            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                print(f"model wants to call {function_name}")
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
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
        return {"response":response_message.message.content,"messages":messages}



class Session():
    def compl_send_await(self,msg):
        resp=compl_send_await(self.websocket,self.mcp,self.manager,self.session_id,msg)
        return resp
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
        result =  flow
        print(f"Generated fun fact: {result}")

# database_manager:
#   role: >
#     {topic} Senior Data Researcher
#   goal: >
#     Find the most relevant items using intelligent vector semantic search
#   backstory: >
#     You're a trained data analyst who accesses the vector database and finds the most relevant {topic} items.
#     You want to help the user finding suiting items and therefore you know how to find the right keywords. 
#     Known for your ability to find the most relevant
#     information and present it in a clear and concise manner.