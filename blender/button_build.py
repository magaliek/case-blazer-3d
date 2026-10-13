import json
import math
import sys
from pathlib import Path

import bpy
import bmesh

info_path = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
info = json.loads(info_path.read_text())
face_png = info_path.with_name(info['name'] + '_face.png')
glb_path = info_path.with_name(info['name'] + '.glb')

R = info['diameter_mm'] / 20
T = 0.14 * info['diameter_mm'] / 10

PROFILE = [
    (0.00, 0.00),
    (0.98, 0.00),
    (1.00, 0.15),
    (1.00, 0.75),
    (0.97, 0.95),
    (0.92, 1.00),
    (0.86, 1.00),
    (0.80, 0.80),
    (0.77, 0.70),
    (0.00, 0.70),
]

bpy.ops.wm.read_factory_settings(use_empty=True)

mesh = bpy.data.meshes.new('button')
obj = bpy.data.objects.new('button', mesh)
bpy.context.scene.collection.objects.link(obj)

bm = bmesh.new()
verts = [bm.verts.new((r * R, 0, z * T)) for r, z in PROFILE]
for a, b in zip(verts, verts[1:]):
    bm.edges.new((a, b))
bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 0, 1),
               dvec=(0, 0, 0), angle=2 * math.pi, steps=64)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(mesh)
bm.free()

bpy.context.view_layer.objects.active = obj
for hole in info['holes']:
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=hole['r'] * R, depth=3 * T,
                                        location=(hole['x'] * R, hole['y'] * R, T / 2))
    cutter = bpy.context.active_object
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new('hole', 'BOOLEAN')
    mod.object = cutter
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier='hole')
    bpy.data.objects.remove(cutter)

while obj.data.uv_layers:
    obj.data.uv_layers.remove(obj.data.uv_layers[0])
obj.data.materials.clear()
bm = bmesh.new()
bm.from_mesh(obj.data)
uv_layer = bm.loops.layers.uv.new('UVMap')
for face in bm.faces:
    for loop in face.loops:
        x, y, _ = loop.vert.co
        distance = math.hypot(x, y)
        if face.normal.z < 0.5 and distance > 0.9 * R:
            x, y = x * 0.97 * R / distance, y * 0.97 * R / distance
        loop[uv_layer].uv = (x / R / 2 + 0.5, y / R / 2 + 0.5)
bm.to_mesh(obj.data)
bm.free()

obj.data.polygons.foreach_set('use_smooth', [True] * len(obj.data.polygons))
split = obj.modifiers.new('split', 'EDGE_SPLIT')
split.split_angle = math.radians(35)
bpy.ops.object.modifier_apply(modifier='split')

mat = bpy.data.materials.new('button_face')
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes['Principled BSDF']
tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(str(face_png))
links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.35
obj.data.materials.append(mat)

bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format='GLB')
print('Wrote', glb_path, '| verts', len(obj.data.vertices), '| faces', len(obj.data.polygons))

