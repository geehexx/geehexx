# Geehexx Repository Instructions

Global Codex rules and shared skills come from `codex-config` through
`$CODEX_HOME/AGENTS.md` and `$CODEX_HOME/config.toml`. Do not copy global rules,
skills, or config tests into this repo.

## Local Scope

- Treat this repo as the resume/profile workspace, not the global control plane.
- Keep repo-specific instructions here and in nested `AGENTS.md` overlays.
- Work on global Codex behavior in `codex-config`, then verify it with a fresh
  Codex run before relying on it here.
- Keep generated resume artifacts under ignored output directories.
- Treat `resume.yaml` as the canonical profile/CV source; generated JSON,
  Markdown, DOCX, PDF, Typst, HTML, and site outputs are review artifacts.
- Preserve public/private profile boundaries explicitly in source data, templates,
  quality policy, and tests.

## Sibling-Repo Learning

- Learn from `cv` and `phraseturner` by reading targeted modules, fixtures,
  configs, and tests.
- The old local `resume/` subtree is a prototype/reference only. Preserve useful
  facts, rendered phrasing, typed-model ideas, deterministic evaluators, fixtures,
  and targeted CLI-test patterns, but do not treat that package as the foundation.
- Do not run the full `cv` test suite by default.
- Use targeted sibling-repo tests only when a specific lesson or compatibility
  question requires execution.
- Avoid integration-heavy or model-loading tests in sibling repos unless the
  current change directly depends on them.

## Implementation Standards

- Prefer small typed helpers, deterministic evaluators, fixtures, and golden
  checks over procedural scripts with hardcoded regex clusters.
- Keep quality policy in data files where it is easier to review.
- Use `StrictUndefined` templates and source-backed rendering; do not hand-edit
  generated profile or resume artifacts.
- Require useful docstrings on public production functions and classes when the
  behavior is not obvious from types and names.

## Verification

- Do not claim resume/profile work is complete without fresh evidence from the
  relevant targeted commands.
- Prefer narrow tests first, then broader checks only when they are affordable
  and directly relevant.
- Never print raw secrets, private tokens, or unredacted sensitive findings.
- For source/rendering changes, write or update the failing targeted test before
  changing behavior.
- For final CV/profile delivery, manually compare README, ATS Markdown, PDF text,
  and DOCX text for aligned dates, titles, project descriptions, skills, and
  contact/privacy boundaries.
