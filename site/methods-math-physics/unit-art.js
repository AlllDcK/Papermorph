// Chalk sketches for the unit headers on the contents page, one per unit, drawn in the unit's colour.
// Each entry is the inside of an SVG with viewBox 0 0 600 180; keep the left ~200 px light (the unit title sits there
// on narrow screens). Classes, styled in index.html:
//   d  a stroke that draws itself in when the unit scrolls into view (--k orders the strokes)
//   t  text or a filled shape that fades in
//   a  faint chalk white instead of the unit colour;  faint  even fainter
// A sketch may add one looping motion after it is drawn (see the .seen .unit-art rules in index.html).
'use strict';
(() => {
  let k = 0;
  const P = (d, cls = '', extra = '') => `<path class="d ${cls}" pathLength="1" style="--k:${k++}" d="${d}" ${extra}/>`;
  const Tx = (x, y, s, size = 24, cls = '', anchor = 'start') => `<text class="t ${cls}" style="--k:${k++}" x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${s}</text>`;
  const reset = s => { k = 0; return s; };
  // y = base − amp · sin(k·π·(x − x0)/w) on [x0, x0 + w], as a polyline path.
  const wave = (x0, w, base, amp, kk) => Array.from({ length: 49 }, (_, i) => {
    const x = x0 + w * i / 48, y = base - amp * Math.sin(kk * Math.PI * i / 48);
    return (i ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1);
  }).join('');

  window.UNIT_ART = [
    // 1 A rod held at zero at both ends: its temperature arch sin x cools down and keeps its shape (u = e^{−t} sin x).
    reset(P('M236 140H564', 'a') + P('M260 128v24') + P('M540 128v24') +
      P(wave(260, 280, 140, 46, 3), 'faint') +
      `<g class="breathe">${P(wave(260, 280, 140, 90, 1))}</g>` +
      Tx(260, 172, '0', 20, 'a', 'middle') + Tx(540, 172, 'π', 20, 'a', 'middle') +
      Tx(596, 30, 'u = e<tspan dy="-10" font-size="16">−t</tspan><tspan dy="10"> sin x</tspan>', 24, '', 'end')),
  ];
})();
