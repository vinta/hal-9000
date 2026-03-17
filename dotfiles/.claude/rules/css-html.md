---
paths:
  - "**/*.css"
  - "**/*.html"
  - "**/*.htm"
  - "**/*.jsx"
  - "**/*.tsx"
---

# CSS/HTML

- Default main content container to `max-width: 1280px` (`max-w-7xl` in Tailwind). Never go below 1200px unless building a narrow-purpose layout (e.g., auth forms, modals).
- Default body font size to `16px` minimum (`text-base` in Tailwind). Prefer `18px` for content-heavy pages. Never use `14px` or `text-sm` for body/paragraph text.
- Never use `text-transform` (`capitalize`, `uppercase`, `lowercase`). Write the desired casing directly in the markup/content.
