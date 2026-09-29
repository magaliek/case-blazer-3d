import bpy

TILE_CM = 20.0   # 1 UV tile = 20 x 20 cm of real fabric (document this in the README)
PARTS = ["body", "collar", "left_sleeve", "right_sleeve", "lining"]

for name in PARTS:
    mesh = bpy.data.objects[name].data

    # throw away the old UV maps, make a fresh one
    for uv in list(mesh.uv_layers):
        mesh.uv_layers.remove(uv)
    mesh.uv_layers.new(name="UVMap")
    uv_data = mesh.uv_layers.active.data

    # front/back faces take U from X, side faces take U from Z; V is always height (Y)
    for poly in mesh.polygons:
        n = poly.normal
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            u = co.z if abs(n.x) > abs(n.z) else co.x
            uv_data[li].uv = (u / TILE_CM, co.y / TILE_CM)

    print(name, "done")

bpy.ops.wm.save_mainfile()