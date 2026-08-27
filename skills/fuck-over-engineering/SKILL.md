---
name: fuck-over-engineering
description: Use when the user asks what could be deleted or reduced to simplify a codebase, says "over-engineered", "find bloat", "YAGNI pass", or wants a repo-, folder-, or file-wide audit for over-engineering — hunts dead code, reinvented stdlib, needless dependencies, and single-implementation abstractions, reports ranked cuts, applies only the picks. Not a diff review and not a bug hunt
argument-hint: "[path, module, or area — omit for whole repo]"
user-invocable: true
---

# Fuck Over-Engineering

Audit the scope for over-engineering and report what to cut, ranked biggest cut first. The best outcome is a shorter codebase with the same behavior. The argument is the scope; without one, the whole tree. Read what the scope holds before judging it, and fan out subagents when it will not fit in context.

## Tags

- `delete:` dead code, unused flexibility, speculative feature. Nothing replaces it.
- `reuse:` bespoke code that a helper already in this codebase, or an installed dependency, already provides. Name the helper or function.
- `stdlib:` hand-rolled thing the language's standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Hunt

Dependencies the stdlib or platform already covers, single-implementation interfaces, factories with one product, wrappers that only delegate, files exporting one thing, dead flags and config, hand-rolled stdlib, near-duplicates of an existing helper, special-case branches bolted onto shared paths, feature logic living in shared modules.

## Evidence

Every finding cites the evidence that makes it a cut: caller count, implementation count, or the stdlib or platform feature and the version that ships it. Count callers through dynamic dispatch, entry points, hooks, and tests, not grep alone. A published package's public export stays at zero in-repo callers. Verify `stdlib:` and `native:` claims against current docs (the find-docs skill when present) before asserting them.

A finding removes lines or concepts; moving them between files is a refactor, not a cut. Fewer, bigger cuts beat a long list: a `shrink:` that saves two lines earns a slot only when it also removes a concept.

## Output

One line per finding, numbered, ranked biggest cut first:

`N. <tag> <what to cut>. <replacement>. <evidence>. [path:line]`

`delete:` omits the replacement sentence. End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

- `1. yagni: AbstractRepository with one implementation. Inline it. 1 subclass, 3 call sites typed to the base. [repo.py:88]`
- `2. reuse: hand-rolled slugify. python-slugify is installed, slugify(). 1 caller. [utils/text.py:10-31]`
- `3. delete: retry wrapper around an idempotent local call. 0 callers outside its own test. [src/net.py:52-71]`

Then offer the findings with AskUserQuestion, multiSelect, in ranked batches of four per question, and apply the picks.

## Boundaries

Over-engineering and complexity only: correctness bugs, security holes, and performance belong to a normal review pass. Trust-boundary validation, data-loss handling, security, and accessibility are never cuts. A single smoke test or assert-based self-check is the minimum, not bloat. Tests enter the report only as collateral of a deleted target.
