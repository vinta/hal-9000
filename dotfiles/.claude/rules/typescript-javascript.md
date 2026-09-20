---
paths:
  - "**/*.{ts,tsx}"
  - "**/*.{js,jsx}"
  - "**/package.json"
---

# TypeScript/JavaScript

- Pin exact dependency versions in `package.json` — no `^` or `~` prefixes
- Pin `@types/node` to the latest release of the oldest Node.js major in `engines.node`, so the compiler flags APIs that major lacks
- Use the `node:` prefix for Node.js built-in modules (`node:fs`, `node:path`)
- Prefer `interface` over `type` for object shapes (extendable, better error messages)
- Avoid enums. Use union types (`type Status = 'active' | 'inactive'`) or `as const` objects
- Write a proper type instead of `any` or a cast (`as any`, `as unknown`). For a genuinely untypable value, use `unknown` and narrow it; `any` is the last resort
- Do not add explicit return types. Let TypeScript infer them, except where the annotation checks returned literals against a declared union or contract
- Mark a property or parameter `readonly` only when nothing about it changes. One that is never reassigned but whose contents are mutated in place (a queue, a cache, a settings object) stays unmarked

## Naming

Every name you pick, in code or in a proposal, passes every bullet here before it lands. An existing name that fails a bullet is not precedent to copy, and not a rename in this change; report it as a follow-up.

- **One value has one name everywhere it appears**. When two records carry the same value under two names, rename to the one that already matches the domain vocabulary
- An identifier mirrors its domain type name (`lateFixes: LateFix[]`, `ambiguousShape: AmbiguousShape`), never a shortened synonym. This covers parameters, loop variables, and destructured locals
- An action is the bare verb, the gerund is the noun or modifier: `spaceText()`, `spacingMode`. A predicate about whether to act takes the verb (`shouldAutoSpace`); a predicate about the concept's state keeps the noun (`hasProperSpacing`). Feature names stay as their ADR spells them (`applyAiSpacing`)
- Name a field or local by its state (`unspaced`, `settled`), never by relative position (`before`, `after`) or by mechanism (`pending`, `unflushed`). One thing at two moments is two types, never one type with optional later-moment fields
- Prefer the concrete compound that names the visible thing and matches existing code over an abstract or mechanism noun: `AmbiguousShape`, not `Ambiguity`
- A transport noun (`Message`, `Request`, `Response`) belongs to the envelope only; the payload is named by what it is: `Candidate`, not `ClassifyRequest`
- A result type is the noun of the verb that produces it: `decideBoundarySpacing()` returns `BoundarySpacingDecision`, not `BoundarySpacingVerdict`
- A callback is named by what changed, never by the container the event came in: `onTextNodesSettled(settledTextNodes)`, not `onBatchSettled`
- A wrapped function keeps the verb first and the wrapper as a suffix: `spaceTitleDebounced`, not `debouncedSpaceTitle`
- A per-item helper beside its batch function is `verbOneNoun` (`classifyCandidates` / `classifyOneCandidate`, `registerContentScripts` / `registerOneContentScript`): the bare singular differs by one trailing `s` and reads alike in a diff. Keep the batch name as is when a message or API shares it
