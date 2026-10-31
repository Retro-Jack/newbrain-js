// Where a tape's data ends, which is not where its signal does.
//
// Every block is followed by gap tone, the last one included, and the ROM
// never plays that final run — it takes the block, sees the last-block flag
// and stops the motor. So `finished` never comes true on a tape that has in
// fact been read right through, and anything waiting on it waits for ever.

import test from 'node:test';
import assert from 'node:assert/strict';
import { encodeTape, TapePlayer, TAPE_DEFAULTS } from '../src/tape.js';

// One well-formed block: 00, a two-byte count, the data, a type byte, two
// checksum bytes, and the nine-byte trailer the writer lays down.
function block(data, type) {
  const b = [0x00, data.length & 0xff, data.length >> 8, ...data, type, 0, 0];
  return [...b, ...Array(9).fill(0)];
}
const tape = Uint8Array.from([
  ...block([0x41, 0x42], 0x81),      // first
  ...block([0x43, 0x44], 0x42),      // last
]);

test('dataEnd falls before the trailing gap, not at the end of the signal', () => {
  const { durations, dataEnd } = encodeTape(tape);
  assert.ok(dataEnd > 0, 'no data end was reported');
  assert.ok(dataEnd < durations.length, 'dataEnd is at the end of the signal');
  // Behind it: the nine unread trailer bytes, then the gap tone. A 0x00 byte
  // is a 1 start bit (four half cycles), eight 0 bits (two each) and a 0 stop
  // bit (two) — 22 in all.
  assert.equal(durations.length - dataEnd, 9 * 22 + TAPE_DEFAULTS.gapCells * 4,
    'dataEnd does not sit exactly before the trailer and the gap');
});

test('a tape reads as played once the data has gone by, before it is finished', () => {
  const { durations, dataEnd } = encodeTape(tape);
  const p = new TapePlayer(durations, dataEnd);
  assert.equal(p.played, false);
  assert.equal(p.finished, false);

  p.index = dataEnd;                 // the ROM has taken the last block
  assert.equal(p.played, true, 'the data has gone past but played is false');
  assert.equal(p.finished, false, 'the gap tone should still be ahead');
  assert.equal(p.progress, 1, 'a fully read tape should show full');
});

test('progress is measured against the data, so it reaches 1', () => {
  const { durations, dataEnd } = encodeTape(tape);
  const p = new TapePlayer(durations, dataEnd);
  p.index = Math.floor(dataEnd / 2);
  assert.ok(p.progress > 0.4 && p.progress < 0.6, `half way read ${p.progress}`);
});
