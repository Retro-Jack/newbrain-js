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

## Running it

Serve the directory over HTTP and open `index.html`. It needs no build step.
Everything is plain ES modules.

    python3 -m http.server 8000

**You must supply the ROMs yourself** — see [ROMS.txt](ROMS.txt). They are not
distributed here.

## State

| | |
|---|---|
| Z80, memory map, ROM paging | working |
| CRT, 40/80 column, green phosphor | working |
| VF display, 16 characters | working |
| Keyboard | working — COP420 scans the matrix |
| Cassette and disc loading | not started |
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
