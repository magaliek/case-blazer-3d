import json
import sys
from pathlib import Path

import cv2
import numpy as np

PHOTO = sys.argv[1]
DIAMETER_MM = float(sys.argv[2])
NAME = sys.argv[3]

OUT_DIR = Path('assets/buttons')
FACE_SIZE = 512
EDGE_MARGIN = 12
LIGHTNESS_WEIGHT = 0.0

OUT_DIR.mkdir(parents=True, exist_ok=True)

img = cv2.imread(PHOTO)
if img is None:
    sys.exit(f'Could not read {PHOTO}')
h, w = img.shape[:2]

lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
m = EDGE_MARGIN
frame = np.concatenate([lab[:m].reshape(-1, 3), lab[-m:].reshape(-1, 3),
                        lab[:, :m].reshape(-1, 3), lab[:, -m:].reshape(-1, 3)])
background = np.median(frame, axis=0)

diff = lab - background
diff[..., 0] *= LIGHTNESS_WEIGHT
distance = np.linalg.norm(diff, axis=2)
distance8 = np.clip(distance * 255 / distance.max(), 0, 255).astype(np.uint8)
_, mask = cv2.threshold(distance8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

_, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
blob = np.uint8(labels == biggest) * 255
contours, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
outline = max(contours, key=cv2.contourArea)

(cx, cy), radius = cv2.minEnclosingCircle(outline)

yy, xx = np.mgrid[:h, :w]
inner = (xx - cx) ** 2 + (yy - cy) ** 2 < (0.6 * radius) ** 2
candidates = np.uint8((mask == 0) & inner) * 255
candidates = cv2.morphologyEx(candidates, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
contours, _ = cv2.findContours(candidates, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

found = []
for c in contours:
    area = cv2.contourArea(c)
    if area < 20:
        continue
    (hx, hy), _ = cv2.minEnclosingCircle(c)
    found.append((area, hx, hy))
found.sort(reverse=True)
found = found[:4]
if len(found) != 4:
    sys.exit(f'Expected 4 holes, found {len(found)}. Check debug image / lighting.')


holes = [{'x': round((hx - cx) / radius, 4),
          'y': round(-(hy - cy) / radius, 4),
          'r': round(float(np.sqrt(area / np.pi)) / radius, 4)}
         for area, hx, hy in found]

scale = FACE_SIZE / (2 * radius)
affine = np.float32([[scale, 0, -scale * (cx - radius)],
                     [0, scale, -scale * (cy - radius)]])
face = cv2.warpAffine(img, affine, (FACE_SIZE, FACE_SIZE),
                      flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
alpha = np.zeros((FACE_SIZE, FACE_SIZE), np.uint8)
cv2.circle(alpha, (FACE_SIZE // 2, FACE_SIZE // 2), FACE_SIZE // 2, 255, -1)
cv2.imwrite(str(OUT_DIR / f'{NAME}_face.png'), cv2.merge([*cv2.split(face), alpha]))

info = {'name': NAME, 'diameter_mm': DIAMETER_MM, 'photo_radius_px': round(radius, 1), 'holes': holes}
(OUT_DIR / f'{NAME}.json').write_text(json.dumps(info, indent=2))

debug = img.copy()
cv2.circle(debug, (int(cx), int(cy)), int(radius), (255, 0, 0), 2)
for area, hx, hy in found:
    cv2.circle(debug, (int(hx), int(hy)), int(np.sqrt(area / np.pi)), (0, 0, 255), 2)
cv2.imwrite(str(OUT_DIR / f'{NAME}_debug.png'), debug)

print(f'Button centre ({cx:.0f}, {cy:.0f}) px, radius {radius:.0f} px')
print(f'Holes found: {len(holes)}')
print(f'Wrote {OUT_DIR}/{NAME}_face.png, {NAME}.json, {NAME}_debug.png')

