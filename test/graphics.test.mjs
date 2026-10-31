// Pixel graphics, driven from a screen built by hand.
//
// Three 00 bytes put the display generator into a bitmap mode for the rest of
// the frame: the flags stop being reset, videoAddr runs on linearly instead of
// returning to the row, the character row counter stops, and each byte is
// eight pixels straight out of grsr, least significant bit first.
//
// This is the one part of the generator our renderer could not reach — the
// per-scanline flag reset that fixes the column-38 striping also meant grLine
// could never come up — so it is pinned here, and the striping case stays
// pinned in frameend.test.mjs because the two pull in opposite directions.

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

// Fixed video mode, so the arithmetic below is not at the mercy of whatever
// the ROM last wrote to TVTL: 40 columns, no border, no reverse field.
m.c80l = 0; m.c32_40 = 0; m.rv = 0; m.ucr = 0;

const STRIDE = 64, COLS = 40, CELL = 10;
const MARKER_ROW = 4;
const base = m.tvl + MARKER_ROW * STRIDE;      // the bitmap is linear from here
const put = (row, col, b) => { m.ram[(m.tvl + row * STRIDE + col) & 0x7fff] = b; };
const lin = (i, b) => { m.ram[(base + i) & 0x7fff] = b; };

for (let r = 0; r < 25; r++) for (let c = 0; c < COLS; c++) put(r, c, 0x20);
for (let i = 0; i < COLS; i++) put(2, i, 0x41);          // a row of text above it

// Everything from the marker onwards is one linear bitmap. The first three
// bytes are the marker itself; the rest is solid, so every graphics scanline
// should come out fully lit — which a row of 0xFF drawn as CHARACTERS never is.
const SPAN = (SCREEN_H - MARKER_ROW * CELL + 1) * COLS;
for (let i = 0; i < SPAN; i++) lin(i, 0xff);
lin(0, 0x00); lin(1, 0x00); lin(2, 0x00);                // three 00s: graphics

// The transition scanline reads the marker row itself, so the first FULL
// graphics scanline starts one row-width in: scanline FIRST_FULL + k reads
// bytes (k + 1) * COLS onwards. A single blank byte pins that stride — get it
// wrong and the picture shears, which is the failure this is here to catch.
const PROBE_K = 2;                   // counted from the first full graphics line
const PROBE_COL = 7;
lin((PROBE_K + 1) * COLS + PROBE_COL, 0x00);

const rgba = new Uint8Array(SCREEN_W * SCREEN_H * 4);
m.renderInto(rgba);

const lit = y => { let n = 0;
  for (let x = 0; x < SCREEN_W; x++) if (rgba[(y * SCREEN_W + x) * 4] > 60) n++;
  return n; };

// Row 4's first scanline is a transition — text, then the marker, then bitmap.
// The first FULL graphics scanline is the one after it.
const FIRST_FULL = MARKER_ROW * CELL + 1;

test('text above the marker still draws', () => {
  const rowLit = [...Array(CELL)].reduce((n, _, i) => n + lit(2 * CELL + i), 0);
  assert.ok(rowLit > 0, 'the row of text above the marker drew nothing');
});

test('three 00 bytes switch the rest of the frame to pixel graphics', () => {
  const y = FIRST_FULL;
  assert.equal(lit(y), SCREEN_W,
    `scanline ${y} lit ${lit(y)} of ${SCREEN_W} px — solid bytes drew as ` +
    `characters, so the graphics path was never reached`);
});

test('graphics runs to the bottom of the frame, not for one row', () => {
  for (let y = FIRST_FULL; y < SCREEN_H; y++) {
    if (y === FIRST_FULL + PROBE_K) continue;             // the stride probe
    assert.equal(lit(y), SCREEN_W, `scanline ${y} lit ${lit(y)} of ${SCREEN_W}`);
  }
});

test('the scanline that starts the region draws its own marker dark', () => {
  // Three 00s at columns 0-2, each eight pixels doubled to sixteen.
  const y = MARKER_ROW * CELL;
  assert.equal(lit(y), SCREEN_W - 3 * 16,
    `the transition scanline lit ${lit(y)} of ${SCREEN_W}`);
});

test('a graphics line consumes one scanline-width of bytes, not a row', () => {
  const y = FIRST_FULL + PROBE_K;
  // One blank byte is 8 pixels, doubled to 16 in 40-column mode.
  assert.equal(lit(y), SCREEN_W - 16,
    `scanline ${y} lit ${lit(y)}; expected ${SCREEN_W - 16} — the blank byte ` +
    `did not land where a ${COLS}-byte stride puts it`);
  const x0 = PROBE_COL * 16;
  assert.equal(rgba[(y * SCREEN_W + x0) * 4] > 60, false,
    `the blank byte is not at column ${PROBE_COL} on scanline ${y}`);
});
