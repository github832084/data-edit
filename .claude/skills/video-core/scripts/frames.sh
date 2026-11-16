#!/usr/bin/env bash
# Turn a clip into a numbered JPEG sequence the canvas can draw (Kit.clip(dir, fps, count)).
#   bash frames.sh CLIP.mp4 OUTDIR [FPS=30] [START=0] [DURATION=all] [VF=extra ffmpeg filter]
# Prints the frame count. Keeps the clip's colours (no colour filters, ever). Rotates by metadata
# automatically. HDR (iPhone HLG/PQ) clips must be converted first (see talking-head-edit), not tone-mapped here.
set -euo pipefail
in="$1"; out="$2"; fps="${3:-30}"; ss="${4:-0}"; dur="${5:-}"; vf="${6:-}"
mkdir -p "$out"
tr=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$in" || true)
case "$tr" in smpte2084|arib-std-b67) echo "HDR clip ($tr): convert it to SDR first (avconvert on a Mac), never with an ffmpeg colour filter." >&2; exit 4;; esac
filt="fps=$fps"; [ -n "$vf" ] && filt="$vf,$filt"
ffmpeg -v error -y -ss "$ss" ${dur:+-t "$dur"} -i "$in" -vf "$filt" -q:v 2 "$out/%06d.jpg"
ls "$out" | grep -c '\.jpg$'
