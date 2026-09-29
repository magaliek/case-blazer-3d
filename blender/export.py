import bpy

PARTS = ["body", "collar", "left_sleeve", "right_sleeve", "lining"]

# make sure nothing is left in Edit Mode
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

for name in PARTS:
    obj = bpy.data.objects[name]
    obj.data.name = name                    # so the glb mesh names match the parts
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = 0.1                         # keep about 10% of the triangles
    mod.delimit = {'UV'}                    # don't collapse across UV borders

inset = bpy.data.objects["lining"].modifiers.new("Inset", 'DISPLACE')
inset.strength = 0.3     # cm, moves the lining inward along its normals
inset.mid_level = 0.0

# select only the jacket parts, so the camera and light aren't exported
for obj in bpy.data.objects:
    obj.select_set(obj.name in PARTS)

bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath("//../assets/blazer.glb"),
    export_format='GLB',
    use_selection=True,
    export_apply=True,
)
print("exported")