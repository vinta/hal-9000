---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "docs/**/*.md"
---

# TypeScript / JavaScript

- Before adding a dependency, search npm or the web for the latest version
- Pin exact dependency versions in `package.json` — no `^` or `~` prefixes
- Use the TypeScript LSP tool for type-aware code navigation when grep's text matching would be ambiguous. LSP resolves symbol relationships through the type system, so `findReferences` on a function returns its actual call sites, not every file containing the same string. Reach for LSP when:
  - Tracing all usages before removing or renaming a symbol (`findReferences`)
  - Understanding a function's callers or callees (`incomingCalls` / `outgoingCalls`)
  - Navigating to a symbol's definition (`goToDefinition`)
  - Checking type information at a position (`hover`)
  - Surveying a file's or workspace's structure (`documentSymbol` / `workspaceSymbol`)
  Use grep for text pattern matching, non-TypeScript files, or when the symbol name is unique enough that text matching suffices.
- Use `node:` prefix for Node.js built-in modules (e.g., `node:fs`, `node:path`)
- Use `const` by default, `let` when reassignment is needed, never `var`
- Prefer `async`/`await` over `.then()` chains
- Use template literals over string concatenation
- Use optional chaining (`?.`) and nullish coalescing (`??`) over manual checks
- Use strict equality (`===` / `!==`), never loose equality
- Never use `as any` or `unknown`. Always write proper types/interfaces. Only use `any` or `unknown` as a last resort when no typed alternative exists
- Prefer `interface` over `type` for object shapes (extendable, better error messages)
- Avoid enums. Use union types (`type Status = 'active' | 'inactive'`) or `as const` objects
- Don't prefix interfaces with `I` or type aliases with `T` (e.g., `User` not `IUser`)
- Mark properties and parameters `readonly` when they should not be mutated
- Do not add explicit return types. Let TypeScript infer them

<verify_with_browser if="you completed a frontend change (UI component, page, client-side behavior)" only_if="agent-browser skill is installed in project or user scope">
After implementing frontend changes, use the `agent-browser` skill to visually verify the result in a real browser. Check layout, responsiveness, and interactive behavior rather than assuming correctness from code alone.
</verify_with_browser>
