#!/usr/bin/env node
// Render a canvas scene page frame by frame in headless Chrome and encode with ffmpeg.
//
//   node render.cjs --page work/x/scene.html --out work/x/out/video.mp4 --w 1080 --h 1920 --fps 30 \
//        --data work/x/align.json,work/x/beats.json --audio work/x/voice.mp3 [--from 0 --to 12] [--workers 4]
//   node render.cjs --page ... --stills 1.5,4,9.2 --stills-dir work/x/stills     (PNG stills for contact sheets)
//
// The page is served over http from the project root, with /kit -> video-core/lib and /fonts -> video-core/fonts.
// It refuses to overwrite an existing --out unless --force is given (ask the user first).
const http = require('http'), fs = require('fs'), path = require('path'), { spawn, spawnSync } = require('child_process');
const { chromium } = require('playwright');

const args = {}; const av = process.argv.slice(2);
for (let i = 0; i < av.length; i++) if (av[i].startsWith('--')) { const k = av[i].slice(2); const v = av[i + 1] && !av[i + 1].startsWith('--') ? av[++i] : true; args[k] = v; }
const ROOT = path.resolve(args.root || process.cwd()), CORE = path.resolve(__dirname, '..');
const W = +args.w || 1920, H = +args.h || 1080, FPS = +args.fps || 30, workers = +args.workers || Math.max(1, Math.min(4, require('os').cpus().length - 1));
if (!args.page) { console.error('need --page'); process.exit(2); }

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf', '.gif': 'image/gif', '.mp4': 'video/mp4', '.webm': 'video/webm' };
function serve() {
  return new Promise((res) => { const srv = http.createServer((req, rsp) => {
      let u = decodeURIComponent(req.url.split('?')[0]), file;
      if (u.startsWith('/kit/')) file = path.join(CORE, 'lib', u.slice(5));
      else if (u.startsWith('/fonts/')) file = path.join(CORE, 'fonts', u.slice(7));
      else file = path.join(ROOT, u);
      if (!file.startsWith(ROOT) && !file.startsWith(CORE)) { rsp.writeHead(403); return rsp.end(); }
      fs.readFile(file, (e, buf) => { if (e) { rsp.writeHead(404); return rsp.end('not found ' + u); }
        rsp.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' }); rsp.end(buf); });
    }); srv.listen(0, '127.0.0.1', () => res(srv)); });
}
const rel = (p) => '/' + path.relative(ROOT, path.resolve(p)).split(path.sep).join('/');

async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: Math.min(W, 1920), height: Math.min(H, 1920) }, deviceScaleFactor: 1 });
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
  page.on('pageerror', (e) => console.error('[page error]', e.message));
  const data = (args.data || '').split(',').filter(Boolean).map(rel).join(',');
  await page.goto(`http://127.0.0.1:${port}${rel(args.page)}?w=${W}&h=${H}&fps=${FPS}&data=${encodeURIComponent(data)}`);
  await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 180000 });
  const err = await page.evaluate('window.__error'); if (err) throw new Error('scene setup failed: ' + err);
  return page;
}
const grab = async (page, t, fmt) => Buffer.from((await page.evaluate(([t, f]) => window.__frame(t, f), [t, fmt])).split(',')[1], 'base64');

(async () => {
  const srv = await serve(), port = srv.address().port;
  const browser = await chromium.launch({ args: ['--disable-web-security', '--font-render-hinting=none', '--disable-gpu-vsync'] });
  try {
    if (args.stills) { // ---- stills mode ----
      const dir = path.resolve(args['stills-dir'] || 'stills'); fs.mkdirSync(dir, { recursive: true }); const page = await openPage(browser, port);
      for (const ts of String(args.stills).split(',')) { const t = +ts, f = path.join(dir, `still_${t.toFixed(2).padStart(7, '0')}.png`);
        fs.writeFileSync(f, await grab(page, t, 'png')); console.log(f); }
      return;
    }
    if (!args.out) throw new Error('need --out (or --stills)');
    const out = path.resolve(args.out);
    if (fs.existsSync(out) && !args.force) { console.error(`REFUSING: ${out} exists. Ask the user, then re-run with --force.`); process.exit(3); }
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const probe = await openPage(browser, port); const dur = await probe.evaluate('window.__duration'); await probe.close();
    const t0 = +(args.from || 0), t1 = +(args.to || dur), N = Math.round((t1 - t0) * FPS);
    console.log(`rendering ${N} frames ${W}x${H}@${FPS} (${t0.toFixed(2)}-${t1.toFixed(2)}s) with ${workers} workers`);
    const tmp = fs.mkdtempSync(path.join(path.dirname(out), '.segs-')); const per = Math.ceil(N / workers); let done = 0; const tStart = Date.now();
    await Promise.all([...Array(workers).keys()].map(async (wi) => {
      const a = wi * per, b = Math.min(N, a + per); if (a >= b) return;
      const page = await openPage(browser, port), seg = path.join(tmp, `seg_${String(wi).padStart(3, '0')}.mp4`);
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', args.preset || 'medium', '-crf', String(args.crf || 16), '-pix_fmt', 'yuv420p', '-r', String(FPS), seg], { stdio: ['pipe', 'inherit', 'inherit'] });
      for (let f = a; f < b; f++) { const buf = await grab(page, t0 + f / FPS, 'jpeg'); if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
        if (++done % 60 === 0) { const el = (Date.now() - tStart) / 1000; console.log(`  ${done}/${N} frames, ${(done / el).toFixed(1)} fps, eta ${((N - done) / (done / el)).toFixed(0)}s`); } }
      ff.stdin.end(); await new Promise((r) => ff.on('close', r)); await page.close();
    }));
    const list = path.join(tmp, 'list.txt'); fs.writeFileSync(list, fs.readdirSync(tmp).filter((f) => f.endsWith('.mp4')).sort().map((f) => `file '${path.join(tmp, f)}'`).join('\n'));
    const ffArgs = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list];
    if (args.audio) ffArgs.push('-ss', String(t0), '-t', String(t1 - t0), '-i', path.resolve(args.audio), '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', args.abr || '256k', '-shortest');
    ffArgs.push('-c:v', 'copy', '-movflags', '+faststart', out);
    const r = spawnSync('ffmpeg', ffArgs, { stdio: 'inherit' }); if (r.status) throw new Error('ffmpeg concat failed');
    fs.rmSync(tmp, { recursive: true, force: true }); console.log('wrote', out);
  } finally { await browser.close(); srv.close(); }
})().catch((e) => { console.error(e.message || e); process.exit(1); });
