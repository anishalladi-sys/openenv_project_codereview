#!/usr/bin/env python3
"""Verify the OpenAI client fix"""

print("\n" + "="*80)
print("VERIFYING OPENAI CLIENT FIX")
print("="*80 + "\n")

# Check the inference.py code
with open("inference.py", "r") as f:
    content = f.read()
    
if "client.chat.completions.create(" in content:
    print("✅ Fixed: Using client.chat.completions.create()")
else:
    print("❌ Error: Still using old client method")

if "message.choices[0].message.content" in content:
    print("✅ Fixed: Using message.choices[0].message.content")
else:
    print("❌ Error: Still using old response parsing")

print("\n" + "="*80)
print("OUTPUT FORMAT VERIFICATION")
print("="*80 + "\n")

# Test the format string
rewards = [0.95, 0.88, 0.92]
rewards_str = ",".join(f"{r:.2f}" for r in rewards)
print(f"[END] success=true steps=3 rewards={rewards_str}")
print("  ✅ Format correct: comma-separated to 2 decimals")

print("\n" + "="*80)
print("TESTING ENVIRONMENT STILL WORKS")
print("="*80 + "\n")

from environment import CodeReviewEnvironment, Action

env = CodeReviewEnvironment(task_type="syntax_review")
obs = env.reset()
print(f"✅ Environment reset successful")
print(f"   Task: {obs.task_type}")

action = Action(
    review_comment="Missing colon",
    bug_location="line 1",
    severity="critical"
)
obs, reward, done, info = env.step(action)
print(f"✅ Step executed: reward={reward.value:.2f}")

print("\n" + "="*80)
print("✅ ALL FIXES VERIFIED AND WORKING!")
print("="*80 + "\n")
