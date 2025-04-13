import bpy
import bmesh
import os
import math

# Set up the scene for mm
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a rectangular lamp shade with an open bottom
def create_rectangular_lamp_shade(width=100, depth=100, height=180, thickness=1, location=(0, 0, 0)):
    # Create a simple cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    cube = bpy.context.active_object
    
    # Scale the cube to the desired dimensions
    cube.scale = (width, depth, height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select only the bottom face
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='FACE')
    
    bm = bmesh.from_edit_mesh(cube.data)
    for face in bm.faces:
        face_center = face.calc_center_median()
        if abs(face_center.z - 0) < 0.001:  # Bottom face has z close to 0
            face.select = True
    
    bmesh.update_edit_mesh(cube.data)
    
    # Delete the selected face to create the opening
    bpy.ops.mesh.delete(type='FACE')
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add solidify modifier to give it thickness
    solidify_mod = cube.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify_mod.thickness = thickness
    solidify_mod.offset = 0.0  # Center the thickness
    
    # Add bevel modifier for rounded edges
    bevel_mod = cube.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 5.0  # 5mm bevel
    bevel_mod.segments = 8  # Segments for smooth bevel
    bevel_mod.limit_method = 'ANGLE'
    bevel_mod.angle_limit = 0.785398  # 45 degrees in radians
    
    # Apply both modifiers
    bpy.ops.object.modifier_apply(modifier=solidify_mod.name)
    bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
    
    # Final cleanup
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.01)  # Merge vertices that are very close
    bpy.ops.mesh.normals_make_consistent(inside=False)  # Correct normals
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Rename the object
    cube.name = "RectangularLampShade"
    return cube

# Create the rectangular lamp shade
lamp_shade = create_rectangular_lamp_shade(
    width=100,      # Width of 100mm as specified
    depth=100,      # Depth of 100mm for a square base
    height=180,     # Height of 180mm as specified
    thickness=1,    # 1mm wall thickness as requested
    location=(0, 0, 0)
)

# Export the lamp shade to STL
export_filepath = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/rectangular_lamp_shade.stl"

# Export function
def export_to_stl(obj, filepath):
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select only our object
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Export to STL
    bpy.ops.export_mesh.stl(
        filepath=filepath,
        check_existing=True,
        filter_glob='*.stl',
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=True,
        ascii=False,
        use_mesh_modifiers=True
    )
    
    print(f"Model exported to: {filepath}")

# Export the model
export_to_stl(lamp_shade, export_filepath)

print("Rectangular lamp shade created with dimensions 100x100x180mm and exported to STL!")
print(f"Exported to: {export_filepath}")
print("Model optimized for 3D printing with a very simple approach: a rectangle with 1mm thickness and open bottom.")