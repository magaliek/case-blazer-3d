import bpy

REMOVE = [
    "buttons",
    "chest_pocket",
    "left_pocket",
    "right_pocket",
    "mini_pockets_x6",
]

for name in REMOVE:
    o = bpy.data.objects.get(name)
    if o:
        print("removing", name)
        bpy.data.objects.remove(o, do_unlink=True)
    else:
        print("not found:", name)

for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)

bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//blazer_blank.blend"))