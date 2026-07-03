# Maintainer Guide

This repository owns the public `geehexx` GitHub profile README and reviewed CV
artifacts. Source data, templates, tests, policy, and workflow configuration are
tracked; generated distribution files stay under ignored output directories.
`README.md` is the one tracked generated output because GitHub renders it as the
special profile page.

## Source Model

`resume.yaml` is the canonical source. It keeps JSON Resume-compatible sections
(`basics`, `work`, `education`, `skills`, `projects`, `languages`, `meta`) plus
repo-owned `x_` fields for profile copy, RenderCV design settings, output names,
and per-surface inclusion flags.

Generated files must not become secondary sources. Regenerate instead of
hand-editing `README.md`, `dist/`, `site/`, review packages, RenderCV YAML,
DOCX, PDF, HTML, or JSON-LD output.

The direct resume email is allowed in `resume.yaml` and resume artifacts. It
must not appear in the public profile README.

Every work entry must declare `x_profile.section` as `career_snapshot`,
`earlier_work`, or `omit`. Profile sections are rendered from those flags, not
from adapter-side company-name lists.

## Commands

```bash
uv sync --frozen --extra dev
uv run profile-cv doctor
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
uv run profile-cv build --clean --no-profile-check
uv run profile-cv review-package
uv run profile-cv qa
```

`uv.lock` is tracked so RenderCV, Pandoc-adjacent Python dependencies, template
behavior, and QA tooling do not drift between local and CI builds.

`profile-cv doctor` checks the external artifact QA tools used by the full
pipeline: RenderCV, Pandoc, Poppler, LibreOffice, and Java. On Ubuntu/CI, install
`pandoc`, `poppler-utils`, `libreoffice`, `libreoffice-java-common`, and
`default-jre-headless`; use `openjdk-21-jre-headless` only if the default
headless runtime package is unavailable.

`profile-cv build` emits reviewed artifacts under `dist/` and a local preview
site under `site/`. `profile-cv review-package` assembles
`dist/review-package/` from the generated artifacts, generated profile README,
site preview, semantic QA metrics, and a manifest with file hashes. Do not enable
or publish GitHub Pages unless a future change explicitly revisits the public
contact boundary. CI installs Pandoc, Poppler, LibreOffice, LibreOffice Java
support, and a headless JRE before artifact generation because PDF text
extraction and DOCX metadata QA depend on those system tools.

## Quality Gates

`quality-gates.yaml` owns the repository surface boundary:

- public/tracked file allowlists;
- generated and non-public path blocks;

General syntax, formatting, typing, tests, workflow schema/security, YAML style,
and secret detection should use standard tools such as pre-commit hooks, Ruff,
mypy, pytest, actionlint, check-jsonschema, yamllint, zizmor, GitHub
protections, and CI. Keep custom Python gates narrow and repo-specific.
Workflow policy checks additionally enforce this repository's release evidence
contract: frozen installs, pinned actions, minimal checkout credentials, artifact
retention, and a CI-uploaded review package.

## Rendering Decisions

RenderCV stays the PDF/Typst renderer because it keeps CV content in text and
handles consistent typography. The default and only supported theme is
`engineeringresumes`; the old comparison workflow was removed after the visual
decision was finalized. Only change theme, font, margins, contact separators, or
spacing after reviewing generated artifacts and confirming no ATS downside.

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

## PR Artifact Review

CI uploads `resume-artifacts` as a temporary GitHub Actions artifact. The
artifact is a review package, not tracked source. Download it from the PR's
current successful `quality` run or with:

```bash
gh run download <run-id> --name resume-artifacts --dir review-artifacts
```

Inside the archive, start with `REVIEW.md`, `index.html`, and `manifest.json`.
Those files point to the generated resume formats, generated profile README,
and site preview. Artifact links expire according to the workflow retention
setting, so every PR body must record the current run URL, artifact URL, digest,
and expiry after the latest push.

## Manual Release Review

Before distributing a CV/profile build:

- compare `README.md`, ATS Markdown, PDF text, and DOCX text for aligned dates,
  titles, project descriptions, skills, and contact/privacy boundaries;
- open the generated PDF, DOCX, HTML, and local site when local viewers are
  available, checking for clipping, overlap, missing glyphs, broken visible
  links, and unexpected pagination drift;
- download the current CI `resume-artifacts` package and confirm
  `REVIEW.md`, `index.html`, and `manifest.json` match the current head SHA;
- keep generated artifacts ignored unless the user explicitly asks to publish
  them elsewhere.
- merge only after current local evidence, current CI evidence, and a recorded
  self-review note. `main` should also require the CI `quality` check through
  branch protection.
