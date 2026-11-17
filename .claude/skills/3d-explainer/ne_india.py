#!/usr/bin/env python3
"""Get India's outline from the official Natural Earth India point-of-view boundary (never hand-drawn).

    python3 ne_india.py OUT.json [--zip ne_10m_admin_0_countries_ind.zip]

Downloads ne_10m_admin_0_countries_ind.zip from naturalearthdata.com (or uses --zip), reads the India
polygon with pyshp (pip install pyshp), simplifies lightly, and writes {"rings":[[[lon,lat],...]], "cx","cy","s"}
for build_scene.py (s = Blender units per degree, so India is ~30 units wide).
"""
import argparse, io, json, os, urllib.request, zipfile
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--zip"); a = ap.parse_args()
import shapefile  # pyshp
URL = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries_ind.zip"
data = open(a.zip, "rb").read() if a.zip else urllib.request.urlopen(URL).read()
z = zipfile.ZipFile(io.BytesIO(data)); base = [n[:-4] for n in z.namelist() if n.endswith(".shp")][0]
r = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), shx=io.BytesIO(z.read(base + ".shx")), dbf=io.BytesIO(z.read(base + ".dbf")))
fields = [f[0] for f in r.fields[1:]]
for rec, shp in zip(r.records(), r.shapes()):
    d = dict(zip(fields, rec))
    if d.get("ADM0_A3") == "IND" or d.get("SOV_A3") == "IND" and d.get("TYPE") in ("Sovereign country", "Country"):
        pts, parts = shp.points, list(shp.parts) + [len(shp.points)]
        rings = [pts[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)]
        rings = [ring[::max(1, len(ring) // 1500)] for ring in rings if len(ring) > 20]
        xs = [p[0] for rr in rings for p in rr]; ys = [p[1] for rr in rings for p in rr]
        json.dump({"rings": rings, "cx": (min(xs) + max(xs)) / 2, "cy": (min(ys) + max(ys)) / 2, "s": 30 / (max(xs) - min(xs))}, open(a.out, "w"))
        print(f"India: {len(rings)} rings -> {a.out}"); break
else:
    raise SystemExit("India not found in the shapefile")
