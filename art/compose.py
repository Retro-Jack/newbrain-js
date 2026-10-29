#!/usr/bin/env python3
"""Prepare the NewBrain layout: a Microvitec CUB bezel and the machine, on
transparency so whatever is behind the page shows through.

The two are emitted as SEPARATE images rather than one composite, because a
composite fixes their arrangement into the pixels: the page cannot then move
the machine below the monitor on a narrow window, or size either to suit. So
each part ships on its own, and regions.json carries two kinds of number --
where each part sits on a nominal 1920x1080 stage, and where its screen sits
WITHIN ITSELF. The second kind is what matters: a region given as a percentage
of its own part travels with that part wherever the page puts it.""" 
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080

cub = Image.open(f"{HERE}/src/Microvitec-CUB.png").convert("RGBA")
nb  = Image.open(f"{HERE}/src/NewBrain.png").convert("RGBA")

# The monitor reads as the main object, so give it the height and sit the
# machine in front of it on the right, overlapping the baseline slightly.
# The monitor carries the content, so it gets the size; the machine only has
# to stay legible, and sits lower as if in front of it.
CUB_H  = 760
cub_s  = CUB_H / cub.height
cub    = cub.resize((round(cub.width * cub_s), CUB_H), Image.LANCZOS)
CUB_X, CUB_Y = 55, 135

NB_W   = 890
nb_s   = NB_W / nb.width
nb     = nb.resize((NB_W, round(nb.height * nb_s)), Image.LANCZOS)
NB_X, NB_Y = 985, 455

assert CUB_X + cub.width  <= W, "monitor overflows the canvas"
assert NB_X  + NB_W       <= W, "machine overflows the canvas"
assert NB_Y  + nb.height  <= H, "machine overflows the canvas" 

cub.save(f"{HERE}/cub.png")
nb.save(f"{HERE}/machine.png")

# --- locate the regions in final canvas coordinates ----------------------
# Per tools/bezel-test/README.md: compare a bezel's picture against the largest
# rectangle INSCRIBED in the hole, not the hole's bounding box. The hole is a
# rounded rectangle, so the bbox overshoots into the bezel and clips the edge
# columns — recorded there as the Electron showing "orn Electron"/"3ASIC", and
# it cost me the same bug here ("IN BASIC" for "NEWBRAIN BASIC").
#
# Two rectangles come out of this:
#   hole - the aperture's bounding box, which the black backing fills so the
#          rounded corners show screen rather than page background
#   crt  - the largest inscribed rectangle, where the picture goes
#
# Measured on the SOURCE bezel then transformed: measuring the resized copy
# picks up LANCZOS edge pixels. Note the CUB also has a second transparent
# region BELOW its bottom frame, so the aperture must be taken as the largest
# contiguous band of hole rows, never min/max over all matching rows.
cub_src = Image.open(f"{HERE}/src/Microvitec-CUB.png").convert("RGBA")
sp = cub_src.load()
SW, SH = cub_src.size

def flood(thresh):
    """Flood-fill the hole from its centre. The bbox of ALL transparent pixels
    is useless — the area outside the machine is transparent too."""
    from collections import deque
    cx, cy = SW // 2, SH // 2
    assert sp[cx, cy][3] < thresh, "bezel centre is not inside the hole"
    seen = [[False] * SW for _ in range(SH)]
    q = deque([(cx, cy)]); seen[cy][cx] = True
    L = R = cx; T = B = cy
    while q:
        x, y = q.popleft()
        L = min(L, x); R = max(R, x); T = min(T, y); B = max(B, y)
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < SW and 0 <= ny < SH and not seen[ny][nx] and sp[nx, ny][3] < thresh:
                seen[ny][nx] = True; q.append((nx, ny))
    return L, T, R, B, seen

# Two thresholds: <32 is the hole proper, <250 includes the feathered ramp.
iL, iT, iR, iB, inner = flood(32)
oL, oT, oR, oB, _     = flood(250)
print(f"# hole inner {iL},{iT}..{iR},{iB}  outer {oL},{oT}..{oR},{oB}  "
      f"feather L{iL-oL} T{iT-oT} R{oR-iR} B{oB-iB}")

# Largest rectangle inscribed in the hole, for the picture.
best = (0, 0, 0, 0, 0)
heights = [0] * SW
for y in range(iT, iB + 1):
    for x in range(SW):
        heights[x] = heights[x] + 1 if inner[y][x] else 0
    stack = []
    for x in range(SW + 1):
        ch = heights[x] if x < SW else 0
        sx0 = x
        while stack and stack[-1][1] >= ch:
            sx, sh = stack.pop()
            if sh * (x - sx) > best[0]:
                best = (sh * (x - sx), sx, y - sh + 1, x - 1, y)
            sx0 = sx
        stack.append((sx0, ch))
_, rL, rT, rR, rB = best
print(f"# inscribed {rL},{rT}..{rR},{rB}   (README records 85,73..753,637)")

def in_cub(L, T, R, B):
    """A rectangle on the CUB source, as a percentage of the resized CUB."""
    return {"left":   round(100 * (L * cub_s) / cub.width,  4),
            "top":    round(100 * (T * cub_s) / cub.height, 4),
            "width":  round(100 * ((R - L + 1) * cub_s) / cub.width,  4),
            "height": round(100 * ((B - T + 1) * cub_s) / cub.height, 4)}

# The backing fills the OUTER bound: if it stopped at the inner one, the
# feather's part-transparent ink would composite with whatever is behind the
# page instead of the backing, and show as a bright fringe the moment the
# backing is not black. (feedback-magenta-bezel-check, the Apple finding.)
hole = in_cub(oL, oT, oR, oB)
crt  = in_cub(rL, rT, rR, rB)
assert hole["top"] + hole["height"] <= 100.5, "hole escapes the bezel"

# VFD: the tube's sixteen cells on the source photo, mapped through the same
# scale and offset. Hunting for the dividers by threshold does fail - the photo
# lights the tube unevenly and the glass is scratched - but detrending the
# column profile and autocorrelating it gives the pitch cleanly: 21.0px, with
# boundaries at 552, 573, 594 ... 888. Sixteen cells is therefore 552..888.
# The lit band is rows 101..130; the bright rows at either end of that are the
# cells' own rims, not glyph space.
#
# The earlier figures were half a cell out horizontally, which told as glyphs
# sitting across the dividers rather than inside the cells.
SRC_VFD = {"x": 552, "y": 101, "w": 336, "h": 30}
vfd = {"left":   round(100 * (SRC_VFD["x"] * nb_s) / nb.width,  4),
       "top":    round(100 * (SRC_VFD["y"] * nb_s) / nb.height, 4),
       "width":  round(100 * (SRC_VFD["w"] * nb_s) / nb.width,  4),
       "height": round(100 * (SRC_VFD["h"] * nb_s) / nb.height, 4)}

def place(x, y, w, h):
    """Where a part sits on the nominal stage, as percentages of it."""
    return {"left": round(100 * x / W, 4), "top": round(100 * y / H, 4),
            "width": round(100 * w / W, 4), "height": round(100 * h / H, 4)}

regions = {
    "stage": {"w": W, "h": H},
    "cub": {
        "src": "cub.png", "w": cub.width, "h": cub.height,
        "place": place(CUB_X, CUB_Y, cub.width, cub.height),
        "hole": hole, "crt": crt,
    },
    "machine": {
        "src": "machine.png", "w": nb.width, "h": nb.height,
        "place": place(NB_X, NB_Y, nb.width, nb.height),
        "vfd": vfd,
    },
}
json.dump(regions, open(f"{HERE}/regions.json", "w"), indent=2)
print(json.dumps(regions, indent=2))
