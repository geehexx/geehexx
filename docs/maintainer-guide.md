# Maintainer Guide

This repository owns the public `geehexx` GitHub profile README and reviewed CV
artifacts. Source data, templates, tests, policy, and workflow configuration are
tracked; generated distribution files stay under ignored output directories.

## Source Model

`resume.yaml` is the canonical source. It keeps JSON Resume-compatible sections
(`basics`, `work`, `education`, `skills`, `projects`, `languages`, `meta`) plus
repo-owned `x_` fields for profile copy, RenderCV design settings, output names,
and per-surface inclusion flags.

Generated files must not become secondary sources. Regenerate instead of
hand-editing `README.md`, `dist/`, `site/`, RenderCV YAML, DOCX, PDF, HTML, or
JSON-LD output.

Every work entry must declare `x_profile.section` as `career_snapshot`,
`earlier_work`, or `omit`. Profile sections are rendered from those flags, not
from adapter-side company-name lists.

## Commands

```bash
uv sync --extra dev
uv run profile-cv validate
uv run profile-cv render-profile --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uvx --from actionlint-py actionlint
uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml
uvx check-jsonschema --builtin-schema custom.github-workflows-require-timeout .github/workflows/*.yml
uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml
uvx yamllint .github/dependabot.yml .github/workflows quality-gates.yaml resume.yaml .yamllint.yml
uvx zizmor --format plain .
uv run python scripts/check_public_surface.py
uv run python scripts/check_workflows.py
uv run python scripts/lint_readme.py README.md
uv run profile-cv compare-themes
uv run profile-cv build --clean --no-profile-check
uv run profile-cv qa
```

`profile-cv build` emits reviewed artifacts under `dist/` and a local preview
site under `site/`. Do not enable or publish GitHub Pages unless a future change
explicitly revisits the public contact boundary. CI installs Pandoc, Poppler,
and LibreOffice before artifact generation because DOCX metadata and visual QA
depend on those system tools.

## Quality Gates

`quality-gates.yaml` owns the repository surface boundary:

- public/tracked file allowlists;
- generated and non-public path blocks;

General syntax, formatting, typing, tests, workflow schema/security, YAML style,
and secret detection should use standard tools such as pre-commit hooks, Ruff,
mypy, pytest, actionlint, check-jsonschema, yamllint, zizmor, GitHub
protections, and CI. Keep custom Python gates narrow and repo-specific.

## Rendering Decisions

RenderCV stays the PDF/Typst renderer because it keeps CV content in text and
handles consistent typography. The default theme is `engineeringresumes`; only
change theme, font, margins, contact separators, or spacing after comparing
generated artifacts and confirming no ATS downside.

ATS surfaces should remain single-column, text-based, standard-heading documents
with readable 10-12pt body text, simple bullets, no icons, no tables used for
layout, no text boxes, and contact details in the main body.

DOCX output is generated from Markdown through Pandoc and finalized by the
metadata normalizer. Keep the normalizer only while tests prove Pandoc leaves
stale or incomplete core/extended properties.

`profile-cv build` syncs vendored Typst preview packages into
`~/.cache/typst/packages/preview` because the embedded Typst compiler used by
RenderCV resolves preview packages from that cache. The sync only rewrites a
package directory when the vendored copy differs.

Artifact QA includes deterministic semantic checks derived from `resume.yaml`.
Use optional LLM/LangExtract-style review only as a non-blocking reviewer; do not
make nondeterministic model output a merge gate.

## Manual Release Review

Before distributing a CV/profile build:

- compare `README.md`, ATS Markdown, PDF text, and DOCX text for aligned dates,
  titles, project descriptions, skills, and contact/privacy boundaries;
- review every PDF and DOCX page rendered to PNG for clipping, overlap, missing
  glyphs, broken visible links, and unexpected pagination drift;
- keep generated artifacts ignored unless the user explicitly asks to publish
  them elsewhere.
- merge only after current local evidence, current CI evidence, and a recorded
  self-review note. `main` should also require the CI `quality` check through
  branch protection.
