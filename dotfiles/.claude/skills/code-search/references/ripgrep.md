# ripgrep Reference

ripgrep (`rg`) is an ultra-fast text search tool with regex support. It respects `.gitignore` by default and provides colorized output.

## CLI Basics

```bash
rg PATTERN [PATH...]              # Basic search
rg PATTERN -t TYPE                # Filter by file type
rg PATTERN -g 'GLOB'              # Filter by glob pattern
rg -F 'LITERAL'                   # Fixed string (no regex)
rg -i PATTERN                     # Case-insensitive
rg -S PATTERN                     # Smart case (case-insensitive unless uppercase present)
```

## Essential Flags

### Search Behavior

| Flag              | Short | Description                                   |
| ----------------- | ----- | --------------------------------------------- |
| `--fixed-strings` | `-F`  | Treat pattern as literal string               |
| `--ignore-case`   | `-i`  | Case-insensitive search                       |
| `--smart-case`    | `-S`  | Case-insensitive unless pattern has uppercase |
| `--word-regexp`   | `-w`  | Match whole words only                        |
| `--multiline`     | `-U`  | Allow matches spanning lines                  |
| `--pcre2`         | `-P`  | Use PCRE2 regex (lookahead/lookbehind)        |

### Output Control

| Flag                    | Short    | Description                     |
| ----------------------- | -------- | ------------------------------- |
| `--count`               | `-c`     | Count matches per file          |
| `--count-matches`       |          | Count total matches             |
| `--files-with-matches`  | `-l`     | List files with matches         |
| `--files-without-match` |          | List files without matches      |
| `--only-matching`       | `-o`     | Print only matched text         |
| `--context`             | `-C NUM` | Show NUM lines before/after     |
| `--before-context`      | `-B NUM` | Show NUM lines before           |
| `--after-context`       | `-A NUM` | Show NUM lines after            |
| `--line-number`         | `-n`     | Show line numbers (default)     |
| `--no-line-number`      | `-N`     | Hide line numbers               |
| `--max-count`           | `-m NUM` | Stop after NUM matches per file |

### File Filtering

| Flag             | Short        | Description                                            |
| ---------------- | ------------ | ------------------------------------------------------ |
| `--type`         | `-t TYPE`    | Only search TYPE files                                 |
| `--type-not`     | `-T TYPE`    | Exclude TYPE files                                     |
| `--glob`         | `-g 'GLOB'`  | Include files matching glob                            |
| `--glob`         | `-g '!GLOB'` | Exclude files matching glob                            |
| `--hidden`       | `-.`         | Search hidden files                                    |
| `--no-ignore`    |              | Don't respect .gitignore                               |
| `--unrestricted` | `-u`         | Progressive unrestricted (-uu = hidden, -uuu = binary) |

### Path Control

| Flag              | Description                     |
| ----------------- | ------------------------------- |
| `--max-depth NUM` | Limit directory depth           |
| `--follow`        | Follow symlinks                 |
| `--no-follow`     | Don't follow symlinks (default) |

## Regex Syntax

ripgrep uses Rust regex syntax (similar to PCRE but not identical).

### Character Classes

```
\d    Digit [0-9]
\D    Non-digit
\w    Word char [a-zA-Z0-9_]
\W    Non-word
\s    Whitespace
\S    Non-whitespace
.     Any char (except newline)
```

### Anchors

```
^     Start of line
$     End of line
\b    Word boundary
\B    Non-word boundary
```

### Quantifiers

```
*     Zero or more
+     One or more
?     Zero or one
{n}   Exactly n
{n,}  n or more
{n,m} Between n and m
```

### Groups and Alternation

```
(...)   Capturing group
(?:...) Non-capturing group
|       Alternation (or)
```

### Examples

```bash
# Word boundary matching
rg '\bfunction\b'             # Match whole word "function"

# Start/end of line
rg '^import'                  # Lines starting with import
rg ';\s*$'                    # Lines ending with semicolon

# Character classes
rg '[A-Z][a-z]+Error'         # PascalCase errors
rg '\d{3}-\d{4}'              # Phone pattern

# Alternation
rg 'TODO|FIXME|HACK'          # Any of these markers
```

## File Type Filtering

### Built-in Types

```bash
rg --type-list                # Show all types

# Common types
rg PATTERN -t js              # JavaScript
rg PATTERN -t ts              # TypeScript
rg PATTERN -t py              # Python
rg PATTERN -t rust            # Rust
rg PATTERN -t go              # Go
rg PATTERN -t java            # Java
rg PATTERN -t c               # C
rg PATTERN -t cpp             # C++
rg PATTERN -t ruby            # Ruby
rg PATTERN -t php             # PHP
rg PATTERN -t html            # HTML
rg PATTERN -t css             # CSS
rg PATTERN -t json            # JSON
rg PATTERN -t yaml            # YAML
rg PATTERN -t md              # Markdown
rg PATTERN -t sh              # Shell scripts
rg PATTERN -t make            # Makefiles
rg PATTERN -t sql             # SQL
```

### Combining Types

```bash
rg PATTERN -t js -t ts        # JavaScript AND TypeScript
rg PATTERN -t js -T test      # JavaScript but not test files
```

### Custom Types

```bash
# Add type for single search
rg PATTERN --type-add 'web:*.{html,css,js}' -t web

# Multiple extensions
rg PATTERN --type-add 'config:*.{json,yaml,toml}' -t config
```

## Glob Filtering

```bash
# Include patterns
rg PATTERN -g '*.js'          # Only .js files
rg PATTERN -g 'src/**/*.ts'   # .ts files in src/

# Exclude patterns (prefix with !)
rg PATTERN -g '!*.test.js'    # Exclude test files
rg PATTERN -g '!node_modules' # Exclude directory
rg PATTERN -g '!{dist,build}' # Exclude multiple dirs

# Combine include and exclude
rg PATTERN -g '*.js' -g '!*.min.js'
```

## Replacements

ripgrep can show replacements but **never modifies files**.

```bash
# Simple replacement
rg 'foo' -r 'bar'             # Show foo replaced with bar

# Using capture groups
rg '(\w+)\.log' -r '$1.debug' # log → debug in method calls

# Named groups
rg '(?P<name>\w+)Error' -r '${name}Exception'

# With only-matching
rg 'TODO:.*' -o -r 'DONE'     # Show what would change
```

## Context and Output

```bash
# Context lines
rg PATTERN -C 3               # 3 lines before and after
rg PATTERN -B 2 -A 4          # 2 before, 4 after

# Just filenames
rg PATTERN -l                 # Files with matches
rg PATTERN --files-without-match  # Files without

# Counting
rg PATTERN -c                 # Count per file
rg PATTERN --count-matches    # Total count

# Statistics
rg PATTERN --stats            # Show search statistics
```

## Performance Tips

1. **Use type filters when possible**:

   ```bash
   rg PATTERN -t rust          # Faster than rg PATTERN *.rs
   ```

2. **Exclude heavy directories**:

   ```bash
   rg PATTERN -g '!node_modules' -g '!.git' -g '!target'
   ```

3. **Limit depth for shallow searches**:

   ```bash
   rg PATTERN --max-depth 2
   ```

4. **Use fixed strings when not using regex**:

   ```bash
   rg -F 'exact.match()'       # Faster than escaping regex
   ```

5. **Memory-mapped files can be faster for large files**:
   ```bash
   rg PATTERN --mmap           # Enable mmap (default on most systems)
   ```

## Common Patterns

### Finding TODOs and FIXMEs

```bash
rg 'TODO|FIXME|HACK|XXX' --type-not markdown
rg 'TODO\(.*\):' -o           # Extract TODO with author
```

### Finding Function Definitions

```bash
rg '^(async\s+)?function\s+\w+' -t js
rg '^def\s+\w+' -t py
rg '^fn\s+\w+' -t rust
rg '^func\s+\w+' -t go
```

### Finding Imports

```bash
rg '^import .* from' -t ts
rg '^from .* import' -t py
rg '^use ' -t rust
rg '^import \(' -t go -U      # Multiline imports
```

### Finding Class Definitions

```bash
rg '^class\s+\w+' -t py -t ts
rg '^(export\s+)?class\s+\w+' -t ts
```

### Security Patterns

```bash
# Hardcoded credentials
rg '(password|secret|api_key|token)\s*[:=]' -i

# SQL with string concatenation (potential injection)
rg 'execute\(.*\+' -t py
rg 'query\(.*\$\{' -t ts

# Dangerous functions
rg '\beval\('
rg 'dangerouslySetInnerHTML'
```

### Finding Dead Code Candidates

```bash
# Unused exports (combine with grep)
rg '^export (const|function|class) (\w+)' -o -t ts | sort | uniq -c | sort -n
```
