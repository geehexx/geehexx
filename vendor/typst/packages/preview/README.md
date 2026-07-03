# Vendored Typst packages

These files make RenderCV builds deterministic in offline CI/runtime environments.

- `rendercv/0.3.0`: copied from the installed `rendercv` Python package's bundled Typst package. Package metadata declares MIT license.
- `fontawesome/0.6.0`: minimal local stub that satisfies RenderCV's import when icons are disabled. The resume design disables icons and external-link icons, so this function should not affect visible output.

`profile-cv build` syncs these packages into `~/.cache/typst/packages/preview` before invoking RenderCV because the embedded Typst compiler used by `typst-py` resolves preview packages from that cache path. The sync skips package directories that already match the vendored copy.
