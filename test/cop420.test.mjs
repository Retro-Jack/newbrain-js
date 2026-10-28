import { readFileSync } from 'fs';
import { COP420 } from '../src/cop420.js';

const rom = new Uint8Array(readFileSync(new URL('../roms/cop420-guw.ic419', import.meta.url)));
console.log(`COP ROM: ${rom.length} bytes`);

// MAME applies two fixes to this BAD_DUMP before running it.
const patched = Uint8Array.from(rom);
patched[0x20a] = 0xc6;
patched[0x231] = 0xa6;
console.log(`patched 0x20a: 0x${rom[0x20a].toString(16)} -> 0xc6`);
console.log(`patched 0x231: 0x${rom[0x231].toString(16)} -> 0xa6`);

let gWrites = 0, dWrites = 0, lastD = -1, lastG = -1;
const cop = new COP420(patched, {
  readG:  () => 0x0f,
  readIN: () => 0x0f,
  writeG: v => { gWrites++; lastG = v; },
  writeD: v => { dWrites++; lastD = v; },
  readSI: () => 0,
});

const pcs = new Set();
let steps = 0;
for (let i = 0; i < 200000; i++) { pcs.add(cop.pc); cop.step(); steps++; }

console.log(`\nran ${steps} cycles`);
console.log(`  distinct PCs visited : ${pcs.size} of 1024`);
console.log(`  PC now               : 0x${cop.pc.toString(16)}`);
console.log(`  G writes ${gWrites} (last 0x${lastG.toString(16)})  D writes ${dWrites} (last 0x${lastD.toString(16)})`);
console.log(`  A=${cop.a} B=0x${cop.b.toString(16)} C=${cop.c} EN=0x${cop.en.toString(16)} SIO=0x${cop.sio.toString(16)} T=0x${cop.t.toString(16)}`);
const nz = [...cop.ram].filter(v => v !== 0).length;
console.log(`  RAM cells written    : ${nz} of 64`);
console.log(`  halted=${cop.halt} idle=${cop.idle}`);
