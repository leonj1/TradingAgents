"""
FastAPI REST API interface for the meta-agent system.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from meta_agent import MetaAgentOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Meta-Agent API",
    description="Dynamic AI agent team creation for any topic",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance (initialized on startup)
orchestrator: Optional[MetaAgentOrchestrator] = None

# Store active tasks
active_tasks: Dict[str, Dict[str, Any]] = {}

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


# Request/Response Models
class TopicRequest(BaseModel):
    """Request model for topic analysis"""
    topic: str = Field(..., description="The topic or question to analyze")
    auto_execute: bool = Field(True, description="Execute workflow after team creation")
    api_key: Optional[str] = Field(None, description="API key (optional if set in env)")


class TopicResponse(BaseModel):
    """Response model for topic analysis"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class TaskStatus(BaseModel):
    """Task status information"""
    task_id: str
    status: str
    domain: Optional[str] = None
    team_size: Optional[int] = None
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AgentInfo(BaseModel):
    """Information about a created agent"""
    name: str
    role: str
    specialization: str
    personality_traits: List[str]


class TeamInfo(BaseModel):
    """Information about the created team"""
    domain: str
    agents: List[AgentInfo]
    workflow_phases: int
    debate_topics: List[str]


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup"""
    global orchestrator
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        raise RuntimeError("OPENAI_API_KEY must be set")
    
    orchestrator = MetaAgentOrchestrator(api_key)
    logger.info("Meta-Agent API started successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Meta-Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze a topic and create agent team",
            "GET /status/{task_id}": "Get task status",
            "GET /tasks": "List all tasks",
            "WS /ws": "WebSocket for real-time updates"
        }
    }


@app.post("/analyze", response_model=TopicResponse)
async def analyze_topic(
    request: TopicRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a topic and create a specialized agent team.
    
    This endpoint:
    1. Analyzes the topic to determine domain
    2. Creates appropriate specialist agents
    3. Optionally executes the workflow
    4. Returns a task_id for tracking progress
    """
    # Use provided API key or fall back to environment
    api_key = request.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    # Create task
    task_id = str(uuid4())
    
    # Initialize task tracking
    active_tasks[task_id] = {
        "status": "analyzing",
        "topic": request.topic,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "progress": 0.0
    }
    
    # Start background processing
    background_tasks.add_task(
        process_topic,
        task_id,
        request.topic,
        request.auto_execute,
        api_key
    )
    
    # Notify WebSocket clients
    await notify_clients({
        "type": "task_created",
        "task_id": task_id,
        "topic": request.topic
    })
    
    return TopicResponse(
        task_id=task_id,
        status="processing",
        message=f"Task created. Processing topic: {request.topic[:100]}..."
    )


async def process_topic(
    task_id: str,
    topic: str,
    auto_execute: bool,
    api_key: str
):
    """Background task to process a topic"""
    try:
        # Update status
        active_tasks[task_id]["status"] = "analyzing"
        active_tasks[task_id]["progress"] = 0.1
        await notify_clients({
            "type": "status_update",
            "task_id": task_id,
            "status": "analyzing",
            "progress": 0.1
        })
        
        # Create orchestrator for this task
        task_orchestrator = MetaAgentOrchestrator(api_key)
        
        # Process topic
        result = await task_orchestrator.respond_to_topic(
            topic=topic,
            auto_execute=auto_execute,
            show_progress=False
        )
        
        # Extract key information
        analysis = result["analysis"]
        team = result["team"]
        
        # Update task with results
        active_tasks[task_id].update({
            "status": "completed",
            "domain": analysis.domain,
            "confidence": analysis.domain_confidence,
            "task_type": analysis.task_type,
            "complexity": analysis.complexity_level,
            "team_size": len(team.agents),
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role.value,
                    "traits": [t.name for t in agent.personality.traits[:3]]
                }
                for agent in team.agents
            ],
            "result": {
                "quality_score": result["result"].quality_score if result["result"] else None,
                "decision": result["result"].decision_rationale if result["result"] else None
            },
            "progress": 1.0,
            "updated_at": datetime.now()
        })
        
        # Notify completion
        await notify_clients({
            "type": "task_completed",
            "task_id": task_id,
            "domain": analysis.domain,
            "team_size": len(team.agents)
        })
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        active_tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.now()
        })
        
        await notify_clients({
            "type": "task_failed",
            "task_id": task_id,
            "error": str(e)
        })


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a specific task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        domain=task.get("domain"),
        team_size=task.get("team_size"),
        progress=task.get("progress", 0.0),
        result=task.get("result"),
        error=task.get("error"),
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )


@app.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50
):
    """List all tasks with optional filtering"""
    tasks = []
    
    for task_id, task in active_tasks.items():
        if status and task["status"] != status:
            continue
            
        tasks.append({
            "task_id": task_id,
            "topic": task["topic"][:100] + "..." if len(task["topic"]) > 100 else task["topic"],
            "status": task["status"],
            "domain": task.get("domain"),
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        })
    
    # Sort by created_at descending
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "total": len(tasks),
        "tasks": tasks[:limit]
    }


@app.get("/task/{task_id}/team", response_model=TeamInfo)
async def get_team_info(task_id: str):
    """Get detailed information about the created team"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    if "agents" not in task:
        raise HTTPException(status_code=404, detail="Team information not available")
    
    agents = [
        AgentInfo(
            name=agent["name"],
            role=agent["role"],
            specialization=agent.get("specialization", "General"),
            personality_traits=agent.get("traits", [])
        )
        for agent in task["agents"]
    ]
    
    return TeamInfo(
        domain=task["domain"],
        agents=agents,
        workflow_phases=3,  # Default workflow phases
        debate_topics=[]  # Would need to store these from analysis
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Meta-Agent WebSocket"
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def notify_clients(message: Dict[str, Any]):
    """Send updates to all connected WebSocket clients"""
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)


@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task from history"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del active_tasks[task_id]
    
    return {"message": f"Task {task_id} deleted"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_tasks": len(active_tasks),
        "active_connections": len(active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)