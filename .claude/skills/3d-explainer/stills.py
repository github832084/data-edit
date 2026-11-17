"""Render one still per shot (the middle frame between camera markers).

    blender -b scene.blend -P stills.py -- OUT_DIR
"""
import bpy, os, sys
out = sys.argv[sys.argv.index("--") + 1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; ms = sorted(sc.timeline_markers, key=lambda m: m.frame)
sc.render.image_settings.file_format = "PNG"
for i, m in enumerate(ms):
    end = ms[i + 1].frame if i + 1 < len(ms) else sc.frame_end
    f = (m.frame + end) // 2; sc.frame_set(f); sc.camera = m.camera
    sc.render.filepath = os.path.join(out, f"still_{f / sc.render.fps:07.2f}.png"); bpy.ops.render.render(write_still=True)
print(f"{len(ms)} stills -> {out}")
