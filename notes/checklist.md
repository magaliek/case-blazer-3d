# Acceptance checklist

Status: ☐ not started · ◐ in progress · ☑ done · ✗ skipped (say why in REPORT)

## A – Base jacket
| | Item | Type | Status | Notes |
|---|---|---|---|---|
| A1 | Blank template: classic collar, no pockets, no buttons, no mannequin | REQ | ☑ | Buttons and pockets removed by blazer_strip.py |
| A2 | Body, sleeves, collar, inside as separate named parts | REQ | ☑ | body, collar, left_sleeve, right_sleeve, lining (confirmed in gltf-transform inspect) |
| A3 | UVs at real scale, cm per tile documented | REQ | ☑ | 1 tile = 20 x 20 cm, assumed (ambientCG has no size), set by TILE_CM in UVs.py |
| A4 | Stripes run lengthwise on every panel | REQ | ☑ | Custom projection, V always height. Checked front/side/back in Blender and in glTF viewer |
| A5 | Compressed .glb ≤ 15 MB, textures ≤ 2K | REQ | ☑ | [re-measure]: blazer_web.glb in the repo is 4.8 MB. The viewer currently loads blazer.glb (32 MB) |
| A6 | Front slightly open state, lining visible | BONUS | ☐ | Not started |

## B – Option parts
| | Item | Type | Status | Notes |
|---|---|---|---|---|
| B1 | Flap pocket | REQ | [☑] | Side pockets from the base model are named nodes (left_pocket, right_pocket), toggled in the viewer |
| B2 | Patch pocket | REQ | [☑] | Chest pocket from the base model is chest_pocket, toggled in the viewer |
| B4 | 2-button closure, buttons + buttonholes placed right | REQ | [☑] | closure2_button (2 buttons + holes), toggled in the viewer |
| B5 | 3-button closure, buttons + buttonholes placed right | REQ | [☑] | closure3_button added on top of closure2_button, placed by place_3rd_button.py at z ≈ 104; x estimated, not measured |
| B7 | Lining covers inside, colour changeable | REQ | ◐ | Lining colour is set from state.lining in the viewer; no colour buttons yet |
| B8 | Sleeve buttons (0/2/4) | BONUS | ☐ | |
| B9 | Welt pocket | BONUS | ☐ | |
| B10 | Butterfly vs full lining | BONUS | ☐ | |
| B11 | Vents (single/double/none) | BONUS | ☐ | |
| B12 | Peak lapel or zip (or written proposal) | BONUS | ☐ | |

## C – Photo to asset
| | Item | Type | Status | Notes |
|---|---|---|---|---|
| C1 | Plain, stripe, check tile seamlessly at real scale | REQ | ☐ | |
| C2 | Button #1 photo → 3D button (clean bg, face, rim, 4 holes) | REQ | ☐ | |
| C3 | Button #2 photo → 3D button | REQ | ☐ | |
| C4 | One-page shooting guide | REQ | ☐ | |
| C5 | One command: photo in folder → texture out | BONUS | ☐ | |

## D – Web viewer
| | Item | Type | Status | Notes |
|---|---|---|---|---|
| D1 | 360° rotate with mouse and touch | REQ | ☑ | OrbitControls |
| D2 | Zoom within limits | REQ | ☑ | controls.minDistance / maxDistance |
| D3 | Reset view button | REQ | ☐ | |
| D4 | Fabric choice (3) | REQ | ◐ | setFabric + texture cache work; swatch buttons not in the HTML yet |
| D5 | Front button count | REQ | ◐ | state.buttons + apply() work; buttons not in the HTML yet |
| D6 | Button model (2) | REQ | ☐ | |
| D7 | Pocket type | REQ | ◐ | state.flapPockets / patchPocket + apply() work; buttons not in the HTML yet |
| D8 | Lining colour | REQ | ◐ | state.lining works; colour buttons not in the HTML yet |
| D9 | All choices update instantly, no reload | REQ | ◐ | Every choice goes through apply(); needs the buttons to test |
| D10 | Works at 375 px, no sideways scroll | REQ | ☐ | |
| D11 | First view < 3 s (measured) | REQ | ☐ | |
| D12 | No console errors | REQ | ☐ | |
| D13 | Works in Chrome | REQ | ☐ | |
| D14 | Works in Safari | REQ | ☐ | |
| D15 | Save front + back PNG in one click | BONUS | ☐ | |

## E – Report
| | Item | Type | Status |
|---|---|---|---|
| E1 | Approach + dropped routes | REQ | ☐ |
| E2 | Tools, assets, licences, AI use | REQ | ☐ |
| E3 | Time per part, code vs manual | REQ | ☐ |
| E4 | Estimates for full product | REQ | ☐ |

## Delivery
| | Item | Status |
|---|---|---|
| 1 | Folder layout matches brief | ☐ |
| 2 | README lets someone else reproduce it | ☐ | README on GitHub is still the empty template: fill in requirements, section 1 commands, manual-steps table |
| 3 | 30–60 s video, phone view included | ☐ |

## Cross-option tests (no choice breaks another)
<!-- Try combos: 3 buttons + flap pocket + stripe; open state + each lining colour; etc. -->
| Combo tested | Result |
|---|---|
| | |
