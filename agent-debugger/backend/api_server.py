"""FastAPI server for the debugging agent with WebSocket support."""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the backend directory to the path so we can import the agent modules
sys.path.insert(0, os.path.dirname(__file__))

from agent_loop_web import create_agent_web, run_agent_web, reset_applied_file_changes
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY environment variable is not set")
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Create FastAPI app
app = FastAPI(title="Debi Agent Debugger API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


class DebugRequest(BaseModel):
    bug_description: str
    repo_url: Optional[str] = None


class DebugResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None


class ConfirmationRequest(BaseModel):
    request_id: str
    action_type: str  # "write_file" or "commit"
    filepath: Optional[str] = None
    diff: Optional[str] = None
    issue_summary: Optional[str] = None
    commit_message: Optional[str] = None


class ConfirmationResponse(BaseModel):
    request_id: str
    approved: bool


# Store active WebSocket connections and session state
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent_instance = None
        self.session_state: Dict[WebSocket, Dict] = {}  # Track state per connection
        self.pending_confirmations: Dict[str, asyncio.Future] = {}  # Track pending confirmation requests

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Initialize session state
        self.session_state[websocket] = {
            'working_directory': None,
            'has_directory': False,
            'original_cwd': os.getcwd()
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Clean up session state
        if websocket in self.session_state:
            del self.session_state[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def set_working_directory(self, websocket: WebSocket, directory: str):
        """Set the working directory for this session."""
        if websocket in self.session_state:
            self.session_state[websocket]['working_directory'] = directory
            self.session_state[websocket]['has_directory'] = True
            logger.info(f"Working directory set to: {directory}")

    def get_working_directory(self, websocket: WebSocket) -> Optional[str]:
        """Get the working directory for this session."""
        if websocket in self.session_state:
            return self.session_state[websocket].get('working_directory')
        return None

    def has_directory(self, websocket: WebSocket) -> bool:
        """Check if working directory has been set."""
        if websocket in self.session_state:
            return self.session_state[websocket].get('has_directory', False)
        return False

    def get_or_create_agent(self):
        if self.agent_instance is None:
            self.agent_instance = create_agent_web(api_key)
            logger.info("Web agent instance created for WebSocket session")
        return self.agent_instance
    
    async def request_confirmation(
        self, 
        websocket: WebSocket,
        request_id: str,
        action_type: str,
        filepath: Optional[str] = None,
        diff: Optional[str] = None,
        issue_summary: Optional[str] = None,
        commit_message: Optional[str] = None,
        timeout: int = 300  # 5 minutes default
    ) -> bool:
        """
        Request user confirmation via WebSocket and wait for response.
        
        Returns:
            True if approved, False if rejected or timeout
        """
        # Create a future to wait for the response
        future = asyncio.Future()
        self.pending_confirmations[request_id] = future
        
        # Send confirmation request to frontend
        await self.send_message({
            "type": "confirmation_request",
            "request_id": request_id,
            "action_type": action_type,
            "filepath": filepath,
            "diff": diff,
            "issue_summary": issue_summary,
            "commit_message": commit_message,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        logger.info(f"Sent confirmation request: {request_id} ({action_type})")
        
        try:
            # Wait for response with timeout
            approved = await asyncio.wait_for(future, timeout=timeout)
            logger.info(f"Confirmation {request_id}: {'approved' if approved else 'rejected'}")
            return approved
        except asyncio.TimeoutError:
            logger.warning(f"Confirmation request {request_id} timed out")
            return False
        finally:
            # Clean up
            if request_id in self.pending_confirmations:
                del self.pending_confirmations[request_id]
    
    def handle_confirmation_response(self, request_id: str, approved: bool):
        """Handle confirmation response from frontend."""
        if request_id in self.pending_confirmations:
            future = self.pending_confirmations[request_id]
            if not future.done():
                future.set_result(approved)
                logger.info(f"Handled confirmation response: {request_id} = {approved}")
        else:
            logger.warning(f"Received confirmation for unknown request_id: {request_id}")


manager = ConnectionManager()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Debi Agent Debugger API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/debug", response_model=DebugResponse)
async def debug_code(request: DebugRequest):
    """
    Endpoint to debug code based on a bug description.
    This is a synchronous endpoint that returns the full response at once.
    """
    try:
        logger.info(f"Received debug request: {request.bug_description[:100]}...")
        
        # Create web agent
        agent = create_agent_web(api_key)
        
        # Run web agent
        response = run_agent_web(agent, request.bug_description)
        
        # Reset file changes
        reset_applied_file_changes()
        
        return DebugResponse(
            response=response,
            success=True,
            error=None
        )
    except Exception as e:
        logger.exception(f"Error in debug endpoint: {e}")
        return DebugResponse(
            response="",
            success=False,
            error=str(e)
        )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with the debugging agent.
    
    Message format:
    Client -> Server:
    {
        "type": "message",
        "content": "user message here",
        "repo_url": "optional repo url"
    }
    
    Server -> Client:
    {
        "type": "message" | "status" | "error" | "request_directory",
        "content": "response content",
        "timestamp": "ISO timestamp"
    }
    """
    await manager.connect(websocket)
    original_cwd = os.getcwd()
    
    try:
        # Send welcome message
        await manager.send_message({
            "type": "message",
            "role": "assistant",
            "content": "Hi, I'm Debi. I do full stack development. What would you like me to help you with?",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Ask for directory path
        await manager.send_message({
            "type": "request_directory",
            "role": "assistant",
            "content": "First, could you please provide the absolute path to your project directory that you'd like me to work with?",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                user_message = data.get("content", "")
                
                # If we don't have a directory yet, treat the message as a directory path
                if not manager.has_directory(websocket):
                    directory_path = user_message.strip()
                    
                    # Validate the directory path
                    if os.path.isdir(directory_path):
                        manager.set_working_directory(websocket, directory_path)
                        await manager.send_message({
                            "type": "message",
                            "role": "assistant",
                            "content": f"Great! I'll work with the project at: `{directory_path}`\n\nNow, what would you like me to help you with?",
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                    else:
                        await manager.send_message({
                            "type": "error",
                            "content": f"I couldn't find a directory at: `{directory_path}`\n\nPlease provide a valid absolute path to your project directory.",
                            "timestamp": datetime.now().isoformat()
                        }, websocket)
                    continue
                
                # We have a directory, process the message normally
                repo_url = data.get("repo_url")
                logger.info(f"Received message: {user_message[:100]}...")
                
                # Send acknowledgment
                await manager.send_message({
                    "type": "status",
                    "content": "Processing your request...",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
                try:
                    # Get the working directory and change to it
                    working_dir = manager.get_working_directory(websocket)
                    if working_dir:
                        logger.info(f"Changing to working directory: {working_dir}")
                        os.chdir(working_dir)
                    
                    # Get or create agent
                    agent = manager.get_or_create_agent()
                    
                    # Send status update
                    await manager.send_message({
                        "type": "status",
                        "content": "Analyzing the issue. This may take a moment...",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
                    # Run agent in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        run_agent_web,
                        agent,
                        user_message
                    )
                    
                    # Send response
                    await manager.send_message({
                        "type": "message",
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
                    # Reset file changes
                    reset_applied_file_changes()
                    
                except Exception as e:
                    logger.exception(f"Error processing message: {e}")
                    await manager.send_message({
                        "type": "error",
                        "content": f"An error occurred: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                finally:
                    # Always restore original working directory
                    os.chdir(original_cwd)
            
            elif data.get("type") == "confirmation_response":
                # Handle confirmation response
                request_id = data.get("request_id")
                approved = data.get("approved", False)
                logger.info(f"Received confirmation response: {request_id} = {approved}")
                manager.handle_confirmation_response(request_id, approved)
            
            elif data.get("type") == "ping":
                # Respond to ping
                await manager.send_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        os.chdir(original_cwd)
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        os.chdir(original_cwd)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
