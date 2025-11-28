# fd File Finding

Expert knowledge for using `fd` as a fast, user-friendly alternative to `find` with smart defaults and powerful filtering.

## Core Expertise

**fd Advantages**

- Fast parallel execution (written in Rust)
- Colorized output by default
- Respects `.gitignore` automatically
- Smart case-insensitive search
- Simpler syntax than `find`
- Regular expression support

## Basic Usage

### Simple File Search

```bash
# Find all files named config
fd config

# Find files with extension
fd -e rs                    # All Rust files
fd -e md                    # All Markdown files
fd -e js -e ts              # JavaScript and TypeScript

# Case-sensitive search
fd -s Config                # Only exact case match
```

### Pattern Matching

```bash
# Regex patterns
fd '^test_.*\.py$'          # Python test files
fd '\.config$'              # Files ending in .config
fd '^[A-Z]'                 # Files starting with uppercase

# Glob patterns
fd '*.lua'                  # All Lua files
fd 'test-*.js'              # test-*.js files
```

## Advanced Filtering

### Type Filtering

```bash
# Search only files
fd -t f pattern             # Files only
fd -t d pattern             # Directories only
fd -t l pattern             # Symlinks only
fd -t x pattern             # Executable files

# Multiple types
fd -t f -t l pattern        # Files and symlinks
```

### Depth Control

```bash
# Limit search depth
fd -d 1 pattern             # Only current directory
fd -d 3 pattern             # Max 3 levels deep
fd --max-depth 2 pattern    # Alternative syntax

# Minimum depth
fd --min-depth 2 pattern    # Skip current directory
```

### Hidden and Ignored Files

```bash
# Include hidden files
fd -H pattern               # Include hidden files (starting with .)

# Include ignored files
fd -I pattern               # Include .gitignore'd files
fd -u pattern               # Unrestricted: hidden + ignored

# Show all files
fd -H -I pattern            # Show everything
```

### Size Filtering

```bash
# File size filters
fd --size +10m              # Files larger than 10 MB
fd --size -1k               # Files smaller than 1 KB
fd --size +100k --size -10m # Between 100 KB and 10 MB
```

### Modification Time

```bash
# Files modified recently
fd --changed-within 1d      # Last 24 hours
fd --changed-within 2w      # Last 2 weeks
fd --changed-within 3m      # Last 3 months

# Files modified before
fd --changed-before 1y      # Older than 1 year
```

## Execution and Processing

### Execute Commands

```bash
# Execute command for each result
fd -e jpg -x convert {} {.}.png     # Convert all JPG to PNG

# Parallel execution
fd -e rs -x rustfmt                 # Format all Rust files

# Execute with multiple results
fd -e md -X wc -l                   # Word count on all Markdown files
```

### Integration with Other Tools

```bash
# Pipe to other commands
fd -e log | xargs rm                # Delete all log files
fd -e rs | xargs cat | wc -l        # Count lines in Rust files

# Use with rg for powerful search
fd -e py | xargs rg "import numpy"  # Find numpy imports in Python files

# Open files in editor
fd -e md | xargs nvim               # Open all Markdown in Neovim
```

## Common Patterns

### Development Workflows

```bash
# Find test files
fd -e test.js -e spec.js            # JavaScript tests
fd '^test_.*\.py$'                  # Python tests
fd '_test\.go$'                     # Go tests

# Find configuration files
fd -g '*.config.js'                 # Config files
fd -g '.env*'                       # Environment files
fd -g '*rc' -H                      # RC files (include hidden)

# Find source files
fd -e rs -e toml -t f               # Rust project files
fd -e py --exclude __pycache__      # Python excluding cache
fd -e ts -e tsx src/                # TypeScript in src/
```

### Cleanup Operations

```bash
# Find and remove
fd -e pyc -x rm                     # Remove Python bytecode
fd node_modules -t d -x rm -rf      # Remove node_modules
fd -g '*.log' --changed-before 30d -X rm  # Remove old logs

# Find large files
fd --size +100m -t f                # Files over 100 MB
fd --size +1g -t f -x du -h         # Size of files over 1 GB
```

### Path-Based Search

```bash
# Search in specific directories
fd pattern src/                     # Only in src/
fd pattern src/ tests/              # Multiple directories

# Exclude paths
fd -e rs -E target/                 # Exclude target directory
fd -e js -E node_modules -E dist    # Exclude multiple paths

# Full path matching
fd -p src/components/.*\.tsx$       # Match full path
```

## Best Practices

**When to Use fd**

- Finding files by name or pattern
- Searching with gitignore awareness
- Fast directory traversal
- Type-specific searches
- Time-based file queries

**When to Use find Instead**

- Complex boolean logic
- POSIX compatibility required
- Advanced permission checks
- Non-standard file attributes

**Performance Tips**

- Use `-j 1` for sequential search if order matters
- Combine with `--max-depth` to limit scope
- Use `-t f` to skip directory processing
- Leverage gitignore for faster searches in repos

**Integration with rg**

```bash
# Two-step search: find files, then search content
fd -e py | xargs rg "class.*Test"   # Find test classes in Python
fd -e rs | xargs rg "TODO"          # Find TODOs in Rust files
fd -e md | xargs rg "# "            # Find headers in Markdown
```

## Quick Reference

### Essential Options

| Option     | Purpose                  | Example              |
| ---------- | ------------------------ | -------------------- |
| `-e EXT`   | Filter by extension      | `fd -e rs`           |
| `-t TYPE`  | Filter by type (f/d/l/x) | `fd -t d`            |
| `-d DEPTH` | Max search depth         | `fd -d 3`            |
| `-H`       | Include hidden files     | `fd -H .env`         |
| `-I`       | Include ignored files    | `fd -I build`        |
| `-u`       | Unrestricted (no ignore) | `fd -u pattern`      |
| `-E PATH`  | Exclude path             | `fd -E node_modules` |
| `-x CMD`   | Execute command          | `fd -e log -x rm`    |
| `-X CMD`   | Batch execute            | `fd -e md -X cat`    |
| `-s`       | Case-sensitive           | `fd -s Config`       |
| `-g GLOB`  | Glob pattern             | `fd -g '*.json'`     |

### Time Units

- `s` = seconds
- `m` = minutes
- `h` = hours
- `d` = days
- `w` = weeks
- `y` = years

### Size Units

- `b` = bytes
- `k` = kilobytes
- `m` = megabytes
- `g` = gigabytes
- `t` = terabytes

## Common Command Patterns

```bash
# Find recently modified source files
fd -e rs --changed-within 1d

# Find large files in current directory
fd -d 1 -t f --size +10m

# Find executable scripts
fd -t x -e sh

# Find config files including hidden
fd -H -g '*config*'

# Find and count lines
fd -e py -X wc -l

# Find files excluding build artifacts
fd -e js -E dist -E node_modules -E build
```

This makes fd the preferred tool for fast, intuitive file finding in development workflows.
