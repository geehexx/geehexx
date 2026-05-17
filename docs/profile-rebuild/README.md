# Profile Rebuild Handoff

Status: current public-safe handoff package for the Andrew Crozier CV/profile rebuild.
Last updated: 2026-05-18.
Repository: `geehexx/geehexx`.

This directory is the working handoff location for the resume/profile rebuild project.
It intentionally contains public-safe implementation guidance only. Raw planning notes,
conversation transcripts, screenshots, Google Docs exports, and sensitive reasoning should
not be committed here.

## Files

- `CODEX_AGENT_PROMPT.md` — prompt to give to the Codex or cloud coding agent.
- `FUTURE_SESSION_STATE.md` — compact state summary for future ChatGPT or agent sessions.
- `CHANGELOG_2026-05-18.md` — latest handoff changes.

## Source policy

Use LinkedIn/PDF chronology as date-authoritative unless Andrew explicitly overrides it.
Use the current GitHub README as the public-builder voice source. Use older Google Docs,
YAML files, screenshots, and prior generated artifacts as content reservoirs only.

Locked decisions:

- Use `linkedin.com/in/ancrozier` everywhere.
- Use `Relocation possible`, not `Relocation possible for the right role`, on ATS material.
- Use ontology wording; do not mention `318-node taxonomy`.
- Do not expose small or weak optimization metrics unless they materially improve the claim.
- Use `multiple squads` for BaxEnergy delivery/process references.
- Avoid exact DORA improvement percentages unless confirmed and useful.
- Use November 2015 for the early freelance/network-engagement start.
- Keep public GitHub and LinkedIn profile material public-safe and less metric-dense than ATS.

## Public/private boundary

The implementation should enforce the boundary with `.gitignore`, validation checks, and
clear output directories. Public-facing documentation generated from this work must not
include private planning rationale, sensitive claim debates, raw screenshots, Google Doc
exports, or agent conversation transcripts.

## How to proceed

Start with `CODEX_AGENT_PROMPT.md`. The implementation agent should inspect
`phraseturner`, `cv-builder`, and this repository, then build or update the resume
generation pipeline in small tested increments.

Do not replace the public GitHub profile README directly without a review step. Generate
a patch or preview first.
