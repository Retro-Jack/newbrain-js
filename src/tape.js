// SPDX-License-Identifier: GPL-3.0-or-later
// Grundy NewBrain AD — cassette.
//
// The COP420 modulates and demodulates the tape itself; the Z80 only hands it
// whole bytes. So a tape is emulated by driving the TPIN pin with a signal the
// real microcode will accept, and the ROM then does its own framing and
// checksumming exactly as it would off a real cassette.
//
// The encoding below was measured from recordings the emulated machine made of
// itself, and verified by decoding them back: 150 half cycles of a saved block
// parse into 15 frames with no framing violations and the bytes the ROM wrote.
//
//   a 1 bit   two cycles of the high tone      four half cycles of ~832
//   a 0 bit   one cycle of the low tone        ~1660 then ~1795
//   a byte    start bit 1, eight data bits most significant first, stop bit 0
//   a leader  repeating 2208 2208 1120 1120, a tone of its own
//
// All figures are Z80 T-states at 4MHz. The leader runs out one half cycle
// into its group before the first frame, which the demodulator needs in order
// to find the start bit — without it nothing decodes at all.

const LEADER_GROUP = [2208, 2208, 1120, 1120];
const JOIN         = 2208;
const ONE          = [832, 832, 832, 832];
const ZERO         = [1660, 1795];

// Leader before a block, and tone after it. The gap has to be long enough for
// the ROM to stow one block and come back for the next.
export const TAPE_DEFAULTS = { leaderCells: 600, gapCells: 200 };

// Splits a tape file into blocks. Each is a 00 the COP lays down itself, a
// two byte count, the data, a type byte, a two byte checksum and nine zeroes.
export function tapeBlocks(bytes) {
  const raw = Uint8Array.from(bytes), out = [];
  let p = 0;
  while (p + 3 <= raw.length && raw[p] === 0x00) {
    const count = raw[p + 1] | (raw[p + 2] << 8);
    const end = p + 3 + count + 3 + 9;
    if (end > raw.length) break;
    out.push(raw.subarray(p, end));
    p = end;
  }
  return out;
}

// Turns a tape file into a list of half cycle lengths.
export function encodeTape(bytes, opts = {}) {
  const { leaderCells, gapCells } = { ...TAPE_DEFAULTS, ...opts };
  const blocks = tapeBlocks(bytes);
  const out = [];
  const push = a => { for (const v of a) out.push(v); };

  for (const block of (blocks.length ? blocks : [Uint8Array.from(bytes)])) {
    for (let i = 0; i < leaderCells; i++) push(LEADER_GROUP);
    out.push(JOIN);
    for (const byte of block) {
      push(ONE);                                        // start
      for (let b = 7; b >= 0; b--) push((byte >> b) & 1 ? ONE : ZERO);
      push(ZERO);                                       // stop
    }
    for (let i = 0; i < gapCells; i++) push(LEADER_GROUP);
  }
  return Int32Array.from(out);
}

// Plays a list of half cycle lengths, flipping the tape level as each elapses.
// It is driven by elapsed time rather than absolute cycles, because the tape
// only moves while the motor is running: the ROM stops it between blocks while
// it stows one away, and the tape has to wait exactly as a real one would.
export class TapePlayer {
  constructor(durations) {
    this.durations = durations;
    this.index = 0;
    this.level = 0;
    this.clock = 0;
    this.nextAt = 0;
  }

  get finished() { return this.index >= this.durations.length; }
  get progress() { return this.durations.length ? this.index / this.durations.length : 1; }

  // Runs the tape on by `delta` T-states, returning the level now at TPIN.
  advance(delta) {
    this.clock += delta;
    while (this.index < this.durations.length && this.clock >= this.nextAt) {
      this.nextAt += this.durations[this.index++];
      this.level ^= 1;
    }
    return this.level;
  }
}
