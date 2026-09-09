---
paths:
  - "**/*.{ts,tsx}"
  - "**/*.{js,jsx}"
  - "**/package.json"
---

# TypeScript / JavaScript

- Pin exact dependency versions in `package.json` — no `^` or `~` prefixes
- Pin `@types/node` to the latest release of the oldest Node.js major in `engines.node`, so the compiler flags APIs that major lacks
- Use the `node:` prefix for Node.js built-in modules (`node:fs`, `node:path`)
- Write proper types/interfaces instead of `any` or casts like `as any` / `as unknown`
  - When a value is genuinely untypable, use `unknown` and narrow it explicitly. `any` is the last resort when no typed alternative exists
- Prefer `interface` over `type` for object shapes (extendable, better error messages)
- Avoid enums. Use union types (`type Status = 'active' | 'inactive'`) or `as const` objects
- Mark properties and parameters `readonly` when they should not be mutated
- Do not add explicit return types. Let TypeScript infer them

## Naming

Check a proposed name against every bullet here before presenting it. Existing code is precedent only where it already follows these bullets.

- **One value has one name everywhere it appears**. When two records carry the same value under two names, rename to the one that already matches the domain vocabulary
- An identifier mirrors its domain type name (`lateFixes: LateFix[]`, `ambiguousShape: AmbiguousShape`), never a shortened synonym. This covers parameters, loop variables, and destructured locals. A generic platform type (`Node`, `string`) carries nothing, so that identifier names its role instead: `contextNode`, not `node`
- An action is the bare verb, the gerund is the noun or modifier: `spaceText()`, `spacingMode`. A predicate about whether to act takes the verb (`shouldAutoSpace`); a predicate about the concept's state keeps the noun (`hasProperSpacing`). Feature names stay as their ADR spells them (`applyAiSpacing`)
- Name a field or local by its state (`unspaced`, `settled`), never by relative position (`before`, `after`) or by mechanism (`pending`, `unflushed`). One thing at two moments is two types, never one type with optional later-moment fields
- Prefer the concrete compound that names the visible thing and matches existing code over an abstract, mechanism, or transport noun: `AmbiguousShape`, not `Ambiguity`; `Candidate`, not `ClassifyRequest`. Only the envelope carries a transport noun (`Message`, `Request`, `Response`)
- A result type is the noun of the verb that produces it: `decideBoundarySpacing()` returns `BoundarySpacingDecision`, not `BoundarySpacingVerdict`
- A callback is named by what changed, never by the container the event came in: `onTextNodesSettled(settledTextNodes)`, not `onBatchSettled`
- A wrapped function keeps the verb first and the wrapper as a suffix: `spaceTitleDebounced`, not `debouncedSpaceTitle`
- A per-item helper beside its batch function is `verbOneNoun` (`classifyCandidates` / `classifyOneCandidate`, `registerContentScripts` / `registerOneContentScript`): the bare singular differs by one trailing `s` and reads alike in a diff. Keep the batch name as is when a message or API shares it
