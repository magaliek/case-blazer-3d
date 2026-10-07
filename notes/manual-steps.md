# Manual steps

| # | Date | Part | What I did by hand | Why not scripted | Could be scripted by… |
|---|---|---|---|---|---|---|
| 1 | 2026-09-25 | A | Selected faces stitch by stitch at first, then used Hide to isolate parts, mass select, join per category, rename. Parts: body, sleeve_L, sleeve_R, collar, lining, chest_pocket, right_pocket, buttons, mini_pockets | Base model is one merged mesh, no rule to split it automatically | Partly: Separate by Loose Parts, then group and rename by a naming rule. Not the lining, that needs a face selection |

| 2 | 2026-09-28 | A | Separated the lining from the body | Same reason, the inner faces have to be picked by hand | included above | Select faces by normal direction or material in a script |

| 3 | 2026-09-29 | A | Joined the leftover pieces (body.2022, body.2102) back into body | Tiny stray pieces, quicker by hand | included in 5 h | Join by name rule in the strip script |

| 4 | 2026-09-29 | A | Visual checks: stripe on the jacket in Material Preview (front, side, back), UV editor look, then the .glb in the glTF viewer | Judging "does it look right" needs eyes, the script only checks numbers | included in 5 h | Not really. Could render turntable screenshots automatically for comparison |

No changes to geometry or UVs. No objects deleted.

| 5 | 2026-10-05 | B | Separated the closure buttons and buttonholes and named them (e.g. top_left_closure_button, top_right_button_hole) | I originally had them merged into one object | Separate by Loose Parts, then name by position (x/z) in a script |

| 6 | 2026-10-05 | B | Checked in Blender that the 3rd button sits on the cloth and isn't tilted wrong | Needs eyes | Render a close-up and compare |

| 7 | 2026-10-07 | D | Checked toggles and fabrics in the browser | Needs eyes | Screenshot tests (Playwright) |