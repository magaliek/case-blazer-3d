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
moments = cv2.moments(outline)
cx = moments['m10'] / moments['m00']
cy = moments['m01'] / moments['m00']
radius = float(np.sqrt(cv2.contourArea(outline) / np.pi))

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


#unfinished