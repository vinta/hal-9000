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
- Adjacent heading levels (h1 > h2 > h3) differ by at least `4px` / `0.25rem`. Never render a heading at body text size.
- Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.
- Reserve accent and link colors for clickable items. Non-interactive elements (inline code, badges, pills, tags) use a neutral or muted color so users don't mistake them for links.
- Balance the space inside a padded container (card, panel, dialog, callout, page section or band) by what the eye sees, not by the padding value: the gap above its first line equals the gap below its last.
  - Text carries leading above its first line and below its last, so trim each edge where text meets it: `text-box: trim-start cap alphabetic` on a first text element that opens the container, `text-box: trim-end cap alphabetic` on a last one that closes it. Trimming lands close, not exact: display-font ascenders rise above `cap` and descenders hang below `alphabetic`, so confirm the gap by glyph ink and adjust the padding.
  - Never apply it to every first or last child: a control row, a strip or an image already sits flush.
  - Add no fallback for browsers without `text-box`; the extra space is acceptable.
  - Judge a gap by glyph ink (the baseline plus the actual characters' ascent and descent), not by line or range boxes. A large or bold line with descenders still reads tight at equal ink gaps, so give the gap under it 2–4px more.
- Keep spacing consistent across sibling components (card lists, grid items): if one card has `padding-bottom: 1rem`, all do.
- Use `rem` for font sizes and spacing.
- Use `gap` in flex/grid layouts, not margin hacks on children.
- Use CSS custom properties (`--var`) for colors and repeated values.
- Never use `text-transform`. Write the casing directly in the markup.

## Visual changes

A visual change is complete when the user approves how it looks, not when the edit lands; this defines "completed" for the commit step in CLAUDE.md. Iterate on injected CSS or uncommitted edits, then commit after approval, one change per commit so each reverts on its own.

Show each visual change before asking, at desktop and phone width, before beside after:

- In the Claude desktop app (`mcp__Claude_Browser__*` tools available), show it live in the browser pane, not as images. Keep a before and an after desktop tab plus one phone tab open for the whole task, so the user never switches the viewport. An emulated viewport can reset between turns, so the phone tab is a page of 375px-wide iframes pointing at the same two builds: the pages the change touches plus one page per template, each before iframe beside its after. When choosing between candidates, open one desktop tab per candidate, labeled on the page with the candidate and its deciding values.
- Elsewhere, render each view (before, after, or candidate) in the real page, compose them into one labeled image side by side, and `open` it. Label each panel with what it shows and its deciding values. When side by side would scale panels below about 0.6, stack them at full width instead, since smaller text stops being readable.
- When the choice is which gaps should match, draw a bar on each gap, colored by the gap it should equal.
- Pair the views with a table of the numbers that decide it (contrast ratio, pixel gaps, rendered width, line count), measured from the rendered page.
- For a palette, render a sheet: one row per element and state (rest, hover), showing the element plus swatches for its text, fill, and border.
- Before each capture, set `transition: none; animation: none` on `*, ::before, ::after`, set `scroll-behavior: auto`, force scroll-in reveal states visible, and wait for layout. `*` alone misses pseudo-elements, a mid-fade capture shows the old color, and a smooth scroll leaves the page short of where you scrolled it.

A one-property tweak on one element skips the before/after and tables: make it, reload the open tabs, and say what changed.
