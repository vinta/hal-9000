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
