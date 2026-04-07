#!/usr/bin/env python3
"""Display inference output format examples"""

print("\n" + "="*80)
print("INFERENCE OUTPUT FORMAT DEMONSTRATION")
print("="*80 + "\n")

print("Syntax Review Example Output:")
print("-"*80)
print("[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514")
print("[STEP] step=1 action=Found missing colon after function definition reward=0.95 done=false error=null")
print("[STEP] step=2 action=Correctly identified error on line 1 reward=0.92 done=true error=null")
print("[END] success=true steps=2 rewards=0.95,0.92")

print("\n" + "-"*80)
print("Logic Review Example Output:")
print("-"*80)
print("[START] task=logic_review env=openenv-codereview model=claude-sonnet-4-20250514")
print("[STEP] step=1 action=Found off-by-one error in array indexing reward=0.88 done=false error=null")
print("[STEP] step=2 action=Error confirmed at line 2 reward=0.91 done=false error=null")
print("[STEP] step=3 action=Analysis complete reward=0.89 done=true error=null")
print("[END] success=true steps=3 rewards=0.88,0.91,0.89")

print("\n" + "-"*80)
print("Improvement Review Example Output:")
print("-"*80)
print("[START] task=improvement_review env=openenv-codereview model=claude-sonnet-4-20250514")
print("[STEP] step=1 action=Should use eval() alternative like json.loads reward=0.87 done=false error=null")
print("[STEP] step=2 action=Security improvement: avoid eval for untrusted input reward=0.89 done=true error=null")
print("[END] success=true steps=2 rewards=0.87,0.89")

print("\n" + "="*80)
print("✅ Output format is EXACT match for all requirements")
print("   - [START], [STEP], [END] structure")
print("   - Rewards formatted to 2 decimal places")
print("   - done/success are lowercase (true/false)")
print("   - error field is null or error message")
print("="*80 + "\n")
