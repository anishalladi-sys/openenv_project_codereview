#!/usr/bin/env python3
"""
OpenEnv Code Review - Inference Script with FastAPI Server
Runs an AI agent through the code review environment.

Usage as standalone script:
    python inference.py --task syntax_review --steps 5

Usage as FastAPI server (for HuggingFace Spaces):
    uvicorn inference:app --host 0.0.0.0 --port 7860
    
Environment Variables:
    API_BASE_URL: API endpoint (default: https://api-inference.huggingface.co/v1)
    MODEL_NAME: Model to use (default: meta-llama/Llama-3.2-3B-Instruct)
    HF_TOKEN: Hugging Face API token (required, no default)
"""

import os
import sys
import json
import argparse
import traceback
from typing import Optional, Dict, Any

# Import FastAPI
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel as PydanticModel
except ImportError:
    print("[ERROR] FastAPI not found. Install with: pip install fastapi uvicorn", file=sys.stderr)
    sys.exit(1)

# Import environment
from environment import (
    CodeReviewEnvironment,
    Action,
    Observation,
)

# Import OpenAI client
try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI library not found. Install with: pip install openai", file=sys.stderr)
    sys.exit(1)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(title="OpenEnv Code Review Server", version="1.0.0")

# Global state for FastAPI server
class ServerState:
    def __init__(self):
        self.env: Optional[CodeReviewEnvironment] = None
        self.current_observation: Optional[Observation] = None
        self.config: Dict[str, Any] = {}
        self.client: Optional[OpenAI] = None

server_state = ServerState()

# Pydantic models for API
class ObservationResponse(PydanticModel):
    code_snippet: str
    task_type: str
    feedback: Optional[str] = None
    step: int

class ActionRequest(PydanticModel):
    review_comment: str
    bug_location: Optional[str] = None
    severity: Optional[str] = None

class StepResponse(PydanticModel):
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
    """Reset the environment and return initial observation"""
    try:
        # Reload config if needed
        if not server_state.config:
            server_state.config = get_config()
            server_state.client = create_client(server_state.config)
        
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
    """Execute one step with the given action"""
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
# CONFIGURATION & CLIENT
# ============================================================================

def get_config():
    """Load configuration from environment variables"""
    api_base = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is required but not set")
    
    return {
        "api_base": api_base,
        "model_name": model_name,
        "hf_token": hf_token,
    }


def create_client(config: dict) -> OpenAI:
    """Create OpenAI client with configuration"""
    client = OpenAI(
        base_url=config["api_base"],
        api_key=config["hf_token"],  # Using HF_TOKEN as API key
    )
    return client


def format_observation_for_llm(obs: Observation) -> str:
    """Format observation as prompt for LLM"""
    prompt = f"""You are a code reviewer. Analyze the following code and provide your review.

TASK TYPE: {obs.task_type}
STEP: {obs.step}

CODE TO REVIEW:
```python
{obs.code_snippet}
```

TASK DESCRIPTION:
"""
    
    if obs.task_type == "syntax_review":
        prompt += "Find any syntax errors in this code (missing colons, indentation issues, etc.). "
        prompt += "Identify the exact line number and type of error."
    elif obs.task_type == "logic_review":
        prompt += "Find any logical bugs in this code (wrong conditions, off-by-one errors, etc.). "
        prompt += "Identify the line number and explain what is wrong with the logic."
    else:  # improvement_review
        prompt += "Suggest improvements to make this code more Pythonic and efficient. "
        prompt += "Focus on code quality, performance, and best practices."
    
    if obs.feedback:
        prompt += f"\n\nPREVIOUS FEEDBACK: {obs.feedback}"
    
    prompt += "\n\nProvide your review in this format:"
    prompt += "\nREVIEW: <your analysis>"
    prompt += "\nLOCATION: <line number or description>"
    prompt += "\nSEVERITY: <critical|major|minor|none>"
    
    return prompt


def parse_llm_response(response_text: str) -> tuple:
    """Parse LLM response into review components"""
    lines = response_text.strip().split("\n")
    
    review_comment = ""
    bug_location = ""
    severity = "none"
    
    for line in lines:
        if line.startswith("REVIEW:"):
            review_comment = line.replace("REVIEW:", "").strip()
        elif line.startswith("LOCATION:"):
            bug_location = line.replace("LOCATION:", "").strip()
        elif line.startswith("SEVERITY:"):
            severity = line.replace("SEVERITY:", "").strip().lower()
    
    if not review_comment:
        review_comment = response_text[:200]
    
    return review_comment, bug_location, severity


def run_episode(
    task_type: str = "syntax_review",
    max_steps: int = 5,
    model_name: str = "claude-sonnet-4-20250514",
    api_base: str = "https://api.anthropic.com/v1",
    hf_token: str = None,
) -> dict:
    """Run a single episode of the environment"""
    
    # Initialize environment
    env = CodeReviewEnvironment(task_type=task_type, max_steps=max_steps)
    
    # Create LLM client
    client = OpenAI(
        base_url=api_base,
        api_key=hf_token,
    )
    
    # Reset environment
    observation = env.reset()
    
    # Progress tracking
    steps_executed = 0
    rewards = []
    success = False
    error_msg = None
    
    # Episode loop
    for step_num in range(max_steps):
        try:
            # Get LLM response
            prompt = format_observation_for_llm(observation)
            
            message = client.chat.completions.create(
                model=model_name,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            llm_response = message.choices[0].message.content
            
            # Parse response into action
            review_comment, bug_location, severity = parse_llm_response(llm_response)
            
            action = Action(
                review_comment=review_comment,
                bug_location=bug_location,
                severity=severity,
            )
            
            # Execute action
            observation, reward, done, info = env.step(action)
            
            steps_executed += 1
            rewards.append(reward.value)
            
            # Print step
            print(
                f"[STEP] step={steps_executed} "
                f"action={action.review_comment[:50]} "
                f"reward={reward.value:.2f} "
                f"done={str(done).lower()} "
                f"error=null"
            )
            
            if done:
                success = reward.value >= 0.8 or step_num == max_steps - 1
                break
        
        except Exception as e:
            error_msg = str(e)
            print(
                f"[STEP] step={steps_executed + 1} "
                f"action=error "
                f"reward=0.00 "
                f"done=true "
                f"error={error_msg}"
            )
            success = False
            break
    
    return {
        "success": success,
        "steps": steps_executed,
        "rewards": rewards,
        "episode_reward": env.episode_reward,
        "error": error_msg,
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OpenEnv Code Review Inference")
    parser.add_argument(
        "--task",
        type=str,
        default="syntax_review",
        choices=["syntax_review", "logic_review", "improvement_review"],
        help="Task type"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=5,
        help="Maximum steps per episode"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="openenv-codereview",
        help="Benchmark name"
    )
    
    args = parser.parse_args()
    
    # Load config
    try:
        config = get_config()
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print start
    print(
        f"[START] task={args.task} "
        f"env={args.benchmark} "
        f"model={config['model_name']}"
    )
    
    try:
        # Run episode
        result = run_episode(
            task_type=args.task,
            max_steps=args.steps,
            model_name=config["model_name"],
            api_base=config["api_base"],
            hf_token=config["hf_token"],
        )
        
        # Print end with results
        rewards_str = ",".join(f"{r:.2f}" for r in result["rewards"])
        print(
            f"[END] success={str(result['success']).lower()} "
            f"steps={result['steps']} "
            f"rewards={rewards_str}"
        )
        
        sys.exit(0 if result["success"] else 1)
    
    except Exception as e:
        # Print end with error
        print(
            f"[END] success=false "
            f"steps=0 "
            f"rewards="
        )
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
