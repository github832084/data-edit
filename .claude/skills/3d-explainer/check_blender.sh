#!/usr/bin/env bash
# Check Blender is installed and renders headless with EEVEE. Installs it if --install is given.
#   bash .claude/skills/3d-explainer/check_blender.sh [--install]
set -u
if ! command -v blender >/dev/null; then
  if [ "${1:-}" = "--install" ]; then
    if command -v brew >/dev/null; then brew install --cask blender
    else
      v=4.2.3; d=/opt/blender-$v
      curl -fL "https://download.blender.org/release/Blender4.2/blender-$v-linux-x64.tar.xz" -o /tmp/blender.tar.xz && mkdir -p "$d" && tar -xJf /tmp/blender.tar.xz -C "$d" --strip-components=1 && ln -sf "$d/blender" /usr/local/bin/blender
      # headless Linux needs these libs for EEVEE
      command -v apt-get >/dev/null && apt-get install -y libxi6 libxkbcommon0 libxxf86vm1 libxfixes3 libxrender1 libgl1 libegl1 >/dev/null 2>&1
    fi
  else
    echo "MISS blender -> Mac: brew install --cask blender | Linux: bash $0 --install (needs download.blender.org) | or download from blender.org"; exit 1
  fi
fi
blender -v | head -1
out=$(mktemp -d)
blender -b --factory-startup --python-expr "
import bpy
s=bpy.context.scene
s.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
s.render.resolution_x, s.render.resolution_y = 108, 192
s.render.filepath = '$out/test.png'
bpy.ops.render.render(write_still=True)
" >/dev/null 2>&1
[ -f "$out/test.png" ] && echo "ok   blender -b renders with EEVEE" || { echo "FAIL blender -b could not render with EEVEE (on a server, EEVEE needs a GPU/EGL; try CYCLES with --cycles in build_scene.py)"; exit 1; }
