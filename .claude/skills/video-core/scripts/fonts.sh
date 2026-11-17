#!/usr/bin/env bash
# Install Google Fonts locally from npm (@fontsource packages), so renders never depend on a font CDN.
#   bash fonts.sh inter bangers yatra-one tiro-devanagari-hindi great-vibes "playfair-display"
# In a scene: await k.fontsource('yatra-one', 'Yatra One', [400], 'devanagari')
# Files land in video-core/fonts/<slug>/files/<slug>-<subset>-<weight>-<style>.woff2
set -euo pipefail
dir="$(cd "$(dirname "$0")/../fonts" && pwd)"; cd "$dir"
for slug in "$@"; do
  slug=$(echo "$slug" | tr 'A-Z ' 'a-z-')
  [ -d "$slug/files" ] && { echo "have $slug"; continue; }
  tgz=$(npm pack "@fontsource/$slug" --silent 2>/dev/null | tail -1) || { echo "no @fontsource/$slug on npm" >&2; continue; }
  mkdir -p "$slug" && tar -xzf "$tgz" -C "$slug" --strip-components=1 && rm -f "$tgz"
  echo "installed $slug: $(ls "$slug/files" | grep -c woff2) files (subsets: $(ls "$slug/files" | sed -E "s/^$slug-([a-z-]+)-[0-9]+-.*/\1/" | sort -u | tr '\n' ' '))"
done
