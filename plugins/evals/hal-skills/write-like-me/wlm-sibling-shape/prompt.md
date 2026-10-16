---
description: "Needs `--scaffold`. The workspace holds three notes: the empty target, a short published how-to (Quick Tunnel, 123 words), and a long published tutorial (Kubernetes, 608 words). The reference is the user's published post, 239 words. Graders: reads-sibling checks the short how-to was opened; length caps the draft at 1.3x the reference; skeleton checks the short how-to shape; rules checks the hard style bans; no-forced-joke checks for an invented joke. Baseline over 5 runs with `--ablation none`, claude-opus-5-5, and the Sonnet judge: 1.00 at 990f23ea, 0.93 at 46723b22 (skeleton split twice)."
plugins: ["../../../../../skills"]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

draft the blog post for my empty note at `notes/Programming/Networking/Use Cloudflare Access to Protect Your Website or Service.md`. reply with the markdown only, I'll paste it myself.

what I did:

- my WordPress blog at https://vinta.ws/code/ gets thousands of brute-force login attempts a day, so I put Cloudflare Access in front of `wp-login.php` and `wp-admin` as an extra layer of security
- it works as long as the domain is hosted on Cloudflare, and anyone not allowed is blocked at Cloudflare's edge before reaching the server
- only the emails I allow can get in, they log in with a one-time PIN sent to their email
- Cloudflare dashboard > Zero Trust:
  - Integrations > Identity providers > Add new identity provider > One-time PIN
  - Access controls > Applications > Create new application > Self-hosted and private
  - Destinations > Public hostnames: domain `vinta.ws`, paths `code/wp-login.php` and `code/wp-admin`
  - Access policies > Create new policy: Action Allow, Include Emails, my email
  - Authentication > Identity: One-time PIN, turn on Apply instant authentication
  - Details: any name, Session Duration 24 hours
- docs: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- after that, opening the protected page shows Cloudflare's login page asking for an email
- no code, no plugin, free
