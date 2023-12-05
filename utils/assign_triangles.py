import pymeshlab
import open3d as o3d
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

def assign_triangles(inp_mesh_path, inp_mat_paths, out_mesh_verts_path, out_material_tris_paths, config):

    mesh = o3d.io.read_triangle_mesh(inp_mesh_path)

    mesh_verts, mesh_tris = np.array(mesh.vertices), np.array(mesh.triangles)

    centroids = []

    for tri in mesh_tris:
        tri0_coords = mesh_verts[tri[0]]
        tri1_coords = mesh_verts[tri[1]]
        tri2_coords = mesh_verts[tri[2]]
        coords = [tri0_coords, tri1_coords, tri2_coords]

        centroid = np.mean(coords, axis=0)

        centroids.append(centroid)
    
    centroids = np.array(centroids)

    material_points = []

    for inp_mat_path in inp_mat_paths:
        meshset = pymeshlab.MeshSet()
        meshset.load_new_mesh(inp_mat_path)
        points = meshset.current_mesh().vertex_matrix()
        
        material_points.append(points)
    
    material_labels = []

    for i, points in enumerate(material_points):
        material_labels.append([i for point in range(len(points))])
    
    n_neighbors = config["params"]["n_neighbors"]
    neigh = KNeighborsClassifier(n_neighbors=n_neighbors)

    X = np.concatenate(material_points)
    y = np.concatenate(material_labels)

    neigh.fit(X, y)

    res = neigh.predict(centroids)

    colormap = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 0, 1)}

    colors = [colormap[x] for x in res]

    colors = np.array(colors)

    viz = o3d.geometry.PointCloud()
    viz.points = o3d.utility.Vector3dVector(centroids) # whole_centroids
    viz.colors = o3d.utility.Vector3dVector(colors)

    ### visualize
    o3d.visualization.draw_geometries([viz])

    if config["debug"]: o3d.io.write_point_cloud(f'debug/out_{n_neighbors}.ply', viz) # save if debug true

    res_tris = [[] for x in range(len(inp_mat_paths))]
    
    for i in range(len(res)):
        tri, mat = mesh_tris[i], res[i]
        res_tris[mat].append(tri)
    
    for i, mat_tris in enumerate(res_tris):
        out_tris = np.array(mat_tris)
        np.save(out_material_tris_paths[i], out_tris)
    
    np.save(out_mesh_verts_path, mesh_verts)