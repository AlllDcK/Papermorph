// Shared drawing helpers for «Оптимальное управление гиперболическими системами» (prefix oc). Load after lib/engine.js.
// The running picture is the rectangle Π in the plane (s, t): s to the right, t upwards; s, t ∈ [0, 1] in model units.
'use strict';

/* ---------- colour meanings (BOOK.md) ---------- */
const C_INIT = COL.int, C_PLUS = COL.whole, C_MINUS = COL.rat, C_ZERO = COL.dim;
const C_U = COL.nat, C_COST = COL.irr, C_ADJ = COL.real;

/* ---------- text and layout ---------- */
const fmt = (v, d = 2) => (v < -1e-12 ? '−' : '') + Math.abs(v).toFixed(d).replace('.', ',');   // decimal comma
const cm = (fill, ...parts) => ({ m: parts, fill });         // coloured inline math for ocRow
const mline = (p, parts, x, y, t0, fill = COL.chalk, size = 44, anchor = 'start') => { const e = M(p, [].concat(parts), { x, y, size, fill, anchor, o: 0 }); show(e, t0); return e; };
const text = (p, str, x, y, t0, { size = 28, fill = COL.chalk, anchor = 'start', weight = 500 } = {}) => { const e = T(p, str, { x, y, size, fill, anchor, weight, o: 0 }); show(e, t0); return e; };

// Words and math side by side on one baseline: items are strings or $m(...) / cm(colour, ...).
function ocRow(p, items, x, y, t0, { size = 28, msize = Math.round(size * 1.3), fill = COL.chalk, weight = 500, anchor = 'start' } = {}) {
  const g = G(p, { o: 0 });
  let cx = 0;
  for (const it of [].concat(items)) {
    if (typeof it === 'string') {
      T(g, it, { x: cx, size, fill, weight });
      ctx2d.font = `${weight} ${size}px ${UI}`;
      cx += ctx2d.measureText(it).width;
    } else cx += M(g, it.m, { x: cx, size: msize, fill: it.fill || fill, anchor: 'start' })._w;
  }
  put(g, { x: anchor === 'middle' ? x - cx / 2 : anchor === 'end' ? x - cx : x, y });
  g._w = cx;
  if (t0 !== undefined) show(g, t0);
  return g;
}
// A formula in a frame (amber by default).
function ocBox(p, parts, x, y, t0, { size = 44, color = COL.task, fill = COL.chalk, anchor = 'start', pad = 18 } = {}) {
  const g = G(p, { o: 0 }), m = M(g, parts, { x, y, size, fill, anchor });
  const tall = parts.some(q => q && (q.f || q.lim)), x1 = anchor === 'middle' ? x - m._w / 2 : anchor === 'end' ? x - m._w : x;
  mk('rect', { x: x1 - pad, y: y - size * (tall ? 1.2 : 1), width: m._w + 2 * pad, height: size * (tall ? 1.85 : 1.4), rx: 12, fill: 'none', stroke: color, 'stroke-width': 3 }, g);
  show(g, t0);
  return g;
}
// Frame an area of the stage (a term of a formula, a part of the picture).
function ocFrame(p, x, y, w, h, color, t0, { width = 3, dash } = {}) {
  const e = mk('rect', { x, y, width: w, height: h, rx: 10, fill: 'none', stroke: color, 'stroke-width': width, ...(dash ? { 'stroke-dasharray': dash } : {}) }, p);
  put(e, { o: 0 });
  show(e, t0, .3);
  return e;
}
// Strike a term out: a diagonal stroke drawn over the box.
function ocCross(p, x, y, w, h, t0, color = COL.bad) {
  const e = path(p, `M${x} ${y + h}L${x + w} ${y}`, { stroke: color, 'stroke-width': 4 }, { d: 0 });
  draw(e, t0, .4);
  return e;
}
function ocArrow(p, x1, y1, x2, y2, color = COL.task, w = 4, head = 15) {
  const a = Math.atan2(y2 - y1, x2 - x1), hx = s => x2 - head * Math.cos(a + s * .5), hy = s => y2 - head * Math.sin(a + s * .5);
  const g = G(p, { o: 0 });
  path(g, `M${x1} ${y1}L${x2} ${y2}`, { stroke: color, 'stroke-width': w });
  path(g, `M${hx(1)} ${hy(1)}L${x2} ${y2}L${hx(-1)} ${hy(-1)}`, { stroke: color, 'stroke-width': w });
  return g;
}
// Curly brace under x1..x2 at height y (dir −1: above, opening downwards).
function ocBrace(p, x1, x2, y, color, t0, dir = 1) {
  const c = (x1 + x2) / 2, k = 12 * dir;
  const e = path(p, `M${x1} ${y}q0 ${k} 12 ${k}H${c - 12}q12 0 12 ${k}q0 ${-k} 12 ${-k}H${x2 - 12}q12 0 12 ${-k}`, { stroke: color, 'stroke-width': 3 }, { d: 0 });
  draw(e, t0, .6);
  return e;
}
const dotAt = (p, x, y, color, r = 9) => { const g = G(p, { x, y, s: 0, o: 0 }); mk('circle', { r, fill: color, stroke: COL.board, 'stroke-width': 2.5 }, g); return g; };
// A numbered step list: rows of [text items] with a coloured number disc.
function ocSteps(p, rows, x, y, gap, times, { size = 27, color = COL.task } = {}) {
  return rows.map((items, i) => {
    const g = G(p, { o: 0, x: -14 });
    mk('circle', { cx: x + 18, cy: y + i * gap - 10, r: 18, fill: color }, g);
    T(g, String(i + 1), { x: x + 18, y: y + i * gap - 1, size: 22, fill: COL.board, weight: 700, anchor: 'middle' });
    const r = ocRow(g, items, x + 52, y + i * gap, undefined, { size });
    put(r, { o: 1 });
    tw(g, { o: 1, x: 0 }, times[i], .5);
    return g;
  });
}

/* ---------- the rectangle Π ---------- */
// D maps model s, t ∈ [0, 1] to the stage: D.X(s), D.Y(t). Edges are separate paths ready to be drawn (d: 0) in their
// colours: bottom t = t0 (initial data), left s = s0, right s = s1, top t = t1.
function ocDomain(p, { x0, y0, w, h, t0 = .1, labels = true, name = 'Π', nameAt = [.5, .5], nameSize = 70,
  sl = ['s', '0', 's', '1'], tl = ['t', '0', 't', '1'], colors = [C_INIT, C_PLUS, C_MINUS, C_COST], axes = true } = {}) {
  const g = G(p, { o: 0 }), ax = { stroke: COL.dim, 'stroke-width': 2.5 };
  const X = s => x0 + w * s, Y = t => y0 - h * t;
  mk('rect', { x: x0, y: y0 - h, width: w, height: h, fill: COL.chalk, 'fill-opacity': .05 }, g);
  if (axes) {
    path(g, `M${x0 - 24} ${y0}H${x0 + w + 60}`, ax);
    path(g, `M${x0 + w + 48} ${y0 - 8}L${x0 + w + 60} ${y0}L${x0 + w + 48} ${y0 + 8}`, ax);
    path(g, `M${x0} ${y0 + 24}V${y0 - h - 56}`, ax);
    path(g, `M${x0 - 8} ${y0 - h - 44}L${x0} ${y0 - h - 56}L${x0 + 8} ${y0 - h - 44}`, ax);
    M(g, ['s'], { x: x0 + w + 64, y: y0 + 34, size: 32, fill: COL.dim });
    M(g, ['t'], { x: x0 - 26, y: y0 - h - 46, size: 32, fill: COL.dim });
  }
  path(g, `M${x0} ${y0 - h}H${x0 + w}V${y0}`, { stroke: COL.faint, 'stroke-width': 2 });
  if (labels) {
    M(g, [sl[0], Sub(sl[1])], { x: x0, y: y0 + 40, size: 28, fill: COL.dim });
    M(g, [sl[2], Sub(sl[3])], { x: x0 + w, y: y0 + 40, size: 28, fill: COL.dim });
    M(g, [tl[0], Sub(tl[1])], { x: x0 - 34, y: y0 + 10, size: 28, fill: COL.dim });
    M(g, [tl[2], Sub(tl[3])], { x: x0 - 34, y: y0 - h + 10, size: 28, fill: COL.dim });
  }
  const label = name ? M(g, [name], { x: X(nameAt[0]), y: Y(nameAt[1]) + nameSize * .35, size: nameSize, fill: COL.dim }) : null;
  const edge = (d, c) => path(p, d, { stroke: c, 'stroke-width': 8 }, { d: 0 });
  const D = { g, X, Y, x0, y0, w, h, label };
  D.bottom = edge(`M${x0} ${y0}H${x0 + w}`, colors[0]);
  D.left = edge(`M${x0} ${y0}V${y0 - h}`, colors[1]);
  D.right = edge(`M${x0 + w} ${y0}V${y0 - h}`, colors[2]);
  D.top = edge(`M${x0} ${y0 - h}H${x0 + w}`, colors[3]);
  if (t0 !== undefined) show(g, t0);
  return D;
}
// Click targets on the sides of Π (pickEls items, in the order bottom, left, right, top).
function ocEdgePicks(D, which = ['bottom', 'left', 'right', 'top']) {
  const { x0, y0, w, h } = D, pad = 30;
  const box = {
    bottom: [x0 + 30, y0 - pad, w - 60, 2 * pad], top: [x0 + 30, y0 - h - pad, w - 60, 2 * pad],
    left: [x0 - pad, y0 - h + 30, 2 * pad, h - 60], right: [x0 + w - pad, y0 - h + 30, 2 * pad, h - 60],
  };
  const label = { bottom: 'нижняя сторона t = t₀', top: 'верхняя сторона t = t₁', left: 'левая сторона s = s₀', right: 'правая сторона s = s₁' };
  return which.map(k => ({ el: D[k], box: box[k], label: label[k], key: k }));
}

/* ---------- characteristics ---------- */
// Points [s, t] of the solution of ds/dt = a(s, t) through (s, t), followed forwards (dir 1) or backwards (dir −1) in t
// until it leaves [0, 1]²; the last point is clipped to the boundary.
function ocTrace(a, s, t, dir = 1, dt = .004) {
  const pts = [[s, t]];
  for (let i = 0; i < 2000; i++) {
    const k1 = a(s, t), k2 = a(s + dir * dt * k1 / 2, t + dir * dt / 2);
    const s2 = s + dir * dt * k2, t2 = t + dir * dt;
    if (s2 < 0 || s2 > 1 || t2 < 0 || t2 > 1) {   // clip to the side it crosses
      let q = 1;
      if (s2 < 0) q = Math.min(q, s / (s - s2));
      if (s2 > 1) q = Math.min(q, (1 - s) / (s2 - s));
      if (t2 < 0) q = Math.min(q, t / (t - t2));
      if (t2 > 1) q = Math.min(q, (1 - t) / (t2 - t));
      pts.push([s + (s2 - s) * q, t + (t2 - t) * q]);
      break;
    }
    s = s2; t = t2;
    pts.push([s, t]);
  }
  return dir < 0 ? pts.reverse() : pts;
}
// The whole characteristic through (s, t): from its entry point to its exit point.
const ocWhole = (a, s, t) => ocTrace(a, s, t, -1).concat(ocTrace(a, s, t, 1).slice(1));
const ocD = (D, pts) => pts.map(([s, t], i) => (i ? 'L' : 'M') + D.X(s).toFixed(1) + ' ' + D.Y(t).toFixed(1)).join('');
const ocChar = (p, D, pts, color, width = 3) => path(p, ocD(D, pts), { stroke: color, 'stroke-width': width }, { d: 0 });
// A small arrowhead at fraction q of a polyline, pointing along it (direction of growing t).
function ocHead(p, D, pts, q, color, size = 13) {
  const i = Math.max(1, Math.min(pts.length - 1, Math.round(q * (pts.length - 1))));
  const [s1, t1] = pts[i - 1], [s2, t2] = pts[i], x = D.X(s2), y = D.Y(t2), a = Math.atan2(D.Y(t2) - D.Y(t1), D.X(s2) - D.X(s1));
  const hx = k => x - size * Math.cos(a + k * .55), hy = k => y - size * Math.sin(a + k * .55);
  return path(p, `M${hx(1)} ${hy(1)}L${x} ${y}L${hx(-1)} ${hy(-1)}`, { stroke: color, 'stroke-width': 3 }, { o: 0 });
}
// A family of characteristics of ds/dt = a(s, t) through the seed points; drawn in from t0, one after another.
function ocFamily(p, D, a, seeds, color, t0, { stagger = .08, dur = .7, width = 3, heads = true } = {}) {
  return seeds.map(([s, t], i) => {
    const pts = ocWhole(a, s, t), e = ocChar(p, D, pts, color, width);
    draw(e, t0 + i * stagger, dur);
    if (heads) { const hd = ocHead(p, D, pts, .55, color); show(hd, t0 + i * stagger + dur * .7, .3); e._head = hd; }
    e._pts = pts;
    return e;
  });
}
// Position [s, t] at arc fraction q of a polyline (for a dot riding along a characteristic).
function ocAlong(pts, q) {
  const n = pts.length - 1, f = Math.max(0, Math.min(1, q)) * n, i = Math.min(n - 1, Math.floor(f)), r = f - i;
  return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r];
}

/* ---------- a field x(s, t) on Π ---------- */
// Value colours: zero is the dark board, positive values glow amber to pale yellow, negative values glow pale blue-grey.
const R_NEG = '#9fb8d8', R_ZERO = '#24363a', R_POS = '#d98a3a', R_HOT = '#f8dc96';
function ocRamp(v) {
  if (v < 0) return mix(R_ZERO, R_NEG, Math.min(1, -v));
  return v < .55 ? mix(R_ZERO, R_POS, v / .55) : mix(R_POS, R_HOT, Math.min(1, (v - .55) / .45));
}
// Adjoint values: violet for one sign, green-grey for the other.
const A_NEG = '#7fae9c', A_POS = '#bba8ee';
const ocRampAdj = v => v < 0 ? mix(R_ZERO, A_NEG, Math.min(1, -v)) : mix(R_ZERO, A_POS, Math.min(1, v));
function ocField(p, D, f, { n = 50, m = 50, scale = 1, ramp = ocRamp, o = .9 } = {}) {
  const g = G(p, { o: 0 }), cw = D.w / n, ch = D.h / m;
  const cells = [];
  for (let j = 0; j < m; j++) for (let i = 0; i < n; i++)
    cells.push([mk('rect', { x: D.x0 + i * cw, y: D.y0 - (j + 1) * ch, width: cw + .6, height: ch + .6 }, g), (i + .5) / n, (j + .5) / m]);
  g.set = (ff, sc = scale) => cells.forEach(([c, s, t]) => { const v = ff(s, t); c.setAttribute('fill', v === null ? 'none' : ramp(v / sc)); });
  g.set(f);
  g._o = o;
  return g;
}

/* ---------- graphs ---------- */
// A graph of v(z) for z ∈ [0, 1] along a horizontal axis: (x0, y0) is (z = 0, v = 0) … axis length w, k px per unit of v.
// az: where the vertical axis stands (z value; 0.5 for a graph over U = [−1, 1] with the axis at u = 0).
function ocGraph(p, { x0, y0, w, k, lo = -1, hi = 1, t0, zl = 's', vl = '', ends = ['0', '1'], tickAt = [], az = 0 } = {}) {
  const g = G(p, { o: 0 }), ax = { stroke: COL.dim, 'stroke-width': 2.5 };
  const X = z => x0 + w * z, Y = v => y0 - k * v, xa = X(az);
  path(g, `M${x0 - 14} ${y0}H${x0 + w + 40}`, ax);
  path(g, `M${x0 + w + 28} ${y0 - 8}L${x0 + w + 40} ${y0}L${x0 + w + 28} ${y0 + 8}`, ax);
  path(g, `M${xa} ${Y(lo) + 10}V${Y(hi) - 30}`, ax);
  path(g, `M${xa - 8} ${Y(hi) - 18}L${xa} ${Y(hi) - 30}L${xa + 8} ${Y(hi) - 18}`, ax);
  path(g, `M${x0 + w} ${y0 - 8}V${y0 + 8}`, ax);
  M(g, [zl], { x: x0 + w + 46, y: y0 + 32, size: 28, fill: COL.dim });
  if (vl) M(g, [].concat(vl), { x: xa + 14, y: Y(hi) - 22, size: 28, fill: COL.dim, anchor: 'start' });
  M(g, [ends[0]], { x: x0 - 16, y: y0 + 32, size: 24, fill: COL.dim });
  M(g, [ends[1]], { x: x0 + w, y: y0 + 32, size: 24, fill: COL.dim });
  for (const [v, lab] of tickAt) { path(g, `M${xa - 7} ${Y(v)}H${xa + 7}`, ax); M(g, [lab], { x: xa - 14, y: Y(v) + 9, size: 22, fill: COL.dim, anchor: 'end' }); }
  if (az) { path(g, `M${x0} ${y0 - 8}V${y0 + 8}`, ax); M(g, ['0'], { x: xa - 14, y: y0 + 30, size: 22, fill: COL.dim, anchor: 'end' }); }
  if (t0 !== undefined) show(g, t0);
  const d = (f, a = 0, b = 1, n = 160) => {
    let s = '';
    for (let i = 0; i <= n; i++) { const z = a + (b - a) * i / n; s += (i ? 'L' : 'M') + X(z).toFixed(1) + ' ' + Y(f(z)).toFixed(1); }
    return s;
  };
  return { g, X, Y, d, x0, y0, w, k };
}
// A graph of v(t) drawn upright beside Π, sharing its t-axis: value to the right of the axis line at xz (v = 0), k px per unit.
function ocVGraph(p, D, { xz, k, lo = -1, hi = 1, t0, vl = '', color = COL.dim, ticks = [] } = {}) {
  const g = G(p, { o: 0 }), ax = { stroke: COL.dim, 'stroke-width': 2 };
  const V = v => xz + k * v;
  path(g, `M${xz} ${D.y0 + 10}V${D.y0 - D.h - 10}`, ax);
  path(g, `M${V(lo) - 6} ${D.y0}H${V(hi) + 6}`, { stroke: COL.faint, 'stroke-width': 2 });
  path(g, `M${V(lo) - 6} ${D.y0 - D.h}H${V(hi) + 6}`, { stroke: COL.faint, 'stroke-width': 2, 'stroke-dasharray': '4 8' });
  for (const [v, lab] of ticks) { path(g, `M${V(v)} ${D.y0 - 6}V${D.y0 + 6}`, ax); M(g, [lab], { x: V(v), y: D.y0 + 30, size: 20, fill: COL.dim }); }
  if (vl) M(g, [].concat(vl), { x: xz, y: D.y0 - D.h - 22, size: 28, fill: color });
  if (t0 !== undefined) show(g, t0);
  const d = (f, a = 0, b = 1, n = 200) => {
    let s = '';
    for (let i = 0; i <= n; i++) { const t = a + (b - a) * i / n; s += (i ? 'L' : 'M') + V(f(t)).toFixed(1) + ' ' + D.Y(t).toFixed(1); }
    return s;
  };
  return { g, V, d, xz, k };
}
const ocCurve = (gr, f, color = COL.chalk, width = 4.5, a, b) => path(gr.g, gr.d(f, a, b), { stroke: color, 'stroke-width': width }, { d: 0 });
const ocSet = (gr, e, f, a, b) => e.setAttribute('d', gr.d(f, a, b));
// Run model time τ from T0 to T1 between t0 and t0 + dur.
const ocRun = (upd, t0, dur, T0, T1, ease = lin) => prog(q => upd(T0 + (T1 - T0) * q), t0, dur, ease);

/* ---------- the toy example (BOOK.md): a = 1, f = 0, ẏ = u, U = [−1, 1], J = ∫ (3s − 1) x(s, 1) ds ---------- */
const TOY = {
  w: s => 3 * s - 1,                                     // weight in J
  psi1: s => 1 - 3 * s,                                  // ψ(s, 1) = −φ_x
  psi: (s, t) => s <= t ? 3 * t - 3 * s - 2 : 0,         // ψ constant along s − t = const; zero where the line leaves through s = 1
  p: t => (3 * t - 1) * (1 - t) / 2,                     // p(t) = ∫_t^1 ψ(0, τ) dτ
  uStar: t => t < 1 / 3 ? -1 : 1,
  // y(t) = ∫_0^t u for a piecewise-constant u given as [[t_k, u_k], …] (u_k on [t_k, t_{k+1})).
  y: (pieces, t) => { let y = 0; pieces.forEach(([a, u], i) => { const b = i + 1 < pieces.length ? pieces[i + 1][0] : 1; if (t > a) y += u * (Math.min(t, b) - a); }); return y; },
  uOf: (pieces, t) => { let u = pieces[0][1]; for (const [a, v] of pieces) if (t >= a) u = v; return u; },
  x: (pieces, s, t) => t >= s ? TOY.y(pieces, t - s) : 0,   // x(s, t) = y(t − s) after the boundary signal arrives
};
const U_STAR = [[0, -1], [1 / 3, 1]], U_ONE = [[0, 1]], U_MINUS = [[0, -1]];
