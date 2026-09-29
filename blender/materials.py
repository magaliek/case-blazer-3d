import bpy

# 1. make a new material
mat = bpy.data.materials.new("Fabric_Stripe")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]

# 2. add an Image Texture node and load the stripe image
tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(
    bpy.path.abspath("//../assets/Fabrics/Fabric072_2K-JPG_Color.jpg")
)

# 3. plug the image's Color into the BSDF's Base Color
mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

# 4. give it to the outer parts, replacing whatever CLO left there
for name in ["body", "collar", "left_sleeve", "right_sleeve"]:
    mesh = bpy.data.objects[name].data
    mesh.materials.clear()
    mesh.materials.append(mat)

lining_mat = bpy.data.materials.new("Lining")
lining_mat.use_nodes = True
lining_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.05, 0.1, 1.0)   # red-ish for now

lining_mesh = bpy.data.objects["lining"].data
lining_mesh.materials.clear()
lining_mesh.materials.append(lining_mat)

bpy.ops.wm.save_mainfile()