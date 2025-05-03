import logging
logger = logging.getLogger(__name__)
import json
import subprocess
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
import asyncio
import mysql
import mysql.connector
from mysql.connector import Error
from langchain_community.retrievers import WikipediaRetriever
from duckduckgo_search import DDGS
from langchain.tools import tool



retriever = WikipediaRetriever()

with open("./../../data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def wiki(page):
    docs = retriever.invoke(page)
    print(docs[0].page_content[:400])
    return docs

def internet_search_tool(query: str) -> list:
    """Search Internet for relevant information based on a query."""
    ddgs = DDGS()
    results = ddgs.text(keywords=query, region='wt-wt', safesearch='moderate', max_results=5)
    return results

    
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


def init_user_database(self):
    """Initializes the connection to the user database."""
    try:
        self.db_config = {
            "host": os.environ.get("POSTGRES_HOST", "localhost"),
            "user": os.environ.get("POSTGRES_USER", ""),
            "password": os.environ.get("POSTGRES_PASSWORD", ""),
            "database": os.environ.get("POSTGRES_DB", "")
        }
        
        self.db_connection = mysql.connector.connect(**self.db_config)
        self.cursor = self.db_connection.cursor()
        logger.info("User database connection established.")
        return True
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to database: {err}")
        return False

def read_user_data(self, user_id):
    """Reads user data from the database."""
    try:
        query = "SELECT * FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return {
            "success": True,
            "data": dict(zip([desc[0] for desc in self.cursor.description], result))
        }
    except mysql.connector.Error as err:
        logger.error(f"Error reading user data: {err}")
        return {"success": False, "error": str(err)}

def write_user_data(self, user_id, data):
    """Writes or updates user data in the database."""
    try:
        # Check if user exists
        exists_query = "SELECT COUNT(*) FROM users WHERE user_id = %s"
        self.cursor.execute(exists_query, (user_id,))
        exists = self.cursor.fetchone()[0] > 0
        
        # Create or update user
        if exists:
            query = "UPDATE users SET {} WHERE user_id = %s".format(
                ", ".join([f"{key} = %s" for key in data.keys()])
            )
            params = list(data.values()) + [user_id]
        else:
            query = "INSERT INTO users ({}) VALUES ({})".format(
                ", ".join(data.keys()),
                ", ".join(["%s"] * len(data))
            )
            params = list(data.values())
            
        self.cursor.execute(query, params)
        self.db_connection.commit()
        return {"success": True}
    except mysql.connector.Error as err:
        logger.error(f"Error writing user data: {err}")
        self.db_connection.rollback()
        return {"success": False, "error": str(err)}
        


tools = [            
         {
                "type": "function",
                "function": {
                    "name": "internet_search_tool",
                    "description": "do a internet search",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search": {
                                "type": "string",
                                "search": "the string containing the keywords or setences you want to sarch",
                            },
                            "unit": {"type": "string"},
                        },
                        "required": ["page"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "wiki",
                    "description": "Get a wiki pedia page",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "string",
                                "page": "the name of the page",
                            },
                            "unit": {"type": "string"},
                        },
                        "required": ["page"],
                    },
                },
            },
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
            {
            "type": "function",
            "function": {
                "name": "read_user_data",
                "description": "Reads user data from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_user_data",
                "description": "Writes or updates user data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user"},
                        "data": {"type": "object", "description": "The data to be written"}
                    },
                    "required": ["user_id", "data"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "init_user_database",
                "description": "init_user_database initializes  new user data in the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the new user"},
                        "data": {"type": "object", "description": "The initial user data to create"}
                    },
                    "required": ["user_id", "data"]
                }
            }
        }
    ]