#!/usr/bin/env bash
set -euo pipefail

pdf_path="${1:-dist/Andrew_Crozier_Resume.pdf}"
out_dir="${2:-_qa_pdf}"
mkdir -p "$out_dir"
pdftoppm -png -r 200 "$pdf_path" "$out_dir/page"
