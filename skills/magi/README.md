# The MAGI System

![The MAGI System](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/magi.webp "The MAGI System")

## Background

In _Neon Genesis Evangelion_, the MAGI System is a trio of supercomputers that governs NERV headquarters and the city of Tokyo-3. Built by Dr. Naoko Akagi, each unit contains a different aspect of her personality imprinted onto its organic components:

- **MELCHIOR-1** -- the Scientist. Naoko as a researcher: analytical, evidence-driven, concerned with what is technically correct.
- **BALTHASAR-2** -- the Mother. Naoko as a parent: protective, risk-aware, weighing the cost of action against the cost of inaction.
- **CASPER-3** -- the Woman. Naoko as a person: intuitive, pragmatic, drawn to the elegant solution over the merely safe one.

The three MAGI reach decisions through a voting protocol. They can agree unanimously, reach a majority, or deadlock -- and a deadlock is itself a meaningful outcome, surfacing genuine tension rather than papering over it. Critical calls like activating the city's self-destruct sequence require all three to concur. The system's strength is not that it always agrees with itself, but that it forces three fundamentally different value systems to confront the same problem.

Named after the Biblical Magi -- the three wise men who followed the star to Bethlehem -- the MAGI embody the idea that wisdom emerges from the convergence of distinct perspectives, not from a single authoritative voice.

## From Anime to Agentic Skill

The [magi](SKILL.md) skill translates this into a three-agent deliberation system built on Claude Code's **Agent Team**. When you face a decision with real trade-offs -- architecture choices, debugging hypotheses, design directions -- it spawns three persistent agents, each locked into one of the MAGI's cognitive modes:

| Agent         | Mode       | Asks                                         |
| ------------- | ---------- | -------------------------------------------- |
| **Scientist** | Analytical | What does the evidence say?                  |
| **Mother**    | Protective | What could go wrong? Do we even need to act? |
| **Woman**     | Creative   | What's the elegant path?                     |

The agents work in two phases. First, they analyze independently with no cross-talk, each arguing their perspective fully without hedging. Then they read each other's positions and cross-critique -- challenging specific claims, identifying blind spots, and stating whether they revise their stance. The team lead synthesizes the result into either a unified recommendation or an articulated disagreement with clear trade-offs.
