#!/usr/bin/env bash
# Separate vocals from music with demucs (htdemucs). Align lyrics on the vocal stem, never on the mix.
#   bash stems.sh SONG.mp3 OUTDIR      ->  OUTDIR/vocals.wav  OUTDIR/no_vocals.wav (instrumental)
set -euo pipefail
in="$1"; out="$2"; mkdir -p "$out"
if [ -f "$out/vocals.wav" ] && [ -f "$out/no_vocals.wav" ]; then echo "stems already in $out"; exit 0; fi
tmp=$(mktemp -d)
python3 -m demucs --two-stems vocals -n htdemucs -o "$tmp" "$in"
d=$(find "$tmp" -name vocals.wav -printf '%h\n' | head -1)
mv "$d/vocals.wav" "$out/vocals.wav"; mv "$d/no_vocals.wav" "$out/no_vocals.wav"; rm -rf "$tmp"
echo "wrote $out/vocals.wav and $out/no_vocals.wav"
