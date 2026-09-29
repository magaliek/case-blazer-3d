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

## Patterns noticed
Claude's mistakes so far were confident claims about how Blender behaves (cube projection direction, what ambientCG publishes, which way the displace goes). Reading the code would not have caught them. Looking at the result did: side view, glTF viewer, inspect output.