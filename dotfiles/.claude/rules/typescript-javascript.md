---
paths:
  - "**/*.{ts,tsx}"
  - "**/*.{js,jsx}"
  - "**/package.json"
---

# TypeScript / JavaScript

- Pin exact dependency versions in `package.json` — no `^` or `~` prefixes
- Use `node:` prefix for Node.js built-in modules (e.g., `node:fs`, `node:path`)
- Write proper types/interfaces instead of `any` or casts like `as any` / `as unknown`. When a value is genuinely untypable, use `unknown` and narrow it explicitly. `any` is the last resort when no typed alternative exists
- Prefer `interface` over `type` for object shapes (extendable, better error messages)
- Avoid enums. Use union types (`type Status = 'active' | 'inactive'`) or `as const` objects
- Mark properties and parameters `readonly` when they should not be mutated
- Do not add explicit return types. Let TypeScript infer them
- Use the `typescript` LSP tool for type-aware code navigation when grep's text matching would be ambiguous
