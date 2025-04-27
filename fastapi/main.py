from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from typing import List, Dict, Optional
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Environment variables
INDEX_HOST = "sg-va8ozeb.svc.aped-4627-b74a.pinecone.io"
NAMESPACE = "__default__"
PINECONE_API_KEY = "pcsk_6x3uAk_9t8PaNmdJx3kTVMJ5PENnRhQXYgdRJ4QZoQA79krQmpcXyL9XmXxWKEBxmLqXYP"

# Load pinecone_data.json
try:
    with open("/home/ji/Dokumente/fashion/StyleRecommendation/pinecone_data.json", "r") as f:
        pinecone_data = json.load(f)
except FileNotFoundError:
    pinecone_data = {}
except json.JSONDecodeError:
    pinecone_data = {}

class SearchRequest:
    query: str
    top_k: int = 5

class SearchResult:
    score: float
    metadata: Dict[str, str]

@app.route("/health", methods=['GET'])
def health_check():
    """Überprüft ob der Server und die Pinecone-Verbindung funktioniert"""
    return jsonify({"status": "healthy", "index": "sg"}), 200

@app.route("/search", methods=['POST'])
def search_items():
    """Sucht nach ähnlichen Fashion-Items"""
    try:
        data = request.get_json()
        query = data.get("query")
        top_k = data.get("top_k", 2)

        if not query:
            return jsonify({"error": "Query must be provided in the request."}), 400
        
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
        # print(stdout)
        # Check for errors
        # if stderr:
        #     print(f"Curl Error: {stderr.decode()}")
        #     return jsonify({"error": stderr.decode()}), 500

        # # Parse the JSON response
        results = json.loads(stdout.decode())

        # # Format the results
        formatted_results = []
        #print(results["result"]["hits"])
        for match in results["result"]["hits"]:
            index = match['_id']
            print(index)
            score = match['_score']
            print(score)
            # print(pinecone_data[int(index)])
            item=    {
                    "score": score,
                    **(pinecone_data[int(index)]) 
                }
            print(item)
            print("--------------------------")
            formatted_results.append(item)
            
        print(formatted_results)
        return formatted_results
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1500, debug=True)
