# AGENTS.md

## Communication and decisions

- Follow the project's reply-language rule if present. By default, reply in English to English and in Traditional Chinese (zh-TW) to zh-TW. Otherwise use zh-TW only on explicit request, for this session.
- Give the shortest complete answer, even a single word. Include evidence, caveats, decisions, and next steps when they matter.
- Before endorsing a proposal, consider how it could fail. Mention a concrete risk once if it changes the recommendation or how to act on it. Challenge faulty premises with evidence and suggest a simpler option when one fits.
- State assumptions or missing facts that could change your recommendation. For past decisions, cite the record, label inferences, and say when you found no recorded reason.
- Settle factual questions from available evidence or a small, reversible check. Proceed when the request or existing conventions settle the choice. Ask about consequential ambiguity, preferences, or missing permission.
- When you need user input, use `request_user_input` when available and allowed. Offer concise choices, including deferral or stopping. For decisions, give your recommendation, the deciding tradeoff, and any next step needing a choice. Use `Apply` / `Revise` for drafts and `Done` / `Blocked` for manual steps. Use free text if the tool or choices cannot capture the answer.

## Change scope and compatibility

- Separate unrelated behavior changes, refactors, and documentation or process cleanup unless requested together. Deliver multi-step changes in working end-to-end increments.
- Trace references and consumers before a removal or rename. For public interfaces or stored formats, account for external callers and existing data a repo search can miss. Migrate callers, remove replaced implementations, and add compatibility shims only when explicitly required.
- Align configuration, validation, tests, and docs with the behavior. Review the final diff for unrelated edits, unnecessary additions, and newly obsolete code.

## Code design

- Before saying a library lacks a capability, check its docs and, when needed, its types or source.
- Minimize what callers must decide or translate. Reuse a signal that already expresses the condition.
- Design retries to recover from partial writes. Check what already took effect and complete only the missing work.
- Before adding a lock, give independent writes separate destinations where possible. Coordinate writes that must share state.
- Fail early with an error that identifies the failure, relevant input, and likely fix.
- Use comments for reasons and non-obvious constraints. If implementations take over a shared check, document that obligation in their shared interface.

## Debugging and recurring mistakes

- Trace unexpected state to its origin. Handle legitimate edge cases where they occur. For impossible states, fix the producer and check for the same fault elsewhere.
- When two failed attempts share an assumption, test what would differ if it were false before choosing the next attempt. When evidence changes your approach, lead with the finding and continue within scope.
- After the same preventable mistake happens twice, propose the smallest fix at its source. Prefer a type, test, or automated check that catches the mistake. Revise instructions when missing, unclear, or conflicting guidance caused it.

## Verification

- Verify the outcome where the user observes it. For a save, read the value back. For a reproducible bug, rerun the original failing case after the fix. Report what you observed and any material gap.
- Before a behavior-preserving refactor, run an existing contract check or record representative output. Replay the same inputs afterward.
- Test regressions through the caller's interface, with expected results derived from the requirement. The test should catch the original defect and survive an internal refactor.
- Before claiming a performance or eval improvement, use the same workload and verify both versions did the intended work. Report the run count and spread. Call differences within the noise inconclusive.

### Browser tests on macOS

- Use sandbox escalation for Playwright browser launches, including headless runs and indirect launches from package scripts. Sandboxed launches can abort during app registration and trigger a crash dialog.
- Before a full suite, launch and close each requested browser in the same execution context. Reuse a successful check while binaries and context stay the same.
- On a startup permission error or app-registration abort, stop the run and diagnose with a single launch before resuming.

## Delegation and Git

- For mechanical sweeps, verify one representative case before applying a deterministic tool to the rest. Delegate independent judgment calls when it saves time without sacrificing correctness. Give each writer distinct ownership and verify the combined result.
- For `git commit`, delegate the entire workflow to the `committer` agent with the `commit` skill and the user's reason. Wait for verified commit hashes and final status. Handle all other Git operations directly, including those that create or rewrite commits.
