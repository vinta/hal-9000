# Parallel Task Execution with Subagents

## Pre-execution Analysis

- Carefully analyze all requested tasks to identify potential conflicts or dependencies
- Flag any tasks that may interfere with each other before starting execution
- If conflicts are detected, propose a resolution strategy before proceeding
- If you found some tasks will absolutely need to run much longer than others, skip time-consumming tasks, do other tasks in parallel first.

## Execution Requirements

1. **Parallel Processing**: Execute all tasks simultaneously using subagents
2. **Real-time Reporting**: Report completion of each subtask immediately upon finish
   - Do NOT wait for all tasks to complete before reporting
   - Provide status updates as each task progresses
3. **Independence**: Ensure each subagent operates independently unless dependencies exist

## Task List

Execute the following tasks in parallel:

$ARGUMENTS

## Expected Behavior

- Start all non-conflicting tasks simultaneously
- Report each completed task immediately with results
- Continue processing remaining tasks while reporting
- If any task fails, report the failure immediately and continue with others
