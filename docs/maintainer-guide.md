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
`poppler-utils`, `libreoffice`, `libreoffice-java-common`, and
`default-jre-headless`; use `openjdk-21-jre-headless` only if the default
headless runtime package is unavailable. Install the pinned upstream Pandoc
release described below rather than relying on a distribution-default version.

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

DOCX output is generated from Markdown through Pandoc, then normalized to an
explicit US Letter page, single-column semantic paragraphs, native bullets, and
portable serif typography. Its title, margins, body size, and heading hierarchy
are aligned with the PDF. RenderCV remains the PDF renderer; different layout
engines and fonts mean line wrapping and pagination need not be identical.
The DOCX metadata normalizer fixes stale core/extended properties, including
an OOXML-compatible numeric application version. ZIP/XML/relationship checks
reject malformed packages, macros, embedded content, and layout text boxes.

Validate the final DOCX with independent text extraction and actual page renders.
Successful LibreOffice rendering is not proof that every Microsoft Word version
or ATS accepts the file. When a recipient reports failure, preserve that exact
file and obtain the application/version and error before claiming a root cause.
Do not replace live text with images or add tables to force PDF-like placement.

`profile-cv build` syncs vendored Typst preview packages into
`~/.cache/typst/packages/preview` because the embedded Typst compiler used by
RenderCV resolves preview packages from that cache. The sync only rewrites a
package directory when the vendored copy differs.

Artifact QA includes deterministic semantic checks derived from `resume.yaml`.
Use optional LLM/LangExtract-style review only as a non-blocking reviewer; do not
make nondeterministic model output a merge gate.

## Checks outside pull requests

The separate `profile-drift` workflow runs on a schedule or manual dispatch, not
on pull requests. Its substantive checks are `profile-cv validate` and
`profile-cv render-profile --check`; both also run in PR CI. Run these explicitly
along with `uv run pre-commit run --all-files` and `uv run pytest -o addopts=""`
for a full local review (the default pytest command excludes integration tests).
A failed historical/default-branch run remains failed until a new run; an
unmerged PR cannot repair the default branch in place.

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

## Project selection and build safety

The CV deliberately selects three complementary projects: human approval in
agent workflows, an AWS Bedrock integration, and a governed delivery case study.
The GitHub profile retains the full portfolio. Selection and order live in
`resume.yaml`; project descriptions and highlights must be backed by the linked
repositories, not invented adoption or impact metrics. This follows
[Amazon's recruiter guidance](https://www.aboutamazon.com/news/workplace/amazon-job-application-resume-writing-tips)
on relevance and demonstrated work. Keep text-first, single-column artifacts:
[Greenhouse documents parsing problems](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)
with complex layouts, image-only documents and contact details in headers or
text boxes. These choices improve inspectability, not guarantee ATS acceptance.

Semantic QA checks source-derived role highlights, every skill keyword, and
selected project descriptions/highlights in each CV surface; profile QA checks
its independently selected copy. Typographic punctuation and whitespace are
normalized, but substantive missing claims fail. Real calendar dates are
validated at the supported year, month or day precision.

Output paths are checked before cleanup. Repository/source paths, overlapping
outputs and symlink paths are rejected. Custom nonempty output directories must
have build ownership evidence; use a new empty directory for a legacy custom
output rather than pointing cleanup at arbitrary existing data. Review packaging
validates an exact staged copy, including the generated README, before replacing
a previous package. Unexpected site files and site/dist mismatches fail instead
of being silently published. Successful LibreOffice conversions still fail QA
when diagnostics report missing Java/JRE or broken profile setup.

## Reproducibility contract

For identical source, source revision and toolchain, generated file bytes must be
stable across processes, hash seeds and rebuild times. Source YAML mapping order
and all array orders are intentional; especially RenderCV section order, career
chronology, project priority and bullet order. Do not alphabetically sort these
to hide a suspected diff. Cross-process tests cover the actual YAML/JSON writers,
JSON-LD, README and Markdown. Full integration rebuilds compare every dist/site
and review-package file under three hash seeds and assert RenderCV does not
rewrite its input YAML. CI runs all integration tests, not only one named build.

The observed binary instability was DOCX ZIP member timestamps, not shuffled
source fields. DOCX packaging now uses stable member ordering and ZIP metadata;
XML content and document reading order are preserved. Source `meta.lastModified`
must be a valid timezone-aware timestamp, not an implicit current-time fallback.
Review metadata records this as `source_modified_at_utc`, explicitly not the
wall-clock build time, and records the revision rather than checkout branch.
Actual run times remain in GitHub Actions. This follows the
[Reproducible Builds timestamp guidance](https://reproducible-builds.org/docs/timestamps/).
The GitHub-hosted download ZIP/container metadata is service-generated and is
not covered by the generated-file byte contract.

Use the frozen lockfile and documented system tools. Repeatability is tested in
each environment; arbitrary Pandoc, LibreOffice, compression, font or renderer
versions are not promised to produce identical bytes or layout. Keep reviewing
PDF text/tag reading order and actual pages after dependency upgrades. The Typst
vendor-cache comparison hashes contents, not only size/mtime, so stale cached
code cannot silently survive an equal-stat replacement.

Custom `build_all(resume_path=...)` inputs are propagated to factual QA. The
current pipeline intentionally supports only `Andrew_Crozier_Resume` as its
output basename; unsupported configuration fails before cleanup instead of
creating mismatched site links.

### Pinned Pandoc renderer

Cross-environment comparison found Ubuntu's Pandoc 3.1.3 and the reviewed local
3.1.11.1 produce different DOCX defaults and HTML CSS. CI therefore downloads
[upstream Pandoc 3.1.11.1](https://github.com/jgm/pandoc/releases/tag/3.1.11.1)
and verifies its Linux amd64 archive SHA-256 before extraction:
`07635f6953201ee261bf90e821b8fe36c045e5a6fbae2ae6b1c2127715432942`.
Use the same version locally (upstream provides other platform binaries).
Build preflight rejects mismatched Pandoc versions before cleaning artifacts.
The upstream release includes DOCX validity fixes, but this is not evidence that
the recipient's specific Word/ATS problem has been reproduced or resolved.
When upgrading, change the reviewed version/hash together and repeat layout,
extraction and cross-process/cross-environment comparisons.
