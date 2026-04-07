#!/usr/bin/env python3
"""
OpenEnv Code Review - FastAPI Server for Multi-Mode Deployment
Wraps the CodeReviewEnvironment with REST endpoints for HuggingFace Spaces compatibility.

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 7860
    server  # via pyproject.toml scripts entry point
"""

import os
import sys
from typing import Optional, Dict, Any

# Import FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import environment
from environment import (
    CodeReviewEnvironment,
    Action,
    Observation,
)

# Import OpenAI client
from openai import OpenAI

# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="OpenEnv Code Review Server",
    description="RL environment for code review with REST API",
    version="1.0.0"
)

# Global state for FastAPI server
class ServerState:
    def __init__(self):
        self.env: Optional[CodeReviewEnvironment] = None
        self.current_observation: Optional[Observation] = None
        self.config: Dict[str, Any] = {}
        self.client: Optional[OpenAI] = None

server_state = ServerState()

# Pydantic models for API
class ActionRequest(BaseModel):
    """Action request from client"""
    review_comment: str
    bug_location: Optional[str] = None
    severity: Optional[str] = None

class StepResponse(BaseModel):
    """Response from step endpoint"""
    observation: Optional[Dict[str, Any]] = None
    reward: Optional[float] = None
    done: bool
    info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/reset")
async def reset_endpoint():
    """
    Reset the environment and return initial observation.
    Called by hackathon system to verify Space is alive.
    """
    try:
        # Initialize client if needed
        if not server_state.client:
            server_state.config = {
                "api_base": API_BASE_URL,
                "model_name": MODEL_NAME,
                "hf_token": HF_TOKEN,
            }
            
            if not server_state.config["hf_token"]:
                raise ValueError("HF_TOKEN environment variable is required")
            
            server_state.client = OpenAI(
                base_url=server_state.config["api_base"],
                api_key=server_state.config["hf_token"],
            )
        
        # Create environment
        server_state.env = CodeReviewEnvironment(
            task_type="syntax_review",
            max_steps=5
        )
        
        # Reset and get observation
        observation = server_state.env.reset()
        server_state.current_observation = observation
        
        return {
            "status": "ok",
            "observation": observation.dict() if observation else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
async def step_endpoint(action: ActionRequest):
    """
    Execute one step with the given action.
    Returns: observation, reward, done flag, and error (if any).
    """
    try:
        if not server_state.env:
            raise ValueError("Environment not initialized. Call /reset first.")
        
        if not server_state.current_observation:
            raise ValueError("No current observation. Call /reset first.")
        
        # Convert request to Action
        api_action = Action(
            review_comment=action.review_comment,
            bug_location=action.bug_location,
            severity=action.severity or "none",
        )
        
        # Execute step
        observation, reward, done, info = server_state.env.step(api_action)
        server_state.current_observation = observation
        
        return {
            "observation": observation.dict() if observation else {},
            "reward": reward.value if reward else 0.0,
            "done": done,
            "info": info,
            "error": None
        }
    except Exception as e:
        return {
            "observation": None,
            "reward": 0.0,
            "done": True,
            "info": {"error": str(e)},
            "error": str(e)
        }


# ============================================================================
# MAIN ENTRY POINT (for pyproject.toml scripts)
# ============================================================================

def main():
    """Main entry point for uvicorn server via pyproject.toml scripts"""
    import uvicorn
    
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting OpenEnv Code Review Server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
