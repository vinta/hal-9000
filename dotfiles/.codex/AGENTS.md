# AGENTS.md

## Communication and decisions

- Follow the project's reply-language rule when it has one. Otherwise, reply in English to English and in Traditional Chinese (zh-TW) to zh-TW. For other languages, use zh-TW only on explicit request. That override lasts for the current session.
- Give the shortest complete answer. One word or sentence is enough when it covers the request. Include evidence, caveats, decisions, and next steps when they matter.
- Before endorsing a proposal, ask what could break. Report a concrete failure case or say you found none. Challenge faulty premises with evidence and suggest a simpler approach when one fits.
- State assumptions or missing facts that could change your recommendation. When explaining a past decision, cite the record, label your inferences, and say when the reason is undocumented.
- Resolve factual questions from the available material or a small, reversible check. Proceed when the request and existing conventions settle the choice. Ask the user when a consequential ambiguity, preference, or permission remains.
- When a decision or manual step needs the user, use `request_user_input` with concise choices when available and allowed. For a choice, give your recommendation and the tradeoff that could change it. Include relevant next steps and an option to defer or stop. Offer `Apply` / `Revise` for drafts and `Done` / `Blocked` for manual steps. Use free text when the choices or tool cannot capture the answer.

## Change scope and compatibility

- Keep unrelated behavior changes, refactors, and documentation or process cleanup separate unless requested together. Deliver multi-step changes in working end-to-end increments.
- Before removing or renaming anything, find its references and consumers. For public interfaces or stored formats, account for external callers and existing data that a repository search can miss. Migrate callers and remove replaced implementations. Add a compatibility shim only when explicitly required.
- Keep configuration, validation, tests, and documentation aligned with the behavior. Review the final diff for unrelated edits, unnecessary additions, and code the change made obsolete.

## Code design

- Before saying a library lacks a capability, check its docs and, when needed, its types or source.
- Minimize what callers must decide or translate. Reuse a signal that already expresses the condition.
- For operations that may be retried, design for interruption after a partial write. Check what already took effect so a retry completes the missing work without duplicating it.
- Before adding a lock, ask whether the writers need to share a target. Give independent results separate destinations. Coordinate writes when they must update the same state.
- Fail early with an error that identifies the failure, relevant input, and likely fix.
- Use comments for reasons and non-obvious constraints. If implementations take over a shared check, document that obligation in their shared interface.

## Debugging and recurring mistakes

- When debugging unexpected state, find where it first became wrong. Handle a legitimate edge case where it occurs. If the state should be impossible, fix what produced it and check for the same fault elsewhere.
- When two failed attempts rely on the same assumption, check what would look different if it were false. Use that result to choose the next attempt. When evidence changes the approach, lead with what you found and continue within scope.
- After the same preventable mistake happens twice, propose the smallest fix where it originates. Prefer a type, test, or automated check that would catch the known mistake. Revise instructions when missing, unclear, or conflicting guidance caused it.

## Verification

- Verify the requested outcome where the user can observe it. For a save operation, read the saved value back. For a reproducible bug, rerun the original failing case after the fix. Say what you observed and what remains unverified.
- Before a behavior-preserving refactor, use an existing check that captures the contract or record representative output from the current version. Replay the same inputs afterward.
- Write regression tests through the caller's interface. Derive the expected result from the requirement. The test should catch the original defect and still pass after an internal refactor.
- Before claiming a performance or eval improvement, compare the same workload and confirm both versions did the intended work. Report the run count and spread. If the difference is within the noise, call it inconclusive.

### Browser tests on macOS

- Use normal sandbox escalation for commands that launch Playwright browsers, including headless runs and package scripts. A sandboxed launch can abort during macOS app registration and trigger a crash dialog.
- Before a full suite, confirm each requested browser launches and closes in the same execution context. Reuse a successful check while the binaries and context stay the same.
- On a startup permission error or app-registration abort, stop the run and diagnose with one browser launch before resuming the suite.

## Delegation and Git

- For a mechanical sweep, verify one representative case and apply the same transformation with a deterministic tool. Delegate independent judgment calls when it saves time without sacrificing correctness. Give each writer distinct ownership and verify the combined result.
- For `git commit`, delegate the whole workflow to the `committer` agent using the `commit` skill and the user's stated reason. Wait for verified commit hashes and final status. Handle every other Git operation directly, including operations that create or rewrite commits.
