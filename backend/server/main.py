import base64
import io
import logging
import os
import dotenv
import json
import sys
from src.ai.img_to_img import ImgToImg
from backend.server.src.agent.session import Session
from fastapi.middleware import cors
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, middleware, Response, HTTPException
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
    UJSONResponse,
)
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass
from pydantic import BaseModel
import uvicorn
from uuid import uuid4
from uuid import UUID


#   --------> LOGGER <--------
logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)
#   --------> SESSIONS <--------
Sessions=[]

# --------> Load environment variables <--------
dotenv.load_dotenv("./.env.local")

# -------> Create FastAPI app <------
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

# ----------> USER_SESSION <----------
class SessionData(BaseModel):
    username: str

cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, SessionData]()
@dataclass
class Task:
    id: str
    status: str
    progress: float
    children: List['Task']
    
# ----------> WEBSOCKET MANAGER <----------
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.tasks: Dict[str, Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
        else:
            raise WebSocketDisconnect(code=404, reason="Session not found")

    async def broadcast_task_update(self, task_id: str, status: str, progress: float):
        update = {"task_id": task_id, "status": status, "progress": progress}
        for ws in self.active_connections.values():
            await ws.send_json(update)

    async def receive_text(self, websocket: WebSocket):
        """Receives text from the WebSocket in a parallel async task and returns a promise."""
        try:
            data = await websocket.receive_text()
            return data
        except WebSocketDisconnect:
            return None
manager = ConnectionManager()

async def stream_task_progress(task_id: str):
    while True:
        task = manager.tasks.get(task_id)
        if task:
            yield json.dumps({
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress
            })
        await asyncio.sleep(1)

@app.post("/create_session/{name}")
async def create_session(name: str, response: Response):
    session = uuid4()
    data = SessionData(username=name)
    await backend.create(session, data)
    cookie.attach_to_response(response, session)
    return f"created session for {name}"

# ------> CREATE_AGENT_SESSION <----------
def create_agent_session(manager,websocket, session_id, args={}):
    """Creates a agent new session.
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
    session = Session(manager,websocket, session_id=session_id, **args)
    Sessions.append(session)
    
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        create_agent_session(manager,websocket,session_id=session_id)
        await asyncio.sleep(100)
        #data = await manager.receive_text(websocket)
        # while True:
            
        #     if data is None:
        #         break  # Exit the loop if the WebSocket is disconnected
        #     try:
        #         message = json.loads(data)
        #         if message.get('type') == 'request_session':
        #             logger.info(f"Session requested from {session_id}")
        #             # Session creation is already handled above, so no need to do anything here
        #             await manager.send_personal_message(session_id, {"message": "Session created successfully"})
        #         else:
        #             logger.info(f"Received message from {session_id}: {data}")
        #             await manager.send_personal_message(session_id, {"message": f"Server received: {data}"})
        #         
            # except json.JSONDecodeError:
                # logger.error(f"Invalid JSON received from {session_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"Error creating agent session: {e}")
        manager.disconnect(session_id)


# ------> Compose  <------
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


# # ------> TEST_VECTOR_DB <----------
# class test_vector_db_args(BaseModel):
#     query: str
#     session_id: int
# @app.get("/test_vector_db", response_model=test_vector_db_args)
# async def test_vector_db(response_model):
#     """Tests the vector database.
#     Args:
#         session_id (int): The session id.
#         query (str): The query to use to test the vector database (e.g., "What is a good casual outfit?").
        
#     Example:
#         curl "http://localhost:1500/test_vector_db?query=shoes%20trousers?"

#     Returns:
#         a json object: {"result": str(result)}
#     """
    
#     result = Sessions[response_model.session_id].mcp.fetch_elements_from_vector_db(response_model.query)
#     return {"recommendation": str(result)}
