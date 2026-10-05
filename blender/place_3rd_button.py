import bpy                                    # Blender's Python module: gives access to the scene, objects, files
from mathutils import Vector, Matrix          # Vector = 3D point/direction, Matrix = a transformation (move/rotate/scale)

BTN_X, BTN_Z = -1.5, 122.1                    # x (side to side) and z (height) of the inner upper button, in cm
HOLE_X, HOLE_Z = 1.0, 122.0                   # same, for the inner upper buttonhole
ROW_GAP = 8.9                                 # distance between two button rows, in cm
# ----------------------------------------------------------   (just a visual divider)

btn_src = bpy.data.objects["top_left_closure_button"]   # the existing button we copy, looked up by name
hole_src = bpy.data.objects["top_right_button_hole"]    # the existing buttonhole we copy

def centre(o):                                            # returns the world-space centre of object o
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]   # the 8 box corners, each converted local -> world
    return sum(pts, Vector()) / 8                         # add the 8 corners (starting from zero) and average them

def surface_point(x, z):                                  # find the cloth at this x and height
    """Ray from in front of the jacket. Returns (point, normal) in WORLD space."""   # docstring: describes the function
    origin = Vector((x, -60, z))                          # laser start: at x and z, 60 cm in front of the jacket (front = -y)
    best = None                                           # "no hit stored yet"

    t = bpy.data.objects["body"]                          # the object the laser shoots at
    M = t.matrix_world                                    # body's transformation: local -> world
    inv = M.inverted()                                    # the reverse: world -> local
    d = (inv.to_3x3() @ Vector((0, 1, 0))).normalized()   # laser direction (+y, front to back) in local space, length 1
    hit, loc, nrm, _ = t.ray_cast(inv @ origin, d)        # fire laser (local space): hit?, point, normal, face index (ignored)
    if hit:                                               # only continue if the laser touched the body
        n_w = (M.to_3x3() @ nrm).normalized()             # surface normal converted to world space
        if n_w.y > 0:                                     # normal points backwards: we hit the inside of the back panel
            raise RuntimeError(f"hit the back at x={x}, z={z}")   # stop with a clear error (this replaces your bare return)
        p = M @ loc                                       # hit point converted to world space
        dist = (p - origin).length                        # distance from laser start to the hit
        if best is None:                                  # first hit: store it
            best = (dist, p, (M.to_3x3() @ nrm).normalized(), t.name)   # store distance, point, world normal, object name
    if best is None:                                      # nothing stored: the laser missed
        raise RuntimeError(f"ray missed at x={x}, z={z}") # stop with a clear message
    print("hit", best[3], "at", best[1])                  # debug printout: object name and hit point
    return best[1], best[2]                               # give back (point, normal)

def place_copy(src, x, z):                                # copy object src and put the copy on the cloth at x, z
    c = centre(src)                                       # world-space centre of the original
    p_src, n_src = surface_point(c.x, c.z)                # cloth point and normal right behind the original
    lift = (c - p_src).dot(n_src)                         # how far the original floats off the cloth, along the normal
    p_new, n_new = surface_point(x, z)                    # cloth point and normal at the new spot
    delta = n_src.rotation_difference(n_new)              # the turn that takes the old normal to the new one

    new = src.copy()                                      # duplicate the object (still shares the mesh)
    new.data = src.data.copy()                            # give the copy its own mesh, so edits don't touch the original
    bpy.context.collection.objects.link(new)              # add the copy to the scene
    # put the geometry's centre on the object origin so .location means something
    new.data.transform(Matrix.Translation(-(src.matrix_world.inverted() @ c)))   # shift the vertices so their centre sits at the origin
    new.location = p_new + n_new * lift                   # place it: cloth point + lift along the normal
    new.rotation_euler = (delta @ src.rotation_euler.to_quaternion()).to_euler() # original's rotation + the extra turn
    return new                                            # hand the new object back

btn3 = place_copy(btn_src, BTN_X, BTN_Z - 2 * ROW_GAP)    # new button, two rows below the upper one (~104.3)
btn3.name = "closure3_button"                             # give it a clear name
hole3 = place_copy(hole_src, HOLE_X, HOLE_Z - 2 * ROW_GAP)   # new buttonhole at the same height
hole3.name = "closure3_hole"                              # name it too

bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//blazer_3_closure.blend"))   # save as a new file next to the source