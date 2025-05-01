import litellm
import json
import subprocess
import json
import os
print(litellm.supports_function_calling(model="ollama/gemma3:27b"))
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "https://chat.kxsb.org/ollama")
OPENWEBUI_KEY=os.environ.get("OPENWEBUI_KEY", "")


# Registrierung des Modells für Funktion-Calls
litellm.register_model(model_cost={
    "ollama/gemma3:27b": {
        "supports_function_calling": True
    },
})
with open('/lite/data.json', 'r') as f:
    data = json.load(f)
def fetch_elements_from_vector_db(query):
    """
    Fetches elements from the vector database based on the given query.
    """
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
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # Check for errors
    if stderr:
        print(f"Curl Error: {stderr.decode()}")
        return {"error": stderr.decode()}
    print(stdout.decode())
    results = json.loads(stdout.decode())
    formatted_results = []
    for match in results["result"]["hits"]:
        index = match['_id']
        print(index)
        score = match['_score']
        print(score)
        item=    {
                "score": score,
                **(data[int(index)]) 
            }
        print(item)
        print("--------------------------")
        formatted_results.append(item)
    return formatted_results
def get_json_element_by_id(id):
    """
Gets a JSON element from the file based on the ID.
Args:
id (str): The ID of the element to search for
Returns:
dict: The found JSON element or None if not found    """
    try:
        with open('../data.json', 'r') as f:
            data = json.load(f)
        def find_element(obj, target_id):
            if isinstance(obj, dict):
                if obj.get('id') == target_id:
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

def test_parallel_function_call(message):
    try:
        # Step 1: send the conversation and available functions to the model
        messages = [{"role": "system", "content": "You are a fashion instructor."}, {"role": "user", "content": message}]
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
                            "description": "Die ID des gesuchten Elements"
                        }
                    },
                    "required": ["id"],
                    "additionalProperties": False
                }
            }
         }
        ]
        response = litellm.completion(
            model="ollama/gemma3:27b",
            messages=messages,
            api_key=OPENWEBUI_KEY,
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
                "get_json_element_by_id":get_json_element_by_id
            }  # only one function in this example, but you can have multiple
            messages.append(response_message)  # extend conversation with assistant's reply
            
            
            # Step 4: send the info for each function call and function response to the model
            
                # ----> ITERATING THROUGH TOOL CALLS <-----            
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # ----> FORMATTING FUNCTION RESPONSE <-----
                
                if(function_name == "get_json_element_by_id"):
                     function_response = function_to_call(id=function_args.get("id"))
                else:
                    function_response = function_to_call(
                        location=function_args.get("location"),
                        unit=function_args.get("unit"),
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
                model="ollama/gemma3:27b",
                messages=messages,
                api_key=OPENWEBUI_KEY,
                base_url=OLLAMA_HOST,
                timeout=60,
                tools=tools,
                tool_choice="auto",  # auto is default, but we'll be explicit
            )  # get a new response from the model where it can see the function response
            print("\nSecond LLM response:\n", second_response)
            return second_response
    except Exception as e:
      print(f"Error occurred: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = "What should I wear to a party?"
    test_parallel_function_call(message)



#     def completion(
    #         model: str,
    #         messages: List = [],
    #         # Optional OpenAI params
    #         timeout: Optional[Union[float, int]] = None,
    #         temperature: Optional[float] = None,
    #         top_p: Optional[float] = None,
    #         n: Optional[int] = None,
    #         stream: Optional[bool] = None,
    #         stream_options: Optional[dict] = None,
    #         stop=None,
    #         max_completion_tokens: Optional[int] = None,
    #         max_tokens: Optional[int] = None,
    #         presence_penalty: Optional[float] = None,
    #         frequency_penalty: Optional[float] = None,
    #         logit_bias: Optional[dict] = None,
    #         user: Optional[str] = None,
    #         # openai v1.0+ new params
    #         response_format: Optional[dict] = None,
    #         seed: Optional[int] = None,
    #         tools: Optional[List] = None,
    #         tool_choice: Optional[str] = None,
    #         parallel_tool_calls: Optional[bool] = None,
    #         logprobs: Optional[bool] = None,
    #         top_logprobs: Optional[int] = None,
    #         deployment_id=None,
    #         # soon to be deprecated params by OpenAI
    #         functions: Optional[List] = None,
    #         function_call: Optional[str] = None,
    #         # set api_base, api_version, api_key
    #         base_url: Optional[str] = None,
    #         api_version: Optional[str] = None,
    #         api_key: Optional[str] = None,
    #         model_list: Optional[list] = None,  # pass in a list of api_base,keys, etc.
    #         # Optional liteLLM function params
    #         **kwargs,
    # )
