import base64
import io
import logging
import os
import dotenv
from fastapi import FastAPI, Query, middleware
from fastapi.middleware import cors
from pydantic import BaseModel
from src.ai.img_to_img import ImgToImg
from src.mcp.mcp import Session
import uvicorn
import sys
Sessions=[]
# sys.path.append(".")
logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
dotenv.load_dotenv("./.env.local")
# Create FastAPI app
app = FastAPI(
    title="StyleGenie API",
    description="AI-Powered Style Assistant API",
    version="0.1.0",
)
# Get allowed origins from environment variable or use default
allowed_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
# Add CORS middleware
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ComposeRequestBody(BaseModel):
    user_img: str
    clothing_item_img: str
# Routes implementation
@app.post("/compose")
async def compose(
    request_body: ComposeRequestBody,
) -> bytes:
    """Generates a composite image based on user image and clothing item.

    Args:
        request_body (ComposeRequestBody): The request body containing the user image and clothing item image.

    Returns:
        bytes: The generated composite image.
    """
    logger.info("Start %s ...", "compose")
    # Decode base64 string into bytes and wrap in a BytesIO with a proper file name and extension.
    user_img_file = io.BytesIO(base64.b64decode(request_body.user_img))
    user_img_file.name = "user_img.png"  # Ensure a supported image format
    clothing_item_img_file = io.BytesIO(base64.b64decode(request_body.clothing_item_img))
    clothing_item_img_file.name = "clothing_item_img.png"  # Ensure a supported image format
    # generate composit image
    img_to_img = ImgToImg()
    return img_to_img.generate(
        reference_img_list=[
            user_img_file,
            clothing_item_img_file,
        ],
    )
class create_session_request(BaseModel):
    model: str
    max_tokens: int
    temperature: float
    max_recursion_depth: int
@app.get("/create_session")
async def create_session(response_model=create_session_request):
    """Creates a new session.
    Args:
        model (str): The model to use (e.g., local_ollama, gemini, openwebui).
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): The temperature to use for sampling.
        max_recursion_depth (int): The maximum number of recursion steps.
        
    Example:
        curl "http://localhost:1500/create_session?model=gemini&max_tokens=150&temperature=0.7&max_recursion_depth=10"

    Returns:
        a session id
    """
    session_id = len(Sessions)
    session = Session(max_tokens=response_model.max_tokens,temperature=response_model.temperature,max_recursion_depth=response_model.max_recursion_depth)
    Sessions.append(session)
    return {"session_id": str(session_id)}

class test_vector_db_request(BaseModel):
    query: str
    session_id: int
@app.get("/test_vector_db", response_model=test_vector_db_request)
async def test_vector_db(response_model):
    """Tests the vector database.
    Args:
        session_id (int): The session id.
        query (str): The query to use to test the vector database (e.g., "What is a good casual outfit?").
        
    Example:
        curl "http://localhost:1500/test_vector_db?query=shoes%20trousers?"

    Returns:
        a json object: {"result": str(result)}
    """
    
    result = Sessions[response_model.session_id].mcp.fetch_elements_from_vector_db(response_model.query)
    return {"recommendation": str(result)}



if __name__ == "__main__":
    print("Starte Uvicorn Server direkt aus main.py...")
    uvicorn.run(
        # WICHTIG: Für reload=True ist es besser, den Import-String anzugeben.
        # Uvicorn muss wissen, wie es deine App neu laden kann.
        "main:app",
        host="127.0.0.1",
        port=1500,
        reload=True  # Aktiviert Auto-Reload bei Code-Änderungen (gut für Entwicklung)
        # log_level="info" # Optional: Setze das Logging-Level
    )






