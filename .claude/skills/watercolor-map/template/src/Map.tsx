import React, { useEffect, useMemo, useState } from 'react';
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig, delayRender, continueRender } from 'remotion';
import { geoNaturalEarth1, geoPath, geoInterpolate, geoDistance, geoContains } from 'd3-geo';
import { feature } from 'topojson-client';
import caveatUrl from '@fontsource/caveat/files/caveat-latin-700-normal.woff2';
// world-atlas: real country shapes (Natural Earth 1:50m) as TopoJSON
import world from 'world-atlas/countries-50m.json';
import route from './route.json';

// Animate ONLY with useCurrentFrame() + interpolate()/spring(). No CSS animations or transitions.
// Load Caveat straight from the npm package (no font CDN). One shared promise per tab; each mount holds
// the frame with delayRender until it resolves (Remotion's documented font pattern).
let fontPromise: Promise<void> | null = null;
const loadCaveat = () => (fontPromise ??= new FontFace('Caveat', `url(${caveatUrl})`, { weight: '700' }).load()
  .then((f) => { document.fonts.add(f); }).catch((e) => console.error('font failed', e)));
const useCaveat = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => { loadCaveat().then(() => continueRender(handle)); }, [handle]);
};

const PAPER = '#f4ecdc';
const PALETTE = ['#9cc5b0', '#e7b97a', '#c9a3c7', '#a7c0de', '#e3a49a', '#bcc98a', '#d8c27a', '#9fb7a9'];
const rnd = (s: number) => { const x = Math.sin(s * 127.1) * 43758.5453; return x - Math.floor(x); };

export const MapVideo: React.FC = () => {
  useCaveat();
  const frame = useCurrentFrame();
  const { width: W, height: H, durationInFrames: D, fps } = useVideoConfig();
  const A: [number, number] = [route.from.lon, route.from.lat];
  const B: [number, number] = [route.to.lon, route.to.lat];

  const { countries, proj, path, arc, km, destId } = useMemo(() => {
    const countries = (feature(world as any, (world as any).objects.countries) as any).features as any[];
    const interp = geoInterpolate(A, B);
    const arc = Array.from({ length: 201 }, (_, i) => interp(i / 200));
    // centre the projection on the route so a great circle never wraps across the map's edge
    const mid = interp(0.5);
    const proj = geoNaturalEarth1().rotate([-mid[0], 0]).fitExtent([[W * 0.12, H * 0.14], [W * 0.88, H * 0.86]], { type: 'MultiPoint', coordinates: arc } as any);
    const path = geoPath(proj);
    const km = geoDistance(A, B) * 6371;
    const dest = countries.find((c) => geoContains(c, B));
    return { countries, proj, path, arc, km, destId: dest ? dest.id : null };
  }, [W, H]);

  // ---- timeline (fractions of the whole video) ----
  const f = (x: number) => Math.round(x * D);
  const pinA = spring({ frame: frame - f(0.06), fps, config: { damping: 9, stiffness: 120 } });
  const fly = interpolate(frame, [f(0.16), f(0.72)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const wash = interpolate(frame, [f(0.74), f(0.86)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  const pinB = spring({ frame: frame - f(0.73), fps, config: { damping: 9, stiffness: 120 } });
  const title = interpolate(frame, [f(0.87), f(0.93)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const mapIn = interpolate(frame, [0, f(0.06)], [0, 1], { extrapolateRight: 'clamp' });

  // ---- plane position + heading on the real great circle ----
  const idx = Math.min(199, Math.floor(fly * 200));
  const pPos = proj(arc[idx]) as [number, number];
  const pNext = proj(arc[Math.min(200, idx + 1)]) as [number, number];
  const heading = (Math.atan2(pNext[1] - pPos[1], pNext[0] - pPos[0]) * 180) / Math.PI;
  const trail = path({ type: 'LineString', coordinates: arc.slice(0, idx + 1) } as any) || '';
  const pa = proj(A) as [number, number], pb = proj(B) as [number, number];

  // ---- camera: close on the start city, out to follow the plane, into the destination ----
  const zoom = interpolate(frame, [0, f(0.14), f(0.3), f(0.62), f(0.8), D], [3.2, 3.2, 1.0, 1.0, 2.6, 2.4], { easing: Easing.inOut(Easing.cubic), extrapolateRight: 'clamp' });
  const focusMix = interpolate(frame, [f(0.12), f(0.3), f(0.62), f(0.8)], [0, 0.5, 0.5, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const mid = [W / 2, H / 2]; // fitExtent centres the whole route, so zoom 1 at the centre shows all of it
  const cx = focusMix < 0.5 ? interpolate(focusMix, [0, 0.5], [pa[0], mid[0]]) : interpolate(focusMix, [0.5, 1], [mid[0], pb[0]]);
  const cy = focusMix < 0.5 ? interpolate(focusMix, [0, 0.5], [pa[1], mid[1]]) : interpolate(focusMix, [0.5, 1], [mid[1], pb[1]]);
  const cam = `translate(${W / 2} ${H / 2}) scale(${zoom}) translate(${-cx} ${-cy})`;
  const kmNow = Math.round(km * fly).toLocaleString('en-IN');
  const label = { fontFamily: 'Caveat', fontWeight: 700, fill: '#3b2f2a' } as const;

  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <svg width={W} height={H}>
        <defs>
          {/* watercolor wash: uneven edges (turbulence + displacement) + darker pooled edge */}
          <filter id="wc" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="4" result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale="14" xChannelSelector="R" yChannelSelector="G" result="d" />
            <feMorphology in="d" operator="erode" radius="2.5" result="er" />
            <feComposite in="d" in2="er" operator="out" result="edge" />
            <feColorMatrix in="edge" type="matrix" values="0.6 0 0 0 0  0 0.55 0 0 0  0 0 0.6 0 0  0 0 0 0.9 0" result="dark" />
            <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="9" result="blotRaw" />
            <feColorMatrix in="blotRaw" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0.5 0 0 -0.35" result="blot" />
            <feComposite in="blot" in2="d" operator="in" result="blotIn" />
            <feComposite in="d" in2="blotIn" operator="out" result="mottled" />
            <feMerge><feMergeNode in="mottled" /><feMergeNode in="dark" /></feMerge>
          </filter>
          <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="2" />
            <feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.25  0.12 0 0 0 0" /></filter>
        </defs>
        <g transform={cam} opacity={mapIn}>
          {/* one filter pass over all countries (fast); the destination gets its own wash on top */}
          <g filter="url(#wc)">
            {countries.map((c, i) => c.id === destId ? null : (
              <path key={i} d={path(c) || ''} fill={PALETTE[Math.floor(rnd(i + 1) * PALETTE.length)]} fillOpacity={0.5} stroke="#6b5a4e" strokeOpacity={0.25} strokeWidth={1.2} />
            ))}
          </g>
          {countries.filter((c) => c.id === destId).map((c, i) => (
            <path key={`d${i}`} d={path(c) || ''} fill="#d9534f" fillOpacity={0.3 + 0.55 * wash} filter="url(#wc)" stroke="#7a1e14" strokeOpacity={0.3} strokeWidth={1.2} />
          ))}
          <path d={trail} fill="none" stroke="#c0392b" strokeWidth={3 / zoom} strokeDasharray={`${10 / zoom} ${7 / zoom}`} strokeLinecap="round" />
          {/* pins */}
          {[{ p: pa, s: pinA, name: route.from.name }, { p: pb, s: frame >= f(0.73) ? pinB : 0, name: route.to.name }].map((q, i) => (
            <g key={i} transform={`translate(${q.p[0]} ${q.p[1] - (1 - Math.min(1, q.s)) * 60 / zoom}) scale(${Math.max(0, q.s) / zoom})`}>
              <path d="M0 0 C -14 -20 -16 -34 0 -44 C 16 -34 14 -20 0 0 Z" fill="#c0392b" stroke="#7a1e14" strokeWidth={2} />
              <circle cy={-30} r={6} fill="#fff" />
              <text x={18} y={-30} fontSize={44} style={label}>{q.name}</text>
            </g>
          ))}
          {fly > 0 && fly < 1 && (
            <g transform={`translate(${pPos[0]} ${pPos[1]}) rotate(${heading}) scale(${1 / zoom})`}>
              <path d="M22 0 L-8 -6 L-14 -22 L-20 -22 L-16 -5 L-26 -4 L-30 -11 L-34 -11 L-32 0 L-34 11 L-30 11 L-26 4 L-16 5 L-20 22 L-14 22 L-8 6 Z" fill="#2c3e50" />
            </g>
          )}
        </g>
        <rect width={W} height={H} filter="url(#grain)" style={{ mixBlendMode: 'multiply' }} />
        {/* running km counter */}
        <text x={W * 0.06} y={H - H * 0.07} fontSize={Math.round(H * 0.06)} style={label} opacity={fly > 0 ? 1 : 0}>{kmNow} km</text>
      </svg>
      {title > 0 && (
        <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', background: `rgba(244,236,220,${0.85 * title})` }}>
          <div style={{ fontFamily: 'Caveat', fontWeight: 700, fontSize: H * 0.11, color: '#3b2f2a', opacity: title, transform: `translateY(${(1 - title) * 30}px)` }}>{route.title}</div>
          <div style={{ fontFamily: 'Caveat', fontSize: H * 0.05, color: '#7a5f50', opacity: title }}>{Math.round(km).toLocaleString('en-IN')} km</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
