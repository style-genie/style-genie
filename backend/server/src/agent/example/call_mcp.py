import requests
import argparse
import os
from dotenv import dotenv_values
from pathlib import Path

# Load and set environment variables directly
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value

# OpenWebUI Configuration
OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/api")
OPENWEBUI_API_KEY = os.environ.get("OPENWEBUI_API_KEY")

# Define the API endpoint
API_ENDPOINT = f"{OPENWEBUI_HOST}/chat/completions"

# Initialize argument parser
parser = argparse.ArgumentParser(description="Call MCP server with specified model and message.")
parser.add_argument(
    "--model",
    type=str,
    default="ollama/gemma3:27b",
    help="Specify the model to use (e.g., ollama/gemma3:27b, gemini, openwebui).",
)
parser.add_argument(
    "--message", type=str, required=True, help="The message to send to the MCP server."
)

args = parser.parse_args()

# Prepare the headers with the Bearer token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
}

# Prepare the payload
payload = {
    "model": args.model,
    "messages": [{"role": "user", "content": args.message}],
    "temperature": 0.7,
    "max_tokens": 150,
}

try:
    # Make the API request
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Print the response
    print(response.json())

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
