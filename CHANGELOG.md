# Changelog

## Unreleased

- Rebased the profile/CV system onto the `geehexx` GitHub profile repo shape.
- Promoted `resume.yaml` to the canonical source of truth.
- Added RenderCV, Pandoc, JSON-LD, README generation, QA checks, hooks, and GitHub Actions.
- Aligned public-facing resume claims after verification: narrowed partner examples, toned down Insydo title/claims, changed Agoda scale to `millions of properties`, and clarified Dubizzle as Naspers-backed growth-period work.
- Added `library-ops` and `PragmaLens` to the public-work model with explicit resume/profile inclusion controls.
- Added DOCX OpenXML metadata normalization and QA checks for current distribution metadata.
- Expanded public-surface checks for generated/private path boundaries and paired them with standard `detect-secrets` coverage.
- Hardened GitHub Actions with pinned uv runtime, tracked `uv.lock` installs, timeouts, concurrency, workflow policy checks, artifact-retention controls, no Pages publishing workflow, and Dependabot action updates.
- Added a generated PR review package with artifact manifests, PDF/DOCX visual previews, theme comparison evidence, and GitHub Actions artifact review links.
- Required LibreOffice Java support and a headless JRE for warning-free DOCX artifact QA, hardened DOCX preview rendering, and made review-package CLI output concise by default.
