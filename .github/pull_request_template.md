## Summary

-

## Reviewer Map

- Source/model:
- Rendering/templates:
- QA/tests:
- Workflows/hooks:
- Docs/process:

## Source, Artifact, And Contact Boundary

- [ ] `resume.yaml` remains the canonical source.
- [ ] `README.md` is generated from `resume.yaml` and remains the tracked GitHub profile output.
- [ ] Generated PDF, DOCX, Markdown, HTML, JSON, Typst, site, preview, and review-package outputs are not committed.
- [ ] Public README does not expose the direct resume email.
- [ ] Resume source and resume artifacts may include intended resume contact details.
- [ ] GitHub Pages publishing is not added or enabled.

## Validation

- [ ] `uv sync --frozen --extra dev`
- [ ] `uv run profile-cv doctor`
- [ ] `uv run profile-cv validate`
- [ ] `uv run profile-cv render-profile --check`
- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy`
- [ ] `uv run pytest`
- [ ] `uvx --from actionlint-py actionlint`
- [ ] `uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml`
- [ ] `uvx check-jsonschema --builtin-schema custom.github-workflows-require-timeout .github/workflows/*.yml`
- [ ] `uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml`
- [ ] `uvx yamllint .github/dependabot.yml .github/workflows quality-gates.yaml resume.yaml .yamllint.yml`
- [ ] `uvx zizmor --format plain .`
- [ ] `uv run python scripts/check_public_surface.py`
- [ ] `uv run python scripts/check_workflows.py`
- [ ] `uv run python scripts/lint_readme.py README.md`
- [ ] `git ls-files -z | xargs -0 uv run --with detect-secrets detect-secrets-hook --exclude-files '^(vendor/typst/)'`
- [ ] `uv run profile-cv build --clean --no-profile-check`
- [ ] `uv run profile-cv compare-themes`
- [ ] `scripts/render_pdf_for_qa.sh dist/Andrew_Crozier_Resume.pdf _qa_pdf`
- [ ] `scripts/render_docx_for_qa.sh dist/Andrew_Crozier_Resume.docx _qa_docx`
- [ ] `uv run profile-cv review-package`
- [ ] `uv run profile-cv qa`
- [ ] PDF/DOCX preview rendering is warning-free; missing LibreOffice Java/JRE support is fixed rather than suppressed.
- [ ] `uv run pre-commit run --all-files`
- [ ] `make check`

## CI / Artifact Evidence

- Head SHA:
- CI run URL:
- Artifact URL:
- Artifact digest:
- Artifact expiry:
- Download command: `gh run download <run-id> --name resume-artifacts --dir review-artifacts`

## Artifact Review

- [ ] Opened review-package `REVIEW.md`, `index.html`, and `manifest.json`.
- [ ] Reviewed PDF page previews for clipping, overlap, glyph issues, and pagination drift.
- [ ] Reviewed DOCX page previews for ATS/layout regressions after LibreOffice conversion.
- [ ] Compared README, ATS Markdown, PDF text, DOCX text, and HTML for aligned dates, titles, project descriptions, skills, and contact boundaries.
- [ ] Reviewed `theme-comparison.md` and theme preview outputs when layout/theme behavior changed.

## Documentation And Process

- [ ] Maintainer docs and `AGENTS.md` still match the implemented workflow.
- [ ] The changelog describes implemented behavior without overstating custom checks.
- [ ] Any local limitations list exact missing tools, warning evidence, or environment gaps.

## Local Limitations

-
