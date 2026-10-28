import { readFileSync } from 'fs';
import { NewBrainSystem, CPU_HZ } from '../src/system.js';
const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const sys = new NewBrainSystem({
  ab: R('../roms/aben191.ic6'), cd: R('../roms/cdi3.ic7'),
  ef: R('../roms/ef iss 1.ic8'), chargen: R('../roms/char eprom iss 1.ic453'),
  cop: (() => { const r = Uint8Array.from(R('../roms/cop420-guw.ic419'));
                r[0x20a] = 0xc6; r[0x231] = 0xa6; return r; })(),
});
const m = sys.machine;
console.log('COP present:', !!m.cop);
sys.run(CPU_HZ * 10);

const tvl = m.tvl;
const row = n => { let s=''; const a = tvl + 122 + n*88;
  for (let c=0;c<40;c++){ const b=m.ram[(a+c)&0x7fff]; if(b===0)break;
    s += (b>=32&&b<127)?String.fromCharCode(b):'?'; } return s; };

console.log(`after boot: r0="${row(0)}" r1="${row(1)}" r2="${row(2)}"`);
console.log(`COP: pc=0x${m.cop.pc.toString(16)} G=0x${m.cop.g.toString(16)} Q=0x${m.cop.q.toString(16)} copint=${m.copint}`);
console.log(`k405=${m.k405} k403d=0x${m.k403d.toString(16)} digits[0]=0x${m.digits[0].toString(16)}`);

// press 'A' — Y13 bit 0
console.log('\npressing A (Y13 bit0) for 150ms...');
m.setKey(13, 0, true);
sys.run(CPU_HZ * 0.15);
m.setKey(13, 0, false);
sys.run(CPU_HZ * 0.35);

console.log(`after keypress: r0="${row(0)}" r1="${row(1)}" r2="${row(2)}"`);
console.log(`COP: pc=0x${m.cop.pc.toString(16)} Q=0x${m.cop.q.toString(16)} copint=${m.copint}`);
console.log(`COPST=0x${m.ram[0x3c].toString(16)} COPBUFF=0x${m.ram[0x3d].toString(16)}`);
console.log(`VFD: "${m.vfdText()}"`);
