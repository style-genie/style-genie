import base64
import logging
import os

import requests
import streamlit as st
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env.local")

def initialize_session_state() -> None:
    """Initialize the session state variables if they are not already set."""
    env_vars = {
        "BACKEND_API": "BACKEND_API",
    }
    for var, env in env_vars.items():
        if var not in st.session_state:
            value = os.getenv(env)
            if value is None:
                message = "Missing env variable: " + env
                logger.exception(message)
                # raise ValueError(message)
            st.session_state[var] = value

# Initialize the session state variables
initialize_session_state()



def send_compose_request(
        user_img_bytes: bytes,
        clothing_item_img_bytes: bytes,
) -> None:
    """Request a composite image."""
    backend_api = st.session_state.get("BACKEND_API", "")
    if not backend_api:
        st.error("Backend API not configured.")
        return

    endpoint = backend_api.rstrip("/") + "/compose"

    # Base64 encode the bytes to strings
    user_img_str = base64.b64encode(user_img_bytes).decode("utf-8")
    clothing_item_img_str = base64.b64encode(clothing_item_img_bytes).decode("utf-8")

    payload = {
        "user_img": user_img_str,
        "clothing_item_img": clothing_item_img_str,
    }

    with st.spinner("Generating composite image..."):
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=60000,
            )
            response.raise_for_status()
            st.image(response.content, caption="Composite Image")
        except requests.RequestException as e:
            st.error(f"Error generating composite image: {e}")


user_img_filepath = st.file_uploader(
    label="Choose a user image",
    key="user_img_filepath",
)
clothing_item_img_filepath = st.file_uploader(
    label="Choose a cloth item",
    key="clothing_item_img_filepath",
)

button = st.button("Compose")

if button and user_img_filepath is not None and clothing_item_img_filepath is not None:
    # To read file as bytes:
    user_img_bytes = user_img_filepath.getvalue()
    clothing_item_img_bytes = clothing_item_img_filepath.getvalue()
    send_compose_request(
        user_img_bytes,
        clothing_item_img_bytes,
    )
