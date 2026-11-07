#!/usr/bin/env python3
"""Build deck-empty.webp: the deck with no cassette, showing the bay.

    python3 art/make-deck-empty.py

Inputs are both in the repository, so this reproduces without anything from
outside it:

    art/src/QFX-boombox-empty-bay.png   the render with an empty bay, 1930x815
    art/deck.webp                       the deck we already ship, 1200x507

The problem this solves is that the two are not the same picture. The source
render is still the original purple; the deck we ship has been graded to a
warm near-monochrome. Rather than guess at that grade, it is measured: the
plastic frame around the bay appears in both, untouched, so binning the
source's luminance against the shipped deck's channels over that frame gives
three curves that ARE the grade, whatever it was made of. The curves go on
the bay, and the bay goes in.

Two things worth not undoing.

The bay is composited into deck.webp rather than re-exported from the full
resolution master. deck.webp is that master downscaled and THEN embossed with
the transport symbols on its buttons -- measured, the two differ by a mean of
5.2 and all of it is in the top row. Re-exporting would quietly drop the
symbols. This way every pixel outside the bay is the shipped file's own.

The grade is fitted against a strip of frame held out of the fit, and the
residual is printed. If that number climbs, the curves have stopped
describing the grade and the bay will not match the deck around it.

Note for anyone lining things up: this render puts the spindles 372px apart
at y=440 in master coordinates, while the cassette's hubs in deck.webp are
308 apart at y=457. The two renders disagree. It does not matter today --
the reel animation only runs when a tape is loaded, so the two are never on
screen together -- but do not take the spindles here as the hub positions.
Those are in regions.json.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "QFX-boombox-empty-bay.png")
DECK = os.path.join(HERE, "deck.webp")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "deck-empty.webp")

MW, MH = 1930, 815          # master coordinates, which the boxes below are in
SW, SH = 1200, 507          # what we ship

# The bay opening, generously bounded. It takes some surrounding frame with
# it, and that frame is identical in both, so it lands on itself after
# grading -- which puts the seam on matching pixels rather than on the
# opening's own edge, where it would show.
BAY = (396, 200, 1216, 724)

# Frame to fit the grade on, and a strip held back to check it against.
FIT = [(330, 196, 396, 724), (1216, 196, 1286, 724), (410, 140, 1200, 196)]
HOLD = [(410, 724, 1200, 772)]

NB = 48
bins = np.linspace(0, 255, NB + 1)
mids = 0.5 * (bins[:-1] + bins[1:])

# The render puts the spindles further apart than the cassette's hubs, so they
# are moved onto them here rather than by editing the source, which stays as
# it arrived. All four centres were found the same way -- a spindle and a hub
# are both rotationally symmetric, so the centre is the point whose
# neighbourhood best matches itself turned 180 degrees, which beats hunting
# for the bright ring (that centroid is pulled towards the lit side, and is
# what first had the hubs 17px too low).
SPINDLES = ((614, 434), (986, 434))      # in the empty-bay render
HUBS = ((643, 440), (952, 440))          # in deck.webp, which is what counts
# 66 is where the well stops: the radial profile is spline and rim detail out
# to about 64 and flat wall at 37 beyond it. It also clears the raised panel
# between the hubs at both ends once moved -- 643+66 against a panel starting
# near 720, and 952-66 against one ending near 880.
WELL_R = 66
# A flat stretch of back wall: measured, y 290..370 is the only band in the
# bay with no structure in it (sd about 3, nothing bright). Its mottle is
# what the rebuilt wall is textured with.
WALL_TEXTURE = (520, 295, 1080, 365)


def _disc(h, w, cx, cy, r, soft=2.5):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    return np.clip((r - np.hypot(xx - cx, yy - cy)) / soft, 0, 1)


def _rebuild_wall(out, rgb, cx, cy, r):
    """Replace a disc with the back wall that belongs behind it.

    The wall is rebuilt, not cloned. Cloning was the first attempt and it
    showed: the only clean wall is the 80px band above the spindles, which is
    too short for a disc this size and carries a vertical gradient of its own,
    so the patch landed as a visible lighter circle beside each spindle.

    Instead the lighting comes from a quadratic surface fitted to the ring
    just outside the disc -- which is the real wall, so it picks up the bay's
    shading wherever the disc happens to be -- and the faint mottle comes from
    a high-pass of that flat band, tiled. Smooth fill alone reads as plastic.
    """
    pad = int(r) + 22
    y0, y1, x0, x1 = cy - pad, cy + pad, cx - pad, cx + pad
    sub = out[y0:y1, x0:x1]
    h, w = sub.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    d = np.hypot(xx - pad, yy - pad)
    ring = (d > r + 3) & (d < r + 19)

    X, Y = (xx - pad) / 100.0, (yy - pad) / 100.0
    terms = [np.ones_like(X), X, Y, X * X, X * Y, Y * Y]
    A = np.column_stack([t[ring] for t in terms])
    full = np.column_stack([t.ravel() for t in terms])
    base = np.empty_like(sub)
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(A, sub[:, :, ch][ring], rcond=None)
        base[:, :, ch] = (full @ coef).reshape(h, w)

    tx0, ty0, tx1, ty1 = WALL_TEXTURE
    band = rgb[ty0:ty1, tx0:tx1]
    blur = np.asarray(Image.fromarray(np.clip(band, 0, 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(4))).astype(np.float64)
    hp = band - blur
    reps = (h // hp.shape[0] + 2, w // hp.shape[1] + 2, 1)
    base += np.tile(hp, reps)[:h, :w]

    m = _disc(h, w, pad, pad, r + 1)[:, :, None]
    out[y0:y1, x0:x1] = sub * (1 - m) + base * m


def move_spindles(rgb):
    """Shift each spindle onto the hub it would actually drive."""
    out = rgb.copy()
    pad = WELL_R + 4
    size = pad * 2

    # Lift both out first: erasing one must not eat the other.
    taken = [rgb[cy - pad:cy + pad, cx - pad:cx + pad].copy() for cx, cy in SPINDLES]

    for cx, cy in SPINDLES:
        _rebuild_wall(out, rgb, cx, cy, WELL_R + 2)

    # Then put them back down on the hubs.
    m = _disc(size, size, pad, pad, WELL_R)[:, :, None]
    for patch, (hx, hy) in zip(taken, HUBS):
        here = out[hy - pad:hy + pad, hx - pad:hx + pad]
        out[hy - pad:hy + pad, hx - pad:hx + pad] = here * (1 - m) + patch * m
    return out


_src = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64)
if _src.shape[:2] != (MH, MW):
    sys.exit("expected a %dx%d source, got %dx%d" % (MW, MH, _src.shape[1], _src.shape[0]))
_src = move_spindles(_src)
for (sx_, sy_), (hx_, hy_) in zip(SPINDLES, HUBS):
    print("  spindle (%d,%d) -> hub (%d,%d)   moved %+d,%+d"
          % (sx_, sy_, hx_, hy_, hx_ - sx_, hy_ - sy_))
src_full = Image.fromarray(np.clip(_src, 0, 255).astype(np.uint8), "RGB")
deck = np.asarray(Image.open(DECK).convert("RGBA")).astype(np.float64)

# Fit at the shipped size, so the two sides of the comparison are the same
# scale and the same softness.
src_small = np.asarray(src_full.resize((SW, SH), Image.LANCZOS)).astype(np.float64)
lum_small = src_small @ np.array([0.299, 0.587, 0.114])
sx, sy = SW / MW, SH / MH


def gather(boxes):
    L, C = [], []
    for x0, y0, x1, y1 in boxes:
        a, b = int(round(x0 * sx)), int(round(y0 * sy))
        c, d = int(round(x1 * sx)), int(round(y1 * sy))
        L.append(lum_small[b:d, a:c].ravel())
        C.append(deck[b:d, a:c, :3].reshape(-1, 3))
    return np.concatenate(L), np.vstack(C)


def fit_curves(L, C):
    """Median shipped channel per luminance bin: the grade, whatever it was."""
    idx = np.clip(np.digitize(L, bins) - 1, 0, NB - 1)
    out = np.full((NB, 3), np.nan)
    for b in range(NB):
        m = idx == b
        if m.sum() >= 24:
            out[b] = np.median(C[m], axis=0)
    for ch in range(3):                      # carry across any empty bins
        good = ~np.isnan(out[:, ch])
        out[:, ch] = np.interp(mids, mids[good], out[good, ch])
    return out


def apply_curves(L, curves):
    return np.stack([np.interp(L, mids, curves[:, ch]) for ch in range(3)], -1)


L, C = gather(FIT)
curves = fit_curves(L, C)
print("  grade fitted on %d px of bay frame" % len(L))
for name, boxes in (("fit", FIT), ("held out", HOLD)):
    Lh, Ch = gather(boxes)
    r = np.abs(apply_curves(Lh, curves) - Ch)
    print("  residual, %-9s mean %5.2f   p95 %5.2f" % (name, r.mean(), np.percentile(r, 95)))

# Grade at full resolution, then downscale: grading after the downscale would
# put the curves through averaged pixels and flatten the mechanism's contrast.
lum_full = np.asarray(src_full).astype(np.float64) @ np.array([0.299, 0.587, 0.114])
graded = Image.fromarray(
    np.clip(apply_curves(lum_full, curves), 0, 255).astype(np.uint8), "RGB")
graded_small = np.asarray(graded.resize((SW, SH), Image.LANCZOS)).astype(np.float64)

x0 = int(round(BAY[0] * sx)) + 2
y0 = int(round(BAY[1] * sy)) + 2
x1 = int(round(BAY[2] * sx)) - 2
y1 = int(round(BAY[3] * sy)) - 2
h, w = y1 - y0, x1 - x0
ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
e = np.minimum.reduce([xs, ys, w - 1 - xs, h - 1 - ys])
feather = np.clip(e / 6.0, 0, 1)[:, :, None]

out = deck.copy()
out[y0:y1, x0:x1, :3] = (deck[y0:y1, x0:x1, :3] * (1 - feather) +
                         graded_small[y0:y1, x0:x1] * feather)
# The deck is cut out against the page; the bay is deep inside the silhouette
# and fully opaque, so deck.webp's own alpha carries straight over.
img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
img.save(OUT, "WEBP", quality=92, method=6)
print("  wrote %s  %dx%d  %s  (bay x %d..%d, y %d..%d)"
      % (OUT, *img.size, img.mode, x0, x1, y0, y1))
