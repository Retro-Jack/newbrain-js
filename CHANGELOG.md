# Changelog

All notable changes to this project are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **A nudge when the tape stops between files.** On a tape with more than one
  file, the machine reads the first and goes back to the prompt, where it will
  sit until told what to do. The readout now says so rather than leaving the
  deck looking stalled.

  The prompt is read off the screen. It began as a guess from the transport
  -- motor stopped longer than a block gap -- and the guess was wrong often
  enough to matter: loading Pacman the gaps between blocks run 0.18s, 2.70s
  and 3.72s, and a 3s threshold duly fired in the middle of the 3.72s one,
  telling the user to type something while the tape was still going.

  The machine will simply say, though. Its display is characters in RAM, 40
  to a row on a 64-byte stride, in plain ASCII, and the cursor is 0x7F.
  Measured across a whole load: 0x7F never appears while the tape is
  reading, never appears during either block gap, and blinks steadily
  through the 13s at the prompt. It is remembered for 800ms rather than
  tested outright, because it is dark for about 280ms at a time.

  That also makes it four times quicker to speak up -- 1.56s after the tape
  stopped, against 6.06s for the timer it replaced.

  It does not say which command, because the deck cannot know: a plain
  multi-file tape wants `LOAD ""` again, while a tape fronted by a loader --
  Pacman is one -- wants `RUN` and then fetches the rest itself.

- **"No tape" now says what to do about it**, across two lines with a blank
  between them:

  ```
          No tape

   Press eject to insert
  ```

  The eject button is how a tape gets in, and that was only discoverable
  from a tooltip, which is a hover away and no use at all on a phone. The
  second line borrows the count's row, moved from six to five so the pair
  straddles the middle row and the block stays centred. "Press eject to
  insert" is exactly twenty-one characters, so it fills the grid without
  having to scroll.

- **"Please wait." while the motor is stopped mid-load.** A load is not one
  continuous run of tape: the ROM stops the motor between blocks while it
  digests what it has just read, and on a long program that pause is easily
  long enough to look like something has gone wrong. Measured on a real load
  of `tycoon.bas`, the first one lasts 1.7 seconds and arrives 6% in. The
  readout now says so, and goes back to "Playing." when the tape moves again.

  Only transitions are announced and the first reading is adopted in silence,
  so this cannot talk over the hint the button press just set -- "Rewound;
  playing from the start." survives until the motor actually changes state.

- **The deck shows its bay when there is no tape in it** -- spindles, heads,
  capstan and pinch roller, instead of a cassette that is not there. It is a
  second photograph of the same machine, laid over the first and revealed
  when the deck is empty rather than swapped in as a `src`, so both are in
  the document from the start and the bay does not arrive a frame late the
  first time a tape is ejected. The reels go with it: they belong to the
  cassette, not the deck, so there is nothing for them to be drawn on.

  It follows the same count the readout does, so the picture and the words
  cannot disagree about whether a tape is in.

  `art/make-deck-empty.py` builds it, and the awkward part is colour, not
  collage: the render is still the original purple while the shipped deck has
  been graded to a warm near-monochrome. The grade is measured rather than
  guessed -- the bay's own frame appears in both images untouched, so binning
  the render's luminance against the shipped deck's channels over that frame
  recovers it as three curves. A strip of frame is held out of the fit and
  the residual printed, so drift shows up as a number.

  Two things in there not to undo. The bay is composited into `deck.webp`
  rather than re-exported from the master, because `deck.webp` is that master
  downscaled and then embossed with the transport symbols -- re-exporting
  drops them. And the render's spindles sit wider apart than the cassette's
  hubs, so they are moved onto them.

  Clearing the wells they leave behind took three goes. Cloning wall from
  above left a lighter circle, because the only clean wall is an 80px band
  that is too short for the disc and has a gradient of its own. Fitting a
  surface to the ring outside the disc fixed that but left a faint arc round
  each spindle: the well is sunk into the wall and lifts a halo 3 to 5 levels
  high that is still there at r=105, and a disc cannot open wide enough to
  swallow it without eating the raised panel between the hubs. So the halo is
  now measured in rings -- outliers dropped so the panel does not drag the
  mean -- and subtracted with a taper to nothing, before the disc is filled.
  No boundary left for an arc to form on: the dome across r=45 to r=125 falls
  from 3.0 and 4.7 levels to 1.3 and 1.8, under the wall's own grain.

### Changed
- The top line steps when it scrolls, a character at a time, rather than
  gliding. A real readout shifts its buffer by a cell; it has no way to move
  half of one. The travel is one period -- the span holds the text and its
  separator twice, and -50% is exactly one of them -- so a `steps()` of that
  period's character count moves precisely one character per step. The
  reading pace is unchanged at about three characters a second; it is the
  same duration, quantised. Measured over 110 samples: eleven distinct
  positions, every one a whole number of characters, nothing in between.

- The readout is laid out on a character grid: seven rows of twenty-one
  columns, which is what it always was pretending to be. The rows are grid
  tracks, so they are equal because the grid makes them so, rather than
  because a line-height was tuned until they looked it. Each line is pinned
  to its own row, so one that is hidden leaves its row empty instead of
  pulling the rest up.

  This replaces a flex column whose rules were zero-height elements with a
  margin above and below, which made the gap at a rule about twice the gap
  between two lines of text. The rules are now twenty-one actual hyphens
  rather than a dashed border, the full width of the grid, which the
  progress bar and the count line span too -- so every full-width line
  starts and ends on the same column. The bar carries nineteen cells
  between its brackets to do it, up from eighteen.

  What made the count line sit half a character to the left of the bar and
  the rules was not the centring: the count ran the full twenty-one columns
  while they ran twenty, and any two lines of unequal parity centre half a
  cell apart. Widening the rules and the bar to the grid fixes it at the
  source -- all three now start on column 0 and end on column 21 whatever
  centres them -- and leaves the short lines free to be centred properly.

  The grid is centred on its ink, not on its cells. Seven rows fill the
  window exactly, so the cells are flush to both edges -- but the ink inside
  them is not centred in them. Measured across the printable set it runs
  from the very top of the cell, which the quote marks reach, to 1.93px
  short of the bottom, where the descenders of g j p q y stop. The readout
  therefore sat hard against the top of the window with a gap beneath it,
  top-heavy by 0.138 of a row, and `Type  LOAD ""  then press play.` put
  those quotes in row one against the edge. The rows carry half that back,
  0.0692em, which measures out at 0.95px clear above and 0.98px below.

  Sizing falls out of the grid instead of being chosen: the type is a row
  high (`100cqh/7`), and since this face is 9x16 with ascent and descent
  coming to exactly 1em, the character grid and the glyph grid become the
  same grid. Columns come from `ch`, which tracks the advance the rasteriser
  actually uses -- 0.562 of a row, not the 0.5625 the font file designs for,
  because Chrome quantises advances; measured, 21ch and 21 advances agree
  exactly, which is all the grid depends on. Twenty-one
  columns is both what fits and the longest line the readout can show. The
  type ends up slightly larger than before, 7.9cqw against 7.8, because the
  grid's gutter replaced a hand-set padding that was costing more.

  Two details that do not show until they are wrong. The unit goes on the
  children, not on the window: the window is the container those units
  resolve against, and a container query unit used on the container itself
  resolves against its ancestor instead. And the name and hint rows need
  `vertical-align:top`, because they hold an inline-block for the scrolling
  and an inline-block sits on the baseline, which would stand their content
  a quarter of a row proud of a cell that cannot grow to take it.

  A fixed grid does not re-centre what is left on it, so with no tape in the
  deck "No tape." would sit on the name's row -- row three of seven, one row
  above the middle. In that one state it drops to row four instead, sharing
  the cell with a progress bar that has nothing in it while the deck is
  empty, and lands dead centre.

  Sharing a cell means naming the column. An item with an explicit row but
  an automatic column is not stacked, it is placed in the next free column,
  so the two lines on row four quietly made the grid two columns and twice
  the window wide -- and every line in that state sat flush against the left
  edge rather than centred. Both axes are pinned now, and the column track
  is declared rather than left implicit.

- The readout's messages are in sentence case and punctuated, as are the
  status line, the button tooltips and the link beside them. The file count
  and the note below it are now one sentence across two rows -- "20 files on
  the tape," then "in that order." -- so a single file ends its line with a
  stop instead of a dangling comma. The longest line the window has to hold
  grows by the full stop, from twenty characters to twenty-one, which is what
  the type size is set against.

- The monitor and the machine now use the shared bezels byte for byte, the
  same files GenX-DOS serves from `systems/_shared/bezels/`. Both were
  already rendered from those exact sources; `compose.py` was re-sizing them
  on the way through and committing a second copy of the same picture. It no
  longer does, so there is one image rather than two. The CUB loses a little
  resolution (883 to 835 wide, still well above the size it draws at) and the
  machine gains a lot (890 to 1060).
- The cassette indicator's artwork is removed with it: `art/cassette.png`,
  `art/cassette-reels.png` and the credit beside them. The deck replaced it.

- The deck's artwork is toned down to sit with the other two machines:
  saturation to 40%, a slight warm shift, and the blazing rim lights
  pulled back. It was the loudest thing on the page and the least
  important — the monitor, which is what you actually read, was the
  dimmest. The readout's green is now the brightest thing on the deck,
  which is the right way round.

### Added
- The deck's window is a readout: what is on the tape across the top,
  scrolling when the names are too long to fit, then a rule and the
  file count with a note that they load in that order. Green, in the
  house DOS font, sized to hold a two-digit count.

### Changed
- The cassette indicator is now a cassette deck on the stage, above the
  machine and sharing its width and left edge, in the space the monitor
  and the machine left empty. The little cassette in the controls panel
  is gone: it did the same job in a tenth of the room, too small to read
  the reels turning. Same binding — play or save engages the transport,
  then the reels follow the motor — and the same sprite-sheet trick, 37
  rows for 36 frames so the steps land on exact frames.

### Removed
- The green motor lamp on the cassette deck. The turning reels say the
  same thing and say it plainly, so the lamp was a second indicator of
  the same state needing its own explanation.

### Added
- The cassette deck shows a cassette whose reels turn while the tape is
  running. Play or rewind engages the transport and save does too; after
  that the reels follow the motor, so they stop between blocks as the tape
  does and stop altogether when it ends. The motor line alone will not serve
  as the cue — typing `LOAD ""` raises it and holds it high while the
  machine waits for a signal, with nothing in the deck and nothing moving.
  Only the reels and the tape window ever move, so the shell is one still
  image and just that box is a sprite sheet driven by `steps()`: 98KB of PNG
  against 2.7MB of animated GIF, and unlike a GIF it can be stopped and
  started. Respects `prefers-reduced-motion`.

### Fixed
- `tools/detokenise.py` reversed the whole block stream instead of each
  block's payload. Output looked right line for line but spliced every line
  that straddled a block boundary, which invented 216 "damaged lines" across
  26 of the library's programs. Caught by running one of them in the
  emulator: the program the decoder called broken played perfectly. 48 of
  the 49 programs read clean.

### Added
- `tools/detokenise.py` — reads a NewBrain BASIC tape back to source. The
  format is undocumented anywhere we could find: a tape is a run of counted,
  checksummed blocks, the program body is stored byte-reversed whole, and
  keywords are single bytes carrying two meanings each depending on whether
  they open a statement. The two token sets are transcribed from the Grundy
  Software Technical Manual. Recovers 47 of the 48 BASIC files in the local
  library; the 48th turns out to be machine code under a `.bas` name.
- Z80 memory map with ROM paging, including the power-up behaviour where every
  access decodes as bank 7 until PWRUP rises on its 5.6 second RC delay.
- I/O port decode: CLCLK, COP microbus, ENRG1, TVL, TVTL and UST.
- CRT renderer — 640x250, 40/80 column, monochrome, scanline-major
  character ROM.
- VF display: reads OUTBUFF and draws 16 cells in Segment16C, with unlit
  segments faint beneath and a tunable brightness gain.
- COP420 CPU core (`src/cop420.js`), running the real microcode with MAME's
  two BAD_DUMP repairs applied in memory. Includes the SK sync pulse, which
  ticks once per instruction while EN0 is clear and SKL is set, and is what
  clocks the VF display's serial register.
- Keyboard, working: the COP420 scans the 16x4 matrix and keypresses reach
  both BASIC and the VF display. Browser keys are mapped by physical
  `event.code`, so the layout does not depend on the host keymap.
- Bezel layout generated by `art/compose.py`, which emits `regions.json` so
  the page positions the picture and the VF display from measured values
  rather than hand-tuned CSS.
- Cassette loading (`src/tape.js`). A tape image is turned into a signal and
  presented at TPIN; nothing intercepts the COP, so the real microcode
  demodulates it and the ROM does its own framing and checksumming, exactly as
  it would off a real cassette. The encoding was measured from recordings the
  machine made of itself and verified by decoding them back: a 1 is two cycles
  of the high tone, a 0 one cycle of the low tone, and each byte is framed
  start bit 1, eight data bits most significant first, stop bit 0. The leader
  runs out one half cycle into its group before the first frame, and without
  that half cycle nothing decodes at all. The two cells are not the same
  length — a 1 runs 3328 T-states against a 0's 3448 — and forcing them equal
  on the reasoning that a fixed-window demodulator would need it makes long
  programs fail a checksum partway through. The figures are measured.
- Tape files whose last block has a truncated trailer load anyway: those nine
  bytes are laid down by the writer and never read back.
- Cassette motor, driven from the COP's G1 and K6 through a relay with a 38ms
  dropout. The ROM stops the motor between blocks while it stows one away, so
  the tape stops with it — which is what makes long multi-block programs load
  rather than running on past the ROM while it is busy.
- Cassette deck in the page: insert a tape file, play, rewind and eject, with a
  lamp that lights while the ROM has the motor running and a bar showing how
  far the tape has got. Buttons blur themselves after a click, or Space and
  Enter would work the button instead of reaching the machine's keyboard.
- Published to GitHub Pages by a workflow that unpacks the ROMs from a secret
  at build time, so they reach the deployed site without ever reaching git.
- A missing ROM now says so on the page. Anyone who has just cloned this has
  no ROMs, and the page used to sit on "booting..." for ever instead.
- README points at the published site, which it did not once there was one.
- ATTRIBUTION names the two shipped font files, and says that the MAME paths
  it lists are MAME's own with a local reading copy in `reference/`.
- Draw only when the machine has moved on, rather than once per
  `requestAnimationFrame`. The emulation was already paced against the clock,
  so timing was right, but a 180Hz panel redrew each 50Hz frame 3.6 times over
  for a picture that could not have changed. The frame counter now measures
  draws, so the figure in the corner reads about 50.
- CRT draws white rather than green. The NewBrain has no colour hardware at
  all — MAME models it as a monochrome palette and the machine sends plain
  luminance out of its UHF and monitor sockets — so the colour was always the
  display's, never the computer's. The bezel here is a Microvitec CUB, which
  is a colour monitor, and a colour monitor fed a monochrome signal shows
  white. The code had claimed the CUB was a green monitor, which it is not.
  The white is warmed a little — a tube's white is never a perfect neutral,
  and a cold one sits badly against the brown surround — at the same
  luminance, so only the tint moves.
- Cassette saving. What the machine writes is captured off the tape line and
  demodulated, the exact inverse of loading, so nothing intercepts the COP in
  either direction and the file carries the 00 the COP puts in front of each
  block. `save...` on the deck downloads it, named after the tape's own name
  block. Verified by saving a program and loading the result into a fresh
  machine, which lists it back unchanged.
- Machine artwork shows an English keyboard. The photograph it had been built
  from is a French machine — AZERTY, with QSDFGHJKLM beneath — so the picture
  was teaching a layout the emulator does not map. The VF tube is unchanged,
  and the measured regions come out identical, so nothing else moved.
- VF glyphs sit inside the tube's cells. The region had been eyeballed off the
  artwork and was about a third of a cell out horizontally and three rows high,
  so the characters straddled the dividers. The photo defeats threshold hunting
  — uneven lighting, scratched glass — but detrending the column profile and
  autocorrelating it gives the pitch cleanly at 21.0px, boundaries at 552
  through 888, and the lit band at rows 101..130.
- ATTRIBUTION says what the machine artwork is made of. The body and VF tube
  are a Wikimedia Commons photograph by Rama & Musée Bolo, CC BY-SA 2.0 FR,
  which `newbrain.png` inherits as a derivative; the replacement keyboard is from
  the Home Computer Museum, which states no licence, and that is recorded as
  such rather than glossed. The CUB frame is jsbeeb's `public/images/cub-monitor.png`, byte
  for byte, GPL-3.0-or-later, and ships as `cub.png`. CC BY-SA and the GPL do
  not mix, so the two are kept as separate files and never composited: each
  stays wholly under its own licence and no combined work is made.
- The monitor and the machine are separate elements. They had been baked into
  one composite image, which fixed their arrangement into the pixels: the page
  could not move the machine below the monitor on a narrow window, or size
  either to suit. Each ships as its own image now, and each screen region is
  given as a percentage **of its own part** rather than of the page, so a
  screen travels with the part it belongs to. Below 900px the two stack and
  take the width, and nothing about the screens needs restating to make that
  work.
- VF panel is drawn at the size it is actually shown, and redrawn when that
  changes. Its backing store had been sized off the nominal 1920 stage, so on
  a narrower window it was a 282px bitmap squeezed into a 220px box — a 0.78x
  downscale, and `image-rendering: pixelated` on a downscale drops whole
  columns and eats parts of strokes. The same trap cost glyphs on the CRT
  before. The panel is drawn rather than blitted, so it simply draws at the
  real resolution now and the pixelated hint is gone.
- Tape sweep counts honestly. Files whose block chain did not consume them
  exactly were dropped without a word, so four never appeared in any figure:
  three merely have a final trailer cut short, which the loader has always
  tolerated, and all three load. The fourth, `scrn#1.bin`, is a damaged rip
  carrying a zeroed checksum, and is now reported as damaged rather than
  quietly omitted. 103 of 118 load byte for byte, where the old filter said
  100 of 115.
- README says what is being emulated: a NewBrain AD as it shipped. The disc
  system was an expansion card rather than part of the machine, so its absence
  is a decision rather than a gap.
- Expansion slot wired, and left empty. Bank 4 is the only part of the map a
  card gets to itself, and a card answering 0xFF boots exactly as an empty
  slot does, so the hook costs nothing while it is unused. Fitting a real disc
  controller is known not to work and the source says so rather than leaving
  it to be rediscovered.
- EXPANSION.md documents the disc hardware: the slot's arbitration, the
  controller's two memory maps and four control registers, the disc geometry
  and CP/M layout, what was built and verified, and the boot failure that
  defeated it. The machine's tape format is published elsewhere; its disc
  hardware is not, so this is written down rather than lost.
- Node test suite covering the memory map, boot, rendering and the COP.

- `test/frameend.test.mjs`, which builds a screen by hand and pins the row
  terminator and the frame end against each other: each of them was fixed
  once by a change that broke the other, so neither is safe to check alone.

- PROVENANCE.md, a clean-room statement. ATTRIBUTION records what was used and
  under what terms; this records how the emulator was written — that it derives
  from MAME's BSD-3-Clause driver and Grundy's own Technical Manual, that
  nothing comes from the one closed-source NewBrain emulator that predates it,
  and what anyone can check for themselves rather than take on trust. The
  separation from MAME is not claimed and is not needed: BSD-3 permits the
  reuse. The separation from closed source is real, so it is described instead
  of asserted. Linked from ATTRIBUTION in both directions. The GenX-DOS
  bundle carries its own copy beside its copy of `src/`, so neither
  repository depends on the other; this one is authoritative and the two
  are kept in step.

### Added
- **The deck says when a file is not a tape.** A file with no block chain in
  it contributes nothing to the signal, so it would sit in the list looking
  loaded and simply not be there. Adv's `ADV.BIN` is one — a raw 28K memory
  image rather than a recording, `01 00 0f` where every real tape starts
  `00` and a byte count. The deck now names it instead of letting it pass.

### Fixed
- **"PLAYING" never went away.** The status sat on it for good once a tape had
  been read, because it waited on the signal running out and the signal never
  does: the ROM takes the last block, sees the last-block flag and stops the
  motor, leaving the gap tone behind it unplayed. Nor does it reach the end of
  the block — each carries nine trailer bytes nobody reads, and the motor
  stops part way through them, 78 half cycles short, measured on BreakOut.

  So `encodeTape` now reports where the last block's **payload** ends — count,
  data, type byte, checksum — and the player has `played` beside `finished`.
  The ROM passes that mark 120 half cycles before it stops, so the status
  clears while the deck is still settling rather than hanging. `progress` is
  measured against the same mark, which is also why the bar now reaches full
  instead of stopping a slab short. `test/tape.test.mjs` pins all three.

### Changed
- **The motor lamp is a bead rather than a flat dot**, in `--green`: a
  highlight off the top left, a dark rim, and a slow breath while the motor
  runs, stilled under `prefers-reduced-motion`.

### Changed
- **PROVENANCE sticks to the claim rather than the history behind it.** What
  the work derives from, and what it does not, is unchanged and still the point
  of the document; the account of how that position was arrived at has gone.
  The checkable facts are unaffected — the first commit's date, the deliberate
  divergence from MAME and its test, the tape results — though there are three
  of them now rather than four.

### Changed
- **The cassette deck is one panel now, in the GenX-DOS design language.** It
  was a row of loose controls in a corner; it reads as a deck: what is in the
  machine on the top line, how far through it is in the middle, the transport
  along the bottom, inside a bordered panel. The page takes the landing
  page's tokens — `--crt`, `--panel`, `--amber`, `--green`, `--cyan`,
  `--paper`, `--dim`, `--line` — so the chrome round the machine belongs to
  the same product as the rest of the site. `--vfd` stays separate: that is
  the colour of the real tube, not a UI choice.

- **The progress bar is a row of slanted slabs** that light one at a time,
  after the loading bars those machines' own software used. They are real
  elements rather than a tiled gradient, because a gradient tile clips its own
  slant at each end and sliced the first and last slab; skewing a box leaves
  the whole parallelogram visible. The fill is floored to whole slabs, so no
  slab is ever part lit, and the count lives in `--slabs` alone — the script
  reads it from the stylesheet.

### Changed
- The machine artwork is `art/newbrain.png`, not `art/machine.png`. It sits
  beside `art/cub.png` and the old name said nothing about which machine.
- Pages workflow: `actions/checkout` v4 to v7, `actions/upload-pages-artifact`
  v3 to v5 and `actions/deploy-pages` v4 to v5, all of which now run on
  Node 24 — the old majors were being force-migrated off the deprecated
  Node 20 on every build. The runner is pinned to `ubuntu-26.04` instead of
  `ubuntu-latest`, which began migrating to Ubuntu 26 on 19/10/2026.

### Added
- **Pixel graphics.** Three `00` bytes hand the rest of the frame to a bitmap:
  the flags stop being reset, `videoAddr` runs on linearly instead of returning
  to the row, the character row counter stops, and each byte is eight pixels
  out of `grsr`, least significant bit first. The code for all of that was
  already here, ported from MAME and unreachable — the per-scanline flag reset
  that fixes the column-38 striping also meant `grLine` could never come up.

  The two needs pull in opposite directions, so the reset now applies to text
  rows only. A row whose zero run reaches three latches the region: that one
  scanline starts clean, its own `00`s bring `qc` down part way across, and
  every scanline after it carries the flags exactly as MAME has them.

  Found by Chess, which draws its board this way and came out as blocks and
  stripes. Confirmed against the machine's own state before anything was
  changed — the title frame's row 5 is a run of 40 zero bytes, and with
  `c32_40` set the bitmap behind it reads cleanly at 32 bytes per scanline.
  `test/graphics.test.mjs` pins the switch, that it runs to the bottom of the
  frame rather than for one row, the dark marker on the transition scanline,
  and the bytes-per-scanline stride — the one that shears the picture if it is
  wrong. Each was checked to fail against the renderer as it stood.

### Fixed
- **A tape could only hold one program, so multi-part titles could not load.**
  Chess is a BASIC loader that asks for a 16K binary once it is running, and
  the deck had nowhere to put the second file: `insert` replaced the tape
  rather than adding to it, so the loader ran and then called for a binary
  that was not there. A cassette holds programs one after another, and that is
  now what the deck models — it keeps a list of files and lays them end to end.
  Nothing is needed between them: each file is already a chain of blocks whose
  type byte flags its own first and last, so the ROM reads the loader, stops at
  its last block, and finds the binary's leader exactly where it left off.

  The file input takes several files at once, and once a tape is in, `insert`
  becomes `add` because that is what it then does. The names show in order,
  with the full list on hover.

  Verified end to end in the browser with `Chess loader.bas` + `Chess.bin`:
  the loader reads, `run` starts it, the motor restarts and the tape carries on
  from 9.1% into the binary, and the game comes up — title, author line, and
  `NEWBRAIN CHESS` on the VF panel — and takes its input.

- **The cassette controls were hard to read, and the page could clip them.**
  Two faults with one symptom. Disabled buttons used `opacity:.35`, which
  fades an element's text *and* its background together — 2.3:1 against each
  other, a shape rather than a word, and with no tape in that is four of the
  five controls. They now carry explicit colours at 4.8:1, still clearly
  secondary to the 9.8:1 of an enabled one; the hint line went from 3.3:1 to
  7.2:1 and the row from 11px to 12px.

  The deck, the status line and the hint were also `position:fixed` in the
  viewport's corners, while the stage is a 16:9 box as wide as the page. On
  any window shallower than `width / 1.778` the artwork overflowed and the
  controls floated over the bottom of it — at 1344x729 the machine's bottom
  row of keys was cut off entirely. They sit in the flow below the stage now,
  aligned to its own edges, and the stage is capped to
  `min(1920px, calc((100vh - 92px) * 1920 / 1080))` so a short or wide window
  shrinks the picture instead. Below 900px the stacked layout resets the cap
  and scrolls as before, with the controls last in flow.

- The display ran past the end of the frame. A program marks the end of its
  screen with two 00 bytes, and nothing below that is meant to be drawn; the
  renderer ignored the marker and painted the rows underneath from whatever
  was next in RAM. Tycoon's title screen ends at row 29 and the two scanlines
  below it were showing its BASIC source, which read as a thin strip along the
  bottom of the picture. The frame end is now latched when a row's first run
  of 00 bytes is exactly two, and everything below it is blank.
- Rows whose terminator fell in column 38 rendered on alternate scanlines.
  This appeared while fixing the frame end, by adopting MAME's handling of the
  terminator flags: it carries them between scanlines and restores only qc,
  from qb, which works when two or more bytes follow the 00 but leaves a stale
  low qb behind when only one does. The next scanline then blanks from its
  first column. Column 38 is where BASIC puts the terminator after a
  38-character line — `PRINT "Time and score displayed at the bottom"` from
  BreakOut's instructions — so the hardware cannot work that way. The
  terminator is handled per scanline and the frame end latched separately,
  which is a deliberate divergence from MAME; `renderInto` says why at length.
- VF display read OUTBUFF left to right; the ROM fills it right to left, so
  the panel showed its text reversed.
- COP420: sixteen opcodes were mis-decoded. `0x0c-0x0f`, `0x1c-0x1f`,
  `0x2c-0x2f` and `0x3c-0x3f` are all `LBI`, but the `XIS`/`LD`/`X`/`XDS`
  masks matched them first and stole them. The dispatch is now verified
  against MAME's opcode table for all 256 values.
- COP420: `0x50` is `CAB`, not `AISC 0`. Decoding it as AISC made it a no-op,
  and CAB is what loads the accumulator into B's low nibble before an `OBD` —
  so the scan never moved off row 0.
- COP420: `LQID` and `JID` were falling through to the generic `JP` handler
  on their second cycle, so instead of loading Q from the jump-table entry
  and returning, they jumped — corrupting the return stack. The COP now
  reaches far more of its microcode and drives the D port.
- Row terminator no longer bleeds past its own line. A 00 in a line's last
  column left the 461's flags low at the end of a scanline, which blanked the
  next scanline two cells in, so the row rendered on alternate scanlines only
  and came out striped — the rows where a printed number changed digit width
  were the ones that landed that way. The flags now restart at the top of each
  character row and every scanline of that row is walked from the same state.
  ▲ This drops what the flags carried between rows, which in MAME's model ends
  the frame on two 00 bytes and starts a graphics line on three; both still
  work within a row, and neither is exercised by anything here yet.
- Display walks video RAM from the TVL latch with rows 64 bytes apart in
  40-column mode and 128 in 80, as the hardware counts them. They had been
  pinned to 122 and columns+8, fitted to the boot screen because the real
  figures appeared to render it wrong; they did not, and the screen they were
  fitted to was itself a symptom of the COP mis-executing its microcode at the
  time. Tuned to one known screen they survived a boot banner and nothing
  else: the second line landed in the wrong place and every line after walked
  further across, which put READY at four different offsets once a few returns
  had been pressed, and made a program listing unreadable.
- Picture is fitted to the largest rectangle inscribed in the bezel's aperture
  rather than its bounding box, which was clipping the edge columns.
- Emulation paced against the clock rather than `requestAnimationFrame`, which
  ran the machine 3.6x fast on a 180Hz display.
- CRT blitted through an offscreen canvas with resampling chosen from the
  actual ratio; `image-rendering: pixelated` was dropping columns whenever the
  picture was wider than its box, taking parts of glyphs with it.
- COP420: SIO's two modes were the wrong way round. EN0 set makes SIO an
  asynchronous binary counter that decrements on each low-going pulse at SI,
  debounced over a four-deep sample history; EN0 clear makes it a shift
  register taking SI into its bottom bit. The counter was the one being driven
  as a shift register, and it ignored SI altogether, so nothing could be read
  from the cassette — that counter is how the COP measures the width of each
  half cycle coming off the tape. SO also carried SIO's bottom bit instead of
  its top one.
- Cassette input was not connected. `ustB` returned a constant with the tape
  bit stubbed out, `ustA` had no case for TPIN at all, and the COP's SI pin
  was tied to zero, so the ROM had no way to see a tape even in principle. SI
  now reads TPIN XORed with TDO, as the hardware wires it, and both status
  ports report the tape line.
