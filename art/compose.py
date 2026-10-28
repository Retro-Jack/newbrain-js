#!/usr/bin/env python3
"""Compose the NewBrain layout: Microvitec CUB bezel + the machine, on
transparency so the GenX-DOS wallpaper shows through.

Emits layout.png plus regions.json, so the page positions things from
measured numbers rather than hand-tuned CSS."""
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

canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
canvas.alpha_composite(cub, (CUB_X, CUB_Y))
canvas.alpha_composite(nb,  (NB_X, NB_Y))
canvas.save(f"{HERE}/layout.png")

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

def to_canvas(L, T, R, B):
    return {"x": round(CUB_X + L * cub_s), "y": round(CUB_Y + T * cub_s),
            "w": round((R - L + 1) * cub_s), "h": round((B - T + 1) * cub_s)}

# The backing fills the OUTER bound: if it stopped at the inner one, the
# feather's part-transparent ink would composite with whatever is behind the
# page instead of the backing, and show as a bright fringe the moment the
# backing is not black. (feedback-magenta-bezel-check, the Apple finding.)
hole = to_canvas(oL, oT, oR, oB)
crt  = to_canvas(rL, rT, rR, rB)
assert hole["y"] + hole["h"] <= CUB_Y + cub.height + 1, "hole escapes the bezel"

# VFD: measured on the source photo (the tube's lit cell run), mapped through
# the same scale and offset. Threshold hunting fails here - the photo lights
# the tube very unevenly - so these come from the artwork directly.
SRC_VFD = {"x": 558, "y": 98, "w": 335, "h": 32}
vfd = {
    "x": round(NB_X + SRC_VFD["x"] * nb_s),
    "y": round(NB_Y + SRC_VFD["y"] * nb_s),
    "w": round(SRC_VFD["w"] * nb_s),
    "h": round(SRC_VFD["h"] * nb_s),
}

regions = {
    "canvas": {"w": W, "h": H},
    "crt": crt, "vfd": vfd, "hole": hole,
    "pct": {
        k: {"left": round(100 * v["x"] / W, 4), "top": round(100 * v["y"] / H, 4),
            "width": round(100 * v["w"] / W, 4), "height": round(100 * v["h"] / H, 4)}
        for k, v in (("crt", crt), ("vfd", vfd), ("hole", hole))
    },
}
json.dump(regions, open(f"{HERE}/regions.json", "w"), indent=2)
print(json.dumps(regions, indent=2))
