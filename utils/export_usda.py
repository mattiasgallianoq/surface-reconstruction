from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade
import numpy as np

def export_usda(inp_vert_path, inp_tri_paths, out_path, config):

    material_verts, material_faces, material_tris = [], [], []

    for inp_tri_path in inp_tri_paths:
        mat_verts = np.load(inp_vert_path)
        mat_faces = np.load(inp_tri_path)
        mat_tris = [3 for i in range(len(mat_faces))]
        mat_faces = mat_faces.flatten()

        material_verts.append(mat_verts)
        material_faces.append(mat_faces)
        material_tris.append(mat_tris)
    
    stage = Usd.Stage.CreateNew(out_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

    model = UsdGeom.Xform.Define(stage, "/Model")
    Usd.ModelAPI(model).SetKind(Kind.Tokens.component)

    for i, x in enumerate(material_verts):

        material_name = list(config["io"]["materials"].keys())[i]
        mat_verts = material_verts[i]
        mat_tris = material_tris[i]
        mat_faces = material_faces[i]

        material_geom = UsdGeom.Mesh.Define(stage, f"/Model/{material_name}")
        material_geom.CreatePointsAttr(mat_verts)
        material_geom.CreateFaceVertexCountsAttr(mat_tris)
        material_geom.CreateFaceVertexIndicesAttr(mat_faces)
        material_geom.CreateExtentAttr([(0, 0, 0), (2, 2, 2)]) # TODO change scale

        material_material = UsdShade.Material.Define(stage, f"/Model/{material_name}Mat") # def mat
        stInput = material_material.CreateInput('fname:stPrimVarName', Sdf.ValueTypeNames.Token)
        stInput.Set(f"{material_name}St")

        color = tuple(config["io"]["materials"][material_name]["properties"]["color"]) # unpack from config
        metallic = float(config["io"]["materials"][material_name]["properties"]["metallic"])
        roughness = float(config["io"]["materials"][material_name]["properties"]["roughness"])

        material_shader = UsdShade.Shader.Define(stage, f"/Model/{material_name}Mat/{material_name}Shader") # def shade
        material_shader.CreateIdAttr("UsdPreviewSurface")
        material_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
        material_shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)
        material_shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        material_material.CreateSurfaceOutput().ConnectToSource(material_shader.ConnectableAPI(), "surface")

        material_geom.GetPrim().ApplyAPI(UsdShade.MaterialBindingAPI) # bind
        UsdShade.MaterialBindingAPI(material_geom).Bind(material_material)

    stage.Save() # save