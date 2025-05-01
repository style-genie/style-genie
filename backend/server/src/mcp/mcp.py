import logging

logger = logging.getLogger(__name__)
import litellm
import json
import subprocess
import json
import os
import sys
import argparse
from pathlib import Path
from dotenv import dotenv_values
import requests
from litellm import Cache

# Load and set environment variables directly
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value
with open("./../../data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Ollama Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "https://chat.kxsb.org/ollama")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

# OpenWebUI Configuration
OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/api")
OPENWEBUI_API_KEY = os.environ.get("OPENWEBUI_API_KEY")

# Initialize argument parser
parser = argparse.ArgumentParser(description="Run MCP server with model selection.")
parser.add_argument(
    "--model",
    type=str,
    default="ollama/gemma3:27b",
    help="Specify the model to use (e.g., ollama/gemma3:27b, gemini, openwebui).",
)
args = parser.parse_args()

print(litellm.supports_function_calling(model=args.model))
try:
# Registrierung des Modells für Funktion-Calls
    litellm.register_model(
        model_cost={
            args.model: {
                "supports_function_calling": True,
                "api_key": OPENWEBUI_API_KEY,
                "api_base": OLLAMA_HOST,
                "base_url": "https://chat.kxsb.org/api",
            }
        }
    )
    print("registered model")
except Exception as e:
    print(f"Failed to register model: {e}")
    sys.exit(1)

def fetch_elements_from_vector_db(query):
    """Fetches elements from the vector database based on the given query."""
    INDEX_HOST = os.environ.get("INDEX_HOST", "sg-va8...")
    NAMESPACE = os.environ.get("NAMESPACE", "__default__")
    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "pcsk_...")
    top_k = 2
    if not query:
        return {"error": "Query must be provided in the request."}
    # Construct the curl command
    curl_command = f"""curl "https://{INDEX_HOST}/records/namespaces/{NAMESPACE}/search" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      -H "Api-Key: {PINECONE_API_KEY}" \
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


def get_json_element_by_id(id):
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



def mcp_completion(message):
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
                            }
                        },
                        "required": ["id"],
                        "additionalProperties": False,
                    },
                },
            },
        ]
        try:
            response = litellm.completion(
                model=args.model,
                messages=messages,
                api_key=OPENWEBUI_API_KEY,
                base_url=OLLAMA_HOST,
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
                    "get_json_element_by_id": get_json_element_by_id
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
                        function_response = function_to_call(
                            location=function_args.get("location"), unit=function_args.get("unit")
                        )
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response
                second_response = litellm.completion(
                    model=args.model,
                    messages=messages,
                    api_key=OPENWEBUI_API_KEY,
                    base_url=OLLAMA_HOST,
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




def get_openwebui_client():
    if not OPENWEBUI_API_KEY:
        raise ValueError("OPENWEBUI_API_KEY environment variable not set")

    logger.info(f"Creating OpenWebUI client with host: {OPENWEBUI_HOST}")

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

    client = OpenWebUIClient(OPENWEBUI_HOST, OPENWEBUI_API_KEY)

    # Test connection
    logger.debug(f"Testing connection to OpenWebUI server at {OPENWEBUI_HOST}")
    try:
        response = client.chat(
            model="deepseek/chat_V3", messages=[{"role": "system", "content": "connection test"}]
        )
        logger.info(f"Successfully connected to {OPENWEBUI_HOST}")
    except Exception as e:
        logger.error(f"Failed to connect to {OPENWEBUI_HOST}: {str(e)}")
        raise

    return client



if __name__ == "__main__":

    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = "What should I wear to a party?"
    mcp_completion(message)
