---
type: regex
target: { source: file, path: skills/release-notes/SKILL.md }
pattern: 'Each entry describes one change: it names what the user can now do or no longer needs to do, it stays silent on how the code achieved it, and it leaves file names and function names out\.'
match: not_contains
---
