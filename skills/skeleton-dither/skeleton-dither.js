/**
 * skeleton-dither.js — ASCII dither skeleton + glyph-grid reveal. Zero dependencies.
 * Clean reimplementation inspired by ascii-reveal by Quan Hoang (MIT):
 * https://github.com/quanhoangindex/ascii-reveal
 *
 *   import { skeletonHTML, createReveal } from './skeleton-dither.js';
 *   slot.innerHTML = skeletonHTML({ lines: 3 });          // 1. instant CSS-only skeleton
 *   slot.innerHTML = realMarkup;                          // 2. data arrived
 *   await createReveal(slot, { preset: 'decode' }).reveal(); // 3. decode it in
 */

/* ---------- utils ---------- */
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
const easeInOut = (x) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
/** Deterministic hash in [0,1): same inputs → same glyph, so SSR matches and flicker is stable per tick. */
export function hash(a, b, c) {
  let h = Math.imul(a | 0, 0x27d4eb2d) ^ Math.imul(((b | 0) + 0x9e3779b9) | 0, 0x85ebca6b) ^ Math.imul(((c | 0) + 0x632be5ab) | 0, 0xc2b2ae35);
  h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d); h ^= h >>> 12; h = Math.imul(h, 0x297a2d39); h ^= h >>> 15;
  return (h >>> 0) / 4294967296;
}
const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const DPR = () => Math.min(devicePixelRatio || 1, 2);
const MONO = '"Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace';

/* ---------- 1. Skeleton (pure HTML + CSS, no JS at runtime) ---------- */
export const SKELETON_VARIANTS = {
  dither:   { base: '░░░░▒', wave: '▒▓▓█▓▒', gap: 0, bias: 0.9 },
  scan:     { base: '··:·:-', wave: '+=*#%@&$', gap: 0.08, bias: 1.6 },
  braille:  { base: '⠢⠔⠑⠊⠡⠌⠒⠤⠕⠪', wave: '⣿⣷⣯⣟⡿⢿⣻⣽⣾⣶', gap: 0.02, bias: 1 },
  terminal: { base: '01', wave: '01', gap: 0.12, bias: 1 },
};
const MASK = 'linear-gradient(90deg,transparent,#000 45%,#000 55%,transparent)';
export const SKELETON_CSS = `
.sd{display:block;font-family:var(--sd-font,${MONO});color:var(--sd-color,currentColor);user-select:none;pointer-events:none;--b:.3;--w:.9;--band:45%;--speed:1.8s}
.sd-line,.sd-block{position:relative;display:block;overflow:hidden;white-space:pre;line-height:1.3;contain:inline-size}
.sd-line+.sd-line{margin-top:.55em}
.sd-block{line-height:1;border-radius:var(--sd-radius,8px);background:color-mix(in srgb,currentColor 6%,transparent)}
.sd-base{display:block;opacity:var(--b)}
.sd-wave{position:absolute;inset:0;display:block;opacity:var(--w);color:var(--sd-wave-color,currentColor);
 -webkit-mask:${MASK} -120% 0/var(--band) 100% no-repeat;mask:${MASK} -120% 0/var(--band) 100% no-repeat;
 animation:sd-sweep var(--speed) cubic-bezier(.45,.05,.55,.95) infinite var(--d,0s),sd-a .24s steps(1,end) infinite}
.sd-wave+.sd-wave{animation-name:sd-sweep,sd-b}
@keyframes sd-sweep{to{-webkit-mask-position:220% 0;mask-position:220% 0}}
@keyframes sd-a{50%{visibility:hidden}}
@keyframes sd-b{0%{visibility:hidden}50%{visibility:visible}}
.sd-dither{--b:.22;--w:.75;--band:55%}.sd-dither .sd-line{line-height:1;letter-spacing:-.02em}
.sd-braille{--b:.35;--w:1;--band:40%}.sd-scan{--b:.28;--w:.95;--band:38%}
.sd-terminal{--b:.16;--w:1;--band:35%;--speed:1.5s;--sd-wave-color:var(--sd-accent,currentColor)}
@media (prefers-reduced-motion:reduce){.sd-wave{display:none}}`;

export function glyphRow(seed, len, ramp, gap, bias) {
  let s = '';
  for (let i = 0; i < len; i++) s += hash(i, seed, 17) < gap ? ' ' : ramp[Math.floor(Math.pow(hash(i, seed, 29), bias) * ramp.length)];
  return s;
}
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const px = (v) => (typeof v === 'number' ? v + 'px' : v);

/**
 * @param {{variant?:keyof SKELETON_VARIANTS, lines?:number, widths?:(string|number)[], rows?:number,
 *          width?:string|number, height?:string|number, circle?:boolean, seed?:number, className?:string}} o
 * `lines` → paragraph bars; `rows` → block (image / avatar). Deterministic per seed.
 */
export function skeletonHTML(o = {}) {
  const { variant = 'dither', lines = 3, widths = ['100%', '94%', '72%', '88%', '60%'], rows, width, height, circle, seed = 1, className = '' } = o;
  const v = SKELETON_VARIANTS[variant] || SKELETON_VARIANTS.dither;
  const layers = (s, n, len) => [v.base, v.wave, v.wave].map((r, k) =>
    Array.from({ length: n }, (_, i) => glyphRow(s + i + k * 300, len, r, v.gap, v.bias)).join('\n'));
  const group = (i, cls, style, n) => {
    const [b, w1, w2] = layers(seed * 97 + i * 13, n, rows ? 120 : 160);
    // 0.09s stagger per line → the sweep reads as one diagonal band
    return `<span class="${cls}" style="${style}--d:${(i * 0.09).toFixed(2)}s"><span class="sd-base">${esc(b)}</span><span class="sd-wave">${esc(w1)}</span><span class="sd-wave">${esc(w2)}</span></span>`;
  };
  const body = rows
    ? group(0, 'sd-block', `${width != null ? `width:${px(width)};` : ''}${height != null ? `height:${px(height)};` : ''}${circle ? '--sd-radius:50%;' : ''}`, rows)
    : Array.from({ length: lines }, (_, i) => group(i, 'sd-line', `width:${px(widths[i % widths.length])};`, 1)).join('');
  return `<span class="sd sd-${variant} ${className}" data-sd-skeleton aria-hidden="true">${body}</span>`;
}
export function injectSkeletonCSS() {
  if (document.querySelector('style[data-sd]')) return;
  const s = document.createElement('style');
  s.setAttribute('data-sd', '');
  s.textContent = SKELETON_CSS + `
[data-sd-t]{-webkit-text-fill-color:transparent!important;text-shadow:none!important}
[data-sd-m],[data-sd-f]{opacity:var(--sd-o,0)!important}
.sd-overlay{position:absolute;inset:0;pointer-events:none;z-index:2}.sd-overlay>canvas{position:absolute;left:0;top:0}`;
  document.head.appendChild(s);
}

/* ---------- 2. Reveal (canvas overlay) ---------- */
export const PRESETS = {
  decode:    { ramp: ' .:-=+*#%@', scramble: 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*+=?/', mode: 'ramp', color: 'mono', cells: [24, 16, 11, 8, 6], tick: 60 },
  dither:    { ramp: ' ░▒▓█', scramble: '░▒▓█', mode: 'ramp', color: 'source', cells: [20, 14, 10, 7, 5], tick: 85 },
  terminal:  { ramp: ' .-:=+*#', scramble: '01<>/\\{}[]|_=+-;:', mode: 'random', color: 'mono', cells: [22, 15, 10, 7, 6], tick: 40 },
  blueprint: { ramp: ' ·-+=x#', scramble: '+-/\\|x·', mode: 'random', color: 'accent', cells: [26, 18, 13, 9, 7], tick: 95 },
};
export const TIMING = {
  // vel px/ms, maxWave ms, char [base, random] ms, media / fade ms
  fast:      { vel: 3.2, maxWave: 220, spread: (n) => Math.min(200, 40 + n * 4), char: [90, 110], media: 450, fade: 220 },
  cinematic: { vel: 1.15, maxWave: Infinity, spread: (n) => Math.min(720, 90 + n * 13), char: [200, 240], media: 1150, fade: 420 },
};

function rgbOf(c) { const m = c.match(/[\d.]+/g); return m ? m.slice(0, 3).map(Number) : [255, 255, 255]; }
function bgOf(el) {
  for (let n = el.parentElement; n; n = n.parentElement) {
    const c = getComputedStyle(n).backgroundColor, m = c.match(/[\d.]+/g);
    if (m && (m[3] === undefined || +m[3] >= 0.5)) return m.slice(0, 3).map(Number);
  }
  return [255, 255, 255];
}

function textTarget(node, ctx, env, seed) {
  const el = node.parentElement, cs = getComputedStyle(el), str = node.nodeValue;
  const r = document.createRange(), seg = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
  const chars = [];
  for (const { segment, index } of seg.segment(str)) {
    if (/^\s+$/.test(segment)) continue;
    r.setStart(node, index); r.setEnd(node, index + segment.length);
    const b = r.getBoundingClientRect();
    if (b.width || b.height) chars.push({ c: cs.textTransform === 'uppercase' ? segment.toUpperCase() : segment, x: b.left - env.ox, y: b.top - env.oy, w: b.width, h: b.height });
  }
  if (!chars.length) return null;
  r.selectNodeContents(node);
  const box = r.getBoundingClientRect(), n = chars.length, P = env.preset, T = env.timing, sc = env.scale;
  const spread = T.spread(n) * sc;
  let dur = 1;
  chars.forEach((ch, k) => {
    ch.s0 = (k / n) * spread * 0.72 + hash(k, seed, 1) * spread * 0.28;   // mostly left→right, a bit of noise
    ch.s1 = ch.s0 + (T.char[0] + hash(k, seed, 2) * T.char[1]) * sc;       // 90–200 ms scramble per char
    ch.ph = hash(k, seed, 3) * 1000;
    dur = Math.max(dur, ch.s1);
  });
  const digits = /^[\d.,%:+\-\s€$£¥]+$/.test(str.trim());
  const set = digits ? '0123456789' : P.scramble;
  const color = cs.color, realFont = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const glyphFont = `400 ${cs.fontSize} ${env.font}`;
  ctx.font = realFont;
  const m = ctx.measureText('Hg'), asc = m.fontBoundingBoxAscent, desc = m.fontBoundingBoxDescent;
  const baseline = (chars[0].h - (asc + desc)) / 2 + asc;
  return {
    hold: el, attr: 'data-sd-t', dur, cx: box.left + box.width / 2, cy: box.top + box.height / 2,
    draw(lt, paint) {
      if (!paint) return;
      ctx.font = glyphFont; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = color; ctx.globalAlpha = 0.5;
      for (let k = 0; k < n; k++) {
        const ch = chars[k];
        if (lt < ch.s0 || lt >= ch.s1) continue;
        const q = (lt - ch.s0) / (ch.s1 - ch.s0), t = Math.floor((lt + ch.ph) / P.tick);
        let g;
        if (P.mode === 'ramp' && !digits && q < 0.7) {          // condense light → dense through the ramp
          let i = 1 + Math.floor((q / 0.7) * (P.ramp.length - 1));
          if (hash(k, t, 5) < 0.35) i += hash(k, t, 6) < 0.5 ? -1 : 1;
          g = P.ramp[clamp(i, 1, P.ramp.length - 1)];
        } else g = set[Math.floor(hash(k, t, 7) * set.length)]; // then random scramble
        ctx.fillText(g, ch.x + ch.w / 2, ch.y + ch.h * 0.48);
      }
      ctx.font = realFont; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.globalAlpha = 1;
      for (const ch of chars) if (lt >= ch.s1) ctx.fillText(ch.c, ch.x, ch.y + baseline); // landed, in the real font
    },
  };
}

function mediaTarget(el, ctx, env) {
  const rc = el.getBoundingClientRect();
  if (rc.width < 2 || rc.height < 2) return null;
  const d = env.dpr, W = Math.round(rc.width * d), H = Math.round(rc.height * d), P = env.preset;
  const dur = env.timing.media * env.scale, cs = getComputedStyle(el);
  const cellScale = clamp(Math.min(rc.width, rc.height) / 230, 0.4, 1);
  const cells = P.cells.map((c) => Math.max(3, c * cellScale) * d);           // coarse → fine
  const fixed = P.color === 'mono' ? cs.color : P.color === 'accent' ? env.accent || cs.color : null;
  const bg = bgOf(el), bgL = (0.2126 * bg[0] + 0.7152 * bg[1] + 0.0722 * bg[2]) / 255;
  const ox = (env.origin.x - rc.left) * d, oy = (env.origin.y - rc.top) * d;
  const maxD = Math.max(Math.hypot(ox, oy), Math.hypot(W - ox, oy), Math.hypot(ox, H - oy), Math.hypot(W - ox, H - oy)) || 1;
  const radius = Math.min((parseFloat(cs.borderTopLeftRadius) || 0) * (cs.borderTopLeftRadius.endsWith('%') ? Math.min(W, H) / 100 : d), Math.min(W, H) / 2);
  let data = null;
  try {
    const off = new OffscreenCanvas(W, H), o = off.getContext('2d', { willReadFrequently: true });
    const iw = el.naturalWidth || el.videoWidth || el.width, ih = el.naturalHeight || el.videoHeight || el.height;
    const s = cs.objectFit === 'cover' ? Math.max(W / iw, H / ih) : cs.objectFit === 'contain' ? Math.min(W / iw, H / ih) : 0;
    s ? o.drawImage(el, (W - iw * s) / 2, (H - ih * s) / 2, iw * s, ih * s) : o.drawImage(el, 0, 0, W, H);
    data = o.getImageData(0, 0, W, H).data;
  } catch { data = null; } // cross-origin without CORS → neutral noise texture
  const sample = (x, y) => {
    if (!data) return [0.22 + 0.5 * hash((x / (8 * d)) | 0, (y / (8 * d)) | 0, 41), 128, 128, 128];
    const i = (clamp(y | 0, 0, H - 1) * W + clamp(x | 0, 0, W - 1)) * 4, a = data[i + 3] / 255;
    const r = data[i] * a + bg[0] * (1 - a), g = data[i + 1] * a + bg[1] * (1 - a), b = data[i + 2] * a + bg[2] * (1 - a);
    const L = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
    return [Math.abs(L - bgL) / Math.max(bgL, 1 - bgL), r | 0, g | 0, b | 0]; // "ink" = contrast vs backdrop
  };
  const steps = [];
  const build = (si) => {
    const ch = cells[si], cw = ch * 0.62, out = [];
    for (let y = ch / 2; y < H + ch / 2; y += ch)
      for (let x = cw / 2; x < W + cw / 2; x += cw) {
        let best = [-1];
        for (const [dx, dy] of [[0, 0], [-1, -1], [1, -1], [-1, 1], [1, 1]]) { const s = sample(x + (dx * cw) / 3, y + (dy * ch) / 3); if (s[0] > best[0]) best = s; }
        if (best[0] < 0.04) continue;
        // gate: 50% noise + 50% distance from wave origin → organic radial fill
        const gate = 0.5 * hash((x / (6 * d)) | 0, (y / (6 * d)) | 0, 11) + 0.5 * (Math.hypot(x - ox, y - oy) / maxD);
        out.push({ x, y, ink: best[0], gate, fill: `rgb(${best[1]},${best[2]},${best[3]})` });
      }
    return { ch, cells: out };
  };
  const setO = (v) => el.style.setProperty('--sd-o', v.toFixed(3));
  return {
    hold: el, attr: 'data-sd-m', dur, cx: rc.left + rc.width / 2, cy: rc.top + rc.height / 2,
    draw(lt, paint) {
      const q = lt / dur;
      setO(q < 0.68 ? 0 : easeInOut((q - 0.68) / 0.32));                  // real pixels cross-fade in at the end
      if (q <= 0 || q >= 1 || !paint) return;
      const si = Math.min(cells.length - 1, Math.floor((q / 0.8) * cells.length)); // cell size steps coarse → fine
      const st = (steps[si] ||= build(si));
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, (rc.left - env.ox) * d, (rc.top - env.oy) * d);
      ctx.beginPath(); radius > 0 ? ctx.roundRect(0, 0, W, H, radius) : ctx.rect(0, 0, W, H); ctx.clip();
      ctx.globalAlpha = q < 0.74 ? 1 : 1 - easeOut((q - 0.74) / 0.26);
      ctx.font = `${Math.round(st.ch * 1.02)}px ${env.font}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (fixed) ctx.fillStyle = fixed;
      const t = Math.floor(lt / P.tick), gate = q * 2.3, L = P.ramp.length;
      st.cells.forEach((c, i) => {
        if (c.gate > gate) return;
        let lv = c.ink;
        if (hash(i, t, 3) < 0.16) lv += (hash(i, t, 77) - 0.5) * 0.35;     // 16% of cells flicker each tick
        const idx = Math.round(clamp(lv * 1.15) * (L - 1));
        if (idx <= 0) return;
        if (!fixed) ctx.fillStyle = c.fill;
        ctx.fillText(P.ramp[idx], c.x, c.y);
      });
      ctx.restore();
    },
  };
}

function fadeTarget(el, env) {
  const rc = el.getBoundingClientRect(), dur = env.timing.fade * env.scale;
  return { hold: el, attr: 'data-sd-f', dur, cx: rc.left + rc.width / 2, cy: rc.top + rc.height / 2, draw(lt) { el.style.setProperty('--sd-o', easeOut(lt / dur).toFixed(3)); } };
}

/**
 * @param {HTMLElement} root
 * @param {{preset?:keyof PRESETS|object, duration?:'fast'|'cinematic', speed?:number,
 *          origin?:'center'|'top-left'|{x:number,y:number}, onDone?:()=>void}} opts
 */
export function createReveal(root, opts = {}) {
  injectSkeletonCSS();
  if (getComputedStyle(root).position === 'static') root.style.position = 'relative';
  let raf = 0, overlay = null;
  const cleanup = (targets) => {
    cancelAnimationFrame(raf);
    for (const t of targets) { t.hold.removeAttribute(t.attr); t.hold.style.removeProperty('--sd-o'); }
    overlay?.remove(); overlay = null;
    root.removeAttribute('aria-busy');
  };
  async function reveal() {
    root.setAttribute('aria-busy', 'true');
    if (reduced()) { // short fade, no glyphs
      await root.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 220, easing: 'ease-out' }).finished;
      root.removeAttribute('aria-busy'); return;
    }
    await document.fonts?.ready; // measure after fonts land, else glyph positions drift
    const imgs = [...root.querySelectorAll('img')];
    // Hide real content first so nothing flashes while images decode.
    imgs.forEach((i) => i.setAttribute('data-sd-m', ''));
    await Promise.all(imgs.map((i) => (i.complete && i.naturalWidth ? 0 : Promise.race([i.decode().catch(() => {}), new Promise((r) => setTimeout(r, 900))]))));
    const rr = root.getBoundingClientRect(), d = DPR(), rs = getComputedStyle(root);
    const o = opts.origin || 'center';
    overlay = document.createElement('div'); overlay.className = 'sd-overlay'; overlay.setAttribute('aria-hidden', 'true');
    const cv = document.createElement('canvas');
    cv.width = Math.round(rr.width * d); cv.height = Math.round(rr.height * d);
    cv.style.width = rr.width + 'px'; cv.style.height = rr.height + 'px';
    overlay.appendChild(cv); root.appendChild(overlay);
    const ctx = cv.getContext('2d');
    const env = {
      preset: typeof opts.preset === 'object' ? opts.preset : PRESETS[opts.preset || 'decode'],
      timing: TIMING[opts.duration || 'fast'], scale: 1 / Math.max(0.1, opts.speed || 1), dpr: d,
      ox: rr.left, oy: rr.top, font: rs.getPropertyValue('--sd-font').trim() || MONO,
      accent: rs.getPropertyValue('--sd-accent').trim() || null,
      origin: o === 'center' ? { x: rr.left + rr.width / 2, y: rr.top + rr.height / 2 } : o === 'top-left' ? { x: rr.left, y: rr.top } : o,
    };
    const targets = [];
    for (const el of root.querySelectorAll('[data-sd="fade"]')) targets.push(fadeTarget(el, env));
    for (const el of imgs) { const t = mediaTarget(el, ctx, env); t ? targets.push(t) : el.removeAttribute('data-sd-m'); }
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) => (n.nodeValue.trim() && !n.parentElement.closest('script,style,[data-sd-skeleton],[data-sd="skip"],.sd-overlay') ? 1 : 2),
    });
    ctx.setTransform(d, 0, 0, d, 0, 0);
    let k = 0, seed = (Math.random() * 1e6) | 0;
    while (walker.nextNode()) { const t = textTarget(walker.currentNode, ctx, env, seed + k++ * 977); if (t) targets.push(t); }
    const vel = env.timing.vel / env.scale;
    for (const t of targets) {
      t.offset = Math.min(Math.hypot(t.cx - env.origin.x, t.cy - env.origin.y) / vel, env.timing.maxWave * env.scale); // radial wave
      t.hold.setAttribute(t.attr, '');
    }
    return new Promise((resolve) => {
      const start = performance.now() + 16;
      let lastPaint = -1e9, slow = 0, last = 0;
      const tick = (now) => {
        if (last && now - last > 45 && ++slow >= 8) { cleanup(targets); opts.onDone?.(); return resolve(); } // watchdog
        last = now;
        const local = now - start, paint = now - lastPaint >= 30; // glyphs repaint ~30fps, opacities every frame
        if (paint) { lastPaint = now; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height); ctx.setTransform(d, 0, 0, d, 0, 0); }
        let done = true;
        for (const t of targets) {
          const lt = clamp(local - t.offset, 0, t.dur);
          if (local - t.offset < t.dur) done = false;
          t.draw(lt, paint);
        }
        if (done) { cleanup(targets); opts.onDone?.(); return resolve(); }
        raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    });
  }
  return { reveal, destroy: () => { cancelAnimationFrame(raf); overlay?.remove(); } };
}
