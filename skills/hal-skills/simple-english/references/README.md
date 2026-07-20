# Sources

## Files in this folder

- `writing-rules.md`: distilled rule reference for this skill, committed. The specification wins on any disagreement.
- `ASD-STE100_ISSUE9.pdf`: the official ASD-STE100 Simplified Technical English specification, Issue 9 (2025-01-15). Part 1 is the writing rules (53 rules in 9 sections plus 8 general recommendations). Part 2 is the dictionary (875 approved words, 1274 unapproved words with approved alternatives). Gitignored, local copy only.
- `ASD-STE100_ISSUE9.txt`: plain-text extraction of the PDF, used by the skill for dictionary Grep lookups. Gitignored, local copy only.

## Getting the raw content

To restore full-fidelity dictionary lookups, or to refactor this skill against the source:

1. Download the official Issue 9 PDF into this folder: https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf
2. Regenerate the text extraction: `pdftotext -layout ASD-STE100_ISSUE9.pdf ASD-STE100_ISSUE9.txt`

The skill works without these files at reduced fidelity: `writing-rules.md` carries the full rule set, the complete approved-verbs list, and the most frequent word mappings, but not the other ~860 approved words or the 1274 unapproved-word alternatives.

## Copyright

ASD-STE100 is owned by ASD (Aerospace, Security and Defence Industries Association of Europe), Brussels. © ASD 2025, EU trademark 017966390. The specification is distributed free of charge but its copyright notice restricts reproduction and publication without written ASD authority, with special usage rights for listed organizations (ASD/AIA/AIAC members and their customers, defense ministries, airworthiness authorities, universities for educational purposes). That is why the PDF and txt are gitignored instead of committed.

## Official links

- Official site: https://www.asd-ste100.org/
- Downloads page (request form, change form): https://www.asd-ste100.org/STE_downloads.html
- STEMG contact: stemg@asd-ste100.org
- Issue cadence: about every 3 years. Issue 10 is scheduled for January 2028. Check the site for newer issues before trusting this folder blindly.
