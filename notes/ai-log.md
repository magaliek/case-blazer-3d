# AI usage log

Log every time AI output ends up in the project (code, text, images, ideas).
Short entries are fine. The "what I changed" column is the important one.

| Date | Tool | Part | What I asked for | What I kept | What I changed / what was wrong |
|---|---|---|---|---|---|
| 2026-09-25 to 09-28 | Claude | A | Guidance on how to use Blender and how to understand the task | General advice on workflow and what the brief asks for | Nothing noted, no errors remembered |

| 2026-09-28 | Claude | A | Save vs export, and whether to export parts separately | One .glb with named parts, save the .blend in blender/ and export the .glb to assets/ | Nothing noted |
| 2026-09-28 | Claude | A | How to fill in the notes files (manual steps, time log, decisions, checklist) | Structure and wording of the entries, drafted from what I told it | I supplied the facts (dates, hours, the hide-and-join method) and corrected details |

| 2026-09-29 | Claude | A | Explain UVs and how to get real-world scale + lengthwise stripes with a script | The idea (fixed cm per tile, V follows the height axis), the per-part loop, resetting UV maps before unwrapping | Claude said Blender's cube projection keeps stripes vertical everywhere. Wrong: side faces got horizontal stripes. Its V-span check couldn't catch it, I saw it in the side view. Replaced with my own projection loop (U from X or Z, V always Y) |
| 2026-09-29 | Claude | A | Debug my UV script (`mesh` was None) | The fix: use `obj.data` and `len(...)` | The bug was mine (looked up the mesh by object name), not Claude's |
| 2026-09-29 | Claude | A | Real-world size of Fabric072 | Nothing | Claude said ambientCG lists it on the page. It doesn't. I picked 20 cm and documented it as an assumption |
| 2026-09-29 | Claude | A | materials.py (fabric material, lining material) | Whole script | made the lining colour a placeholder |
| 2026-09-29 | Claude | A | export.py + glTF-Transform command | Selection of parts only, export, optimize with webp and 2048 | Export failed because the .blend was saved in Edit Mode (added a mode guard). Optimizer merged parts (added --join false). Mesh was 1.4M triangles, added per-part Decimate ratios (body 0.1) |
| 2026-09-29 | Claude | A | Fix for the lining showing through the back | Inset with a Displace modifier at export | First sign was wrong (-0.3 pushed the lining outside the body). Flipped to +0.3 |

| 2026-10-01 | Claude | A | Tutor me through every step of Part A so I can redo it alone | Explanations of mesh/UV/units/export/decimation/lining/glTF Transform; hints for the RATIOS dict (I wrote the dict myself) | Nothing wrong found this time. Claude flagged that the committed export.py uses 0.1 on every part (notes say 0.1/0.25/0.4), that the GitHub README is still the empty template, and that manual-steps row 2 is misformatted. Claude checked the glTF Transform flags against its `--help` text instead of from memory |
| 2026-10-01 | Claude | D (test) | Barebones page + small Python server to check blazer.glb on laptop and phone | model-viewer page and serve.py as written | My glb path had a typo (`//assets/`), fixed. Claude's min/max camera limits kept the camera stuck too close, removed them. The auto-rotate checkbox didn't work for me, removed it |

| 2026-10-05 | Claude | B | How to approach Part B, and whether to reuse the buttons and pockets that came with the CLO model | Reuse the original parts as separate named nodes that the viewer shows or hides | Claude first suggested generating copies of everything in code. I chose hide/show for the existing parts, which is less work |
| 2026-10-05 | Claude | B | Script to place a 3rd closure button and buttonhole on the body | Ray-cast to find the cloth, copy a template button and hole, lift by the measured gap, tilt by the difference between surface normals | First version put the button on the back of the jacket. Claude picked z = 131, above where the jacket closes, so the ray passed through the lapel opening. Moved it below the lowest row (z ≈ 104) and made back hits raise an error. The x values (-1.5 and 1.0) were Claude's guesses, not measured. The collar target was unnecessary and I removed it |
| 2026-10-05 | Claude | B | Line-by-line explanation of the script (coordinate spaces, matrix_world, ray_cast, normals, dot product) | Explanations | Nothing wrong found |

| 2026-10-07 | Claude | D | How to build show/hide toggles for buttons and pockets, and fabric/lining changes, in the three.js viewer | One `state` object + one `apply()` that recomputes visibility from a lookup; `setFabric` + texture cache; `clothMesh()` helper for the pockets. | Bugs found while testing: Python-style loops (`.items()`, `in` instead of `of`), `new Set(...)` without brackets, TOOGLEABLE/TOGGLEABLE spelling mismatch, fabric id passed where a URL was needed, lining colour overwritten by the white default, relative texture paths (404), pockets load as Groups so `.material` was undefined |
| 2026-10-07 | Claude | B/D | Which pocket material slot is the cloth | Cloth is `kruvaze_blazer_FRONT_2303`, leave `Material.001` alone | Unverified guess from the GLB (Material.001 looks like stitching, shared with the buttonholes). [confirm by hiding that child in the viewer] |

## Patterns noticed
Claude's mistakes so far were confident claims about how Blender behaves (cube projection direction, what ambientCG publishes, which way the displace goes). Reading the code would not have caught them. Looking at the result did: side view, glTF viewer, inspect output.