---
paths:
  - "**/*.css"
  - "**/*.{html,htm}"
  - "**/*.jsx"
  - "**/*.tsx"
---

# CSS/HTML

- Main content container defaults to `max-width: 1280px`. Never go below 1200px unless building a narrow-purpose layout (auth forms, modals, settings pages, browser extension pages).
- Body font size `16px` minimum, `18px` for content-heavy pages. Never use `14px` or `text-sm` for body text.
- Adjacent heading levels (h1→h2→h3) differ by at least `4px` / `0.25rem`. Never render a heading at body text size.
- Reserve accent and link colors for clickable items. Non-interactive elements (inline code, badges, pills, tags) use a neutral or muted color so users don't mistake them for links.
- Keep spacing consistent across sibling components (card lists, grid items): if one card has `padding-bottom: 1rem`, all do.
- Never use `text-transform`. Write the casing directly in the markup.
- Use CSS custom properties (`--var`) for colors and repeated values
- Use `rem` for font sizes and spacing, `px` only for borders and shadows
- Use `gap` in flex/grid layouts, not margin hacks on children
- Use logical properties (`margin-inline`, `padding-block`) over physical ones (`margin-left`, `padding-top`)
- Never use `!important`. Fix specificity instead. Use it only when no better choice exists

## Visual changes

A visual change is complete when the user approves how it looks, not when the edit lands; this defines "completed" for the commit step in CLAUDE.md. Iterate on injected CSS or uncommitted edits, then commit after approval, one change per commit so each reverts on its own.

When a change spans several components, states, or colors, or you are choosing between candidates, show it before asking:

- Render each candidate in the real page, compose them into one labeled image side by side, and `open` it. Label each panel with the candidate and its deciding values.
- Pair the image with a table of the numbers that decide it (contrast ratio, pixel gaps, rendered width, line count), measured from the rendered page.
- For a palette, render a sheet: one row per element and state (rest, hover), showing the element plus swatches for its text, fill, and border.
- Before each capture, set `transition: none; animation: none` on `*, ::before, ::after` and wait for layout. `*` alone misses pseudo-elements, and a mid-fade capture shows the old color.

A one-property tweak on one element skips the images and tables: make it and say what changed.
