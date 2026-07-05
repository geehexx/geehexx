# Changelog

## 1.0.0 - 2026-07-03

- Rebased the profile/CV system onto the `geehexx` GitHub profile repo shape.
- Promoted `resume.yaml` to the canonical source of truth.
- Added RenderCV, Pandoc, JSON-LD, README generation, deterministic QA checks, hooks, and GitHub Actions.
- Aligned public-facing resume claims after verification: narrowed partner examples, consolidated early-career chronology, changed Agoda scale to `millions of properties`, and clarified Dubizzle as Naspers-backed growth-period work.
- Normalized the CV/profile title to Engineering Manager, removed forced summary/acronym emphasis, removed Australia relocation wording, and added resume-only phone contact details.
- Added `geehexx`, `library-ops`, and `PragmaLens` to the public-work model with explicit resume/profile inclusion controls.
- Added DOCX OpenXML metadata normalization and QA checks for current distribution metadata.
- Expanded public-surface checks for generated/private path boundaries and paired them with standard `detect-secrets` coverage.
- Hardened GitHub Actions with pinned uv runtime, tracked `uv.lock` installs, timeouts, concurrency, workflow policy checks, artifact-retention controls, no Pages publishing workflow, and Dependabot action updates.
- Added a generated PR review package with artifact manifests, source-derived artifacts, generated profile output, local site preview, deterministic QA evidence, and GitHub Actions artifact review links.
- Finalized `engineeringresumes` as the single supported RenderCV theme and removed the temporary layout-comparison and page-preview workflows from CLI, CI, tests, docs, and artifacts.
- Required LibreOffice Java support and a headless JRE for DOCX metadata QA, and made review-package CLI output concise by default.
