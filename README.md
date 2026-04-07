# OpenEnv Code Review Environment

**Tag: openenv**

An RL environment where an AI agent reviews code snippets and identifies bugs across three difficulty levels.

## Overview

This environment tests an AI agent's ability to review Python code and identify issues at varying levels of complexity:

- **Easy**: Syntax errors (missing colons, indentation, undefined variables)
- **Medium**: Logical bugs (off-by-one errors, wrong conditions, incomplete logic)
- **Hard**: Code improvement suggestions (Pythonic patterns, efficiency, best practices)

The agent receives a code snippet, analyzes it, and provides a review with bug locations and severity levels. A deterministic grader evaluates the quality of each review, providing incremental rewards.

## Motivation

As AI systems become more capable, their ability to review and improve code is increasingly valuable. This environment tests:

1. **Code Understanding**: Can the agent parse and understand Python syntax and semantics?
2. **Bug Detection**: Can the agent identify various classes of bugs without being explicitly trained on them?
3. **Code Quality**: Can the agent suggest meaningful improvements and best practices?
4. **Reasoning**: Can the agent localize issues and explain problems clearly?

This is a challenging benchmark because it requires both language understanding and programming domain knowledge.

## Action Space

Actions are structured with three fields:

```
review_comment: str
    - The agent's analysis or comment about the code
    - Examples: "Missing colon after function definition"
    
bug_location: Optional[str]
    - Where the issue is located (line number or description)
    - Examples: "line 1", "line 3-4", "function definition"
    
severity: Optional[str] in {"critical", "major", "minor", "none"}
    - Severity of the issue or improvement
    - "none" typically used for improvement suggestions
```

## Observation Space

Observations are structured with four fields:

```
code_snippet: str
    - The Python code to review (string)
    - 5-10 lines typically
    
task_type: str in {"syntax_review", "logic_review", "improvement_review"}
    - Specifies the difficulty and type of task
    
feedback: Optional[str]
    - Feedback from the grader on the previous step
    - Helps agent refine its analysis
    
step: int
    - Current step number (starts at 0)
    - Max 5 steps per episode
```

## Task Descriptions

### Task 1: Syntax Review (Easy)

**Objective**: Find syntax errors that prevent code from running.

**Examples of errors**:
- Missing colons after function/loop definitions
- Inconsistent indentation
- Undefined variables
- Mismatched parentheses

**Grading**: Agent scores based on:
- Identifying error keywords (colon, indentation, etc.)
- Correct line number identification
- Severity marking (should be "critical" for syntax errors)

**Baseline Performance**: 0.75 average reward

**Example Snippets**:
```python
# Snippet 1: Missing colon
def calculate_sum(numbers)
    total = 0
    for num in numbers:
        total += num
    return total

# Snippet 2: Indentation error
def greet(name):
    message = f"Hello, {name}!"
print(message)
    return message

# Snippet 3: Undefined variable
x = 10
y = 20
print(x + undefined_var)
print(y)
```

### Task 2: Logic Review (Medium)

**Objective**: Find logical bugs that allow code to run but produce wrong results.

**Examples of bugs**:
- Off-by-one errors in indexing
- Wrong comparison operators (< vs >)
- Inverted boolean logic
- Missing cases in conditionals or loops

**Grading**: Agent scores based on:
- Identifying logic error keywords
- Correct line localization
- Proper severity marking
- Explanation quality

**Baseline Performance**: 0.65 average reward

**Example Snippets**:
```python
# Snippet 1: Wrong comparison in find_min
def find_min(numbers):
    min_val = float('inf')
    for num in numbers:
        if num > min_val:  # Should be < not >
            min_val = num
    return min_val

# Snippet 2: Inverted boolean logic
def is_valid_index(index, length):
    if index >= length or index < 0:
        return True  # Should be False
    return False  # Should be True

# Snippet 3: Off-by-one error
def get_nth_element(lst, n):
    return lst[n-1]  # Off-by-one, should be lst[n] or different logic
```

### Task 3: Improvement Review (Hard)

**Objective**: Suggest improvements to working but suboptimal code.

**Types of improvements**:
- Using Python idioms (list comprehensions, context managers)
- Using appropriate built-in functions
- Performance optimizations
- Better error handling
- Security improvements

**Grading**: Agent scores based on:
- Suggesting meaningful improvements
- Explanation clarity and actionability
- Alignment with Python best practices
- Severity appropriately marked as "minor" or "none"

**Baseline Performance**: 0.70 average reward

**Example Snippets**:
```python
# Snippet 1: Can use list comprehension
def get_even_numbers(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num)
    return result

# Snippet 2: Should use context manager
import os
def read_file(path):
    f = open(path, 'r')
    content = f.read()
    f.close()
    return content

# Snippet 3: Should use eval alternatives
def parse_config(config_str):
    try:
        config = eval(config_str)
    except:
        config = {}
    return config
```

## Setup & Installation

### Prerequisites

- Python 3.11+
- OpenAI-compatible API (Anthropic, etc.)
- Hugging Face API token (for demo inference)

### Local Installation

```bash
# Clone or download the environment
cd openenv-codereview

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_BASE_URL="https://api.anthropic.com/v1"
export MODEL_NAME="claude-sonnet-4-20250514"
export HF_TOKEN="your_hf_token_here"
```

### Docker Setup

```bash
# Build Docker image
docker build -t openenv-codereview .

# Run in Docker
docker run \
  -e API_BASE_URL="https://api.anthropic.com/v1" \
  -e MODEL_NAME="claude-sonnet-4-20250514" \
  -e HF_TOKEN="your_hf_token_here" \
  openenv-codereview \
  python inference.py --task syntax_review --steps 5
```

## Usage

### Python API

```python
from environment import CodeReviewEnvironment, Action

# Create environment
env = CodeReviewEnvironment(task_type="syntax_review", max_steps=5)

# Reset
observation = env.reset()
print(f"Code: {observation.code_snippet}")
print(f"Task: {observation.task_type}")

# Take action
action = Action(
    review_comment="Missing colon after function definition",
    bug_location="line 1",
    severity="critical"
)

observation, reward, done, info = env.step(action)
print(f"Reward: {reward.value:.2f}")
print(f"Feedback: {reward.message}")
```

### Command Line

```bash
# Run inference with syntax review task
python inference.py --task syntax_review --steps 5

# Run logic review task
python inference.py --task logic_review --steps 5

# Run improvement review task
python inference.py --task improvement_review --steps 5

# Custom settings
python inference.py --task syntax_review --steps 3 --benchmark custom-benchmark
```

### Output Format

Each run produces timestamped output:

```
[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Missing colon after function definition reward=0.95 done=false error=null
[STEP] step=2 action=Check indentation error reward=0.88 done=true error=null
[END] success=true steps=2 rewards=0.95,0.88
```

## Reward Function

The reward function is **incremental** (given at each step, not just at episode end):

### Syntax Review Grading
- 0.3 points for identifying error keywords (colon, indentation, syntax, etc.)
- 0.7 points for correct line identification (±1 acceptable)
- Total: 0.0 to 1.0

### Logic Review Grading
- 0.3 points for identifying logic error keywords
- 0.7 points for correct line identification
- Total: 0.0 to 1.0

### Improvement Review Grading
- 0.4 points for suggesting improvement keywords
- 0.3 points for detailed explanations (>20 chars)
- 0.3 points for appropriate severity (should be "minor" or "none")
- Total: 0.0 to 1.0

## Baseline Performance

| Task | Baseline Score | Notes |
|------|-----------------|-------|
| syntax_review | 0.75 | Keyword matching + line detection |
| logic_review | 0.65 | Requires deeper semantic understanding |
| improvement_review | 0.70 | Pattern matching for Pythonic suggestions |

These baselines represent simple rule-based approaches. Advanced models should exceed these scores through better code understanding and reasoning.

## Environment Properties

- **Deterministic**: Yes (same snippet → same grading criteria)
- **Episodic**: Yes (max 5 steps per episode)
- **Observation Type**: Pydantic models
- **Action Type**: Pydantic models
- **Reward Type**: Float [0.0, 1.0]
- **Reproducible**: Yes (fixed code snippets and grading rules)

## Code Snippets Included

### Easy (Syntax Review)
- 5 hand-crafted Python snippets with syntax errors
- Error types: missing colons, indentation, undefined variables

### Medium (Logic Review)
- 5 hand-crafted Python snippets with logical bugs
- Bug types: off-by-one, wrong comparisons, inverted logic, incomplete loops

### Hard (Improvement Review)
- 5 hand-crafted Python snippets with improvement opportunities
- Improvement types: list comprehensions, context managers, built-ins, security

## Extending the Environment

### Adding New Code Snippets

Edit `environment.py` and add to the corresponding list:

```python
SYNTAX_REVIEW_SNIPPETS.append({
    "code": "...",
    "errors": ["..."],
    "error_lines": [1, 2],
    "description": "..."
})
```

### Custom Task

Create a subclass:

```python
class CustomReviewEnvironment(CodeReviewEnvironment):
    def _grade_action(self, action):
        # Custom grading logic
        pass
```

## License

MIT License - Free to use for research and development.

## Citation

If you use this environment, please cite:

```
@software{openenv_codereview_2025,
  title={OpenEnv Code Review Environment},
  author={OpenEnv Contributors},
  year={2025},
  url={https://github.com/openenv/code-review}
}
```

## Contact

For issues, questions, or contributions:
1. Check existing documentation
2. Review code snippets and grading logic
3. Extend with your own tasks and metrics

## Acknowledgments

Built for the Meta OpenEnv RL Hackathon.
