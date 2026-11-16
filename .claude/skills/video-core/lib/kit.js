// video-core canvas kit: the shared runtime every scene page loads.
// A scene calls Kit.scene({ setup, draw }). render.cjs then calls window.__frame(t)
// for every frame. Rules: no Date.now(), no requestAnimationFrame, no CSS animation,
// no Math.random(). Everything is a pure function of t, so every render is identical.
(function () {
  const qs = new URLSearchParams(location.search);
  const W = +qs.get('w') || 1920, H = +qs.get('h') || 1080, FPS = +qs.get('fps') || 30;
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H; canvas.id = 'c';
  document.body.style.margin = '0'; document.body.style.background = '#000';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  // ---------- math + easing ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const prog = (t, a, b) => clamp((t - a) / (b - a)); // 0..1 progress of t through [a,b]
  const smooth = (x) => x * x * (3 - 2 * x);
  const ease = {
    linear: (x) => x,
    inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    out: (x) => 1 - Math.pow(1 - x, 3),
    in: (x) => x * x * x,
    outExpo: (x) => (x === 1 ? 1 : 1 - Math.pow(2, -10 * x)), // fast in, long settle
    outBack: (x, s = 1.70158) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2),
    outElastic: (x) => (x === 0 || x === 1 ? x : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1),
  };

  // ---------- deterministic randomness ----------
  function rng(seed) { // mulberry32
    let a = (seed * 2654435761) >>> 0;
    return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const hash = (n) => { const r = rng(Math.floor(n) + 1); return r(); };
  function noise1(x, seed = 0) { // smooth value noise, -1..1
    const i = Math.floor(x), f = x - i, a = hash(i * 7.13 + seed * 101), b = hash((i + 1) * 7.13 + seed * 101);
    return lerp(a, b, smooth(f)) * 2 - 1;
  }
  // "boil": a seed that changes `rate` times a second, for hand-drawn jitter
  const boil = (t, rate = 8) => Math.floor(t * rate);

  // ---------- timing data (from align.py / beats.py / mouth.py) ----------
  const words = (al) => al.lines.flatMap((l, li) => l.words.map((w) => ({ ...w, line: li, speaker: l.speaker })));
  const lineAt = (al, t, pad = 0) => al.lines.findIndex((l) => t >= l.start - pad && t < l.end + pad);
  const wordAt = (ws, t) => ws.findIndex((w) => t >= w.start && t < w.end);
  function chunks(ws, n = 3) { // 2-3 or 3-5 word caption chunks that never cross a line
    const out = []; let cur = [];
    ws.forEach((w, i) => { cur.push(w); const next = ws[i + 1];
      if (cur.length >= n || !next || next.line !== w.line || next.start - w.end > 0.6) { out.push(cur); cur = []; } });
    return out.map((c) => ({ words: c, start: c[0].start, end: c[c.length - 1].end }));
  }
  const chunkAt = (cs, t, hold = 0.25) => cs.findIndex((c, i) => t >= c.start && t < Math.min(c.end + hold, cs[i + 1] ? cs[i + 1].start : 1e9));
  const beatPulse = (beats, t, decay = 0.18) => { // 1 right on a beat, falling to 0
    let last = -1e9; for (const b of beats) { if (b <= t) last = b; else break; } return Math.exp(-(t - last) / decay) * (t >= last ? 1 : 0); };
  const lastBefore = (arr, t) => { let r = -1; for (let i = 0; i < arr.length; i++) { if (arr[i] <= t) r = i; else break; } return r; };
  const frameVal = (arr, t) => (arr && arr.length ? arr[clamp(Math.round(t * FPS), 0, arr.length - 1)] : 0);

  // ---------- loading ----------
  const imgCache = new Map();
  async function img(src) {
    if (imgCache.has(src)) return imgCache.get(src);
    const r = await fetch(src); if (!r.ok) throw new Error('missing image ' + src);
    const bmp = await createImageBitmap(await r.blob()); imgCache.set(src, bmp); return bmp;
  }
  async function json(src) { const r = await fetch(src); if (!r.ok) throw new Error('missing ' + src); return r.json(); }
  async function font(family, url, desc = {}) { const f = new FontFace(family, `url(${url})`, desc); await f.load(); document.fonts.add(f); return f; }
  // Fonts installed by fonts.sh (npm @fontsource packages): fontsource('inter', 'Inter', [400, 900], 'latin')
  async function fontsource(slug, family, weights = [400], subset = 'latin', style = 'normal') {
    for (const w of weights) await font(family, `/fonts/${slug}/files/${slug}-${subset}-${w}-${style}.woff2`, { weight: String(w), style });
  }
  // A pre-extracted frame sequence (frames.sh): clip('/work/clipA', 30, 240).get(t)
  function clip(dir, fps, count, ext = 'jpg') {
    const cache = new Map();
    return { fps, count, duration: count / fps,
      async get(t) { const i = clamp(Math.floor(t * fps), 0, count - 1) + 1;
        if (cache.has(i)) return cache.get(i);
        const b = await img(`${dir}/${String(i).padStart(6, '0')}.${ext}`); imgCache.delete(`${dir}/${String(i).padStart(6, '0')}.${ext}`);
        cache.set(i, b); if (cache.size > 6) { const k = cache.keys().next().value; cache.get(k).close?.(); cache.delete(k); } return b; } };
  }

  // ---------- drawing helpers ----------
  function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }
  function cover(c, im, x, y, w, h, fx = 0.5, fy = 0.5, zoom = 1) { // object-fit: cover, focus point fx/fy
    const s = Math.max(w / im.width, h / im.height) * zoom, iw = im.width * s, ih = im.height * s;
    c.drawImage(im, x + (w - iw) * fx, y + (h - ih) * fy, iw, ih);
  }
  function shake(t, amp = 12, until = 1e9, seed = 3) { // returns [dx,dy]; apply with ctx.translate
    if (t > until) return [0, 0]; return [noise1(t * 30, seed) * amp, noise1(t * 30, seed + 9) * amp];
  }
  function speedLines(c, cx, cy, n, inner, outer, color, t = 0, seed = 1) {
    const r = rng(seed + boil(t, 12)); c.save(); c.fillStyle = color;
    for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2 + r() * 0.08, wd = 0.004 + r() * 0.012, ri = inner * (0.8 + r() * 0.5);
      c.beginPath(); c.moveTo(cx + Math.cos(a - wd) * outer, cy + Math.sin(a - wd) * outer);
      c.lineTo(cx + Math.cos(a) * ri, cy + Math.sin(a) * ri); c.lineTo(cx + Math.cos(a + wd) * outer, cy + Math.sin(a + wd) * outer); c.fill(); }
    c.restore();
  }
  function halftone(c, x, y, w, h, color, step = 14, maxR = 5, angle = 0.4, falloff = (u, v) => 1) {
    c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip(); c.fillStyle = color;
    c.translate(x + w / 2, y + h / 2); c.rotate(angle); const R = Math.hypot(w, h) / 2;
    for (let yy = -R; yy < R; yy += step) for (let xx = -R; xx < R; xx += step) {
      const u = (xx + R) / (2 * R), v = (yy + R) / (2 * R), rad = maxR * clamp(falloff(u, v));
      if (rad > 0.3) { c.beginPath(); c.arc(xx, yy, rad, 0, 7); c.fill(); } }
    c.restore();
  }
  function burst(c, x, y, r, opts = {}) { // comic POW star
    const { points = 14, fill = '#ffe600', stroke = '#000', lw = 8, text = '', font = '900 80px sans-serif', textColor = '#e00', seed = 2, rot = -0.08 } = opts;
    const rnd = rng(seed); c.save(); c.translate(x, y); c.rotate(rot); c.beginPath();
    for (let i = 0; i < points * 2; i++) { const a = (i / (points * 2)) * Math.PI * 2, rad = i % 2 ? r * (0.55 + rnd() * 0.1) : r * (0.9 + rnd() * 0.2);
      c.lineTo(Math.cos(a) * rad, Math.sin(a) * rad); }
    c.closePath(); c.fillStyle = fill; c.fill(); c.lineWidth = lw; c.strokeStyle = stroke; c.lineJoin = 'round'; c.stroke();
    if (text) { c.font = font; c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineWidth = lw; c.strokeStyle = stroke; c.strokeText(text, 0, 0); c.fillStyle = textColor; c.fillText(text, 0, 0); }
    c.restore();
  }
  function bubble(c, x, y, w, h, tailX, tailY, opts = {}) { // speech bubble with a tail pointing at (tailX, tailY)
    const { fill = '#fff', stroke = '#000', lw = 6, r = 40 } = opts;
    c.save(); c.lineWidth = lw; c.strokeStyle = stroke; c.fillStyle = fill; c.lineJoin = 'round';
    const bx = clamp(tailX, x + r + 20, x + w - r - 60), by = tailY > y + h / 2 ? y + h : y;
    c.beginPath(); c.moveTo(bx, by); c.lineTo(tailX, tailY); c.lineTo(bx + 44, by); c.closePath(); c.fill(); c.stroke();
    rr(c, x, y, w, h, r); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(bx + 3, by); c.lineTo(bx + 41, by); c.lineWidth = lw + 2; c.strokeStyle = fill; c.stroke(); c.restore();
  }
  // Wobbly marker / crayon / pencil stroke. pts = [[x,y],...]. amp jitter re-seeded by boil step.
  function wobble(pts, amp, seed) { const r = rng(seed); return pts.map(([x, y]) => [x + (r() - 0.5) * amp, y + (r() - 0.5) * amp]); }
  function strokePath(c, pts, progress = 1, opts = {}) { // draw-on along length
    const { color = '#fff', width = 6, cap = 'round', glow = 0, smoothPath = true } = opts;
    if (pts.length < 2 || progress <= 0) return; let len = 0; const seg = [];
    for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); len += d; }
    c.save(); c.lineCap = cap; c.lineJoin = 'round'; c.strokeStyle = color; c.lineWidth = width;
    if (glow) { c.shadowColor = color; c.shadowBlur = glow; }
    c.setLineDash([len * clamp(progress), len + 1]); c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
    if (smoothPath) for (let i = 1; i < pts.length - 1; i++) { const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2; c.quadraticCurveTo(pts[i][0], pts[i][1], mx, my); }
    c.lineTo(pts[pts.length - 1][0], pts[pts.length - 1][1]); c.stroke(); c.restore();
  }
  // Pen-tip position at progress p along pts (for a glowing nib or pen dot)
  function pointAt(pts, p) { let len = 0; const seg = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); len += d; }
    let target = len * clamp(p); for (let i = 0; i < seg.length; i++) { if (target <= seg[i]) { const u = target / (seg[i] || 1); return [lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u)]; } target -= seg[i]; }
    return pts[pts.length - 1]; }

  // Film grain: 4 pre-baked noise tiles, cycled per frame
  let grainTiles = null;
  function grain(c, t, amount = 0.08, size = 256) {
    if (!grainTiles) grainTiles = [0, 1, 2, 3].map((s) => { const g = new OffscreenCanvas(size, size), gc = g.getContext('2d'), d = gc.createImageData(size, size), r = rng(s + 11);
      for (let i = 0; i < d.data.length; i += 4) { const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } gc.putImageData(d, 0, 0); return g; });
    c.save(); c.globalAlpha = amount; c.globalCompositeOperation = 'overlay'; c.fillStyle = c.createPattern(grainTiles[Math.floor(t * FPS) % 4], 'repeat');
    c.fillRect(0, 0, W, H); c.restore();
  }
  function vignette(c, strength = 0.55, inner = 0.45, color = '0,0,0') {
    const g = c.createRadialGradient(W / 2, H / 2, Math.min(W, H) * inner * 0.5, W / 2, H / 2, Math.hypot(W, H) / 2);
    g.addColorStop(0, `rgba(${color},0)`); g.addColorStop(1, `rgba(${color},${strength})`); c.save(); c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
  }
  // Eyes blink ~every 3-5 s for 0.12 s. Returns 0 (open) .. 1 (closed).
  function blink(t, seed = 1) { const period = 3 + hash(seed) * 2, ph = (t + hash(seed + 5) * period) % period; return ph < 0.12 ? Math.sin((ph / 0.12) * Math.PI) : 0; }
  // Mouth openness 0..1 from mouth.py curves: mouth(data.mouth.speakerA, t)
  const mouth = (curve, t) => clamp(frameVal(curve, t));

  // Karaoke caption: draws a chunk of words centred at (cx, cy); the active word gets `hi` style.
  function caption(c, chunk, t, o = {}) {
    let { font = '800 64px sans-serif', color = '#fff', hi = '#ffd400', hiPill = null, pillText = '#000', stroke = 'rgba(0,0,0,.85)', strokeW = 10,
      gap = null, cx = W / 2, cy = H * 0.78, maxW = W * 0.86, popIn = 0.12, upper = false, wordColor = null, shadow = true } = o;
    c.save(); c.font = font; c.textBaseline = 'middle';
    const fpx = parseInt(font.match(/(\d+)px/)[1]); if (gap == null) gap = fpx * 0.34;
    const ws = chunk.words.map((w) => (upper ? w.w.toUpperCase() : w.w)), widths = ws.map((s) => c.measureText(s).width);
    let total = widths.reduce((a, b) => a + b, 0) + gap * (ws.length - 1), scale = Math.min(1, maxW / total);
    c.translate(cx, cy); c.scale(scale, scale); let x = -total / 2;
    chunk.words.forEach((w, i) => { const on = t >= w.start, active = t >= w.start && t < w.end + 0.05, p = ease.outBack(prog(t, w.start, w.start + popIn));
      if (!on && t < chunk.start) { x += widths[i] + gap; return; }
      c.save(); c.translate(x + widths[i] / 2, 0); const s = on ? lerp(0.6, 1, p) * (active ? 1.08 : 1) : 1; c.scale(s, s); c.globalAlpha = on ? 1 : 0.55;
      if (active && hiPill) { c.fillStyle = hiPill; rr(c, -widths[i] / 2 - 16, -parseInt(font.match(/(\d+)px/)[1]) * 0.62, widths[i] + 32, parseInt(font.match(/(\d+)px/)[1]) * 1.24, 18); c.fill(); }
      if (shadow) { c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 12; c.shadowOffsetY = 4; }
      if (strokeW) { c.lineWidth = strokeW; c.strokeStyle = stroke; c.lineJoin = 'round'; c.strokeText(ws[i], -widths[i] / 2, 0); }
      c.shadowColor = 'transparent'; c.fillStyle = active ? (hiPill ? pillText : hi) : (wordColor ? wordColor(w) : color); c.fillText(ws[i], -widths[i] / 2, 0);
      c.restore(); x += widths[i] + gap; });
    c.restore();
  }
  // Letter-by-letter write-on of a word between t0 and t1. Works for Devanagari by grapheme clusters.
  function writeOn(c, text, x, y, t, t0, t1, opts = {}) {
    const { font = '64px serif', color = '#fff', align = 'left' } = opts; c.save(); c.font = font; c.fillStyle = color; c.textAlign = 'left'; c.textBaseline = 'alphabetic';
    const seg = [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(text)].map((s) => s.segment);
    const n = Math.ceil(seg.length * prog(t, t0, t1)), full = c.measureText(text).width; let x0 = align === 'center' ? x - full / 2 : align === 'right' ? x - full : x;
    c.fillText(seg.slice(0, n).join(''), x0, y); c.restore(); return full;
  }
  // Instagram 9:16 safe zone: keep text out of the top 250 px and bottom 420 px
  const SAFE = { top: 250, bottom: 420, side: 60 };
  const inSafe = (y) => H === 1920 ? clamp(y, SAFE.top, H - SAFE.bottom) : y;

  // ---------- scene registration + frame hook ----------
  let scene = null;
  const k = { W, H, FPS, ctx, canvas, qs, clamp, lerp, prog, smooth, ease, rng, hash, noise1, boil, words, lineAt, wordAt, chunks, chunkAt, beatPulse, lastBefore, frameVal,
    img, json, font, fontsource, clip, rr, cover, shake, speedLines, halftone, burst, bubble, wobble, strokePath, pointAt, grain, vignette, blink, mouth, caption, writeOn, SAFE, inSafe,
    vertical: H > W, data: {} };
  window.Kit = { ...k, scene(def) { scene = def; (async () => {
      const dataList = (qs.get('data') || '').split(',').filter(Boolean);
      for (const d of dataList) { const name = d.split('/').pop().replace(/\.json$/, ''); k.data[name] = await json(d); }
      if (def.setup) await def.setup(k); await document.fonts.ready; window.__duration = def.duration ? def.duration(k) : (k.data.align ? k.data.align.duration : 10); window.__ready = true;
    })().catch((e) => { window.__error = String(e && e.stack || e); }); } };
  window.__frame = async (t, fmt = 'jpeg') => {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none'; ctx.clearRect(0, 0, W, H);
    ctx.save(); await scene.draw(ctx, t, k); ctx.restore();
    return canvas.toDataURL(fmt === 'png' ? 'image/png' : 'image/jpeg', 0.94);
  };
})();
