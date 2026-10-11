---
type: regex
target: { source: file, path: skills/release-notes/SKILL.md }
pattern: 'The heading takes its version from the argument when one is given; when none is given, it takes the version from the VERSION file at the repo root, and that file''s value is what the heading shows\.'
match: not_contains
---
