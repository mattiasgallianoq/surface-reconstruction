import pymeshlab

def smooth(inp_path, out_path, config):
    ms = pymeshlab.MeshSet()

    ms.load_new_mesh(inp_path)

    repair_iters = config['params']['repair_iters']

    while repair_iters: # repair loop
        ms.meshing_repair_non_manifold_vertices()
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_close_holes(maxholesize=100)

        repair_iters -= 1
    
    remesh_iters = config['params']['remesh_iters']
    face_threshold = config['params']['face_threshold']

    while remesh_iters:
        faces = ms.current_mesh().face_number()

        while faces >= face_threshold:
            target = faces // 2
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target)
            faces = ms.current_mesh().face_number()
        
        ms.meshing_repair_non_manifold_vertices()
        ms.meshing_repair_non_manifold_edges()
        
        ms.meshing_surface_subdivision_ls3_loop(threshold=pymeshlab.Percentage(1))
        
        remesh_iters -= 1

    ms.meshing_isotropic_explicit_remeshing(targetlen=pymeshlab.Percentage(0.25))

    ms.save_current_mesh(out_path)