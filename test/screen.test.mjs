import { readFileSync, writeFileSync } from 'fs';
import { NewBrainSystem, CPU_HZ } from '../src/system.js';
import { SCREEN_W, SCREEN_H } from '../src/newbrain.js';
const R = p => new Uint8Array(readFileSync(new URL(p, import.meta.url)));
const sys = new NewBrainSystem({
  ab: R('../roms/aben191.ic6'), cd: R('../roms/cdi3.ic7'),
  ef: R('../roms/ef iss 1.ic8'), chargen: R('../roms/char eprom iss 1.ic453'),
});
const m = sys.machine;
sys.run(CPU_HZ * 10);   // past PWRUP + RAM test

const rgba = new Uint8Array(SCREEN_W * SCREEN_H * 4);
m.renderInto(rgba);

let lit = 0;
for (let i = 0; i < rgba.length; i += 4) if (rgba[i+1] > 0) lit++;
console.log(`lit pixels: ${lit} / ${SCREEN_W*SCREEN_H}  (${(100*lit/(SCREEN_W*SCREEN_H)).toFixed(2)}%)`);
console.log(`tvp=${m.tvp} tvl=0x${m.tvl.toString(16)} 80col=${m.c80l} ucr=${m.ucr} rv=${m.rv}`);

// ASCII view, 2x1 downsample of the top-left
console.log('\n--- top-left 100x40 of the screen ---');
for (let y = 0; y < 40; y++) {
  let row = '';
  for (let x = 0; x < 200; x += 2) {
    const i = (y * SCREEN_W + x) * 4;
    row += rgba[i+1] > 0 ? '#' : '.';
  }
  console.log('  ' + row);
}
writeFileSync(new URL('../screen.raw', import.meta.url), rgba);
console.log('\nraw RGBA written to screen.raw');
