// The row terminator and the frame end, driven from a screen built by hand.
//
// Both of these were wrong at different times and each masked the other, so
// they are pinned here together: the frame end has to blank what lies below it
// WITHOUT the row terminator bleeding between scanlines. See the long comment
// in renderInto for why this does not match MAME.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'fs';
import { NewBrainSystem, CPU_HZ } from '../src/system.js';
import { SCREEN_W, SCREEN_H } from '../src/newbrain.js';

const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const sys = new NewBrainSystem({
  ab: R('../roms/aben191.ic6'), cd: R('../roms/cdi3.ic7'),
  ef: R('../roms/ef iss 1.ic8'), chargen: R('../roms/char eprom iss 1.ic453'),
});
const m = sys.machine;
sys.run(CPU_HZ * 10);           // past PWRUP and the RAM test

const STRIDE = 64, COLS = 40, CELL = 10;
const put = (row, col, byte) => { m.ram[(m.tvl + row * STRIDE + col) & 0x7fff] = byte; };
const text = (row, s, col = 0) => { for (let i = 0; i < s.length; i++) put(row, col + i, s.charCodeAt(i)); };

// A blank field, then rows that exercise each case.
for (let r = 0; r < 25; r++) for (let c = 0; c < COLS; c++) put(r, c, 0x20);

text(2, 'A'.repeat(38)); put(2, 38, 0x00);     // terminator in the last-but-one column
text(4, 'B'.repeat(10)); put(4, 10, 0x00);     // terminator early in the row
put(6, 0, 0x00); put(6, 1, 0x00);              // two 00s: the frame ends here
text(8, 'C'.repeat(10)); put(8, 10, 0x00);     // below the frame end, must not draw

const rgba = new Uint8Array(SCREEN_W * SCREEN_H * 4);
m.renderInto(rgba);

const litPerScanline = [];
for (let y = 0; y < SCREEN_H; y++) {
  let n = 0;
  for (let x = 0; x < SCREEN_W; x++) if (rgba[(y * SCREEN_W + x) * 4] > 60) n++;
  litPerScanline.push(n);
}
const rowScan = r => litPerScanline.slice(r * CELL, r * CELL + CELL);
const rowLit  = r => rowScan(r).reduce((a, b) => a + b, 0);

// A striped row is one with a blank scanline BETWEEN two lit ones.
function striped(r) {
  const s = rowScan(r);
  const first = s.findIndex(v => v > 0);
  if (first < 0) return false;
  const last = s.length - 1 - [...s].reverse().findIndex(v => v > 0);
  return s.slice(first, last + 1).some(v => v === 0);
}

test('a terminator in column 38 does not stripe the row', () => {
  assert.ok(rowLit(2) > 0, 'row 2 drew nothing at all');
  assert.equal(striped(2), false, `row 2 striped: [${rowScan(2)}]`);
  // Same glyph on every column, so the lit span must match the early-terminator
  // row's shape scanline for scanline.
  const shape = s => s.map(v => (v > 0 ? 1 : 0)).join('');
  assert.equal(shape(rowScan(2)), shape(rowScan(4)),
    `row 2 [${rowScan(2)}] has a different scanline shape to row 4 [${rowScan(4)}]`);
});

test('a single terminator leaves the rows below it alone', () => {
  assert.ok(rowLit(4) > 0, 'row 4 drew nothing, so row 2 did not end cleanly');
});

test('two 00 bytes end the frame', () => {
  assert.equal(rowLit(6), 0, `the marker row itself drew: [${rowScan(6)}]`);
  assert.equal(rowLit(8), 0, `content below the frame end drew: [${rowScan(8)}]`);
  for (let y = 7 * CELL; y < SCREEN_H; y++) {
    assert.equal(litPerScanline[y], 0, `scanline ${y} drew below the frame end`);
  }
});
