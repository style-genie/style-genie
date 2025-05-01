import logging

logger = logging.getLogger(__name__)
import litellm
import json
import subprocess
import json
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
import requests

# Load and set environment variables directly
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value
with open("./../../data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
class ModelContextProtocol:
    def __init__(self):
        self.default_host = ""
        self.PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
        if(self.PINECONE_API_KEY == ""):
            raise ValueError("PINECONE_API_KEY environment variable not set")
        self.INDEX_HOST = os.environ.get("INDEX_HOST", "" )
        if self.INDEX_HOST == "":
            raise ValueError("INDEX_HOST environment variable not set")
        self.NAMESPACE = os.environ.get("NAMESPACE", "__default__")
        #   ----------> CHECKING IF OLLAMA_HOST IS SET <----------
        self.OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
        if self.OLLAMA_API_KEY != "":
            self.register_host("ollama_local",self.OLLAMA_HOST,self.OLLAMA_API_KEY)
            self.default_host = self.OLLAMA_HOST
        #   ----------> CHECKING IF OPENWEBUI_HOST IS SET <----------
        self.OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/ollama")
        self.OPENWEBUI_API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
        if self.OPENWEBUI_API_KEY != "":
            self.register_host("openwebui",self.OPENWEBUI_HOST,self.OPENWEBUI_API_KEY)
            self.default_host = self.OPENWEBUI_HOST
        #   ----------> CHECKING IF GEMINI_HOST IS SET <----------
        self.GEMINI_HOST = os.environ.get("GEMINI_HOST", "gemini/gemini-pro")
        self.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "" )
        if self.GEMINI_API_KEY != "":
            self.register_host("gemini",self.GEMINI_HOST,self.GEMINI_API_KEY)
            self.default_host = self.GEMINI_HOST

    
    def register_host(self, host_type, host_url, api_key, arguments=[]):
        """Registers a host after the server has started."""
        if host_type == "ollama_local":
            self.OLLAMA_HOST = host_url
            self.OLLAMA_API_KEY = api_key
        elif host_type == "openwebui":
            self.OPENWEBUI_HOST = host_url
            self.OPENWEBUI_API_KEY = api_key
        elif host_type == "gemini":
            self.GEMINI_HOST = host_url
            self.GEMINI_API_KEY = api_key
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
    def mcp_completion(self, message, host="gemini"):
        """Tests parallel function calling."""
        try:
            # Step 1: send the conversation and available functions to the model
            messages = [
                {"role": "system", "content": "You are a fashion instructor."},
                {"role": "user", "content": message},
            ]
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
            try:
                response = litellm.completion(
                    model=self.models[0],
                    messages=messages,
                    api_key=self.OPENWEBUI_API_KEY,
                    base_url=self.OLLAMA_HOST,
                    timeout=60,
                    tools=tools,
                    tool_choice="auto",  # auto is default, but we'll be explicit
                )
                print("\nFirst LLM Response:\n", response)
                response_message = response.choices[0].message
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
                    second_response = litellm.completion(
                        model=self.models[0],
                        messages=messages,
                        api_key=self.OPENWEBUI_API_KEY,
                        base_url=self.OLLAMA_HOST,
                        timeout=60,
                        tools=tools,
                        tool_choice="auto",  # auto is default, but we'll be explicit
                    )  # get a new response from the model where it can see the function response
                    print("\nSecond LLM response:\n", second_response)
                    return second_response
            except Exception as e:
                print(f"Error in inner try: {e}")
                return f"Error in inner try: {e}"
        except Exception as e:
            print(f"Error occurred: {e}")
            return f"Error occurred: {e}"
    def get_openwebui_client(self):
        if not self.OPENWEBUI_API_KEY:
            raise ValueError("OPENWEBUI_API_KEY environment variable not set")
        logger.info(f"Creating OpenWebUI client with host: {self.OPENWEBUI_HOST}")
        class OpenWebUIClient:
            def __init__(self, host, api_key):
                self.host = host
                self.headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                }
            def chat(self, model, messages, temperature=0.7, max_tokens=150):
                url = f"{self.host}/api/chat/completions"
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                try:
                    response = requests.post(url, headers=self.headers, json=payload)
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    logger.error(f"Failed to connect to {self.host}: {str(e)}")
                    raise
        client = OpenWebUIClient(self.OPENWEBUI_HOST, self.OPENWEBUI_API_KEY)
        # Test connection
        logger.debug(f"Testing connection to OpenWebUI server at {self.OPENWEBUI_HOST}")
        try:
            response = client.chat(
                model="deepseek/chat_V3", messages=[{"role": "system", "content": "connection test"}]
            )
            logger.info(f"Successfully connected to {self.OPENWEBUI_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.OPENWEBUI_HOST}: {str(e)}")
            raise
        return client
