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
- **Chosen:** body 0.1, collar 0.4, left/right sleeve 0.25, lining 0.1
- **Why:** Tuned by eye to get from 1.4M to about 245k triangles (4.28 MB, well under the 15 MB limit). The body is large and smooth, so it takes the strongest reduction. The collar is small and its lapel edges are the most visible, so it keeps more. Sleeves in between. Not tested systematically.
- **Status:** open

### 2026-10-01 – Per-part decimate ratios in a dict
- **Part:** A
- **Problem:** The committed export.py applies 0.1 to every part, but the notes say body 0.1, sleeves 0.25, collar 0.4. Someone running the repo would get a different .glb
- **Chosen:** RATIOS dict in export.py (body 0.1, collar 0.4, left/right sleeve 0.25, lining 0.1), looked up by part name in the loop
- **Why:** Matches what the notes say was exported, and the numbers sit in one place
- **Status:** in progress (dict written, loop not yet updated and pushed)

### 2026-10-01 – Open: optimize defaults that may bite in Part B/D
- **Part:** B/D
- **Problem:** Per `optimize --help`: `--palette` (merge materials) is on by default but only acts with 5+ unique material values, so it could merge materials once buttons and pockets are added. Geometry is meshopt-compressed by default, so the web viewer needs the meshopt decoder
- **Status:** open, not tested yet

### 2026-10-05 – Closures: reuse the CLO buttons, add the 3rd by code
- **Part:** B
- **Problem:** Brief needs a 2-button and a 3-button closure. The base model's closure is double-breasted: 6 front buttons in two columns of 3, plus 3 per cuff, with a buttonhole opposite each
- **Options considered:** Only hide/show the existing buttons; generate every button position in code; move a button by hand with snapping; copy one button and one hole and place a third by ray-cast
- **Chosen:** Existing buttons and holes become separate named parts that the viewer shows or hides. The 3rd button and hole are added by place_3rd_button.py
- **Why:** Hiding buttons only gives even counts (2, 4, 6), never 3. Placing by hand needs a manual tilt and isn't reproducible
- **Status:** kept. x position of the 3rd button is estimated, not measured
- **If dropped, why:** By hand with snapping: didn't work well and the tilt was hard. Placing the 3rd button above the top row (z = 131): the lapel is open there, so the ray hit the back panel

### 2026-10-07 – State + apply() for the viewer
- **Part:** D
- **Problem:** Options interact (3 buttons shows two nodes, pockets show one to two)
- **Options considered:** A click handler per button that shows or hides nodes; one state object and one function that recomputes everything
- **Chosen:** One `state` object, one `apply()` that sets every node's visibility from lookup tables
- **Why:** No choice can leave a stale node behind, which is the "no choice breaks another" criterion
- **Status:** kept
- **If dropped, why:** Per-button handlers dropped: every handler has to set every node and breaks when options are added

### 2026-10-07 – 3 buttons is cumulative
- **Part:** B/D
- **Problem:** How the 2-button and 3-button closures map onto the exported nodes
- **Chosen:** 2 buttons shows closure2_button (2 buttons + holes). 3 buttons shows closure2_button + closure3_button
- **Why:** closure3_button only holds the third button and hole (3662 vs 1831 vertices in the GLB)
- **Status:** kept

### 2026-10-07 – Fabric swap on the shared material, pockets by child
- **Part:** D
- **Problem:** Body, collar and sleeves share one material. left_pocket and right_pocket have 2 materials, so they load as Groups
- **Chosen:** Swap `map` on the shared material. `clothMesh()` picks the pocket child by material name
- **Why:** Material.001 is shared with the buttonholes, so it must not be changed
- **Status:** kept. Open: pocket UVs are not in UVs.py, so fabric scale is wrong on the pockets

### 2026-10-07 – CLO basicblazer_* maps not used in the viewer
- **Part:** D
- **Problem:** Unsure whether the PNGs in assets/textures are selectable textures
- **Chosen:** Not used
- **Why:** They are laid out on CLO's UVs, which UVs.py replaced. 4096 px (over the 2K limit). Not fabrics
- **Status:** dropped
- **If dropped, why:** Wrong UV layout, wrong size, not fabrics

### 2026-10-07 – Open: colour x texture
- **Part:** D
- **Problem:** Three multiplies the colour with the image, so any non-white colour tints the fabric
- **Options considered:** Keep the tint; force white when a texture is picked
- **Chosen:** [decide]
- **Status:** open
---
