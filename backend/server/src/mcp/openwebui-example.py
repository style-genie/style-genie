from pathlib import Path
from dotenv import dotenv_values
import os
import logging
import requests

logger = logging.getLogger(__name__)

# Load and set environment variables directly
config = dotenv_values(Path(__file__).parent.parent.parent / ".env")
for key, value in config.items():
    os.environ[key] = value

# Ollama Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "https://chat.kxsb.org/ollama")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

# OpenWebUI Configuration
OPENWEBUI_HOST = os.environ.get("OPENWEBUI_HOST", "https://chat.kxsb.org/api")
OPENWEBUI_API_KEY = OLLAMA_API_KEY#os.environ.get("OPENWEBUI_API_KEY")


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


def get_ollama_client():
    from ollama import Client

    if not OLLAMA_HOST:
        raise ValueError("OLLAMA_HOST environment variable not set")

    logger.info(f"Creating Ollama client with host: {OLLAMA_HOST}")

    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
        logger.info("Added API key to headers")

    client = Client(host=OLLAMA_HOST, headers=headers)

    # Test connection and log destination
    logger.debug(f"Testing connection to Ollama server at {OLLAMA_HOST}")
    try:
        response = client.chat(
            model="phi4", messages=[{"role": "system", "content": "connection test"}]
        )
        logger.info(f"Successfully connected to {OLLAMA_HOST}")
    except Exception as e:
        logger.error(f"Failed to connect to {OLLAMA_HOST}: {str(e)}")
        raise

    return client