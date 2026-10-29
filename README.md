# NewBrain

A Grundy NewBrain AD in a browser.

The NewBrain was a 1982 British home computer, designed by Newbury
Laboratories and sold by Grundy Business Systems. It is remembered mostly for
having nearly become the BBC Micro. It has two displays at once: a 40/80
column picture on a television, and a 16-character vacuum-fluorescent panel
built into the case.

As far as I can establish, no browser-based NewBrain emulator existed before
this one. The Internet Archive holds twenty-one NewBrain items and not one of
them is emulatable.

## Try it

**<https://retro-jack.github.io/newbrain-js/>**

The ROMs are not in this repository and the published site carries its own
copy; see [ROMS.txt](ROMS.txt) if you are running it yourself.

## Running it

Serve the directory over HTTP and open `index.html`. It needs no build step.
Everything is plain ES modules.

    python3 -m http.server 8000

**You must supply the ROMs yourself** — see [ROMS.txt](ROMS.txt). They are not
distributed here.

## Loading a program from tape

The deck is at the bottom right. Press **insert** and pick a tape file, then:

1. Type `LOAD ""` on the machine and press Enter.
2. Press **play**.

That order matters, exactly as it does with a real recorder: the machine has to
be listening before the tape starts. The lamp lights while the motor is
running, and the bar shows how far through the tape has got. If a load fails,
**rewind** plays it again from the start without reselecting the file.

To save, type `SAVE "NAME"` on the machine and wait for it to finish, then
press **save…**. The file is demodulated off the tape line rather than
intercepted, so what you get is the same shape as a tape off real hardware and
loads straight back in.

Loading is not a shortcut around the hardware. The file is turned into a
signal and presented at the cassette input, and the machine's own COP420
microcode demodulates it, so the ROM frames and checksums every block just as
it would off tape. Errors it reports are the real ones: `ERROR 132` is a
checksum failure, `ERROR 131` means the block will not fit the loader's
buffer.

Of the 118 tape images tested, 103 load byte for byte. (A 119th,
`scrn#1.bin`, is a damaged rip — one of its blocks carries a zeroed checksum —
so it is reported as such rather than counted.) Most of the rest are
machine code or assembler output rather than BASIC — `.COM`, `.BIN`, `.S`,
`.O` — which BASIC's `LOAD` cannot accept whatever the tape does; the bytes
arrive intact and the ROM declines them.

## State

| | |
|---|---|
| Z80, memory map, ROM paging | working |
| CRT, 40/80 column | working |
| VF display, 16 characters | working |
| Keyboard | working — COP420 scans the matrix |
| Cassette loading | working — 103 of 118 tape images load byte for byte |
| Cassette saving | working — `SAVE` then **save…** downloads a tape file |
| Disc loading | not started — needs the FDC expansion |
| Sound | the machine has none |

It boots to `NEWBRAIN BASIC` / `READY` and you can type at it.

### Accuracy notes

Two constants in `src/newbrain.js` — `VIDEO_START` and the row stride — are
**empirical rather than derived**. The hardware walks a flag-driven structure
where a `00` byte ends a row, a frame, or starts graphics; that walk is not
correctly ported yet, so the two values are pinned against known-good output
instead. They are right, but not yet explained.

The row stride is **columns + 8**, not the 2 x columns MAME uses. MAME's
`newbrain_v.cpp` carries a TODO about accurate video timing, and the driver
only became `working` after release 0.229.

## Testing

The core is testable without a browser:

    node test/memmap.test.mjs      # memory map and I/O decode
    node test/boot.test.mjs        # runs the real boot ROM
    node test/screen.test.mjs      # renders a frame
    node test/cop420.test.mjs      # runs the COP microcode

## Licence

GPL-3.0-or-later, see [COPYING](COPYING). Third-party components and the
sources this was reimplemented from are recorded in
[ATTRIBUTION.md](ATTRIBUTION.md).
