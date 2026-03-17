---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---

# TypeScript / JavaScript

- Before adding a dependency, search npm or the web for the latest version
- Pin exact dependency versions in `package.json` — no `^` or `~` prefixes
- Use `node:` prefix for Node.js built-in modules (e.g., `node:fs`, `node:path`)
- Prefer `async`/`await` over `.then()` chains
- Use template literals over string concatenation
- Use optional chaining (`?.`) and nullish coalescing (`??`) over manual checks
- Use strict equality (`===` / `!==`), never loose equality
