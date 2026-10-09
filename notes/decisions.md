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
- **Chosen:** Lining is a flat colour (see 2026-10-09). Cloth parts always use white, so only the lining is coloured
- **Status:** resolved

### 2026-10-09 – Option buttons driven by data attributes
- **Part:** D
- **Problem:** Five option groups, and every new option would need its own click handler
- **Options considered:** One handler per button; one loop that reads data-option / data-value from the HTML
- **Chosen:** Buttons carry data-option (the state key) and data-value. One loop sets state and calls apply(). toValue() turns the strings into numbers and booleans
- **Why:** Adding an option only means adding HTML. It also keeps the "state + apply()" rule from 10-07
- **Status:** kept
- **If dropped, why:** Per-button handlers: repeated code for every button

### 2026-10-09 – Lining: flat colour from a picker, no texture
- **Part:** D
- **Problem:** Closes the open "colour x texture" item for the lining. I tried the lining in CLOTH_PARTS so it got fabric and colour
- **Options considered:** Fabric texture × colour; flat colour only; four preset swatches
- **Chosen:** Native colour picker, flat colour (fabric: null in setFabric)
- **Why:** Colour multiplies the texture, so on dark fabrics a bright colour came out as a dark, muddy shade (pink on the dark check looked maroon). Looked ugly. The picker allows any colour and needs no list
- **Status:** kept. The cloth parts stay white, so they are not tinted
- **If dropped, why:** Texture × colour: muddy. Swatches: fixed list, replaced by the picker

### 2026-10-09 – Reset view needs damping off for the call
- **Part:** D
- **Problem:** With damping on, controls.reset() put the camera back, but leftover drag inertia kept moving it afterwards (it ended up well off its start position in a test)
- **Chosen:** controls.saveState() once after the camera is placed. The button sets enableDamping = false, calls update(), reset(), then turns damping back on
- **Why:** update() with damping off uses up the leftover spin before the reset
- **Status:** kept

### 2026-10-09 – Large files: Git LFS for the .blend
- **Part:** delivery
- **Problem:** blazer_3_closure.blend is 103.1 MiB. GitHub blocks files over 100 MiB
- **Options considered:** Lossless Compress in Blender (was already on); stripping unused data (not tried); Git LFS; GitHub Release or Drive link
- **Chosen:** Git LFS for *.blend. The glbs (30.8 and 4.6 MB) go in normally
- **Why:** The file stays exactly as it is. Free quota is enough
- **Status:** kept. Anyone who pulls needs git lfs installed

---
