import base64
import io
import logging
import os
import dotenv
import json
import sys
from src.ai.img_to_img import ImgToImg
from src.mcp.mcp import Session
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

    async def broadcast_task_update(self, task_id: str, status: str, progress: float):
        update = {"task_id": task_id, "status": status, "progress": progress}
        for ws in self.active_connections.values():
            await ws.send_json(update)

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

class TaskRequest(BaseModel):
    session_id: str
    model: str
    max_tokens: int
    temperature: float
    max_recursion_depth: int

@app.post("/start_task")
async def start_task(request: TaskRequest):
    task_id = str(uuid4())
    task = Task(
        id=task_id,
        status="pending",
        progress=0.0,
        children=[]
    )
    manager.tasks[task_id] = task
    
    async def execute_recursive_tasks(task: Task, depth: int = 0):
        # Hier Ihre rekursive Logik implementieren
        await asyncio.sleep(1)  # Simuliere Arbeit
        
        # Fortschritt aktualisieren
        task.progress += 25
        await manager.broadcast_task_update(task.id, task.status, task.progress)
        
        if depth < request.max_recursion_depth:
            child_task = Task(
                id=str(uuid4()),
                status="pending",
                progress=0.0,
                children=[]
            )
            task.children.append(child_task)
            
            # Rekursiver Aufruf
            await execute_recursive_tasks(child_task, depth + 1)
            
            # Fortschritt aktualisieren
            task.progress += 25
            await manager.broadcast_task_update(task.id, task.status, task.progress)
    
    # Task im Hintergrund ausführen
    asyncio.create_task(execute_recursive_tasks(task))
    
    return {"task_id": task_id}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Hier können Sie Nachrichten vom Client verarbeiten
            await manager.send_personal_message(session_id, {"message": "Received"})
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/stream_progress/{task_id}")
async def stream_progress(task_id: str):
    return StreamingResponse(stream_task_progress(task_id))









@app.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    session = uuid4()
    data = SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"

# ------> CREATE_AGENT_SESSION <----------
class create_agent_session_args(BaseModel):
    user: str
    model: str
    max_tokens: int
    temperature: float
    max_recursion_depth: int
    
@app.get("/create_agent_session")
async def create_agent_session(response_model=create_agent_session_args):
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

    session_id = len(Sessions)
    session = Session(max_tokens=response_model.max_tokens,temperature=response_model.temperature,max_recursion_depth=response_model.max_recursion_depth)
    Sessions.append(session)
    return {"session_id": str(session_id)}




    # response=StreamingResponse(
    # content,
    # status_code=200,
    # headers=None,
    # media_type=None,
    # background=None,
    # )
# ------> TEST_VECTOR_DB <----------
class test_vector_db_args(BaseModel):
    query: str
    session_id: int
    
@app.get("/test_vector_db", response_model=test_vector_db_args)
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






