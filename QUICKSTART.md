# Quick Start Guide

## For Local Testing (No API Key Required)

```bash
# Install dependencies
pip install -r requirements.txt

# Run environment tests
python test_environment.py

# Test environment directly
python -c "
from environment import CodeReviewEnvironment, Action
env = CodeReviewEnvironment(task_type='syntax_review', max_steps=3)
obs = env.reset()
print('Code:', obs.code_snippet[:50], '...')
action = Action(review_comment='Missing colon', bug_location='line 1', severity='critical')
obs, reward, done, info = env.step(action)
print(f'Reward: {reward.value:.2f}', reward.message)
"
```

## For Inference (Requires API Setup)

### Step 1: Get API Credentials
- Anthropic API: https://console.anthropic.com/
- Hugging Face Token: https://huggingface.co/settings/tokens

### Step 2: Set Environment Variables
```bash
# Linux/Mac
export API_BASE_URL="https://api.anthropic.com/v1"
export MODEL_NAME="claude-sonnet-4-20250514"
export HF_TOKEN="your_hf_token_here"

# Windows PowerShell
$env:API_BASE_URL="https://api.anthropic.com/v1"
$env:MODEL_NAME="claude-sonnet-4-20250514"
$env:HF_TOKEN="your_hf_token_here"
```

### Step 3: Run Inference
```bash
# Syntax review
python inference.py --task syntax_review --steps 5

# Logic review
python inference.py --task logic_review --steps 5

# Improvement review
python inference.py --task improvement_review --steps 5
```

Expected output:
```
[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Missing colon... reward=0.85 done=false error=null
[STEP] step=2 action=Indentation... reward=0.92 done=true error=null
[END] success=true steps=2 rewards=0.85,0.92
```

## Docker Quick Start

```bash
# Build image
docker build -t openenv-codereview .

# Run with env vars from file
docker run --env-file .env openenv-codereview

# Run inline
docker run \
  -e API_BASE_URL="https://api.anthropic.com/v1" \
  -e MODEL_NAME="claude-sonnet-4-20250514" \
  -e HF_TOKEN="your_token" \
  openenv-codereview
```

## File Descriptions

| File | Purpose |
|------|---------|
| **environment.py** | Core environment with 3 tasks, Pydantic models, 15 code snippets |
| **inference.py** | Main entry point, runs agent through environment with exact output format |
| **test_environment.py** | Comprehensive test suite (all tests passing ✓) |
| **Dockerfile** | Container setup with all dependencies |
| **openenv.yaml** | OpenEnv metadata and task definitions |
| **requirements.txt** | Python dependencies |
| **README.md** | Full documentation |

## Test Results

```
✓ Environment initialization (syntax, logic, improvement)
✓ Reset and observation generation
✓ 15 code snippets (5 each task)
✓ Syntax review grading
✓ Logic review grading
✓ Improvement review grading
✓ Full episode execution
✓ State tracking
```

## Architecture

```
Input Code Snippet
      ↓
   Task Type (easy/medium/hard)
      ↓
  Agent Reviews (via LLM or custom logic)
      ↓
   Grading (deterministic)
      ↓
  Reward [0.0 - 1.0]
```

## Features

- ✅ 3 difficulty levels (Easy/Medium/Hard)
- ✅ Deterministic, reproducible grading
- ✅ 15 hand-crafted code snippets
- ✅ Pydantic models for structured I/O
- ✅ Incremental reward per step
- ✅ OpenEnv-compliant format
- ✅ Docker support
- ✅ Comprehensive tests
- ✅ OpenAI client integration
- ✅ Exact output format compliance

## Customization

### Add More Snippets

```python
# In environment.py
SYNTAX_REVIEW_SNIPPETS.append({
    "code": "your code here",
    "errors": ["description"],
    "error_lines": [line_numbers],
    "description": "brief desc"
})
```

### Different LLM Provider

Edit `inference.py` client initialization:
```python
client = OpenAI(
    base_url="https://your-api-endpoint/v1",
    api_key="your_key"
)
```

## Troubleshooting

**ImportError: openai**
```bash
pip install openai
```

**ValueError: HF_TOKEN not set**
```bash
# Set environment variable before running
export HF_TOKEN="your_token"
```

**Connection error**
```bash
# Check API base URL and credentials
env | grep -E "API_BASE|MODEL_NAME|HF_TOKEN"
```

## Next Steps

1. Run tests: `python test_environment.py`
2. Explore environment: `python -c "from environment import *"`
3. Integrate with your agent
4. Submit to Meta OpenEnv Hackathon!
