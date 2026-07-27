#!/usr/bin/env bash
# to_pdf.sh — Convierte un .docx a .pdf conservando el diseño exacto.
# Uso:  bash to_pdf.sh <archivo.docx> [carpeta_salida]
# Requiere LibreOffice (soffice). En el sandbox:  apt-get install -y libreoffice
set -euo pipefail

IN="${1:?Uso: bash to_pdf.sh <archivo.docx> [carpeta_salida]}"
OUTDIR="${2:-$(dirname "$IN")}"

if ! command -v soffice >/dev/null 2>&1; then
  echo "LibreOffice (soffice) no está instalado."
  echo "Instálalo con:  apt-get install -y libreoffice   (o libreoffice-writer)"
  exit 1
fi

# Perfil temporal para evitar bloqueos si hay otra instancia de LibreOffice.
PROFILE="$(mktemp -d)"
soffice --headless --convert-to pdf --outdir "$OUTDIR" \
  -env:UserInstallation="file://$PROFILE" "$IN"
rm -rf "$PROFILE"

echo "PDF -> $OUTDIR/$(basename "${IN%.docx}").pdf"
