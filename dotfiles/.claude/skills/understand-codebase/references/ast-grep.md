# ast-grep Reference

ast-grep (`sg`) performs syntax-aware structural search using Abstract Syntax Trees. It understands code semantics, not just text patterns.

## CLI Basics

```bash
sg -p 'PATTERN' [PATH]           # Search with pattern
sg -p 'PATTERN' -l LANG          # Specify language
sg -p 'PATTERN' -r 'REPLACEMENT' # Search and replace (dry-run)
sg -p 'PATTERN' -r 'REPL' -U     # Apply replacement
sg --debug-query                 # Debug pattern parsing
```

### Language Identifiers

`js`, `ts`, `tsx`, `jsx`, `py`, `python`, `rs`, `rust`, `go`, `java`, `c`, `cpp`, `rb`, `ruby`, `php`, `swift`, `kotlin`, `scala`, `lua`

## Metavariables

Metavariables are placeholders that capture matching code.

| Syntax   | Captures                        | Example                                     |
| -------- | ------------------------------- | ------------------------------------------- |
| `$VAR`   | Single named node               | `console.log($MSG)` → captures the argument |
| `$$VAR`  | Single unnamed node (operators) | `$A $$OP $B` → captures `+`, `-`, etc.      |
| `$$$VAR` | Zero or more nodes              | `function($$$ARGS)` → any number of args    |
| `$_VAR`  | Non-capturing (performance)     | `$_FUNC($_)` → matches but doesn't capture  |

### Metavariable Rules

- Must be UPPERCASE: `$META`, `$META_VAR` (not `$meta`)
- Underscore prefix = non-capturing: `$_IGNORED`
- Same name = same content: `$A == $A` matches `x == x` not `x == y`
- Must be sole content of AST node: `obj.$PROP` works, `obj.on$EVENT` doesn't

## Pattern Examples by Language

### JavaScript/TypeScript

```bash
# Function definitions
sg -p 'function $NAME($$$ARGS) { $$$ }' -l js
sg -p 'const $NAME = ($$$) => $BODY' -l js
sg -p 'const $NAME = async ($$$) => $BODY' -l js

# Class patterns
sg -p 'class $NAME extends $PARENT { $$$ }' -l ts
sg -p 'class $NAME implements $IFACE { $$$ }' -l ts

# React patterns
sg -p 'useState($INITIAL)' -l tsx
sg -p 'useEffect(() => { $$$ }, [$$$DEPS])' -l tsx
sg -p '<$COMP $$$PROPS />' -l tsx
sg -p '<$COMP $$$PROPS>$$$CHILDREN</$COMP>' -l tsx

# Async patterns
sg -p 'await $PROMISE' -l js
sg -p 'async function $NAME($$$) { $$$ }' -l js
sg -p '$PROMISE.then($CALLBACK)' -l js

# Error handling
sg -p 'try { $$$ } catch ($E) { $$$ }' -l js
sg -p 'try { $$$ } catch ($E) { $$$ } finally { $$$ }' -l js
```

### Python

```bash
# Function definitions
sg -p 'def $NAME($$$ARGS): $$$BODY' -l py
sg -p 'async def $NAME($$$): $$$' -l py

# Class patterns
sg -p 'class $NAME($$$BASES): $$$' -l py
sg -p '@$DECORATOR
class $NAME: $$$' -l py

# Decorators
sg -p '@$DECORATOR
def $NAME($$$): $$$' -l py

# Context managers
sg -p 'with $EXPR as $VAR: $$$' -l py

# Exception handling
sg -p 'try: $$$
except $E: $$$' -l py
```

### Go

```bash
# Function definitions
sg -p 'func $NAME($$$ARGS) $RET { $$$ }' -l go
sg -p 'func ($RECV) $NAME($$$) $RET { $$$ }' -l go  # methods

# Error handling
sg -p 'if err != nil { $$$ }' -l go

# Goroutines
sg -p 'go $FUNC($$$)' -l go

# Defer
sg -p 'defer $EXPR' -l go
```

### Rust

```bash
# Function definitions
sg -p 'fn $NAME($$$) -> $RET { $$$ }' -l rs
sg -p 'async fn $NAME($$$) -> $RET { $$$ }' -l rs
sg -p 'pub fn $NAME($$$) { $$$ }' -l rs

# Impl blocks
sg -p 'impl $TRAIT for $TYPE { $$$ }' -l rs

# Match expressions
sg -p 'match $EXPR { $$$ }' -l rs

# Result/Option handling
sg -p '$EXPR.unwrap()' -l rs
sg -p '$EXPR?' -l rs
```

## Relational Rules (CLI)

Use `--has` and `--inside` for contextual matching:

```bash
# Find async functions that use await
sg -p 'async function $NAME($$$) { $$$ }' --has 'await $EXPR' -l js

# Find functions inside classes
sg -p 'function $NAME($$$) { $$$ }' --inside 'class $C { $$$ }' -l js

# Negate with --not
sg -p 'async function $NAME($$$) { $$$ }' --not-has 'try' -l js
```

## YAML Rule Files

For complex patterns, use YAML rule files:

```yaml
# rule.yaml
id: find-console-logs
language: javascript
rule:
  pattern: console.$METHOD($$$ARGS)
```

```bash
sg scan -r rule.yaml
```

### Composite Rules

```yaml
# Match any console method
rule:
  any:
    - pattern: console.log($$$)
    - pattern: console.warn($$$)
    - pattern: console.error($$$)
```

```yaml
# Match all conditions
rule:
  all:
    - kind: function_declaration
    - has:
        pattern: await $EXPR
        stopBy: end
    - not:
        has:
          pattern: try { $$$ } catch ($E) { $$$ }
          stopBy: end
```

### Relational Rules in YAML

```yaml
# Find console.log inside async functions
rule:
  pattern: console.log($$$)
  inside:
    pattern: async function $NAME($$$) { $$$ }
    stopBy: end # Search to end of scope
```

```yaml
# Find functions that have a specific pattern
rule:
  kind: function_declaration
  has:
    pattern: return null
    stopBy: end
```

### stopBy Options

- `neighbor` (default): Stop at immediate surrounding node
- `end`: Search to end of direction (most common for deep searches)
- Rule object: Stop when rule matches

## Debugging Patterns

```bash
# Show AST structure
sg --debug-query -p 'your pattern' file.js

# Dump syntax tree
sg --dump-syntax-tree file.js | head -50
```

## Common Issues

1. **Pattern doesn't match**: Check AST structure with `--debug-query`
2. **Wrong node kind**: Use language's tree-sitter grammar names
3. **Metavariable not captured**: Ensure it's the sole content of its node
4. **Relational rule too narrow**: Add `stopBy: end` for deep searches
