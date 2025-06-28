# Pair Programming with Gemini CLI

When researching complex topics that require multiple independent searches, launch parallel Gemini subagents to gather information simultaneously. This dramatically reduces research time and enables comprehensive analysis across multiple domains.

## Command Structure

```bash
gemini -p "prompt"              # Code analysis (read-only)
gemini --sandbox -p "prompt"    # Web searches and exploration
gemini --yolo -p "prompt"       # File modifications (use sparingly)
gemini --all_files -p "prompt"  # Include all files in current directory
```

## File/Directory Analysis

### Basic Syntax

```bash
gemini -p "@file.py Analyze this file"
gemini -p "@src/ Summarize this directory"
gemini -p "@src/ @tests/ Compare these directories"
gemini -p "@./ Analyze entire project"
```

### Common Analysis Tasks

```bash
# Architecture overview
gemini -p "@src/ What's the architecture pattern? List main components"

# Security audit
gemini -p "@./ Find security vulnerabilities (XSS, SQL injection, hardcoded secrets)"

# Feature verification
gemini -p "@src/ Is OAuth2 implemented? Show the flow"

# Code quality
gemini -p "@src/ Find code smells and suggest refactoring"
```

## Parallel Search Pattern

### Basic Template

```bash
# Launch parallel searches
gemini --sandbox -p "search query 1" > result1.txt &
gemini --sandbox -p "search query 2" > result2.txt &
gemini --sandbox -p "search query 3" > result3.txt &
wait

# Synthesize results
cat result*.txt | gemini --sandbox -p "Synthesize findings into actionable insights"
```

### Practical Examples

#### Technology Research

```bash
TECH="React Server Components"
gemini --sandbox -p "$TECH implementation patterns" > patterns.txt &
gemini --sandbox -p "$TECH performance benchmarks" > performance.txt &
gemini --sandbox -p "$TECH common pitfalls" > pitfalls.txt &
wait
cat *.txt | gemini --sandbox -p "Create $TECH implementation guide"
```

#### Stack Comparison

```bash
for stack in "Next.js" "Remix" "SvelteKit"; do
  gemini --sandbox -p "$stack pros/cons for SaaS in 2024" > ${stack}.txt &
done
wait
cat *.txt | gemini --sandbox -p "Create comparison table with recommendation"
```

#### Security Research

```bash
gemini --sandbox -p "OWASP Top 10 2024" > owasp.txt &
gemini --sandbox -p "JWT vulnerabilities and fixes" > jwt.txt &
gemini -p "@src/ Analyze our authentication" > our_auth.txt &
wait
cat *.txt | gemini -p "Create security audit checklist for our codebase"
```

## Process Management

```bash
jobs -l                  # List running searches
kill %1                  # Kill job #1
pkill -f "gemini"       # Kill all gemini processes
wait                     # Wait for all jobs
wait $!                  # Wait for last job
```

## When to Use

### Use Gemini for:

- Files > 100KB or entire repositories
- Multiple file comparisons
- Technical research requiring current information
- Parallel analysis of complex topics

### Use `--sandbox` for:

- Web searches
- Best practices research
- API documentation lookups
- Current technology comparisons

### Use file inclusion (@) for:

- Code analysis
- Architecture review
- Security audits
- Feature verification

## Best Practices

1. **Parallel searches**: Limit to 5-10 concurrent processes
2. **File paths**: Always relative to current directory
3. **Output files**: Use descriptive names (e.g., `auth_analysis.txt`)
4. **Complex topics**: Break into focused sub-queries
5. **Synthesis**: Always aggregate parallel results

## Quick Examples

```bash
# Analyze large codebase
gemini --all_files -p "Summarize this project's architecture"

# Research + implement
gemini --sandbox -p "WebSocket best practices 2024" > research.txt &
gemini -p "@src/websocket/ Analyze our implementation" > current.txt &
wait
cat *.txt | gemini -p "How to improve our WebSocket implementation?"

# Multi-domain research
TOPIC="microservices migration"
gemini --sandbox -p "$TOPIC technical guide" > tech.txt &
gemini --sandbox -p "$TOPIC cost analysis" > cost.txt &
gemini --sandbox -p "$TOPIC case studies" > cases.txt &
wait
cat *.txt | gemini --sandbox -p "Create migration roadmap"
```

## Error Handling

```bash
# Capture errors
gemini --sandbox -p "search" > out.txt 2> err.txt &

# Timeout long searches
timeout 60s gemini --sandbox -p "complex search" > result.txt &

# Retry on failure
until gemini --sandbox -p "search" > result.txt || [ $RETRY -eq 3 ]; do
  RETRY=$((RETRY+1))
  sleep 5
done
```

---

**Tasks to execute:**

$ARGUMENTS
