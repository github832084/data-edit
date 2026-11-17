"""Build every shot of a 3D explainer in ONE Blender scene, with camera cuts on aligned words.

    blender -b -P build_scene.py -- shots.json align.json scene.blend [--india india.json] [--cycles]

shots.json: [{"id": "pads", "start_word": 12, "models": ["launch_pad", "rocket"], "camera": "push"|"orbit"|"rise",
              "labels": [{"text": "4 LAUNCH PADS", "word": 15, "pos": [0, 0, 6]}], "color": "#ff7a00"}]
- Each shot is built around x = index*100 (its own area), with its own camera.
- Camera cut = timeline marker bound to that camera at round(word.start * fps).
- Labels (English only: Blender's text cannot shape Devanagari) pop in (scale 0 -> 1.1 -> 1) at their word.
- Model kinds: rocket, launch_pad, india_map (needs --india from ne_india.py), pin, storm, earth, sea, bars.
Render: blender -b scene.blend -a   (EEVEE, 1080x1920, 30 fps, writes shots.mp4 next to scene.blend)
"""
import bpy, json, math, os, sys

argv = sys.argv[sys.argv.index("--") + 1:]
shots_p, align_p, out_blend = argv[:3]
india_p = argv[argv.index("--india") + 1] if "--india" in argv else None
FPS = 30
shots = json.load(open(shots_p)); al = json.load(open(align_p))
words = [w for l in al["lines"] for w in l["words"]]
fr = lambda t: max(1, round(t * FPS) + 1)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "CYCLES" if "--cycles" in argv else ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE")
sc.render.resolution_x, sc.render.resolution_y, sc.render.fps = 1080, 1920, FPS
sc.frame_start, sc.frame_end = 1, fr(al["duration"])
sc.render.image_settings.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "HIGH"
sc.render.filepath = os.path.join(os.path.dirname(os.path.abspath(out_blend)), "shots.mp4")
try: sc.eevee.use_bloom = True; sc.eevee.bloom_intensity = 0.08          # EEVEE legacy (<= 4.1)
except Exception: pass
# Bloom for EEVEE Next (4.2+): compositor glare
sc.use_nodes = True; nt = sc.node_tree
rl = nt.nodes.get("Render Layers") or nt.nodes.new("CompositorNodeRLayers"); comp = nt.nodes.get("Composite") or nt.nodes.new("CompositorNodeComposite")
gl = nt.nodes.new("CompositorNodeGlare")
try: gl.glare_type = "BLOOM"
except Exception: gl.glare_type = "FOG_GLOW"
gl.threshold = 0.9; nt.links.new(rl.outputs["Image"], gl.inputs["Image"]); nt.links.new(gl.outputs["Image"], comp.inputs["Image"])
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.05, 1); world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

def hexc(h, a=1): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)
def mat(name, color, emit=0.0, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        key = "Emission Color" if "Emission Color" in b.inputs else "Emission"
        b.inputs[key].default_value = hexc(color) if isinstance(color, str) else color; b.inputs["Emission Strength"].default_value = emit
    return m
def put(obj, m, coll):
    obj.data.materials.append(m)
    for c in obj.users_collection: c.objects.unlink(obj)
    coll.objects.link(obj); return obj

def rocket(x, coll):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=6, location=(x, 0, 4)); put(bpy.context.object, mat("body", "#f2f2f2", rough=0.3), coll)
    bpy.ops.mesh.primitive_cone_add(radius1=0.6, depth=1.6, location=(x, 0, 7.8)); put(bpy.context.object, mat("nose", "#ff5a1f"), coll)
    for i in range(4):
        a = i * math.pi / 2; bpy.ops.mesh.primitive_cube_add(size=1, location=(x + math.cos(a) * 0.8, math.sin(a) * 0.8, 1.6))
        o = bpy.context.object; o.scale = (0.08 if i % 2 == 0 else 0.6, 0.6 if i % 2 == 0 else 0.08, 0.8); put(o, mat("fin", "#333a44"), coll)
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, depth=2.2, location=(x, 0, 0.0), rotation=(math.pi, 0, 0)); put(bpy.context.object, mat("flame", "#ffb020", emit=25), coll)
def launch_pad(x, coll):
    bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=0.5, location=(x, 0, 0.25)); put(bpy.context.object, mat("pad", "#5b6270"), coll)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + 2, 0, 4)); o = bpy.context.object; o.scale = (0.4, 0.4, 8); put(o, mat("tower", "#c23b22", metal=0.4), coll)
def sea(x, coll, color="#0b3b6b"):
    bpy.ops.mesh.primitive_plane_add(size=80, location=(x, 0, 0)); put(bpy.context.object, mat("sea", color, rough=0.15), coll)
def earth(x, coll):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=6, location=(x, 0, 6), segments=96, ring_count=48); o = bpy.context.object
    m = mat("earth", "#1d5fa8", rough=0.6); nt2 = m.node_tree; n = nt2.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 3
    ramp = nt2.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = hexc("#1d5fa8"); ramp.color_ramp.elements[1].color = hexc("#3f8f3a"); ramp.color_ramp.elements[0].position = 0.52; ramp.color_ramp.elements[1].position = 0.56
    nt2.links.new(n.outputs["Fac"], ramp.inputs["Fac"]); nt2.links.new(ramp.outputs["Color"], nt2.nodes["Principled BSDF"].inputs["Base Color"]); put(o, m, coll)
    am = mat("atmo", "#6fb7ff", emit=0.6, rough=1); am.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.15
    try: am.blend_method = "BLEND"
    except Exception: pass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=6.25, location=(x, 0, 6)); put(bpy.context.object, am, coll)
def storm(x, coll, start, end):
    sea(x, coll, "#0a2a44")
    for i in range(140):
        a = i * 0.45; r = 0.4 + i * 0.09; bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25 + i * 0.012, location=(x + math.cos(a) * r, math.sin(a) * r, 1.2 + (i % 5) * 0.08))
        o = bpy.context.object; o.scale.z = 0.3; put(o, mat(f"cloud{i % 3}", "#e8eef5", rough=1), coll)
    piv = bpy.data.objects.new("storm_pivot", None); coll.objects.link(piv); piv.location = (x, 0, 0)
    for o in list(coll.objects):
        if o.name.startswith("Sphere") and o.parent is None: o.parent = piv; o.location.x -= x
    piv.rotation_euler.z = 0; piv.keyframe_insert("rotation_euler", frame=start); piv.rotation_euler.z = -math.pi * 2 * (end - start) / FPS / 6; piv.keyframe_insert("rotation_euler", frame=end)
def pin(x, y, coll, color="#ff3b30"):
    bpy.ops.mesh.primitive_cone_add(radius1=0.25, depth=1.0, location=(x, y, 1.0), rotation=(math.pi, 0, 0)); put(bpy.context.object, mat("pin", color, emit=8), coll)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(x, y, 1.6)); put(bpy.context.object, mat("pinhead", color, emit=12), coll)
def india_map(x, coll, color="#2f7d5b"):
    if not india_p: raise SystemExit("india_map needs --india india.json (run ne_india.py: official Natural Earth India POV boundary)")
    data = json.load(open(india_p)); verts_all = []
    for k, ring in enumerate(data["rings"]):
        mesh = bpy.data.meshes.new(f"india{k}"); vs = [(x + (lon - data["cx"]) * data["s"], (lat - data["cy"]) * data["s"], 0) for lon, lat in ring]
        mesh.from_pydata(vs, [], [list(range(len(vs)))]); o = bpy.data.objects.new(f"india{k}", mesh); coll.objects.link(o)
        mod = o.modifiers.new("solid", "SOLIDIFY"); mod.thickness = 0.6; o.data.materials.append(mat("india", color, rough=0.5))
MODELS = {"rocket": rocket, "launch_pad": launch_pad, "earth": earth, "sea": sea, "india_map": india_map}

markers = sc.timeline_markers
for i, s in enumerate(shots):
    x = i * 100.0; coll = bpy.data.collections.new(f"shot_{i}_{s.get('id', '')}"); sc.collection.children.link(coll)
    t0 = words[s["start_word"]]["start"] if i else 0.0
    t1 = words[shots[i + 1]["start_word"]]["start"] if i + 1 < len(shots) else al["duration"]
    f0, f1 = fr(t0), fr(t1)
    for m in s.get("models", []):
        if m == "storm": storm(x, coll, f0, f1)
        elif m == "pin":
            for (px, py) in s.get("pins", [[0, 0]]): pin(x + px, py, coll)
        elif m in MODELS: MODELS[m](x, coll)
    # soft studio light
    for j, (lx, ly, lz, e) in enumerate([(8, -8, 12, 800), (-10, -4, 8, 300), (0, 10, 10, 400)]):
        ld = bpy.data.lights.new(f"L{i}{j}", "AREA"); ld.energy = e; ld.size = 8; lo = bpy.data.objects.new(f"L{i}{j}", ld); coll.objects.link(lo); lo.location = (x + lx, ly, lz)
        lo.rotation_euler = (math.atan2(math.hypot(lx, ly), lz), 0, math.atan2(ly, lx) + math.pi / 2)
    # camera with a slow push / orbit / rise over the shot
    cd = bpy.data.cameras.new(f"C{i}"); cd.lens = 35; cam = bpy.data.objects.new(f"C{i}", cd); coll.objects.link(cam)
    tgt = bpy.data.objects.new(f"T{i}", None); coll.objects.link(tgt); tgt.location = (x, 0, s.get("look_z", 3))
    con = cam.constraints.new("TRACK_TO"); con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    dist = s.get("distance", 22); mode = s.get("camera", "push")
    for f, p in ((f0, 0.0), (f1, 1.0)):
        if mode == "orbit": a = -math.pi / 2 + p * 0.6; cam.location = (x + math.cos(a) * dist, math.sin(a) * dist, dist * 0.35)
        elif mode == "rise": cam.location = (x, -dist, 1 + p * dist * 0.6)
        else: cam.location = (x, -dist * (1 - 0.18 * p), dist * 0.35)
        cam.keyframe_insert("location", frame=f)
    mk = markers.new(f"shot{i}", frame=f0); mk.camera = cam
    if i == 0: sc.camera = cam
    # labels pop in on their word
    for lab in s.get("labels", []):
        cu = bpy.data.curves.new(f"lab{i}", "FONT"); cu.body = lab["text"]; cu.align_x = "CENTER"; cu.extrude = 0.08; cu.size = lab.get("size", 1.6)
        o = bpy.data.objects.new(f"lab{i}", cu); coll.objects.link(o); px, py, pz = lab.get("pos", [0, 0, 7]); o.location = (x + px, py, pz); o.rotation_euler = (math.pi / 2, 0, 0)
        o.data.materials.append(mat("label", lab.get("color", s.get("color", "#ff7a00")), emit=6))
        fw = fr(words[lab["word"]]["start"])
        for f, sz in ((fw - 1, 0.0), (fw + 4, 1.12), (fw + 8, 1.0)): o.scale = (sz, sz, sz); o.keyframe_insert("scale", frame=f)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out_blend))
print(f"built {len(shots)} shots, {sc.frame_end} frames -> {out_blend}")
