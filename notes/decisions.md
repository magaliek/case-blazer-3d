# Decisions and dropped routes

Write an entry whenever you pick between options or abandon something.
Dropped routes go straight into the report, so note WHY while you still remember.

## Template
### [Date] – Short title
- **Part:** 
- **Problem:** 
- **Options considered:** 
- **Chosen:** 
- **Why:** 
- **Status:** kept / dropped
- **If dropped, why:** 

### 2026-09-29 – How to make the UVs
- **Part:** A
- **Problem:** CLO's UVs were unusable. Need the same cm per tile on every part and stripes lengthwise on every panel.
- **Options considered:** Smart UV; mark seams and unwrap, then scale islands; Blender's cube_project; own projection loop
- **Chosen:** Own projection loop in UVs.py: U from X (front/back faces) or Z (side faces), V = height, all divided by TILE_CM
- **Why:** No seams to place by hand, scale is identical on every part, stripe direction can't drift
- **Status:** kept
- **If dropped, why:** Smart UV: island size and rotation vary per part. cube_project: side faces turn the stripes 90° (seen in the side view). Seams route: hand work, against the brief

### 2026-09-29 – Tile size
- **Part:** A
- **Problem:** Need to document how many cm one tile covers, but ambientCG doesn't publish it
- **Options considered:** Measure from stripe spacing; pick a plausible value
- **Chosen:** 20 cm, documented as an assumption
- **Why:** The requirement is a documented, consistent number. It's one constant, so it's easy to change and re-export
- **Status:** kept (not measured against real stripe spacing, revisit if time)

### 2026-09-29 – Getting the file size and triangle count down
- **Part:** A
- **Problem:** Raw export was 108 MB and 1.4M triangles. The default optimize merged all parts of the same material into one mesh
- **Options considered:** Optimizer's own simplify only; Decimate in Blender per part; optimizer join on/off
- **Chosen:** Decimate modifiers in export.py (body 0.1, sleeves 0.25, collar 0.4, applied at export only) and `--join false`
- **Why:** Optimizer alone removed only about 15%. Join broke the "separate named parts" requirement
- **Status:** kept
- **If dropped, why:** Default optimize with join was dropped because it merged the parts

### 2026-09-29 – Lining poking through the back
- **Part:** A
- **Problem:** After decimation, white specks showed through the body's back. The lining sits right behind it
- **Options considered:** Give the lining a material only; raise body ratio to 0.15; push lining inward
- **Chosen:** Displace modifier on the lining at export, +0.3 cm
- **Why:** Cheap, invisible from outside, doesn't add triangles
- **Status:** kept
- **If dropped, why:** Material only: changes the colour, not the holes. Higher ratio: about 100k more triangles, held in reserve. First attempt with -0.3 moved the lining outward

### 2026-09-29 – Leftover CLO materials
- **Part:** A
- **Problem:** Parts carried CLO's leftover materials and shared slots
- **Chosen:** materials.py clears every slot and assigns one fabric material (lining gets its own)
- **Why:** Reproducible from the README, no hand edits
- **Status:** kept

### 2026-09-29 – Open: lapel edges
- **Part:** A
- **Problem:** Lapel edges look slightly ragged and the stripes wobble there, probably from decimation
- **Options considered:** Collar ratio 0.4 → 0.7; body ratio 0.15
- **Chosen:** Not done yet
- **Status:** open

---
