import { readFileSync } from 'fs';
import { NewBrain } from '../src/newbrain.js';

const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const m = new NewBrain({
  ab:      R('../roms/aben191.ic6'),
  cd:      R('../roms/cdi3.ic7'),
  ef:      R('../roms/ef iss 1.ic8'),
  chargen: R('../roms/char eprom iss 1.ic453'),
});

let pass = 0, fail = 0;
const hex = v => '0x' + (v >>> 0).toString(16).toUpperCase().padStart(2, '0');
function eq(name, got, want) {
  const ok = got === want;
  ok ? pass++ : fail++;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}: got ${hex(got)} want ${hex(want)}`);
}

console.log('--- at reset: every access must decode as bank 7 (EF ROM) ---');
eq('read(0x0000) is JP opcode',      m.read(0x0000), 0xC3);
eq('read(0x0001) low  of JP target', m.read(0x0001), 0x03);
eq('read(0x0002) high of JP target', m.read(0x0002), 0xE0);
eq('read(0x4321) also reads EF ROM', m.read(0x4321), m.rom[0x4000 + (0x4321 & 0x1fff)]);

console.log('--- after PWRUP: normal bank decode ---');
m.pwrup = 1;
eq('0xE000 -> EF ROM',  m.read(0xE000), 0xC3);
eq('0xA000 -> AB ROM',  m.read(0xA000), m.rom[0x0000]);
eq('0xC000 -> CD ROM',  m.read(0xC000), m.rom[0x2000]);
eq('0x8000 unmapped',   m.read(0x8000), 0xFF);

console.log('--- RAM is writable, ROM is not ---');
m.write(0x1234, 0x5A); eq('RAM holds a write', m.read(0x1234), 0x5A);
m.write(0xE000, 0x00); eq('ROM ignores writes', m.read(0xE000), 0xC3);

console.log('--- I/O decode ---');
m.ioWrite(0x07, 0x04); eq('ENRG1 bit2 sets TVP', m.tvp, 1);
m.ioWrite(0x0C, 0x40); eq('TVTL bit6 sets 80col', m.c80l, 1);
m.ioWrite(0x0C, 0x00); eq('TVTL clears 80col',    m.c80l, 0);

console.log(`\n  ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
