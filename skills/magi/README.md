# The MAGI System

![The MAGI System](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/magi.webp "The MAGI System")

## Background

In _Neon Genesis Evangelion_, the MAGI are a three-part bio-computer system used by NERV to run operations and adjudicate high-stakes decisions via voting rather than a single monolithic machine.

The three units are named after the Biblical Magi (Melchior, Balthasar, Casper). Dr. Naoko Akagi created the system by imprinting three aspects of herself:

- **MELCHIOR-1 (Scientist):** evidence, logic, technical correctness
- **BALTHASAR-2 (Mother):** protection, stability, "what could go wrong"
- **CASPER-3 (Woman):** desire/attachment, pragmatism, and the will to choose a direction

In the show, CASPER is not "neutral compute": it can become the deciding factor and even veto a destructive command in ways characters interpret as Naoko's "woman" aspect choosing based on attachment.

## From Anime to Agentic Skill

The [magi](SKILL.md) skill translates this into a three-agent deliberation workflow built on Claude Code's **Agent Team**:

1. Analysis (includes discovery, option evaluation, and framing; no cross-talk)
2. Direct peer-to-peer debate
3. A formal vote (unanimous / majority / deadlock)

The goal is not forced consensus; it's making trade-offs explicit under three incompatible lenses.
