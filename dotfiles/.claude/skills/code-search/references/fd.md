# fd Reference

fd is a fast, user-friendly alternative to `find`. It respects `.gitignore` automatically and uses parallel execution.

## CLI Basics

```bash
fd PATTERN [PATH...]              # Search for files matching pattern
fd -e EXT                         # Search by extension
fd -t TYPE                        # Search by type (f=file, d=dir, l=link, x=exec)
fd -H                             # Include hidden files
fd -I                             # Include gitignored files
```

## Essential Flags

### Pattern Matching

| Flag               | Short | Description                            |
| ------------------ | ----- | -------------------------------------- |
| (default)          |       | Regex pattern matching                 |
| `--glob`           | `-g`  | Glob pattern instead of regex          |
| `--fixed-strings`  | `-F`  | Treat pattern as literal               |
| `--case-sensitive` | `-s`  | Case-sensitive (default is smart-case) |
| `--ignore-case`    | `-i`  | Force case-insensitive                 |

### Type Filtering

| Flag                | Short    | Description                      |
| ------------------- | -------- | -------------------------------- |
| `--type file`       | `-t f`   | Only files                       |
| `--type directory`  | `-t d`   | Only directories                 |
| `--type symlink`    | `-t l`   | Only symlinks                    |
| `--type executable` | `-t x`   | Only executables                 |
| `--extension`       | `-e EXT` | Filter by extension (repeatable) |

### Visibility Filtering

| Flag             | Short | Description                        |
| ---------------- | ----- | ---------------------------------- |
| `--hidden`       | `-H`  | Include hidden files/dirs          |
| `--no-ignore`    | `-I`  | Include gitignored files           |
| `--unrestricted` | `-u`  | Hidden + ignored (repeat for more) |

### Path Filtering

| Flag                         | Description                    |
| ---------------------------- | ------------------------------ |
| `--max-depth NUM` / `-d NUM` | Maximum search depth           |
| `--min-depth NUM`            | Minimum search depth           |
| `--exclude PATTERN` / `-E`   | Exclude paths matching pattern |
| `--full-path` / `-p`         | Match against full path        |

### Time Filtering

| Flag                    | Description               |
| ----------------------- | ------------------------- |
| `--changed-within TIME` | Modified within timeframe |
| `--changed-before TIME` | Modified before timeframe |

### Size Filtering

| Flag           | Description       |
| -------------- | ----------------- |
| `--size +SIZE` | Larger than SIZE  |
| `--size -SIZE` | Smaller than SIZE |

### Execution

| Flag               | Short | Description                  |
| ------------------ | ----- | ---------------------------- |
| `--exec CMD`       | `-x`  | Execute CMD for each result  |
| `--exec-batch CMD` | `-X`  | Execute CMD with all results |

## Pattern Matching

### Regex (Default)

```bash
fd '^test_.*\.py$'            # Python test files
fd '\.config$'                # Files ending in .config
fd '^[A-Z]'                   # Files starting with uppercase
fd 'component.*\.tsx$'        # Component TSX files
```

### Glob Mode

```bash
fd -g '*.lua'                 # All Lua files
fd -g 'test-*.js'             # test-*.js files
fd -g '*.{json,yaml,toml}'    # Config files
```

### Fixed Strings

```bash
fd -F 'my.config'             # Exact match (no regex)
```

## Extension Filtering

```bash
# Single extension
fd -e rs                      # Rust files
fd -e md                      # Markdown files

# Multiple extensions
fd -e ts -e tsx               # TypeScript files
fd -e jpg -e jpeg -e png      # Image files
fd -e json -e yaml -e toml    # Config files
```

## Type Filtering

```bash
# Files only
fd -t f PATTERN

# Directories only
fd -t d PATTERN

# Executable files
fd -t x

# Symlinks
fd -t l

# Combine types
fd -t f -t l PATTERN          # Files and symlinks
```

## Depth Control

```bash
# Current directory only
fd -d 1 PATTERN

# Max 3 levels deep
fd -d 3 PATTERN
fd --max-depth 3 PATTERN

# Skip current directory (min depth 2)
fd --min-depth 2 PATTERN
```

## Hidden and Ignored Files

```bash
# Include hidden files (starting with .)
fd -H PATTERN
fd --hidden PATTERN

# Include gitignored files
fd -I PATTERN
fd --no-ignore PATTERN

# Include both
fd -HI PATTERN
fd -u PATTERN                 # Shorthand

# Include all (hidden, ignored, and no global ignore)
fd -uu PATTERN
```

## Exclusions

```bash
# Exclude directories
fd PATTERN -E node_modules
fd PATTERN -E node_modules -E dist -E build

# Exclude patterns
fd -e js -E '*.min.js'
fd -e py -E '__pycache__'
fd -e rs -E target

# Combine with hidden
fd -H -E .git
```

## Time-Based Search

### Time Units

- `s` = seconds
- `m` = minutes
- `h` = hours
- `d` = days
- `w` = weeks
- `y` = years

### Examples

```bash
# Recently modified
fd --changed-within 1d        # Last 24 hours
fd --changed-within 2w        # Last 2 weeks
fd --changed-within 3h        # Last 3 hours

# Older files
fd --changed-before 1y        # Older than 1 year
fd --changed-before 30d       # Older than 30 days

# Combine with other filters
fd -e log --changed-before 7d # Old log files
```

## Size-Based Search

### Size Units

- `b` = bytes
- `k` = kilobytes
- `m` = megabytes
- `g` = gigabytes
- `t` = terabytes

### Examples

```bash
# Large files
fd --size +10m                # Larger than 10 MB
fd --size +1g                 # Larger than 1 GB

# Small files
fd --size -1k                 # Smaller than 1 KB

# Range
fd --size +100k --size -10m   # Between 100 KB and 10 MB
```

## Command Execution

### Per-Result Execution (-x)

```bash
# Placeholders:
#   {}   Full path
#   {/}  Basename
#   {//} Parent directory
#   {.}  Path without extension
#   {/.} Basename without extension

# Delete files
fd -e log -x rm {}

# Convert images
fd -e jpg -x convert {} {.}.png

# Format code
fd -e rs -x rustfmt {}
fd -e py -x black {}

# Show file info
fd -e py -x wc -l {}
```

### Batch Execution (-X)

```bash
# Single command with all files
fd -e md -X wc -l             # Word count all markdown
fd -e rs -X cargo fmt --       # Format all Rust files
fd -e py -X cat | wc -l       # Total lines in Python files
```

## Integration with Other Tools

### With ripgrep

```bash
# Find files, then search content
fd -e py | xargs rg 'import numpy'
fd -e ts | xargs rg 'TODO'
fd -e md | xargs rg '# '

# More complex pipelines
fd -e js -E node_modules | xargs rg 'console\.log'
```

### With xargs

```bash
# Delete files
fd -e pyc | xargs rm
fd node_modules -t d | xargs rm -rf

# Open in editor
fd -e md | xargs vim
fd -e tsx | xargs code
```

## Common Patterns

### Development Workflows

```bash
# Find test files
fd -e test.js -e spec.js
fd '^test_.*\.py$'
fd '_test\.go$'

# Find configuration
fd -g '*.config.js'
fd -g '.env*' -H
fd -g '*rc' -H

# Find source files
fd -e rs -e toml -t f
fd -e py -E __pycache__
fd -e ts -e tsx src/
```

### Cleanup

```bash
# Remove build artifacts
fd -e pyc -x rm
fd -t d node_modules -x rm -rf
fd -g '*.log' --changed-before 30d -X rm

# Find large files
fd --size +100m -t f
fd --size +1g -t f -x du -h
```

### Path-Based Search

```bash
# Only in specific directories
fd PATTERN src/
fd PATTERN src/ tests/

# Full path matching
fd -p 'src/components/.*\.tsx$'
fd -p 'tests/.*test.*\.py$'
```

## Performance Tips

1. **Use depth limits when possible**:

   ```bash
   fd -d 2 PATTERN             # Faster than unlimited
   ```

2. **Exclude heavy directories**:

   ```bash
   fd PATTERN -E node_modules -E .git -E target
   ```

3. **Use type filters**:

   ```bash
   fd -t f PATTERN             # Skip directory processing
   ```

4. **Leverage gitignore** (default behavior):

   - fd automatically respects `.gitignore`
   - Use `-I` only when needed

5. **Sequential search if order matters**:
   ```bash
   fd PATTERN -j 1             # Single-threaded
   ```
