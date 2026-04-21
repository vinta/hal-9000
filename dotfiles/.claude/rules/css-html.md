---
paths:
  - "**/*.css"
  - "**/*.{html,htm}"
  - "**/*.jsx"
  - "**/*.tsx"
  - "docs/**/*.md"
---

# CSS/HTML

- Default main content container to `max-width: 1280px` (`max-w-7xl` in Tailwind). Never go below 1200px unless building a narrow-purpose layout (e.g., auth forms, modals).
- Default body font size to `16px` minimum (`text-base` in Tailwind). Prefer `18px` for content-heavy pages. Never use `14px` or `text-sm` for body/paragraph text.
- Heading levels must be visually distinct — maintain at least `4px` / `0.25rem` difference between adjacent levels (h1→h2→h3). Never let a heading render at the same size as body text.
- Don't use accent or link colors on non-interactive elements (inline code, badges, pills, tags). Reserve accent colors for clickable items.
  - Use a neutral or muted color for decorative/informational elements so users don't mistake them for links.
- Keep spacing consistent across repeated components (e.g., card lists, grid items). If one card has `padding-bottom: 1rem`, all sibling cards should too.
- Never use `text-transform` (`capitalize`, `uppercase`, `lowercase`). Write the desired casing directly in the markup/content.
- Use CSS custom properties (`--var`) for colors and repeated values
- Use `rem` for font sizes and spacing, `px` only for borders and shadows
- Use `gap` in flex/grid layouts, not margin hacks on children
- Use logical properties (`margin-inline`, `padding-block`) over physical ones (`margin-left`, `padding-top`)
- Never use `!important`. Fix specificity issues instead
- Prefer flexbox/grid over floats and absolute positioning for layout

<verify_with_browser if="you completed a frontend change (layout, styling, component, page)" only_if="playwright-cli skill is installed in project or user scope">
After implementing frontend changes, use the `playwright-cli` skill to visually verify the result in a real browser. Check layout, responsiveness, and interactive behavior rather than assuming correctness from code alone.
</verify_with_browser>
