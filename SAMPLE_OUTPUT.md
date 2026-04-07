# Sample Output Examples

## Syntax Review Task

```
[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Missing colon after function definition on line 1 reward=0.95 done=false error=null
[STEP] step=2 action=Review complete - error identified and located reward=0.92 done=true error=null
[END] success=true steps=2 rewards=0.95,0.92
```

**Code Reviewed:**
```python
def calculate_sum(numbers)  # Missing colon here
    total = 0
    for num in numbers:
        total += num
    return total
```

## Logic Review Task

```
[START] task=logic_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Found off-by-one error in indexing at line 2 reward=0.88 done=false error=null
[STEP] step=2 action=Confirmed wrong comparison operator - should be less than reward=0.91 done=false error=null
[STEP] step=3 action=Final analysis complete - logic bug confirmed reward=0.89 done=true error=null
[END] success=true steps=3 rewards=0.88,0.91,0.89
```

**Code Reviewed:**
```python
def find_min(numbers):
    min_val = float('inf')
    for num in numbers:
        if num > min_val:  # Bug: should be < not >
            min_val = num
    return min_val
```

## Improvement Review Task

```
[START] task=improvement_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Can use list comprehension for Pythonic code improvement reward=0.85 done=false error=null
[STEP] step=2 action=Recommend list comprehension: [n for n in numbers if n % 2 == 0] reward=0.90 done=true error=null
[END] success=true steps=2 rewards=0.85,0.90
```

**Code Reviewed:**
```python
def get_even_numbers(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num)
    return result
```

## Error Handling

```
[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=error reward=0.00 done=true error=Connection timeout after 30s
[END] success=false steps=1 rewards=
```

## Multiple Episodes

```
=== EPISODE 1 ===
[START] task=syntax_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Missing colon reward=0.92 done=false error=null
[STEP] step=2 action=Confirmed error reward=0.88 done=true error=null
[END] success=true steps=2 rewards=0.92,0.88

=== EPISODE 2 ===
[START] task=logic_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=Off-by-one error found reward=0.87 done=false error=null
[STEP] step=2 action=Error localized to line 2 reward=0.91 done=false error=null
[STEP] step=3 action=Analysis complete reward=0.89 done=true error=null
[END] success=true steps=3 rewards=0.87,0.91,0.89

=== EPISODE 3 ===
[START] task=improvement_review env=openenv-codereview model=claude-sonnet-4-20250514
[STEP] step=1 action=List comprehension improvement reward=0.84 done=false error=null
[STEP] step=2 action=Context manager for file handling reward=0.86 done=true error=null
[END] success=true steps=2 rewards=0.84,0.86
```

## Reward Distribution

### Syntax Review (Easy)
- Perfect detection: 0.95-1.00
- Correct with minor deviation: 0.80-0.95
- Partial detection: 0.50-0.80
- Missed detection: 0.00-0.50

### Logic Review (Medium)
- Correct bug identified: 0.90-1.00
- Correct with wrong line: 0.70-0.90
- Partial understanding: 0.40-0.70
- Incorrect: 0.00-0.40

### Improvement Review (Hard)
- Excellent suggestion: 0.90-1.00
- Good suggestion: 0.70-0.90
- Acceptable suggestion: 0.50-0.70
- Weak suggestion: 0.00-0.50

## Baseline Runs

### Random Agent (Expected Baseline)
```
Syntax Review Average: 0.45
Logic Review Average: 0.35
Improvement Review: 0.40
```

### Keyword Matching Agent (Proposed Baseline: 0.70)
```
Syntax Review Average: 0.75
Logic Review Average: 0.65
Improvement Review: 0.70
```

### Claude 3.5 Sonnet (Advanced Agent - Expected)
```
Syntax Review Average: 0.92
Logic Review Average: 0.88
Improvement Review: 0.85
```

## Output Format Validation

✓ [START] exactly 3 fields (task, env, model)
✓ [STEP] has exactly 5 fields (step, action, reward, done, error)
✓ Rewards formatted to 2 decimal places (0.00 to 1.00)
✓ done values are lowercase (true/false)
✓ error field is null or error message
✓ [END] exactly 3 fields (success, steps, rewards)
✓ success values are lowercase (true/false)
✓ Multiple rewards comma-separated in [END]
