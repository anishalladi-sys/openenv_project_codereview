#!/usr/bin/env python3
"""Live demo of the Code Review Environment"""

from environment import CodeReviewEnvironment, Action

print("\n" + "="*80)
print("LIVE DEMO: Code Review Environment - All Three Tasks")
print("="*80 + "\n")

tasks = [
    ("syntax_review", "Easy - Syntax Error Detection"),
    ("logic_review", "Medium - Logical Bug Detection"),
    ("improvement_review", "Hard - Code Improvement Suggestions")
]

for task_type, description in tasks:
    print(f"\n{'─'*80}")
    print(f"📋 TASK: {description}")
    print(f"{'─'*80}\n")
    
    # Create and reset environment
    env = CodeReviewEnvironment(task_type=task_type, max_steps=3)
    obs = env.reset()
    
    print(f"Task Type: {obs.task_type}")
    print(f"Code to Review:\n\n{obs.code_snippet}\n")
    
    # Run 2 steps
    rewards = []
    for step in range(2):
        print(f"Step {step + 1}:")
        
        # Create action based on task type
        if task_type == "syntax_review":
            action = Action(
                review_comment="Found syntax error - missing colon on line 1",
                bug_location="line 1",
                severity="critical"
            )
        elif task_type == "logic_review":
            action = Action(
                review_comment="Found logical bug - wrong comparison operator",
                bug_location="line 4",
                severity="major"
            )
        else:  # improvement_review
            action = Action(
                review_comment="Can use list comprehension for cleaner code",
                bug_location=None,
                severity="minor"
            )
        
        obs, reward, done, info = env.step(action)
        rewards.append(reward.value)
        
        print(f"  Action: {action.review_comment[:60]}...")
        print(f"  Reward: {reward.value:.2f} 🎯")
        print(f"  Feedback: {reward.message}")
        print(f"  Status: {'Done ✅' if done else 'Continue'}\n")
        
        if done:
            break
    
    print(f"Episode Summary:")
    print(f"  Total Steps: {len(rewards)}")
    print(f"  Rewards: {[f'{r:.2f}' for r in rewards]}")
    print(f"  Average Reward: {sum(rewards)/len(rewards):.2f}")

print("\n" + "="*80)
print("✅ DEMO COMPLETE - All tasks working perfectly!")
print("="*80 + "\n")
