# Manual steps

| # | Date | Part | What I did by hand | Why not scripted | Time | Could be scripted by… |
|---|---|---|---|---|---|---|
| 1 | 2026-09-25 | A | Selected faces stitch by stitch at first, then used Hide to isolate parts, mass select, join per category, rename. Parts: body, sleeve_L, sleeve_R, collar, lining, chest_pocket, right_pocket, buttons, mini_pockets | Base model is one merged mesh, no rule to split it automatically | Partly: Separate by Loose Parts, then group and rename by a naming rule. Not the lining, that needs a face selection |

| 2 | 2026-09-28 | A | Separated the lining from the body | Same reason, the inner faces have to be picked by hand | included above | Select faces by normal direction or material in a script |

| 3 | 2026-09-29 | A | Joined the leftover pieces (body.2022, body.2102) back into body | Tiny stray pieces, quicker by hand | included in 5 h | Join by name rule in the strip script |

| 4 | 2026-09-29 | A | Visual checks: stripe on the jacket in Material Preview (front, side, back), UV editor look, then the .glb in the glTF viewer | Judging "does it look right" needs eyes, the script only checks numbers | included in 5 h | Not really. Could render turntable screenshots automatically for comparison |

No changes to geometry or UVs. No objects deleted.