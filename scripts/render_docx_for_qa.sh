#!/usr/bin/env bash
set -euo pipefail

docx_path="${1:-dist/Andrew_Crozier_Resume.docx}"
out_dir="${2:-_qa_docx}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
libreoffice --headless --convert-to pdf --outdir "$tmp_dir" "$docx_path" >/dev/null
pdf_name="$(basename "${docx_path%.*}.pdf")"
"$(dirname "$0")/render_pdf_for_qa.sh" "$tmp_dir/$pdf_name" "$out_dir"
