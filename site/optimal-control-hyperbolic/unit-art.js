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

  window.UNIT_ART = [
    // 1 The rectangle Π in the (s, t) plane: a control signal enters at the left side s = s0 and rides into Π along
    //   the tilted characteristics ds/dt = a > 0; a dot rides along one of them.
    reset(P('M300 160H540V20H300Z', 'a') +
      P('M300 160L420 20', 'faint') + P('M300 120L386 20', 'faint') + P('M300 80L352 20', 'faint') +
      P('M360 160L480 20', 'faint') + P('M420 160L540 20', 'faint') +
      P('M300 160C284 140 312 124 296 104S286 64 300 44S290 30 300 20') +
      Tx(546, 176, 's', 20, 'a') + Tx(292, 16, 't', 20, 'a', 'end') + Tx(470, 110, 'Π', 30, 'a', 'middle') +
      `<circle class="ride" r="6" fill="currentColor" stroke="none" style="offset-path: path('M300 120L386 20')"/>`),
  ];
})();
