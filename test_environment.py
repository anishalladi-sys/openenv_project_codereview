#!/usr/bin/env python3
"""
Test suite for Code Review Environment
Tests all three tasks and validates grading logic.
"""

import sys
from environment import (
    CodeReviewEnvironment,
    Action,
    Observation,
    SYNTAX_REVIEW_SNIPPETS,
    LOGIC_REVIEW_SNIPPETS,
    IMPROVEMENT_REVIEW_SNIPPETS,
)


def test_environment_initialization():
    """Test environment initialization"""
    print("Testing environment initialization...")
    
    for task_type in ["syntax_review", "logic_review", "improvement_review"]:
        env = CodeReviewEnvironment(task_type=task_type, max_steps=5)
        assert env.task_type == task_type
        assert env.max_steps == 5
        assert env.current_step == 0
        assert not env.done
        print(f"  ✓ {task_type} initialization OK")


def test_environment_reset():
    """Test environment reset"""
    print("Testing environment reset...")
    
    env = CodeReviewEnvironment(task_type="syntax_review", max_steps=5)
    obs = env.reset()
    
    assert isinstance(obs, Observation)
    assert isinstance(obs.code_snippet, str)
    assert len(obs.code_snippet) > 0
    assert obs.task_type == "syntax_review"
    assert env.current_step == 0
    assert not env.done
    print("  ✓ Reset OK")


def test_syntax_review_task():
    """Test syntax review task"""
    print("Testing syntax review task...")
    
    env = CodeReviewEnvironment(task_type="syntax_review", max_steps=5)
    env.reset()
    
    # Test with good action
    action = Action(
        review_comment="Missing colon after function definition",
        bug_location="line 1",
        severity="critical"
    )
    
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward.value, float)
    assert 0.0 <= reward.value <= 1.0
    assert isinstance(reward.message, str)
    assert len(reward.message) > 0
    print(f"  ✓ Step executed, reward={reward.value:.2f}")
    print(f"    Message: {reward.message}")


def test_logic_review_task():
    """Test logic review task"""
    print("Testing logic review task...")
    
    env = CodeReviewEnvironment(task_type="logic_review", max_steps=5)
    env.reset()
    
    action = Action(
        review_comment="Off-by-one error in comparison",
        bug_location="line 4",
        severity="major"
    )
    
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward.value, float)
    assert 0.0 <= reward.value <= 1.0
    print(f"  ✓ Step executed, reward={reward.value:.2f}")
    print(f"    Message: {reward.message}")


def test_improvement_review_task():
    """Test improvement review task"""
    print("Testing improvement review task...")
    
    env = CodeReviewEnvironment(task_type="improvement_review", max_steps=5)
    env.reset()
    
    action = Action(
        review_comment="Can use list comprehension for more Pythonic code",
        bug_location=None,
        severity="minor"
    )
    
    obs, reward, done, info = env.step(action)
    
    assert isinstance(reward.value, float)
    assert 0.0 <= reward.value <= 1.0
    print(f"  ✓ Step executed, reward={reward.value:.2f}")
    print(f"    Message: {reward.message}")


def test_episode_completion():
    """Test full episode completion"""
    print("Testing full episode...")
    
    env = CodeReviewEnvironment(task_type="syntax_review", max_steps=3)
    obs = env.reset()
    
    total_reward = 0.0
    for step in range(3):
        action = Action(
            review_comment="This is an issue",
            bug_location=f"line {step+1}",
            severity="major" if step < 2 else "minor"
        )
        obs, reward, done, info = env.step(action)
        total_reward += reward.value
        
        if done:
            print(f"  Episode ended at step {step+1}")
            break
    
    assert env.current_step > 0
    assert total_reward >= 0.0
    print(f"  ✓ Episode completed, total_reward={total_reward:.2f}")


def test_environment_state():
    """Test environment state tracking"""
    print("Testing state tracking...")
    
    env = CodeReviewEnvironment(task_type="logic_review", max_steps=5)
    obs = env.reset()
    
    state = env.state()
    
    assert state["task_type"] == "logic_review"
    assert state["step"] == 0
    assert state["max_steps"] == 5
    assert not state["done"]
    assert state["episode_reward"] == 0.0
    
    # Take action
    action = Action(review_comment="Test comment", bug_location="line 1", severity="minor")
    obs, reward, done, info = env.step(action)
    
    state = env.state()
    assert state["step"] == 1
    assert state["episode_reward"] > 0.0
    assert state["num_actions"] == 1
    
    print("  ✓ State tracking OK")


def test_code_snippets():
    """Verify code snippets are available"""
    print("Testing code snippets...")
    
    assert len(SYNTAX_REVIEW_SNIPPETS) >= 5
    assert len(LOGIC_REVIEW_SNIPPETS) >= 5
    assert len(IMPROVEMENT_REVIEW_SNIPPETS) >= 5
    
    for snippet in SYNTAX_REVIEW_SNIPPETS:
        assert "code" in snippet
        assert "errors" in snippet
        assert len(snippet["code"]) > 0
        assert len(snippet["errors"]) > 0
    
    print(f"  ✓ Syntax snippets: {len(SYNTAX_REVIEW_SNIPPETS)}")
    print(f"  ✓ Logic snippets: {len(LOGIC_REVIEW_SNIPPETS)}")
    print(f"  ✓ Improvement snippets: {len(IMPROVEMENT_REVIEW_SNIPPETS)}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Code Review Environment Tests")
    print("="*60 + "\n")
    
    try:
        test_environment_initialization()
        test_environment_reset()
        test_code_snippets()
        test_syntax_review_task()
        test_logic_review_task()
        test_improvement_review_task()
        test_episode_completion()
        test_environment_state()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
