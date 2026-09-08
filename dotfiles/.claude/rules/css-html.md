---
paths:
  - "**/*.css"
  - "**/*.{html,htm}"
  - "**/*.jsx"
  - "**/*.tsx"
---

# CSS/HTML

- Main content container defaults to `max-width: 1280px` (`max-w-7xl` in Tailwind). Never go below 1200px unless building a narrow-purpose layout (auth forms, modals).
- Body font size `16px` minimum (`text-base` in Tailwind), `18px` for content-heavy pages. Never use `14px` or `text-sm` for body text.
- Adjacent heading levels (h1→h2→h3) differ by at least `4px` / `0.25rem`. Never render a heading at body text size.
- Reserve accent and link colors for clickable items. Non-interactive elements (inline code, badges, pills, tags) use a neutral or muted color so users don't mistake them for links.
- Keep spacing consistent across sibling components (card lists, grid items): if one card has `padding-bottom: 1rem`, all do.
- Never use `text-transform`. Write the casing directly in the markup.
- Use CSS custom properties (`--var`) for colors and repeated values
- Use `rem` for font sizes and spacing, `px` only for borders and shadows
- Use `gap` in flex/grid layouts, not margin hacks on children
- Use logical properties (`margin-inline`, `padding-block`) over physical ones (`margin-left`, `padding-top`)
- Never use `!important`. Fix specificity instead
