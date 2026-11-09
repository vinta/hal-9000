---
paths:
  - "**/*.svg"
  - "**/*.{html,htm}"
---

# Diagrams

For hand-drawn SVG diagrams: architecture maps, flowcharts, boxes and arrows.

## Content

- Take every node and edge from the code or config and label them with real identifiers. Show what exists now; leave out planned or environment-specific items unless asked.
- When redrawing an existing diagram, keep its node names and their relative positions, so the two can be compared side by side.
- Draw one node per real entity: three topics are three boxes, not one name with slashes. When every member of a container shares a prefix, make the prefix the container's title and start each name with `.`.
- Keep labels to the name, role and the one fact the reader needs; move sizing, container lists and similar detail to notes under the figure.
- Use one term per concept across boxes ("producer" for every Kafka writer, not "publisher" for one).
- Give each edge type (gRPC, Kafka topic, HTTP, database access) its own line style, and name each style in a legend.

## Layout

- Lay flows out left to right: producers and sources on the left, consumers and sinks on the right.
- Put a diagram too large for one screen on a pan-and-zoom canvas that opens on its most useful region, so the reader does not have to scroll or zoom first.
- Draw containers and boxes before lines and labels: a box's fill hides every line drawn under it.
- Keep at least 20 units between neighboring boxes, every arrowhead at least 16 units from any border it crosses, and every line at least 10 units from a box edge it runs alongside; inset nodes in their container to make room.
- Keep each label inside the box it names, clear of other text and of every line; put an edge label in open space beside its line, never across a box edge.
- Gather a fan-out or fan-in on one bar with a dot at the junction, and split the path there, so it reads as one source splitting rather than lines crossing.

## Verify

- After each edit, run a scripted geometry audit over every diagram on the page (text overlap, text across a box edge, lines through text, arrowheads near a crossed border, lines hugging an edge) and fix every hit before reporting: a screenshot misses near-misses, and a fix found in one diagram usually applies to the others.
- Reload the page before checking it: a hash-only navigation does not refetch, and a static server without `Cache-Control: no-store` can serve the old file.
