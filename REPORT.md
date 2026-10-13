# Report – Blazer 3D Configurator

## 1. Approach

I started by preparing the Blender file by hand: I regrouped the parts of the CLO model one by one, so that the body (with its stitching), the collar, the left and right sleeve, the lining, the pockets and the buttons are separate named objects. I chose the groups based on what I thought should be customizable later, which is why the collar and the sleeves are separate. After that, everything that could be repeated became a script, written with the help of Claude:

- `UVs.py` throws away CLO's UVs and builds new ones at a fixed real-world scale
- `materials.py` clears CLO's leftover materials and assigns a fabric material and a lining material
- `export.py` decimates each part, moves the lining in a bit and exports the `.glb`
- glTF-Transform compresses the `.glb` (meshopt + WebP textures at 2048 px)
- `place_3rd_button.py` adds the third closure button and buttonhole by ray-casting onto the body
- `button_prep.py` (OpenCV) and `button_build.py` (Blender) turn a top-down button photo into a 3D button

The viewer is one three.js page (`web/`). It loads the `.glb`, shows or hides named parts, swaps the fabric texture and changes the lining colour. My loop was: write the code, check it in Blender and in the browser / glTF viewer, correct, move on.

### Why this approach
- The brief describes how Hockerty and Sumissura do it: one realistic base jacket, options as separate parts, fabric as a texture. I followed that literally: one base jacket from CLO and every option as its own named node.
- Anything that could be a script is a script, not a hand edit, because someone else should be able to get the same result. Example: my own UV projection has no seams to place by hand, the scale is identical on every part and the stripe direction can't drift.
- For the options I reuse the pockets and buttons that came with the CLO model and show/hide them, instead of generating them in code. It was much less work and the parts already sit on the jacket without gaps. The price is that the brief asks for generated parts, and here only the third button and its buttonhole are generated.
- In the viewer there is one `state` object and one `apply()` that sets the visibility of every node from lookup tables. That way no choice can leave a stale part behind, which is the "no choice breaks another" criterion.
- I used model-viewer for the first test page and three.js for the configurator. I had to switch because I needed direct scene access to toggle nodes and change modes etc...

### Routes tried and dropped

| Route | Part | Why dropped |
|---|---|---|
| Smart UV Project | A | Island size and rotation differ per part, so the scale isn't the same everywhere |
| Marking seams and unwrapping | A | Hand work, against the brief |
| Blender's cube projection | A | On side faces the stripes turned 90° (I saw it in the side view). Claude had said it keeps stripes vertical, which was wrong |
| Measuring the tile size from the stripe spacing | A | Not done. I assumed 20 cm and documented it (ambientCG doesn't publish a size) |
| glTF-Transform optimize with its default join | A | It merged all parts with the same material into one mesh, which breaks "separate named parts". Fixed with `--join false` |
| Optimizer's own simplify only | A | It removed only about 15% of the triangles. Per-part Decimate modifiers in `export.py` got from 1.4M to about 245k |
| Giving the lining only a material / raising the body decimate ratio to 0.15 | A | A material changes the colour, not the holes. A higher ratio adds about 100k triangles (kept in reserve) |
| Displace on the lining with -0.3 | A | Wrong sign, it pushed the lining outside the body. +0.3 works |
| Using CLO's `basicblazer_*` texture maps | D | They sit on CLO's UVs (which I replaced), they are 4096 px and they aren't fabrics |
| Generating every button and pocket in code | B | Considered first (Claude's suggestion). I chose hide/show of the existing parts because it was less work |
| Only hiding/showing the existing buttons | B | Gives even counts only (2, 4, 6), never 3 |
| Placing the third button by hand with snapping | B | The tilt was hard to get right and the result isn't reproducible |
| Placing the third button at z = 131 | B | The lapel is open there, so the ray hit the back panel. Moved below the lowest row (z ≈ 104) |
| One click handler per button | D | Every handler has to set every node and breaks when options are added. Replaced by data attributes + one loop |
| Fabric texture × lining colour, and a list of preset swatches | D | The colour multiplies the texture, so bright colours on dark fabric looked muddy. Now a flat colour from a colour picker |
| Hosting the 103 MiB `.blend` as a Release or Drive link | delivery | Git LFS keeps the file as it is and the free quota is enough |

## 2. Tools and assets

### Tools
No trial versions and nothing paid.

| Tool | Used for | Version | Licence |
|---|---|---|---|
| Blender (Python API `bpy`) | Splitting parts, UVs, materials, decimation, export, button builder | glTF exporter 5.2.40 (from the `.glb` header, Blender 5.2) | GPL, free |
| glTF-Transform CLI | Compressing the `.glb` | 4.5.1 | MIT |
| three.js (GLTFLoader, OrbitControls, MeshoptDecoder) | Web viewer | 0.186.1, loaded from the jsDelivr CDN | MIT |
| OpenCV + NumPy (Python) | Button photo → face texture and hole positions | Apache-2.0 / BSD |
| Python `http.server` (`serve.py`) | Local test server for laptop and phone | – | – |
| Git, GitHub, Git LFS | Delivery (the `.blend` is 103 MiB) | – | Free tier |
| Claude | AI help, see below | – | – |


### Assets and licence findings

| Asset | Source | Can it be shown to website visitors? |
|---|---|---|
| Base blazer ("Man Basic Blazer Modeling in Clo3D") | CGTrader, free | I understood from the CGTrader page that the free model is OK to use non-commercially. A public configurator for a company is commercial use, so for the real product the licence has to be checked again or the model replaced |
| Fabric031, Fabric072, Fabric083 | ambientCG | CC0 |
| Button photos (gold and silver) | Taken from the internet by me | I only used them as test input for the button pipeline. In real use the buttons are photographed by the team, so their licence doesn't matter there. The generated buttons in `assets/buttons/` come from these photos, so they are test files too |
| Fonts | None. The page uses the system font | – |

I didn't check the licences as carefully as the brief asks, so the table above is what I know, not a full clearance. The repo is public and contains the original CLO project (`blender/men basic blazer.zprj`). If the model licence doesn't allow redistribution, that file should be removed from the repo.

### Where I used AI
I used Claude (claude.ai chat) for the whole project. Most of the code was first drafted by Claude: `materials.py`, `export.py`, `place_3rd_button.py`, `serve.py` and the first version of the viewer logic. I wrote some parts myself: the `RATIOS` dict, the data-attribute option wiring, the colour picker and the idea of my own UV projection loop. I also used it as a tutor, where it explained UVs, matrices and ray-casting and I read the code line by line.

What I had to fix, from `notes/ai-log.md`:

- **Wrong claims about how things work:** the cube projection direction, that ambientCG publishes the fabric size, the sign of the displace modifier. Reading the code wouldn't have caught these, only looking at the result did (side view, glTF viewer).
- **Part B:** the first version of `place_3rd_button.py` put the button on the back of the jacket, and the x positions were guesses, not measurements.
- **Part D:** Python-style loops in JavaScript (`.items()`, `in` instead of `of`), a spelling mismatch (TOOGLEABLE / TOGGLEABLE), relative texture paths (404), pockets loading as Groups, and the lining colour being overwritten by the white default.
- **Bugs I only knew about because the code was run:** the reset-view drift after a drag (damping inertia) and a `getElementsById` typo were found by Claude running my code, not by me reading it. I found some myself, like the `mesh` being None in the UV script and the `//assets/` typo in the glb path.
----
- **This report** was drafted with Claude from the notes folder, and I corrected it.

## 3. Results per part

### A – Base jacket
**Works**
- Blank template with no pockets and no buttons, no mannequin (`blazer_strip.py`), with a classic collar.
- Body, collar, left sleeve, right sleeve and lining are separate named parts (confirmed with `gltf-transform inspect`).
- UVs at real scale: 1 tile = 20 × 20 cm. Stripes run lengthwise on every panel (checked front, side and back in Blender and in the glTF viewer).
- All textures are at most 2048 × 2048.

**Doesn't work / open**
- **File size:** the compressed `blazer_web.glb` is 4.8 MB, but it was made before the options were added and only contains the 5 base parts. The `.glb` with the options (`blazer.glb`) is 32.3 MB and not compressed, which is over the 15 MB limit, and that is the file the viewer loads. I need to re-run the glTF-Transform command on the new `blazer.glb` and point the viewer at the result. `main.js` already has the meshopt decoder. The two flap pockets are not decimated and are about 4 MB each, so they are the first thing to reduce.
- **Pockets have no real-scale UVs:** `UVs.py` doesn't cover them, so the stripe scale is wrong on the pockets.
- **Lapel edges** look slightly ragged and the stripes wobble there, probably from the decimation. I tuned the ratios by eye (body 0.1, collar 0.4, sleeves 0.25) and didn't test it systematically.
- **The 20 cm tile size is an assumption**, not measured.
- **Bonus not done:** the second state with the front open.

### B – Option parts
**Works**
- Two pocket types as named nodes: flap pockets (left, right or both) and a chest pocket. They are the pockets from the base model, so they sit on the jacket without gaps.
- Two front closures: 2 buttons (`closure2_button`: 2 buttons + buttonholes) and 3 buttons (`closure3_button` added on top). The third button and buttonhole are generated by `place_3rd_button.py` with a ray-cast.
- Lining covers the inside and its colour can change (flat colour, no texture).

**Doesn't work / open**
- Most option parts are the original CLO parts that I show and hide, not parts generated by code. Only the third button and hole are generated.
- The x position of the third button is an estimate, not a measurement.
- **Topstitching** is a required item that I didn't track in the checklist. The stitching on the pockets and buttonholes comes from the CLO model, and I haven't checked it up close or from one metre away. **[CONFIRM by looking at it]**
- The "no gaps from one metre" check for the pockets isn't documented.
- **Bonus not done:** sleeve buttons (0/2/4, the cuff buttons are one fixed block), welt pocket, butterfly lining, vents, peak lapel/zip.

### C – Photo to asset
**Works**
- Button pipeline in two commands:
  1. `python blender/button_prep.py <photo> <diameter_mm> <name>` finds the button, cuts out a clean round face with an alpha channel, finds the four holes and writes a JSON and a debug image.
  2. `blender -b -P blender/button_build.py -- assets/buttons/<name>.json` spins a button with a raised rim, cuts the four holes with a boolean and exports a `.glb`.
- Two buttons are built this way (`gold_button`, `silver_button`).
- The three fabrics are the ambientCG tiles, which tile seamlessly by design.

**Doesn't work / open**
- The buttons aren't in the viewer yet, so there is no "button model" choice (D6). The jacket still shows the CLO buttons.
- The gold button photo is small (about 214 px across), so the face texture is low resolution.
- There is no photo → fabric texture path, so the "simulate a phone photo of a fabric" case isn't covered. Also missing: the one-page shooting guide (decided not to make it) and the one-command bonus.

### D – Web viewer
**Works**
- 360° rotation with mouse and touch, zoom within limits, reset view button (damping is switched off for the call, otherwise leftover inertia moved the camera).
- Choices that update at once without reloading: fabric (wool, stripe, check), front buttons (none, 2, 3), flap pockets (off, left, right, both), chest pocket on/off, lining colour (colour picker).
- Checked by hand in Chrome and Safari.

**Doesn't work / open**
------
- **First view time isn't measured.** `logTime()` in `main.js` prints the time, but I haven't written the value down. It is probably over 3 seconds: the page loads the 32.3 MB `.glb` plus a 5–7 MB fabric JPG, and at roughly 9 Mbit/s (Chrome's Fast 4G) that is already more than 30 seconds. That is arithmetic, not a measurement. The fix is the compressed `.glb` and WebP textures.
- **Console:** the only error I saw was the `favicon.ico` 404. The fix (`<link rel="icon" href="data:,">`) is not in `web/index.html`, so the error is still there. `main.js` also still has debug `console.log` lines.
- **375 px phone check isn't documented.** The layout wraps the controls in a bar with `max-height: 40vh` and scrolling, and has a viewport meta tag, but I didn't record a test on a 375 px screen.
- **The first view is not the blank template.** The default state shows 2 buttons, the right flap pocket, the chest pocket and the cuff buttons, and there is no button to hide the cuff buttons.
- Combination tests ("3 buttons + flap pocket + stripe" etc.) are not filled in.
- **Bonus not done:** PNG export of front and back.


### Key measurements

| What | Value | How measured |
|---|---|---|
| UV scale (cm per texture tile) | 20 × 20 cm. An assumption: ambientCG doesn't publish the real size | Set by `TILE_CM` in `blender/UVs.py` |
| blazer.glb size | `blazer.glb` (with options, uncompressed): 32.3 MB. `blazer_web.glb` (compressed, base parts only): 4.8 MB | File sizes in the repo (32,299,204 and 4,795,720 bytes). The brief's limit is 15 MB |
| Max texture size | 2048 × 2048 px (the fabric JPGs for swapping are 2048 too) | `gltf-transform inspect` |
| First view load time |  | – |
| Browsers tested | Chrome and Safari | By hand |

## 4. Time spent

Hours come from `notes/time-log.md`; days assume 8 h per day. I added a research column because a lot of the time went into learning Blender, UVs and JavaScript, and "code" and "manual" alone would not add up to 100%.

| Part | Suggested | Actual | % code | % manual | % research/setup |
|---|---|---|---|---|---|
| A – Base jacket | 1.5 d | 17 h (≈ 2.1 d) | 29% (5 h) | 29% (5 h) | 41% (7 h) |
| B – Option parts | 2 d | 5 h (≈ 0.6 d) | 20% (1 h) | 20% (1 h) | 60% (3 h) |
| C – Photo to asset | 1 d |  | | | |
| D – Web viewer | 2 d | 9 h (≈ 1.1 d) | 67% (6 h) | 0% | 33% (3 h) |
| E – Report | 0.5 d | | | | |
| Delivery (Git LFS) | – | 0.5 h | | | 100% setup |
| **Total logged** | 7 d | 31.5 h (≈ 3.9 d), without C and E | | | |

Note: the "Running totals" table in `time-log.md` is wrong for A and D. A is 17 h, not 15 (the 2 h on 2026-10-01 are missing). D is 6 h code and 3 h research, not "6 h manual", and the 0.5 h Git LFS setup belongs to delivery, not D.

### Code vs manual
Everything repeatable is a script. The by-hand work was:

1. **Splitting the CLO mesh into named parts** (body, sleeves, collar, lining, pockets, buttons, about 6 h). The base model is one merged mesh and there is no rule to split it automatically. It could partly be scripted (Separate by Loose Parts and a naming rule), but not the lining, which needs a face selection.
2. **Separating the lining** from the body, same reason (could be done by selecting faces by normal direction or material).
3. **Joining a few stray pieces** back into the body (quicker by hand).
4. **Separating and naming the closure buttons and buttonholes** (could be scripted by position).
5. **Visual checks:** stripes in Blender, the third button's position and tilt, the toggles and fabrics in the browser, reset view, the console. These need eyes. Playwright screenshot tests could automate some of it.

Because steps 1–4 were done by hand, the prepared `.blend` (`blender/blazer_3_closure.blend`, in Git LFS) is the starting point for the scripts, and the part grouping can't be rebuilt from the original CLO file by script alone. That is a reproducibility limit and I'd rather say it than hide it. There were no changes to the geometry or the UVs by hand, and no objects were deleted by hand.

## 5. Estimates for the full product

| Feature | Estimate | What it needs | Main risk |
|---|---|---|---|
| Lapel types (peak, shawl) | 3–4 days each | A second base model with that lapel, or a collar part rebuilt in Blender. Then the same pipeline (split, UVs, export) and a collar swap in the viewer | The lapel meets the body front, so gaps or mismatched edges. The lapel edges were already the roughest part after decimation |
| Zip closure | 2–3 days | A zip strip with teeth and a pull (small mesh or normal map), placed on the front edge like the third button, buttons and buttonholes hidden | The base jacket is double-breasted with an overlap, so a zip needs a different front edge on the body |
| Snap closure | 0.5–1 day | A snap head built from a profile like `button_build.py`, placed with the ray-cast script | Little. The underlap isn't visible |
| Vents (single, double, none) | 2–3 days | Cutting a slit in the back hem of the body and adding an underlap flap in Blender, UVs re-run with `UVs.py`, vent variants as named nodes | The body is one decimated mesh, so cutting it can leave gaps with the lining. Needs hand checks |
| New garment: overshirt | 3–4 days | A free base model with a licence that allows web display, the same scripts with new part names and ratios, new rows in the viewer lookup | Splitting the model into parts by hand, same as in A. No lining, so simpler |
| New garment: coat | 4–6 days | Same as the overshirt, plus more decimation and a stricter size budget | The blazer already needed 1.4M → 245k triangles to be small enough. A coat is bigger. Lining and long sleeves add parts |

### Reasoning behind the estimates
These are based on one jacket, so the error band is wide.

- **The slow, unscriptable step is splitting a base model into named parts.** For one jacket it took about 6 hours by hand, and a new garment pays that again. That is the main part of the overshirt and coat estimates.
- **Everything after the split is cheap on a second run.** The UV loop, materials and export are parameters (part names, `TILE_CM`, `RATIOS`), and adding a viewer option means adding HTML plus lookup rows. That's why Part D took 9 hours including learning, and why Part B took 5.
- **Placing small parts by ray-cast and template is cheap.** The third button needed about 1 hour of code, but 3 hours to learn the idea. A second use (snaps, sleeve buttons) should be much faster, which is why snaps are the smallest item.
- **Changing the shape of the body is the expensive and risky kind of work.** Lapels, zip and vents all touch the one big body mesh, where decimation already caused ragged lapel edges and the lining sits right behind the body. That is why those estimates are higher and why I'd budget extra for hand checks.
- **Size is a real constraint.** The raw export was 108 MB and the first optimized version still needed per-part decimation, so every new garment or part needs a size check against the 15 MB limit.
- **A licence check is part of every new base model.** I didn't do it properly this time and I wouldn't skip it for a real product.