# The expansion slot, and the disc system

This emulator is a NewBrain AD as it left the factory, so nothing is fitted in
the slot. The slot itself is wired, and this is what was learned trying to put
a disc controller in it — what the hardware is, what was built and verified,
and what defeated it.

It is written down because none of it is documented publicly. The block format
of a NewBrain *tape* is [published][tapefmt]; its disc hardware is not, and
what follows was read out of MAME's driver and measured against the real ROMs.

[tapefmt]: https://newbrainemu.eu/2026/08/19/newbrain-tape-block-format/

---

## The slot

A card is bank 4 of the machine's address space — `0x8000-0x9FFF` — and that is
the only part of the map it gets to itself.

The arbitration is simpler than it looks. On every memory access the machine
asks the card **first**, then the main board answers over the top wherever the
board owns the address:

    banks 0-3   the board's RAM wins
    bank  4     nothing on the board matches, so the card's answer stands
    banks 5-7   the board's ROM wins

Which is why a card only ever needs to answer bank 4, and why an empty slot
reads as `0xFF` without anything having to arrange it.

A card in this emulator supplies three methods and is fitted with
`machine.fitExpansion(card)`:

| method | when |
|---|---|
| `hostRead(addr)` | bank 4 read, `addr` is `0000-1FFF` |
| `hostWrite(addr, v)` | bank 4 write |
| `hostControl(v)` | write to port `FF` with address line 9 high |

That port decode is worth noting: Z80 I/O carries the B register on the top
half of the address bus, so A9 is real and a card can decode more of the bus
than the machine's own ports do. A handler that masks the port to 8 bits
before testing will never see it.

---

## The disc controller

It is not a peripheral chip. It is a **second computer** on the end of the bus:

    Z80 @ 4MHz              its own CPU
    d417-1.rom / d417-2.rom its own 8K ROM (issue 1 / issue 2; MAME runs 2)
    uPD765A @ 8MHz          the floppy controller
    4 drive connectors      5.25" DD or QD, standard MFM

### What the controller's Z80 sees

    mem  0000-1FFF   its own ROM, mirrored up to 7FFF
         8000-FFFF   a window onto the NewBrain

    io   (address masked to 0x71)
         00-01       uPD765A status / data
         20          auxiliary, write
         40          control, read

The window is how the two machines share memory. The address it reaches is
`(PA15 << 15) | offset`, and when the host is paging the bank goes on top as
`(MA16 << 16) | addr`. PA15 is set by the card's own Z80; MA16 by the host.

**Auxiliary, written by the controller (port 20):**

    bit 0   MOTON        drive motor
    bit 1   765 RESET
    bit 2   TC           terminal count, ends a transfer
    bit 5   PA15         which half of the host's space the window shows

**Control, read by the controller (port 40):**

    bit 5   FDC INT      the 765 wants attention
    bit 6   PAGING
    bit 7   FDC ATT      the host wants attention

### What the host sees

Bank 4, split:

    0000-1BFF   the d413 ROM
    1C00-1FFF   1K of RAM shared between the two machines

There are **no host-side I/O ports** for the card beyond the control register.
Work is passed through that shared kilobyte.

**Control register, written by the host (port FF, A9 high):**

    bit 0   PAGING
    bit 2   MA16
    bit 3   MPM
    bit 5   _FDC RESET   low holds the controller's Z80 in reset
    bit 7   FDC ATT

---

## Discs

Geometry, from the `dir2dsk.py` in [shaeon/newbrain][shaeon] (GPL-3):

| | 200K | 400K | 800K |
|---|---|---|---|
| cylinders | 40 | 40 | 80 |
| heads | 1 | 2 | 2 |
| sectors per track | 10 | 10 | 10 |
| sector size | 512 | 512 | 512 |
| reserved tracks | 2 | 2 | 2 |
| block size | 2048 | 2048 | 2048 |
| directory entries | 64 | 64 | 128 |
| blocks (DSM+1) | 95 | 195 | 395 |

[shaeon]: https://github.com/shaeon/newbrain

Sectors sit on the track as **1, 6, 2, 7, 3, 8, 4, 9, 5, 10** rather than in
order, so the next sector CP/M wants has come round by the time it asks. The
controller reads by sector ID, so a disc held in memory can key on the ID and
leave the interleave to whoever writes an image file — but an image written in
plain order will be read in the wrong sequence, which looks like corruption
rather than like a layout problem.

The container is EDSK. A 64-byte disc specification block sits at track 0,
sector 1.

### ▲ The CP/M extent trap

A directory entry carries sixteen block pointers. With 2K blocks that is
**32K — two of CP/M's 16K extents, not one.**

So `EX` counts in extents while an entry covers two of them, and `RC` is the
record count of the **last** extent the entry holds. Advancing `EX` once per
128 records while allocating sixteen blocks per entry produces entries whose
extent number has run ahead of their blocks — the second entry of a file comes
out as `ext=2 rc=26 blocks=` with nothing in it, and **every file over 16K
reads short**.

This costs an hour to find and is invisible on small files, because a file
under 16K never reaches a second extent. Test with something over 32K.

---

## What was built, and verified

All three stand up on their own. They are kept outside this repository, at
`newbrain-fdc-experiment/`, since nothing ships in the slot.

**The controller's Z80 runs.** It boots `d417-2.rom`, initialises — two writes
to the auxiliary port — and settles into a tight loop polling the control port
for `FDC ATT`. That is a disc controller idling correctly with no host talking
to it.

**The uPD765A reads.** `SPECIFY`, `RECALIBRATE`, `SEEK`, `SENSE INTERRUPT
STATUS`, `READ ID` and `READ DATA`, driven by hand exactly as the controller's
Z80 drives them — poll the status register, push command bytes, pull the
result. Reading cylinder 1, head 0, sector 1 of a disc built below returns the
CP/M directory: `ADV.COM`, `ADV.DOC`, `ADVD.SAV`, matching the disc.

Note the controller's Z80 polls and moves every byte itself; there is no DMA
controller in the card, so the chip's execution phase hands bytes over one at
a time with RQM and EXM set.

**Discs build.** A CP/M filesystem from ordinary files, with the geometry
above. A 41K file spanning two directory entries round-trips byte for byte
through a parser sharing no code with the writer.

---

## What defeated it

**The host never used the card.** `FDC ATT` was never raised and the control
register never written, so the handshake across the shared RAM was never
begun. Every sector read above came from a harness standing in for the
controller's Z80, not from the NewBrain.

**Fitting a card stops the machine booting**, and this is the thing to solve
first. It was isolated cleanly:

    no card at all                     NEWBRAIN BASIC / READY
    card answering 0xFF                NEWBRAIN BASIC / READY
    card answering the real d413 ROM   garbage, and no boot

and it behaves the same on **all five BIOS revisions** — issue 1, issue 2,
issue 3, series 2 and the v2.0 set.

So the slot wiring is right: a card that answers like an empty slot is
indistinguishable from one. Something about presenting the d413 ROM's actual
contents at bank 4 is wrong, and it is not the ROM revision.

Candidates not yet ruled out:

- the d413 image wants a different offset or masking than `addr & 0x1fff`
- `raminh`, `exrm` or `mpm` are being supplied as constants where the real
  card drives them, so the board is answering where it should defer or the
  reverse
- the machine wants RAM in that region once a disc system is present, and a
  disc machine is simply a different configuration

Worth saying plainly: during this the host was observed reading bank 4 nearly
fourteen thousand times, which looks like a card being found and used. It is
not — the host spends 99.7% of its time in bank 7 and only reads the card. **A
read count is not a handshake**, and the useful signal is in the first dozen
accesses and the branch the ROM takes after them, not in the total.

---

## Where things come from

ROMs are in MAME's `newbrain_fdc` set: `d413-2.rom`, `d417-1.rom`,
`d417-2.rom`. They are not distributed here, as with every other ROM.

**No disc images are published anywhere I could find.** newbrainemu.eu has a
CP/M bootdisk — Teledisk format, holding 200K, 400K and 800K images — behind a
registration whose validation email does not arrive. shaeon's repository ships
conversion tools but no images and no ROMs. Museum catalogues list physical
5.25" disks only.

Building one is the realistic route, and the geometry above is enough to do
it. A disc built from files is readable but **not bootable**: booting CP/M
also needs a system on the two reserved tracks, which means CCP and BDOS plus
a NewBrain CBIOS that does not exist publicly and would have to be written.

The hardware arrangement here is read from MAME's `newbrain` FDC device
(BSD-3-Clause, Curt Coder); the disc geometry from shaeon's `dir2dsk.py`
(GPL-3). No code from either was copied. See [ATTRIBUTION.md](ATTRIBUTION.md).
