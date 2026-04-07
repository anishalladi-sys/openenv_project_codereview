"""
OpenEnv Code Review Environment

An RL environment where an AI agent reviews code snippets and identifies bugs.
Tasks cover Easy (syntax), Medium (logic), and Hard (improvement) levels.
"""

from enum import Enum
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass, asdict
import json
import random

from pydantic import BaseModel, Field


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Observation(BaseModel):
    """Observation provided to the agent"""
    code_snippet: str = Field(..., description="Python code to review")
    task_type: str = Field(..., description="Type of task: syntax_review, logic_review, or improvement_review")
    feedback: Optional[str] = Field(None, description="Feedback from previous action")
    step: int = Field(0, description="Current step number")


class Action(BaseModel):
    """Action taken by the agent"""
    review_comment: str = Field(..., description="Comment about the code")
    bug_location: Optional[str] = Field(None, description="Line number or description of bug location")
    severity: Optional[str] = Field(None, description="Severity level: critical, major, minor, none")


class Reward(BaseModel):
    """Reward information"""
    value: float = Field(..., ge=0.0, le=1.0, description="Reward score 0.0-1.0")
    message: str = Field(..., description="Explanation of reward")


# ============================================================================
# CODE SNIPPETS FOR TASKS
# ============================================================================

SYNTAX_REVIEW_SNIPPETS = [
    {
        "code": """def calculate_sum(numbers)
    total = 0
    for num in numbers:
        total += num
    return total""",
        "errors": ["Missing colon after function definition (line 1)"],
        "error_lines": [1],
        "description": "Missing colon after function definition"
    },
    {
        "code": """def greet(name):
    message = f"Hello, {name}!"
print(message)
    return message""",
        "errors": ["Inconsistent indentation (line 3)"],
        "error_lines": [3],
        "description": "Indentation error"
    },
    {
        "code": """def process_data(data):
    result = []
    for item in data
        result.append(item * 2)
    return result""",
        "errors": ["Missing colon after for loop (line 3)"],
        "error_lines": [3],
        "description": "Missing colon in for loop"
    },
    {
        "code": """x = 10
y = 20
print(x + undefined_var)
print(y)""",
        "errors": ["Undefined variable 'undefined_var' (line 3)"],
        "error_lines": [3],
        "description": "Undefined variable"
    },
    {
        "code": """def multiply(a, b)
    return a * b
print(multiply(3, 4))""",
        "errors": ["Missing colon after function definition (line 1)"],
        "error_lines": [1],
        "description": "Missing colon after function definition"
    },
]

LOGIC_REVIEW_SNIPPETS = [
    {
        "code": """def find_min(numbers):
    min_val = float('inf')
    for num in numbers:
        if num > min_val:
            min_val = num
    return min_val""",
        "errors": ["Wrong comparison operator (should be < not >, line 4)"],
        "error_lines": [4],
        "description": "Find minimum has wrong comparison"
    },
    {
        "code": """def is_valid_index(index, length):
    if index >= length or index < 0:
        return True
    return False""",
        "errors": ["Inverted logic (should return False for invalid, line 2)"],
        "error_lines": [2, 3],
        "description": "Inverted boolean logic"
    },
    {
        "code": """def get_nth_element(lst, n):
    return lst[n-1]  # Off-by-one error
    
def test():
    arr = [1, 2, 3, 4, 5]
    print(get_nth_element(arr, 5))  # Expected: 5, Got: 4""",
        "errors": ["Off-by-one error (line 2)"],
        "error_lines": [2],
        "description": "Off-by-one indexing error"
    },
    {
        "code": """def count_even(numbers):
    count = 0
    for num in numbers:
        if num % 2 == 0:
            count += 1
        else:
            count += 2  # Bug: should not increment on odd
    return count""",
        "errors": ["Wrong count increment for odd numbers (line 6)"],
        "error_lines": [6],
        "description": "Incorrect counter logic"
    },
    {
        "code": """def merge_sorted(a, b):
    result = []
    i, j = 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    # Missing: result.extend(b[j:])
    return result""",
        "errors": ["Incomplete merge logic (missing remaining b elements, line 12)"],
        "error_lines": [12],
        "description": "Incomplete merge in two-pointer algorithm"
    },
]

IMPROVEMENT_REVIEW_SNIPPETS = [
    {
        "code": """def get_even_numbers(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num)
    return result""",
        "improvement": "Use list comprehension for Pythonic code: [n for n in numbers if n % 2 == 0]",
    },
    {
        "code": """def process_users(users):
    valid_users = []
    for user in users:
        if user.get('age') and user.get('email'):
            valid_users.append(user)
    return valid_users""",
        "improvement": "Use filter() or a more concise comprehension. Add validation logic.",
    },
    {
        "code": """import os
def read_file(path):
    f = open(path, 'r')
    content = f.read()
    f.close()
    return content""",
        "improvement": "Use context manager 'with' for proper resource handling",
    },
    {
        "code": """def calculate_stats(data):
    sum_val = 0
    for x in data:
        sum_val += x
    avg = sum_val / len(data)
    return avg""",
        "improvement": "Use built-in functions: sum() and statistics.mean() for clarity",
    },
    {
        "code": """def parse_config(config_str):
    try:
        config = eval(config_str)
    except:
        config = {}
    return config""",
        "improvement": "Avoid eval() for security. Use json.loads() or ast.literal_eval()",
    },
]


# ============================================================================
# ENVIRONMENT CLASS
# ============================================================================

class CodeReviewEnvironment:
    """OpenEnv-compliant Code Review environment"""

    def __init__(self, task_type: str = "syntax_review", max_steps: int = 5):
        """
        Initialize the environment.
        
        Args:
            task_type: "syntax_review", "logic_review", or "improvement_review"
            max_steps: Maximum steps per episode
        """
        assert task_type in ["syntax_review", "logic_review", "improvement_review"]
        self.task_type = task_type
        self.max_steps = max_steps
        self.current_step = 0
        self.episode_reward = 0.0
        self.done = False
        
        # Select appropriate snippets
        if task_type == "syntax_review":
            self.snippets = SYNTAX_REVIEW_SNIPPETS
        elif task_type == "logic_review":
            self.snippets = LOGIC_REVIEW_SNIPPETS
        else:  # improvement_review
            self.snippets = IMPROVEMENT_REVIEW_SNIPPETS
        
        self.current_snippet = None
        self.current_snippet_index = None
        self.agent_actions = []
        
    def reset(self) -> Observation:
        """Reset environment and return initial observation"""
        self.current_step = 0
        self.episode_reward = 0.0
        self.done = False
        self.agent_actions = []
        
        # Select random snippet
        self.current_snippet_index = random.randint(0, len(self.snippets) - 1)
        self.current_snippet = self.snippets[self.current_snippet_index]
        
        return Observation(
            code_snippet=self.current_snippet["code"],
            task_type=self.task_type,
            feedback="Review the provided code snippet.",
            step=0
        )
    
    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Execute one step of the environment.
        
        Args:
            action: Agent's action (review comment, bug location, severity)
            
        Returns:
            observation, reward, done, info
        """
        self.current_step += 1
        self.agent_actions.append(action)
        
        # Grade the action
        reward, feedback = self._grade_action(action)
        self.episode_reward += reward.value
        
        # Check if done
        self.done = self.current_step >= self.max_steps or reward.value >= 0.9
        
        # Create next observation
        next_observation = Observation(
            code_snippet=self.current_snippet["code"],
            task_type=self.task_type,
            feedback=reward.message,
            step=self.current_step
        )
        
        info = {
            "step": self.current_step,
            "task_type": self.task_type,
            "snippet_index": self.current_snippet_index,
            "episode_reward": self.episode_reward,
        }
        
        return next_observation, reward, self.done, info
    
    def state(self) -> Dict[str, Any]:
        """Return current environment state"""
        return {
            "task_type": self.task_type,
            "step": self.current_step,
            "max_steps": self.max_steps,
            "done": self.done,
            "episode_reward": self.episode_reward,
            "current_snippet_index": self.current_snippet_index,
            "num_actions": len(self.agent_actions),
        }
    
    # ============================================================================
    # GRADING FUNCTIONS
    # ============================================================================
    
    def _grade_action(self, action: Action) -> Tuple[Reward, str]:
        """Grade the agent's action"""
        if self.task_type == "syntax_review":
            return self._grade_syntax_review(action)
        elif self.task_type == "logic_review":
            return self._grade_logic_review(action)
        else:
            return self._grade_improvement_review(action)
    
    def _grade_syntax_review(self, action: Action) -> Tuple[Reward, str]:
        """Grade syntax error detection"""
        comment = action.review_comment.lower()
        bug_loc = action.bug_location or ""
        
        # Check if agent identified errors correctly
        score = 0.0
        msg = "Syntax review: "
        
        # Look for error keywords
        error_keywords = ["colon", "indentation", "syntax", "undefined", "missing"]
        found_keywords = sum(1 for kw in error_keywords if kw in comment)
        
        if found_keywords > 0:
            score += 0.3
        
        # Check if bug location is close to actual error
        if bug_loc:
            try:
                reported_line = int(''.join(filter(str.isdigit, bug_loc)))
                actual_lines = self.current_snippet.get("error_lines", [])
                if reported_line in actual_lines or reported_line == actual_lines[0]:
                    score += 0.7
                else:
                    score += 0.2
            except:
                score += 0.2
        else:
            score += 0.2
        
        score = min(1.0, score)
        
        if score >= 0.8:
            msg += f"Correct! Score: {score:.2f}"
        elif score >= 0.5:
            msg += f"Partial credit. Score: {score:.2f}"
        else:
            msg += f"Incorrect detection. Score: {score:.2f}"
        
        return Reward(value=score, message=msg), msg
    
    def _grade_logic_review(self, action: Action) -> Tuple[Reward, str]:
        """Grade logical bug detection"""
        comment = action.review_comment.lower()
        bug_loc = action.bug_location or ""
        
        score = 0.0
        msg = "Logic review: "
        
        # Look for logic error keywords
        logic_keywords = ["off-by-one", "wrong", "comparison", "logic", "incorrect", "condition"]
        found_keywords = sum(1 for kw in logic_keywords if kw in comment)
        
        if found_keywords > 0:
            score += 0.3
        
        # Check bug location accuracy
        if bug_loc:
            try:
                reported_line = int(''.join(filter(str.isdigit, bug_loc)))
                actual_lines = self.current_snippet.get("error_lines", [])
                if reported_line in actual_lines:
                    score += 0.7
                else:
                    score += 0.2
            except:
                score += 0.2
        else:
            score += 0.2
        
        score = min(1.0, score)
        
        if score >= 0.8:
            msg += f"Correct logical bug found! Score: {score:.2f}"
        elif score >= 0.5:
            msg += f"Partially correct. Score: {score:.2f}"
        else:
            msg += f"Incorrect analysis. Score: {score:.2f}"
        
        return Reward(value=score, message=msg), msg
    
    def _grade_improvement_review(self, action: Action) -> Tuple[Reward, str]:
        """Grade code improvement suggestions"""
        comment = action.review_comment.lower()
        severity = (action.severity or "").lower()
        
        score = 0.0
        msg = "Improvement review: "
        
        # Look for improvement keywords
        improvement_keywords = ["refactor", "simplify", "optimize", "pythonic", "better", "improvement", 
                               "cython", "comprehension", "listcomp", "context", "with", "builtin", "library"]
        found_keywords = sum(1 for kw in improvement_keywords if kw in comment)
        
        if found_keywords > 0:
            score += 0.4
        
        # Check if suggestion is actionable
        if len(comment) > 20:
            score += 0.3
        
        # Check severity level
        if severity in ["minor", "low", "improvement"]:
            score += 0.3
        elif severity in ["major", "critical"]:
            score += 0.1  # Should suggest improvements, not mark as critical
        else:
            score += 0.2
        
        score = min(1.0, score)
        
        if score >= 0.8:
            msg += f"Excellent improvement suggestion! Score: {score:.2f}"
        elif score >= 0.5:
            msg += f"Good suggestion. Score: {score:.2f}"
        else:
            msg += f"Suggestion could be more specific. Score: {score:.2f}"
        
        return Reward(value=score, message=msg), msg


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_environment(task_type: str = "syntax_review", max_steps: int = 5) -> CodeReviewEnvironment:
    """Factory function to create environment"""
    return CodeReviewEnvironment(task_type=task_type, max_steps=max_steps)


if __name__ == "__main__":
    # Test the environment
    env = CodeReviewEnvironment(task_type="syntax_review", max_steps=3)
    obs = env.reset()
    
    print(f"Task Type: {obs.task_type}")
    print(f"Code Snippet:\n{obs.code_snippet}\n")
    
    # Simulate an action
    action = Action(
        review_comment="Missing colon after function definition",
        bug_location="line 1",
        severity="critical"
    )
    
    next_obs, reward, done, info = env.step(action)
    print(f"Reward: {reward.value:.2f}")
    print(f"Message: {reward.message}")
    print(f"Done: {done}")
