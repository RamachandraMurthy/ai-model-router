from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import asyncio
import json

from utils import select_llm_model, call_llm_api, verify_api_key, rate_limiter
from celery_worker import process_async_workflow
from models import ChatHistory
from database import SessionLocal, init_db
from config import API_KEY

# Initialize the database
init_db()

app = FastAPI(title="Multi-Model AI Automation Platform")

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Connection Manager for Real-Time Logs ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Global Middleware for Rate Limiting ---
@app.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    rate_limiter(request)
    response = await call_next(request)
    return response

# --- REST API Endpoints ---

@app.get("/")
def root():
    return {"message": "Welcome to the Multi-Model AI Automation Platform API"}

@app.post("/chat", dependencies=[Depends(verify_api_key)])
async def chat_endpoint(request: Request, payload: dict):
    """
    Handles chat requests. Expects JSON payload with "user" and "prompt".
    """
    db = SessionLocal()
    try:
        user = payload.get("user", "anonymous")
        prompt = payload.get("prompt")
        if not prompt:
            return JSONResponse(status_code=400, content={"detail": "Prompt is required"})
        
        # Select best-fit model
        model = select_llm_model(prompt)
        
        # Call the selected LLM API (simulated)
        llm_result = call_llm_api(model, prompt)
        
        # Trigger asynchronous workflow processing
        process_async_workflow.delay(prompt, model)
        
        # Save the chat interaction in the database
        chat_entry = ChatHistory(
            user=user,
            prompt=prompt,
            response=llm_result["response"],
            model_used=model,
            tokens_used=llm_result["tokens_used"],
            cost=llm_result["cost"]
        )
        db.add(chat_entry)
        db.commit()
        
        # Broadcast log message to connected WebSocket clients
        asyncio.create_task(manager.broadcast(f"User '{user}' used model {model}"))
        
        return {
            "user": user,
            "model_used": model,
            "response": llm_result["response"],
            "tokens_used": llm_result["tokens_used"],
            "cost": llm_result["cost"]
        }
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    finally:
        db.close()

@app.get("/analytics", dependencies=[Depends(verify_api_key)])
def analytics_endpoint():
    """
    Returns aggregated analytics from chat history.
    """
    db = SessionLocal()
    try:
        total_chats = db.query(ChatHistory).count()
        total_tokens = sum(entry.tokens_used for entry in db.query(ChatHistory).all())
        total_cost = sum(entry.cost for entry in db.query(ChatHistory).all())
        return {"total_chats": total_chats, "total_tokens": total_tokens, "total_cost": total_cost}
    except Exception as e:
        logger.error(f"Error in analytics_endpoint: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    finally:
        db.close()

# --- WebSocket Endpoint for Real-Time Logs ---
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    try:
        # Accept the connection first
        await websocket.accept()
        
        # Get the first message which should contain authentication
        data = await websocket.receive_text()
        
        # Try to parse as JSON for authentication
        try:
            auth_data = json.loads(data)
            if auth_data.get("type") == "authentication":
                api_key = auth_data.get("api_key")
                if api_key != API_KEY:
                    await websocket.send_text("Authentication failed: Invalid API key")
                    await websocket.close(code=1008)
                    return
                
                # Authentication successful
                await websocket.send_text("Authentication successful")
                await manager.connect(websocket)
                
                # Keep the connection alive
                while True:
                    data = await websocket.receive_text()
                    # Just echo back for now
                    await websocket.send_text(f"Echo: {data}")
            else:
                await websocket.send_text("Authentication required")
                await websocket.close(code=1008)
        except json.JSONDecodeError:
            await websocket.send_text("Invalid authentication format")
            await websocket.close(code=1008)
            
    except WebSocketDisconnect:
        # This will be called if the client disconnects
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
