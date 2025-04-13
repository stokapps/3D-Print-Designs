import bpy
import os
import math

# Set up the scene for mm
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a super simple rectangular lamp shade
bpy.ops.mesh.primitive_cube_add(size=1)
cube = bpy.context.active_object

# Scale to our dimensions (100x100x180mm)
cube.scale = (50, 50, 90)
bpy.ops.object.transform_apply(scale=True)

# Position it so the bottom is at z=0
cube.location = (0, 0, 90)
bpy.ops.object.transform_apply(location=True)

# Remove the bottom face
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_mode(type='FACE')

# Switch to object mode to select the face
bpy.ops.object.mode_set(mode='OBJECT')
for face in cube.data.polygons:
    if face.normal.z < -0.5:  # Bottom face (normal points down)
        face.select = True

# Delete the face
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='FACE')

# Add thickness
bpy.ops.object.mode_set(mode='OBJECT')
solidify = cube.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 1.0  # 1mm thickness
bpy.ops.object.modifier_apply(modifier=solidify.name)

# STL export path
stl_path = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/rectangular_lamp_shade.stl"

# Make sure the directory exists
os.makedirs(os.path.dirname(stl_path), exist_ok=True)

# Try exporting
bpy.ops.object.select_all(action='DESELECT')
cube.select_set(True)
bpy.context.view_layer.objects.active = cube

try:
    # This is the newer method (Blender 4.x)
    bpy.ops.wm.stl_export(filepath=stl_path)
    print(f"STL exported with wm.stl_export to {stl_path}")
except Exception as e:
    print(f"Export with wm.stl_export failed: {e}")
    
    try:
        # This is the older method (pre-4.x)
        bpy.ops.export_mesh.stl(filepath=stl_path)
        print(f"STL exported with export_mesh.stl to {stl_path}")
    except Exception as e:
        print(f"Export with export_mesh.stl failed: {e}")
        
        try:
            # Use the io_mesh_stl add-on directly
            if "io_mesh_stl" not in bpy.context.preferences.addons:
                bpy.ops.preferences.addon_enable(module="io_mesh_stl")
            
            # Now try again with the add-on loaded
            bpy.ops.export_mesh.stl(filepath=stl_path)
            print(f"STL exported with add-on enabled to {stl_path}")
        except Exception as e:
            print(f"All automatic export methods failed: {e}")
            
            # Last resort - manual ASCII STL export
            try:
                with open(stl_path, 'w') as f:
                    f.write("solid RectangularLampShade\n")
                    
                    # Get mesh data
                    mesh = cube.data
                    
                    # Write triangles
                    for poly in mesh.polygons:
                        # Write normal
                        normal = poly.normal
                        f.write(f"  facet normal {normal.x} {normal.y} {normal.z}\n")
                        f.write("    outer loop\n")
                        
                        # Write vertices
                        for vert_idx in poly.vertices:
                            vert = mesh.vertices[vert_idx].co
                            f.write(f"      vertex {vert.x} {vert.y} {vert.z}\n")
                        
                        f.write("    endloop\n")
                        f.write("  endfacet\n")
                    
                    f.write("endsolid RectangularLampShade\n")
                
                print(f"STL exported manually in ASCII format to {stl_path}")
            except Exception as e:
                print(f"All export methods failed: {e}")

print("Basic rectangular lamp shade created with dimensions 100x100x180mm and exported to STL")
print("Features: Simple rectangular shape with 1mm wall thickness and open bottom")