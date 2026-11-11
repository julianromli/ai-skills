// Editorial edit engine for raea. Copied into PROJECT/raea/ by prep.py; do not edit the copy, edit the data:
//   timeline.json  scenes, media, text layers (programme seconds)      style.json  the look
//   captions.json  word-timed captions (build_captions.py)              manifest.json  baked media (prep.py)
// Layers per frame: picture -> text behind the presenter -> presenter cutout (BiRefNet mask) -> grain -> front text
// -> captions. Media are graded and bloomed in prep.py; raea lays out, animates, composites and encodes.
// raea notes (0.1.0-canary.3): CSS url() needs an absolute file:// path (staticFile is for <Img>/<Video>); a CSS
// background doesn't repeat; an element with a CSS filter draws over later siblings, so shadows are baked PNGs.
import React from "react";
import { AbsoluteFill, Composition, Img, Sequence, Video, registerRoot, staticFile, useCurrentFrame } from "raea";
import T from "./timeline.json";
import ST from "./style.json";
import CAP from "./captions.json";
import M from "./manifest.json";

const TL: any = T, S: any = ST, MAN: any = M, CAPS: any = CAP;
// Output canvas (W x H) can differ from the source (SW x SH): e.g. a 9:16 version of a 16:9 talk.
const SW: number = TL.source.width, SH: number = TL.source.height, FPS: number = TL.source.fps;
const W: number = TL.output?.width ?? SW, H: number = TL.output?.height ?? SH;
const NFR: number = TL.source.frames;
// All sizes in timeline.json and style.json are px at style.ref_height (1440p) on the canvas's short side.
const K: number = Math.min(W, H) / (S.ref_height ?? 1440);
// Reframe track [[t, cx, cy, zoom], ...]: the source point (cx, cy) (0-1) sits at the canvas centre, zoom >= 1 on
// top of "cover". Written by make_format.py from face tracking; without it the crop is centred on the presenter.
const RF: number[][] = TL.reframe ?? [];
const PCX: number = TL.source.presenter_center_x ?? 0.5;
const TM = S.type_motion, SPL = S.split, CAPST = S.captions, GR = S.grain;
// "burn" (default): captions drawn into the picture; "srt": only the .srt file; "none": no captions at all
const CAPMODE: string = TL.captions ?? "burn";
const FILE = (n: string) => `file://${MAN.media_dir}/${n}`;
const rgb = (c: number[], a = 1) => `rgba(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)},${a})`;
const COL = { ink: rgb(S.colors.ink), cream: rgb(S.colors.cream), paper: rgb(S.colors.paper), oxide: rgb(S.colors.oxide) };

// CSS faces for the style's font keys. baseline = distance from the line box top to the baseline, in em
// (line-height 1.15), measured against the Python renderer.
const FACE: Record<string, { family: string; weight: number; style: string; baseline: number }> = {
  sans: { family: "Helvetica Neue", weight: 700, style: "normal", baseline: 0.93 },
  sans_medium: { family: "Helvetica Neue", weight: 500, style: "normal", baseline: 0.93 },
  sans_light: { family: "Helvetica Neue", weight: 300, style: "normal", baseline: 0.93 },
  serif: { family: "Didot", weight: 400, style: "normal", baseline: 0.93 },
  serif_it: { family: "Didot", weight: 400, style: "italic", baseline: 0.93 },
  mono: { family: "Menlo", weight: 400, style: "normal", baseline: 0.93 },
  ...(S.css_fonts ?? {}),
};

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const easeOut = (p: number) => 1 - (1 - p) ** 3;
const easeIn = (p: number) => p ** 3;
const easeIO = (p: number) => (p < 0.5 ? 4 * p ** 3 : 1 - (-2 * p + 2) ** 3 / 2);
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
const sceneAt = (t: number) => TL.scenes.find((s: any) => s.t0 <= t && t < s.t1) ?? TL.scenes[TL.scenes.length - 1];
const pick = (list: any[], t: number) => list.find((x) => x.t0 <= t && t < x.t1) ?? list[list.length - 1];

// cover a box with media of iw x ih, focus point at the box centre (clamped so no edge shows), extra zoom
function cover(iw: number, ih: number, bw: number, bh: number, fx: number, fy: number, z: number) {
  const s = Math.max(bw / iw, bh / ih) * z;
  const cx = Math.min(Math.max(fx * iw, bw / (2 * s)), iw - bw / (2 * s));
  const cy = Math.min(Math.max(fy * ih, bh / (2 * s)), ih - bh / (2 * s));
  return { position: "absolute" as const, width: iw * s, height: ih * s, left: bw / 2 - s * cx, top: bh / 2 - s * cy };
}

// ---------------------------------------------------------------- media in a box (image or graded clip)
function MediaBox({ id, w, h, fx, fy, z, from, srcT0 = 0 }: { id: string; w: number; h: number; fx: number; fy: number;
  z: number; from: number; srcT0?: number }) {
  const m = MAN.media[id];
  const style = cover(m.w, m.h, w, h, fx, fy, z);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: w, height: h, overflow: "hidden" }}>
      {m.kind === "video" ? (
        <Sequence from={Math.round(from * FPS)} layout="none">
          <Video src={staticFile(m.file)} startFrom={Math.round(srcT0 * FPS)} muted style={style} />
        </Sequence>
      ) : (
        <Img src={staticFile(m.file)} style={style} />
      )}
    </div>
  );
}

function reframeAt(t: number) {
  if (!RF.length) return [W / H > SW / SH + 0.01 ? 0.5 : (W / H < SW / SH - 0.01 ? PCX : 0.5), 0.5, 1];
  if (t <= RF[0][0]) return RF[0].slice(1);
  for (let i = 1; i < RF.length; i++) {
    if (t <= RF[i][0]) {
      const a = RF[i - 1], b = RF[i], p = (t - a[0]) / Math.max(b[0] - a[0], 1e-6);
      return [1, 2, 3].map((k) => lerp(a[k], b[k], p));
    }
  }
  return RF[RF.length - 1].slice(1);
}
// The source plate placed on the canvas by the reframe track; `mask` cuts it out with that frame's person mask
// (masks are in source geometry, so they move with the plate).
function Plate({ t, dx = 0, mask }: { t: number; dx?: number; mask?: string }) {
  const [cx, cy, z] = reframeAt(t);
  const s = Math.max(W / SW, H / SH) * z, pw = SW * s, ph = SH * s;
  const left = Math.min(0, Math.max(W - pw, W / 2 - cx * pw)), top = Math.min(0, Math.max(H - ph, H / 2 - cy * ph));
  return (
    <AbsoluteFill style={{ transform: `translateX(${dx}px)`, overflow: "hidden" }}>
      <div style={{ position: "absolute", left, top, width: pw, height: ph,
        ...(mask ? { maskImage: `url(${mask})`, maskMode: "luminance", maskSize: "100% 100%", maskRepeat: "no-repeat" } : {}) }}>
        <Video src={staticFile("source.mp4")} muted style={{ width: pw, height: ph }} />
      </div>
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------- grain: per-frame field, rolled and flipped
function rng(seed: number) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function Grain({ n, amp, x0 = 0, x1 = W, gain }: { n: number; amp: number; x0?: number; x1?: number; gain?: number }) {
  if (x1 - x0 < 1 || amp <= 0) return null;
  const r = rng(n * 7919 + 17);
  const k = Math.floor(r() * GR.bank), x = Math.floor(r() * W), y = Math.floor(r() * H);
  const fx = r() < 0.5 ? -1 : 1, fy = r() < 0.5 ? -1 : 1;
  const g = gain ?? GR.overlay_gain ?? 2.4;
  return (
    <AbsoluteFill style={{ clipPath: `inset(0 ${W - x1}px 0 ${x0}px)`, overflow: "hidden", mixBlendMode: "overlay",
      opacity: Math.min(1, (amp * g) / (GR.png_scale ?? 0.3)) }}>
      <AbsoluteFill style={{ transform: `scale(${fx}, ${fy})` }}>
        {[[x - W, y - H], [x, y - H], [x - W, y], [x, y]].map(([l, tp], i) => (
          <Img key={i} src={staticFile(`grain_${k}.png`)} style={{ position: "absolute", left: l, top: tp, width: W, height: H }} />
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------- kinetic type
function tokens(spec: any) {
  const out: { w: string; it: boolean; t0: number }[] = [];
  let i = 0;
  String(spec.text).split("*").forEach((part, pi) => {
    for (const w of part.split(" ")) {
      if (!w) continue;
      if (!/[\p{L}\p{N}]/u.test(w)) { out.push({ w, it: pi % 2 === 1, t0: out.length ? out[out.length - 1].t0 : spec.t0 }); continue; }
      out.push({ w, it: pi % 2 === 1, t0: spec.words?.[i] ?? spec.t0 }); i++;
    }
  });
  return out;
}
function Kinetic({ s, t, dx = 0, pw = W }: { s: any; t: number; dx?: number; pw?: number }) {
  if (t < s.t0 || t >= s.t1) return null;
  const size: number = s.size * K, base = FACE[s.font] ?? FACE.sans;
  const q = (s.exit ?? "soft") === "soft" ? easeIn(clamp01((t - (s.t1 - TM.exit)) / TM.exit)) : 0;
  const top = s.y * H - TM.drift_px_s * K * (t - s.t0) - q * 0.15 * size - base.baseline * size;
  const anc = String(s.anchor ?? "ls")[0];
  const shift = anc === "m" ? "-50%" : anc === "r" ? "-100%" : "0%";
  const color = s.color === "cream" ? COL.cream : COL.ink;
  const toks = tokens(s);
  const stepT = (lt: number) => (s.step ? Math.floor(lt * TM.step_fps) / TM.step_fps : lt);
  const ce = easeOut(clamp01(stepT(t - toks[0].t0) / TM.enter));
  const cardK = (String(s.id).length * 31) % (MAN.cards ?? 6);
  return (
    <div style={{ position: "absolute", left: dx + s.x * pw, top, transform: `translateX(${shift})`, whiteSpace: "nowrap" }}>
      {s.card && t >= toks[0].t0 ? (
        <div style={{ position: "absolute", left: -0.25 * size, right: -0.25 * size, top: 0.07 * size + (1 - ce) * 0.15 * size,
          height: 1.12 * size, opacity: ce * (1 - q) }}>
          <Img src={staticFile(`card_${cardK}_sh.png`)} style={{ position: "absolute", left: "-2.5%", top: "-10%", width: "105%", height: "120%",
            transform: `translate(${3 * K}px, ${6 * K}px)` }} />
          <div style={{ position: "absolute", inset: 0, background: COL.paper, maskImage: `url(${FILE(`card_${cardK}.png`)})`,
            maskSize: "100% 100%", maskRepeat: "no-repeat" }} />
        </div>
      ) : null}
      <div style={{ position: "relative", fontFamily: base.family, fontWeight: base.weight, fontStyle: base.style,
        fontSize: size, lineHeight: 1.15, color }}>
        {toks.map((tk, i) => {
          if (t < tk.t0) return <span key={i} style={{ display: "inline-block", opacity: 0 }}>{tk.w}{i < toks.length - 1 ? " " : ""}</span>;
          const e = s.enter === "cut" ? 1 : easeOut(clamp01(stepT(t - tk.t0) / TM.enter));
          const a = e * (1 - q);
          const blur = ((1 - e) * TM.blur_px + q * 6) * K;
          const f = tk.it ? FACE.serif_it : base;
          const sz = tk.it && String(s.font).startsWith("sans") ? 1.1 : 1;
          return (
            <span key={i} style={{ display: "inline-block", opacity: a, fontFamily: f.family, fontWeight: f.weight, fontStyle: f.style,
              fontSize: `${sz}em`, letterSpacing: tk.it ? 0 : `${(s.tracking ?? 0) * size}px`,
              transform: `translateY(${(1 - e) * TM.rise_em * size}px) scale(${1 + (1 - e) * TM.scale_in})`, transformOrigin: "left bottom",
              filter: blur > 0.3 ? `blur(${blur}px)` : "none",
              textShadow: s.shadow ? `${2 * K}px ${5 * K}px ${12 * K}px rgba(0,0,0,0.5)` : "none" }}>
              {tk.w}{i < toks.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- captions
function Captions({ t, ink, cx, xmin = 0, xmax = W }: { t: number; ink: boolean; cx: number; xmin?: number; xmax?: number }) {
  const ch = CAPS.chunks.find((c: any) => !c.suppressed && c.t0 <= t && t < c.t1);
  if (!ch) return null;
  const out = clamp01((t - (ch.t1 - CAPST.out)) / CAPST.out);
  const fg = ink ? COL.ink : COL.cream;
  const sh = ink ? rgb(S.colors.cream, 0.55) : `rgba(0,0,0,${CAPST.shadow_alpha})`;
  const fs: number = CAPST.size * K, base = FACE[CAPST.font] ?? FACE.sans_medium, acc = FACE[CAPST.accent_font] ?? FACE.serif_it;
  const half = Math.min(cx - xmin, xmax - cx) - 48 * K;
  return (
    // bottom-anchored at the caption baseline: a line too wide for its area wraps to a 2nd line that grows upward
    <div style={{ position: "absolute", left: cx - half, width: 2 * half, bottom: H - CAPST.y * H - (1.15 - base.baseline) * fs,
      display: "flex", justifyContent: "center" }}>
      <div style={{ whiteSpace: "normal", textAlign: "center", maxWidth: "100%", fontSize: fs, lineHeight: 1.15, color: fg }}>
        {ch.words.map((w: any, i: number) => {
          const e = easeOut(clamp01((t - w.t0 + 0.04) / CAPST.fade));
          const a = t < w.t0 - 0.04 ? 0 : e * (1 - out);
          const f = w.accent ? acc : base;
          return (
            <span key={i} style={{ display: "inline-block", opacity: a, transform: `translateY(${(1 - e) * 6 * K}px)`,
              fontFamily: f.family, fontStyle: f.style, fontWeight: f.weight, fontSize: w.accent ? fs * 1.14 : fs,
              textShadow: `0 ${3 * K}px ${CAPST.shadow_sigma * K}px ${sh}, 0 ${K}px ${2 * K}px ${sh}`, marginRight: fs * 0.28 }}>{w.w}</span>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- scenes
function Collage({ sc, t }: { sc: any; t: number }) {
  const items = MAN.collage[sc.id] ?? [];
  return (
    <AbsoluteFill>
      <Img src={staticFile("paper.png")} style={{ position: "absolute", left: 0, top: 0, width: W, height: H }} />
      {sc.items.map((it: any, k: number) => {
        const a0 = it.t0 ?? sc.t0, a1 = it.t1 ?? sc.t1;
        if (t < a0 || t >= a1) return null;
        const b = items[k], p = (t - a0) / Math.max(a1 - a0, 1e-3);
        const z = lerp(...((it.push ?? [1, 1]) as [number, number]), p);
        return (
          <div key={k} style={{ position: "absolute", left: it.rect[0] * W, top: it.rect[1] * H, width: b.w, height: b.h,
            transform: `rotate(${-(it.rot ?? 0)}deg)` }}>
            <Img src={staticFile(b.shadow)} style={{ position: "absolute", left: -b.pad, top: -b.pad, width: b.w + 2 * b.pad, height: b.h + 2 * b.pad }} />
            <div style={{ position: "absolute", inset: 0, maskImage: `url(${FILE(b.mask)})`, maskSize: "100% 100%", maskRepeat: "no-repeat" }}>
              <MediaBox id={it.media} w={b.w} h={b.h} fx={it.focus[0]} fy={it.focus[1]} z={z} from={a0} srcT0={it.src_t0 ?? 0} />
            </div>
          </div>
        );
      })}
      {(sc.lines ?? []).map((ln: any, i: number) => {
        if (t < ln.t0 || t >= ln.t1) return null;
        const p = easeOut(clamp01((t - ln.t0) / 0.45));
        return <div key={`l${i}`} style={{ position: "absolute", left: ln.x0 * W, top: ln.y0 * H - 1.5 * K, height: 3 * K,
          width: (ln.x1 - ln.x0) * W * p, background: COL.oxide }} />;
      })}
    </AbsoluteFill>
  );
}

function Edit() {
  const n = useCurrentFrame(), t = n / FPS, sc = sceneAt(t);
  let picture: React.ReactNode = null, grain: React.ReactNode = null;
  let panel: { id: string; dx: number; pw: number; cx: number; xmin: number; xmax: number } | null = null;
  let presenter = false;

  if (sc.type === "presenter") {
    presenter = true;
    picture = <Plate t={t} />;
    grain = <Grain n={n} amp={GR[sc.grain ?? "presenter"]} gain={sc.grain ? undefined : GR.overlay_gain_presenter} />;
  } else if (sc.type === "full" || sc.type === "montage") {
    const shot = sc.type === "full" ? sc : pick(sc.shots, t);
    const p = (t - shot.t0) / (shot.t1 - shot.t0), mv = shot.move ?? { from: [0.5, 0.5, 1], to: [0.5, 0.5, 1] };
    const f = mv.from.map((a: number, i: number) => lerp(a, mv.to[i], p));
    picture = <MediaBox id={shot.media ?? sc.media} w={W} h={H} fx={f[0]} fy={f[1]} z={f[2]} from={shot.t0} srcT0={sc.src_t0 ?? 0} />;
    grain = <Grain n={n} amp={GR.insert} />;
  } else if (sc.type === "collage") {
    picture = <Collage sc={sc} t={t} />;
    grain = <Grain n={n} amp={GR.collage} />;
  } else if (sc.type === "split") {
    const pw = Math.round(sc.at * W);
    let e = sc.entry ?? true ? easeIO(clamp01((t - sc.t0) / SPL.entry)) : 1;
    if (sc.exit) e *= 1 - easeIO(clamp01((t - (sc.t1 - SPL.exit)) / SPL.exit));
    const edge = Math.round(pw * e), right = sc.side === "right";
    const shift = (right ? 0.25 - PCX : 0.75 - PCX) * W * e;
    const ins = pick(sc.inserts, t);
    const z = lerp(...((ins.push ?? [1, 1]) as [number, number]), (t - ins.t0) / (ins.t1 - ins.t0));
    const px0 = right ? W - edge : 0, innerLeft = right ? 0 : edge - pw;
    picture = (
      <AbsoluteFill>
        <Plate t={t} dx={shift} />
        <div style={{ position: "absolute", left: px0, top: 0, width: edge, height: H, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: innerLeft, top: 0, width: pw, height: H }}>
            <MediaBox id={ins.media} w={pw} h={H} fx={ins.focus[0]} fy={ins.focus[1]} z={z} from={ins.t0} srcT0={ins.src_t0 ?? 0} />
          </div>
        </div>
      </AbsoluteFill>
    );
    grain = right ? (
      <><Grain n={n} amp={GR.presenter} x1={W - edge} gain={GR.overlay_gain_presenter} /><Grain n={n} amp={GR.insert} x0={W - edge} /></>
    ) : (
      <><Grain n={n} amp={GR.insert} x1={edge} /><Grain n={n} amp={GR.presenter} x0={edge} gain={GR.overlay_gain_presenter} /></>
    );
    panel = right ? { id: sc.id, dx: W - edge, pw, cx: W / 2 + shift, xmin: 0, xmax: W - edge }
                  : { id: sc.id, dx: edge - pw, pw, cx: W / 2 + shift, xmin: edge, xmax: W };
    presenter = edge < W;
  }

  const live = TL.text.filter((x: any) => x.t0 <= t && t < x.t1);
  const behind = sc.type === "presenter" ? live.filter((x: any) => x.behind) : [];
  const front = live.filter((x: any) => !x.behind || sc.type !== "presenter");
  const masked = behind.length > 0 && (MAN.mask_frames ?? []).some(([a, b]: number[]) => a <= n && n <= b);
  // in a split, centre captions in the presenter's part of the frame (never clipped by the panel or the edge)
  const capX = panel ? (panel.xmin + panel.xmax) / 2 : (sc.cap_x ?? 0.5) * W;

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {picture}
      {behind.map((x: any) => <Kinetic key={x.id} s={x} t={t} />)}
      {masked ? (
        <Plate t={t} mask={`file://${MAN.masks_dir}/${String(n).padStart(5, "0")}.png`} />
      ) : null}
      {grain}
      {front.map((x: any) => x.panel ? (panel && panel.id === x.panel ? <Kinetic key={x.id} s={x} t={t} dx={panel.dx} pw={panel.pw} /> : null)
                                     : <Kinetic key={x.id} s={x} t={t} />)}
      {CAPMODE === "burn" && sc.cap !== "off" ? <Captions t={t} ink={sc.cap === "ink"} cx={capX} xmin={panel ? panel.xmin : 0} xmax={panel ? panel.xmax : W} /> : null}
    </AbsoluteFill>
  );
}

registerRoot(() => <Composition id="edit" component={Edit} width={W} height={H} fps={FPS} durationInFrames={NFR} />);
