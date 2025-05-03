import os
import json
from typing import List, Dict, Optional
import subprocess
from flask import jsonify

# Environment variables

INDEX_HOST = os.environ.get("INDEX_HOST", "sg-va...")
NAMESPACE = os.environ.get("NAMESPACE", "__default__")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "pcsk_...")

# # Load pinecone_data.json
# try:
#     with open("/root/data.json", "r") as f:
#         pinecone_data = json.load(f)
# except FileNotFoundError:
#     pinecone_data = {}
# except json.JSONDecodeError:
#     pinecone_data = {}

class SearchRequest:
    query: str
    top_k: int = 5

class SearchResult:
    score: float
    metadata: Dict[str, str]


try:
    top_k = 2 
    query="trousers"
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
    
    print(stdout)
    # Check for errors
    # if stderr:
    #     print(f"Curl Error: {stderr.decode()}")
    #     return jsonify({"error": stderr.decode()}), 500

    # # Parse the JSON response
    results = json.loads(stdout.decode())

    # # Format the results
    formatted_results = []
    #print(results["result"]["hits"])
    # for match in results["result"]["hits"]:
    #     index = match['_id']
    #     print(index)
    #     score = match['_score']
    #     print(score)
    #     # print(pinecone_data[int(index)])
    #     item=    {
    #             "score": score,
    #             **(pinecone_data[int(index)]) 
    #         }
    #     print(item)
    #     print("--------------------------")
    #     formatted_results.append(item)
        
    print(formatted_results)
except Exception as e:
    print(e)
    print( jsonify({"error": str(e)}), 500)
