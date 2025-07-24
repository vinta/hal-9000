# Spawn Subagents

## Step 1: Analyze Tasks

- Identify dependencies between tasks
- Detect resource conflicts (files, directories)
- Estimate execution time: quick (<1min), medium (1-5min), long (>5min)

## Step 2: Handle Time Disparities

If one task takes 10+ minutes while others take 1-3 minutes:

- Report: "Task X: ~10+ min, Tasks Y,Z: ~1-3 min. Execute shorter tasks first?"
- Default: Yes, defer long task

## Step 3: Execute Tasks In Parallel

- Launch all independent tasks simultaneously as subagents
- Each subagent runs in isolation
- Dependent tasks wait for prerequisites

## Step 4: Monitor & Report

- Track all subagents continuously
- Report completion as tasks finish
- Continue remaining tasks if one fails (unless dependent)
- Final summary: list each task with ✓ or ✗ status

### Error Handling

- Capture errors without stopping other tasks
- Halt dependent tasks if prerequisite fails
- Include actionable fixes in error messages

---

**Tasks to execute:**

$ARGUMENTS
