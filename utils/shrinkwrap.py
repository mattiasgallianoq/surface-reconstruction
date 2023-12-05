import bpy

def shrinkwrap(inp_path, out_path, target_path, config):
    bpy.ops.import_mesh.ply(filepath=target_path)
    target = bpy.context.object

    bpy.ops.import_mesh.ply(filepath=inp_path)
    object = bpy.context.object

    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers['Shrinkwrap'].target = target
    bpy.ops.export_scene.obj(filepath=out_path, use_selection=True, use_mesh_modifiers=True, path_mode="RELATIVE", axis_forward="Y", axis_up="Z")