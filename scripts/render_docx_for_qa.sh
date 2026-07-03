#!/usr/bin/env bash
set -euo pipefail

docx_path="${1:-dist/Andrew_Crozier_Resume.docx}"
out_dir="${2:-_qa_docx}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
lo_home="$tmp_dir/home"
lo_out="$tmp_dir/out"
stdout_file="$tmp_dir/libreoffice.stdout"
stderr_file="$tmp_dir/libreoffice.stderr"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$lo_home" "$lo_out"
user_installation="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().as_uri())' "$lo_home")"

if ! HOME="$lo_home" libreoffice \
  "-env:UserInstallation=$user_installation" \
  --headless \
  --norestore \
  --nodefault \
  --nofirststartwizard \
  --nolockcheck \
  --convert-to pdf \
  --outdir "$lo_out" \
  "$docx_path" >"$stdout_file" 2>"$stderr_file"; then
  echo "LibreOffice failed while rendering $docx_path" >&2
  sed 's/^/stdout: /' "$stdout_file" >&2
  sed 's/^/stderr: /' "$stderr_file" >&2
  exit 1
fi

pdf_name="$(basename "${docx_path%.*}.pdf")"
pdf_path="$lo_out/$pdf_name"
if [[ ! -s "$pdf_path" ]]; then
  echo "LibreOffice did not produce $pdf_path" >&2
  sed 's/^/stdout: /' "$stdout_file" >&2
  sed 's/^/stderr: /' "$stderr_file" >&2
  exit 1
fi

if [[ -s "$stderr_file" ]]; then
  echo "LibreOffice produced unexpected stderr while rendering $docx_path" >&2
  sed 's/^/stderr: /' "$stderr_file" >&2
  exit 1
fi

"$script_dir/render_pdf_for_qa.sh" "$pdf_path" "$out_dir"
