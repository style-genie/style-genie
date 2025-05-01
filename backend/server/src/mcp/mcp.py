import logging

logger = logging.getLogger(__name__)
import litellm
import json
import subprocess
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
import requests
import json
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
import requests
instruction_message ={"role": "system", "content": """
                    You are a fashion instructor. 
                    You must help the user to find the perfect outfits that match their preferences. 
                    Here are some important instructions you must follow:
                    - document your steps and output in on readable json format.
                    - your output must be a json object.
                    - your output must have the same format as the example:
                        output = {
                        "achievements": ['''
                            - step 1: ask the user for their preferences
                        ''',],
                        "next_steps:'''
                            - step 2: use the get_json_element_by_id function to get the data from data.json
                            - step 3: use the fetch_elements_from_vector_db function to get the data from the vector database
                        ''',
                        "user_feedback_required": False,
                        "markdown_media_portal":'''
                            I found some addionation for you that i wanna share with you:
                            ## Clothing recommendation
                            - i was looking for some darker colors that mach your bright hair
                            - for the trouser i selected a blue color as you wanted
                            ### Trend insights
                            - the nike sportswear collection is very popular right now, i collected some data from the internet for you:
                            - image: !(image)[https://images.unsplash.com/photo]
                            - forbes reported that nike sportswear is the most popular brand in the world:
                                - https://www.forbes.com/sites/forbestechcouncil/2022/08/02/nike-sportswear-earnings-2022/#6b2e1b5d7f4f
                                > the also reported that nike sportswear was sold more than any other brand in the world, here is the data:
                                - https://www.forbes.com/sites/forbestechcouncil/2022/08/02/nike-sportswear-earnings-2022/#6b2e1b5d7f4f
                        '''
                        "tools_required_next": ["get_json_element_by_id", "fetch_elements_from_vector_db"],
                        "important_notes": "You must use the tools in order to get the data. The user noted that it is important to find armani only!",
                        "task_finished": False,
                        "step_failed": False
                        }
                    """
}
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
# Load and set environment variables directly
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value
with open("./../../data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
class ModelContextProtocol:
    def __init__(self):
        self.models = {}
        #   ----------> CHECKING IF PINECONE_API_KEY IS SET <----------
        self.PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
        if(self.PINECONE_API_KEY == ""):
            raise ValueError("PINECONE_API_KEY environment variable not set")
        self.INDEX_HOST = os.environ.get("INDEX_HOST", "" )
        if self.INDEX_HOST == "":
            raise ValueError("INDEX_HOST environment variable not set")
        self.NAMESPACE = os.environ.get("NAMESPACE", "__default__")
        
        #   ----------> CHECKING IF OLLAMA_HOST IS SET <----------
        OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
        if OLLAMA_API_KEY != "":
            self.register_host("ollama_local",OLLAMA_HOST,OLLAMA_API_KEY)

        #   ----------> CHECKING IF OPENWEBUI_HOST IS SET <----------
        OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/ollama")
        OPENWEBUI_API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
        if OPENWEBUI_API_KEY != "":
            self.register_host("openwebui",OPENWEBUI_HOST,OPENWEBUI_API_KEY)
            
        #   ----------> CHECKING IF GEMINI_HOST IS SET <----------
        GEMINI_HOST = os.environ.get("GEMINI_HOST", "gemini/gemini-pro")
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "" )
        if GEMINI_API_KEY != "":
            self.register_host("gemini",GEMINI_HOST,GEMINI_API_KEY)
            

    
    def register_host(self, host_type, host_url, api_key, arguments=[]):
        """Registers a host after the server has started."""
        if host_type == "ollama_local":
            self.models["ollama_local"]={"api_key": api_key, "api_base": host_url, "model":"ollama/gemma3:27b", **arguments}
        elif host_type == "openwebui":
            self.models["openwebui"]={"api_key": api_key, "api_base": host_url,"model":"ollama/gemma3:27b", **arguments}
        elif host_type == "gemini":
            self.models["gemini"]={"api_key": api_key, "api_base": host_url, "model": "gemini/gemini-pro",**arguments}
        else:
            raise ValueError("Invalid host type. Must be 'ollama_local', 'gemini' or 'openwebui'.")
        try:
                # we use base_url since api_base seems to be a deprecated argument
                litellm.register_model(
                    model_cost={
                        "openwebui": {
                            "supports_function_calling": True,
                            "api_key": api_key,
                            #"api_base": self.OLLAMA_HOST,
                            "base_url": host_url,
                            **arguments,
                        }
                    }
                )
                print(f"Registered OpenWebUI host: {host_url}")
        except Exception as e:
            print(f"Failed to register OpenWebUI host {host_url}: {e}")
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
    def mcp_completion(self, messages, model="gemini",step=1):
        """Tests parallel function calling."""
        try:
            response = litellm.completion(
                model=self.models[model],
                messages=messages,
                api_key=self.models[model]["api_key"],
                base_url=self.models[model]["base_url"],
                tools=tools,
                tool_choice="auto",  # auto is default, but we'll be explicit
            )
            print("\nLLM Response:\n", response)
            response_message = response.choices[0].message
            json_response = json.loads(response_message.content)    
            tool_calls = response_message.tool_calls
            print("\nLength of tool calls", len(tool_calls))
            # Step 2: check if the model wanted to call a function
            if tool_calls:
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
            json_response["messages"] = messages
            json_response["step"] = step+1
            return json_response
        except Exception as e:
            print(f"Error in inner try: {e}")
            return f"Error in inner try: {e}"

class Session:
    def __init__(self, max_tokens=150,temperature=0.7,max_recursion_depth=10):
        self.mcp = ModelContextProtocol()
        self.models = self.mcp.models
        self.history = []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_recursion_depth = max_recursion_depth
        self.conversation_history = []
        self.messages = []
    def start(self, message, model="gemini"):
        try:
            messages = [
                instruction_message,
                {
                    "role": "history",
                    "content": message.history,
                },
            ]
            json_response = self.mcp.mcp_completion(
                messages=messages,
                model=model,
            )
            self.conversation_history.extend(json_response["messages"])
            if(json_response.get("task_finished")):
                return json_response
            else:
                print(f"""
--------------------------------------
        Task not finished
        {json_response}
--------------------------------------
""") 
                json_response["messages"]=messages
                if(json_response["step"]>self.max_recursion_depth and not json_response.get("step_failed")):
                    return json_response
                else:
                    return self.mcp.mcp_completion(
                        messages=json.dumps(json_response),
                        model="gemini",
                        step=json_response["step"]
                    )
        except Exception as e:
            print(f"Error in inner try: {e}")
            return f"Error in inner try: {e}"

        
        
        
        
        
        
        
        
        
        
        
        
        
        
# ----------------> Examples <-------------------
        
        
    # def get_openwebui_client(self):
    #     if not self.models["openwebui"]["api_key"]:
    #         raise ValueError("OPENWEBUI_API_KEY environment variable not set")
    #     class OpenWebUIClient:
    #         def __init__(self, host, api_key):
    #             self.host = host
    #             self.headers = {
    #                 "Content-Type": "application/json",
    #                 "Authorization": f"Bearer {api_key}",
    #             }
    #         def chat(self, model, messages, temperature=0.7, max_tokens=150):
    #             url = f"{self.host}/api/chat/completions"
    #             payload = {
    #                 "model": model,
    #                 "messages": messages,
    #                 "temperature": temperature,
    #                 "max_tokens": max_tokens,
    #             }
    #             try:
    #                 response = requests.post(url, headers=self.headers, json=payload)
    #                 response.raise_for_status()
    #                 return response.json()
    #             except Exception as e:
    #                 logger.error(f"Failed to connect to {self.host}: {str(e)}")
    #                 raise
    #     client = OpenWebUIClient(self.OPENWEBUI_HOST, self.OPENWEBUI_API_KEY)
    #     # Test connection
    #     logger.debug(f"Testing connection to OpenWebUI server at {self.OPENWEBUI_HOST}")
    #     try:
    #         response = client.chat(
    #             model="deepseek/chat_V3", messages=[{"role": "system", "content": "connection test"}]
    #         )
    #         logger.info(f"Successfully connected to {self.OPENWEBUI_HOST}")
    #     except Exception as e:
    #         logger.error(f"Failed to connect to {self.OPENWEBUI_HOST}: {str(e)}")
    #         raise
    #     return client
