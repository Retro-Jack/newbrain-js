import { readFileSync } from 'fs';
import { NewBrainSystem, CPU_HZ } from '../src/system.js';

const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const sys = new NewBrainSystem({
  ab:      R('../roms/aben191.ic6'),
  cd:      R('../roms/cdi3.ic7'),
  ef:      R('../roms/ef iss 1.ic8'),
  chargen: R('../roms/char eprom iss 1.ic453'),
});
const m = sys.machine;

const h4 = v => '0x' + (v >>> 0).toString(16).toUpperCase().padStart(4, '0');

// Watch what the ROM touches.
const ioLog = new Map();
const origIoW = m.ioWrite.bind(m);
m.ioWrite = (p, v) => { ioLog.set(p & 0xff, (ioLog.get(p & 0xff) || 0) + 1); origIoW(p, v); };

console.log('--- first 12 instructions out of reset ---');
for (let i = 0; i < 12; i++) {
  const pc = sys.pc;
  const op = m.read(pc), o1 = m.read(pc + 1), o2 = m.read(pc + 2);
  console.log(`  PC=${h4(pc)}  ${op.toString(16).padStart(2,'0')} ${o1.toString(16).padStart(2,'0')} ${o2.toString(16).padStart(2,'0')}`);
  sys.run(1);
}

console.log('\n--- running 7 emulated seconds (PWRUP is at 5.6s) ---');
const t0 = Date.now();
let instr = 0;
for (let s = 0; s < 7; s++) {
  instr += sys.run(CPU_HZ);
  const ramUsed = m.ram.reduce((n, b) => n + (b !== 0 ? 1 : 0), 0);
  console.log(`  t=${s + 1}s  PC=${h4(sys.pc)}  pwrup=${m.pwrup}  ` +
              `tvp=${m.tvp}  tvl=${h4(m.tvl)}  RAM non-zero=${ramUsed}`);
}
console.log(`  ${(instr/1e6).toFixed(1)}M instructions in ${((Date.now()-t0)/1000).toFixed(1)}s wall`);

console.log('\n--- I/O ports the ROM used ---');
for (const [p, n] of [...ioLog].sort((a,b) => a[0]-b[0])) {
  const grp = (p >> 2) & 7;
  const name = grp===1 ? ['CLCLK','?','COP','ENRG1'][p&3] : grp===2 ? 'TVL' : grp===3 ? 'TVTL' : grp===5 ? 'UST' : '?';
  console.log(`  port 0x${p.toString(16).padStart(2,'0')}  ${String(n).padStart(7)} writes   ${name}`);
}

console.log('\n--- video state ---');
console.log(`  tvp(display on)=${m.tvp}  80col=${m.c80l}  ucr=${m.ucr}  rv=${m.rv}  tvl=${h4(m.tvl)}`);
