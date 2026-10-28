import { readFileSync } from 'fs';
import { NewBrainSystem, CPU_HZ } from '../src/system.js';
const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const sys = new NewBrainSystem({
  ab: R('../roms/aben191.ic6'), cd: R('../roms/cdi3.ic7'),
  ef: R('../roms/ef iss 1.ic8'), chargen: R('../roms/char eprom iss 1.ic453'),
});
const m = sys.machine;
sys.run(CPU_HZ * 10);

const cols = m.c80l ? 80 : 40;
console.log(`video RAM at 0x${m.tvl.toString(16)}, ${cols} columns\n`);
const pr = b => (b >= 32 && b < 127) ? String.fromCharCode(b) : (b === 0 ? '.' : '·');
for (let row = 0; row < 14; row++) {
  const base = m.tvl + row * (m.c80l ? 128 : 64);
  let txt = '', hex = '';
  for (let c = 0; c < cols; c++) {
    const b = m.ram[(base + c) & 0x7fff];
    txt += pr(b);
    if (c < 16) hex += b.toString(16).padStart(2,'0') + ' ';
  }
  console.log(`  r${String(row).padStart(2)} |${txt}|`);
  if (row < 3) console.log(`      hex: ${hex}`);
}
