# Attribution

This emulator is original work, but it stands on other people's. This file is
the canonical record of what was used and under what terms. It is maintained
alongside [CHANGELOG.md](CHANGELOG.md): anything added or replaced gets an
entry here.

[PROVENANCE.md](PROVENANCE.md) is its companion: this file records *what* was
used and under what terms, that one records *how* the emulator was written —
what the code derives from, what it deliberately does not, and which of those
claims can be checked.

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

How that reading was done, and the line held against the one closed-source
NewBrain emulator that predates this work, is set out in
[PROVENANCE.md](PROVENANCE.md).

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

Two images, built by [`art/compose.py`](art/compose.py): `cub.png`, the
Microvitec CUB monitor, and `newbrain.png`, the NewBrain itself. They are
separate files under separate licences; the page places them side by side
rather than combining them into one picture.

**The machine carries a binding obligation.** Its body and VF tube are from
[File:New Brain IMG 4244.jpg](https://commons.wikimedia.org/wiki/File:New_Brain_IMG_4244.jpg)
on Wikimedia Commons, by **Rama & Musée Bolo**, of a machine on display at the
Musée Bolo, EPFL, Lausanne.

- Licence: **CC BY-SA 2.0 FR**, or CeCILL v2 at the user's choice
- Share-alike: `art/newbrain.png` is a derivative and inherits it. That is a
  condition on that one image, not on the emulator — `src/` stays GPL-3.0,
  and `art/cub.png` is untouched by it.

That photograph is of a **French** NewBrain, and its keyboard is AZERTY. Since
a picture of the machine is the one place a reader looks to find where a key
is, and the emulator maps a QWERTY matrix, the keyboard was replaced with one
taken from the Home Computer Museum's
[NewBrain page](https://www.homecomputermuseum.nl/en/collectie/grundy-business-systems-ltd/grundy-newbrain/).
**That site states no licence and credits no photographer**, so unlike the
Commons image it is not source-cleared; it is recorded here so that it is at
least known, and the removal offer at the top of this file applies to it as
much as to anything else.

**`cub.png` is jsbeeb's.** It is
`public/images/cub-monitor.png` from Matt Godbolt's BBC Micro emulator, byte
for byte.

- Source: https://github.com/mattgodbolt/jsbeeb/blob/main/public/images/cub-monitor.png
- Licence: **GPL-3.0-or-later**

▲ **A note on keeping the two apart.** CC BY-SA 2.0 and the GPL are not
compatible licences, and the monitor and the machine are under one each. They
are kept as separate files for that reason as well as for layout: each is
wholly under its own licence, and the page only displays them alongside one
another. Nothing combines them into a single image, so no combined work is
made and the incompatibility does not arise. Were one ever wanted, the
Commons file is offered under *either* CC BY-SA 2.0 FR *or* **CeCILL v2** at
the user's choice, and CeCILL v2 is written to be GPL-compatible, so that is
the option that would be taken. Attribution to Rama & Musée Bolo is given
either way. This is a reading, not legal advice; it is written down so the
reasoning can be checked rather than assumed.

---

## This emulator

Everything in `src/` other than `src/vendor/` is original, and is licensed
**GPL-3.0-or-later** — see [COPYING](COPYING).
