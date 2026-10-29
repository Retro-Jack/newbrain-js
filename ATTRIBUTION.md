# Attribution

This emulator is original work, but it stands on other people's. This file is
the canonical record of what was used and under what terms. It is maintained
alongside [CHANGELOG.md](CHANGELOG.md): anything added or replaced gets an
entry here.

---

## Removal upon request

If you hold rights in anything named here, or legally represent someone who
does, and you would rather it were not used this way, say so and it will be
removed. No argument, no delay.

---

## The hardware

The Grundy NewBrain was designed by Newbury Laboratories and sold by Grundy
Business Systems Ltd from 1982. Grundy is long gone. Nothing here is endorsed
by anyone.

**No ROMs are distributed with this repository.** The system ROMs are Grundy's
and the keyboard controller's microcode is National Semiconductor's. See
[ROMS.txt](ROMS.txt) for what is needed and where to put it.

---

## Code

### Z80 CPU — `src/vendor/Z80.js`

Molly Howell's Z80 interpreter, used unmodified except for two mechanical
changes recorded in [`src/vendor/MODIFICATIONS.md`](src/vendor/MODIFICATIONS.md).

- Source: https://github.com/DrGoldfire/Z80.js
- Licence: **MIT** — full text in [`src/vendor/Z80.LICENSE.md`](src/vendor/Z80.LICENSE.md)

### Hardware behaviour — MAME

The memory map, video generation, COP420 instruction set and the wiring
between the Z80, the COP420, the keyboard matrix and the VF display were all
worked out by reading MAME's NewBrain driver and its COP400 CPU device.

**No MAME code is copied into this repository.** Those files are reference
material; `src/` is a reimplementation in JavaScript. The reference sources
are deliberately excluded from version control.

Paths below are MAME's own, within its tree. A local copy for reading is kept
in `reference/`, which `.gitignore` holds back.

- `src/mame/grundy/newbrain.cpp`, `newbrain.h`, `newbrain_v.cpp`
- `src/devices/bus/newbrain/*`
- `src/devices/cpu/cop400/*`
- Source: https://github.com/mamedev/mame
- Licence: **BSD-3-Clause**, copyright **Curt Coder**

BSD-3-Clause requires the copyright notice be retained in redistributions, and
this is it. Curt Coder did the hard archaeology on this machine; without that
driver none of this would have been feasible.

### Documentation

The COP420 command set, the DISPCOM transfer format and the page-zero
variables were taken from Grundy's own **NewBrain Software Technical Manual**
(1981), which documents them directly. Where it and MAME disagreed, observed
behaviour on the real ROMs decided it.

---

## Assets

### Segment16C — `art/fonts/`

The VF display's 16-segment glyphs.

- Daniel Wikholm, 2017
- Licence: **CC0 Public Domain** — no rights reserved, no attribution
  required. Credited here anyway, because it is a good font and that seems
  the decent thing.
- Full text: [`art/fonts/Segment16-LICENCE.txt`](art/fonts/Segment16-LICENCE.txt)
- Shipped subsetted to `U+0020-007E` plus `U+2588`, converted from the
  original TTF, as `Segment16C-Regular.woff2` and `Segment16C-Regular.woff`.

### Bezel artwork — `art/`

`layout.png` is composited by [`art/compose.py`](art/compose.py) from two
photographs: a Microvitec CUB monitor and a NewBrain. Both are from the
GenX-DOS shared bezel set.

---

## This emulator

Everything in `src/` other than `src/vendor/` is original, and is licensed
**GPL-3.0-or-later** — see [COPYING](COPYING).
