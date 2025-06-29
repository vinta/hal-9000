# Pair Programming with Gemini CLI

When researching complex topics that require multiple independent searches, launch parallel Gemini subagents to gather information simultaneously. This dramatically reduces research time and enables comprehensive analysis across multiple domains.

## File/Folder Analysis Pattern

```bash
# Architecture overview
gemini --all_files -p "@src/ What's the architecture pattern? List main components"

# Security audit
gemini --all_files -p "@./ Find security vulnerabilities (XSS, SQL injection, hardcoded secrets)"

# Feature verification
gemini --all_files -p "@src/ Is OAuth2 implemented? Show the flow"

# Code quality
gemini --all_files -p "@src/ Find code smells and suggest refactoring"
```

## Parallel Search Pattern

```bash
# Research + implement
gemini --sandbox -p "WebSocket best practices 2024" > research.txt &
gemini -p "@src/websocket/ Analyze our implementation" > current.txt &
wait
cat *.txt | gemini -p "How to improve our WebSocket implementation?"
```

## Process Management

```bash
jobs -l                  # List running searches
kill %1                  # Kill job #1
pkill -f "gemini"       # Kill all gemini processes
wait                     # Wait for all jobs
wait $!                  # Wait for last job
```

## When to Use gemini

- Files > 100KB or entire repositories
- Multiple file comparisons
- Technical research requiring current information
- Parallel analysis of complex topics

---

**Tasks to execute:**

$ARGUMENTS
