import bpy

RATIOS = {"body": 0.1, "collar": 0.4, "left_sleeve": 0.25, "right_sleeve": 0.25, "lining": 0.1}

PARTS = [*list(RATIOS.keys()), "chest_pocket", "closure2_button", "closure3_button", "cuff_buttons", "left_pocket", "right_pocket"]

# make sure nothing is left in Edit Mode
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

for name, ratio in RATIOS.items():
    obj = bpy.data.objects[name]
    obj.data.name = name                    # so the glb mesh names match the parts
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = ratio
    mod.delimit = {'UV'}                    # don't collapse across UV borders

for part in PARTS:                          #no need to decimate small parts
    obj = bpy.data.objects[part]
    obj.data.name = part

inset = bpy.data.objects["lining"].modifiers.new("Inset", 'DISPLACE')
inset.strength = 0.3     # cm, moves the lining inward along its normals
inset.mid_level = 0.0

for obj in bpy.data.objects:
    obj.select_set(obj.name in PARTS)

bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//../assets/blazer.glb"),
    export_format='GLB',
    use_selection=True,
    export_apply=True,
)
print("exported")


# npx @gltf-transform/cli optimize assets/blazer.glb assets/blazer_web.glb --texture-compress webp --texture-size 2048 --join false
# npx @gltf-transform/cli inspect assets/blazer_web.glb