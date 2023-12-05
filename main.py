import os
import bpy # TODO this has to be imported before pymeshlab??
import pymeshlab
import json
import shutil
import pathlib
from utils import smooth, shrinkwrap, assign_triangles, export_usda

'''
setup:
conda create -n surface-recon python=3.10
conda activate surface-recon
pip install -r "requirements.txt"

running:
edit config

run surface recon model e.g. finn TODO may need to sub this model due to scaling / offset, also required env possibly incompatible with bpy
e.g. os.system(f"powershell cp {surfel_cloud} ./FINN/")
os.system(f"conda activate finn && cd FINN && python surface_reconstruct.py --pc_num 10000 --model FINN -g 0")

specify input global mesh, material clouds, properties, parameterts in config.json

python main.py
'''

def run():
    os.makedirs("tmp", exist_ok=True) # create tmp dir
    
    ### read config
    with open('config/config.json') as f: config = json.load(f)
    print("finished reading config")

    mesh_path = config["io"]["mesh_path"] # set mesh path
    material_paths = [config["io"]["materials"][material]["cloud_path"] for material in config["io"]["materials"]] # set material paths

    ### repair, smooth raw mesh
    inp_path = mesh_path
    output_path = os.path.join("tmp", os.path.splitext(os.path.basename(inp_path))[0] + "_smooth" + os.path.splitext(inp_path)[1])
    smoothed_path = output_path # save path for later

    smooth.smooth(inp_path, output_path, config)
    print("finished smooothing")

    ### shrinkwrap material segment clouds to smoothed mesh
    shrink_paths = [] # save paths for later

    for material_path in material_paths:
        inp_path = material_path
        out_path = os.path.join("tmp", os.path.splitext(os.path.basename(inp_path))[0] + "_shrink" + ".obj")
        target_path = smoothed_path
        
        shrinkwrap.shrinkwrap(inp_path, out_path, target_path, config)
        print(f"finished shrinkwrapping {inp_path}")

        shrink_path = out_path # save paths for later
        shrink_paths.append(shrink_path)

    ### assign shrinwrapped material segment clouds to smoothed mesh triangles via greedy clustering
    inp_mesh_path = smoothed_path
    inp_material_paths = shrink_paths
    out_mesh_verts_path = os.path.join("tmp", os.path.splitext(os.path.basename(inp_mesh_path))[0] + "_verts" + ".npy")
    out_material_tris_paths = [os.path.join("tmp", os.path.splitext(os.path.basename(inp_material_path))[0] + "_tris" + ".npy") for inp_material_path in inp_material_paths]

    assign_triangles.assign_triangles(inp_mesh_path, inp_material_paths, out_mesh_verts_path, out_material_tris_paths, config)
    print("finished material mapping")
    
    ### convert smoothed mesh vertices, material assigned-triangles, and material properties to usd scene
    inp_vert_path = out_mesh_verts_path
    inp_tri_paths = out_material_tris_paths
    out_path = config["io"]["output_path"]

    export_usda.export_usda(inp_vert_path, inp_tri_paths, out_path, config)
    print("finished export")

    shutil.rmtree("tmp") # cleanup

if __name__ == "__main__":
    run()