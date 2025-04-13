import bpy
import bmesh
import os

# Set up the scene for mm
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create an open-bottomed cube using BMesh
def create_open_bottom_cube(size=200, location=(0, 0, 0)):
    # Create a new mesh and bmesh
    mesh = bpy.data.meshes.new("OpenBottomCube_Mesh")
    bm = bmesh.new()
    
    # Half of the size for vertex coordinates
    half_size = size / 2
    
    # Create vertices (8 corners of a cube)
    v1 = bm.verts.new((-half_size, -half_size, -half_size))  # Bottom front left
    v2 = bm.verts.new((half_size, -half_size, -half_size))   # Bottom front right
    v3 = bm.verts.new((half_size, half_size, -half_size))    # Bottom back right
    v4 = bm.verts.new((-half_size, half_size, -half_size))   # Bottom back left
    v5 = bm.verts.new((-half_size, -half_size, half_size))   # Top front left
    v6 = bm.verts.new((half_size, -half_size, half_size))    # Top front right
    v7 = bm.verts.new((half_size, half_size, half_size))     # Top back right
    v8 = bm.verts.new((-half_size, half_size, half_size))    # Top back left
    
    # Create the 5 faces (excluding the bottom)
    # Top face
    bm.faces.new([v5, v6, v7, v8])
    # Front face
    bm.faces.new([v1, v2, v6, v5])
    # Right face
    bm.faces.new([v2, v3, v7, v6])
    # Back face
    bm.faces.new([v3, v4, v8, v7])
    # Left face
    bm.faces.new([v4, v1, v5, v8])
    
    # Note: We're intentionally NOT creating the bottom face
    
    # Write the bmesh to the mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Create object from mesh
    obj = bpy.data.objects.new("LampShade_Base", mesh)
    
    # Link object to scene collection
    bpy.context.collection.objects.link(obj)
    
    # Position the object
    obj.location = location
    
    # Make the created object active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    return obj

# Create the open-bottomed cube
lamp_shade = create_open_bottom_cube(size=200, location=(0, 0, 0))

# Add a material
material = bpy.data.materials.new(name="LampShade_Material")
material.use_nodes = True
lamp_shade.data.materials.append(material)

# Make it slightly transparent - handle different Blender versions
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1.0)  # White color

# Handle "Transmission" property which might have different names in different Blender versions
transmission_input = None
# Try different possible names for transmission
possible_names = ["Transmission", "Alpha", "Transparency"]
for name in possible_names:
    if name in bsdf.inputs:
        transmission_input = bsdf.inputs[name]
        break

# Set transmission if found
if transmission_input:
    transmission_input.default_value = 0.3  # Slight transparency
else:
    print("Warning: Could not find transparency/transmission input in Principled BSDF shader")

# Add bevel modifier for rounded edges
bpy.ops.object.modifier_add(type='BEVEL')
bevel_modifier = lamp_shade.modifiers["Bevel"]
bevel_modifier.width = 30.0  # 30mm large bevel
bevel_modifier.segments = 10  # More segments for smoother bevel
bevel_modifier.limit_method = 'ANGLE'  # Only bevel edges at certain angles
bevel_modifier.angle_limit = 0.785398  # 45 degrees in radians
bevel_modifier.profile = 0.5  # Rounded profile (0.5 is a semicircle)

# Add solidify modifier for thickness
bpy.ops.object.modifier_add(type='SOLIDIFY')
solidify_modifier = lamp_shade.modifiers["Solidify"]
solidify_modifier.thickness = 3.0  # 3mm thickness
solidify_modifier.offset = 0.0

# Smooth the shade
bpy.ops.object.shade_smooth()

# Export the lamp shade to STL for 3D printing
def export_to_stl(obj, filepath):
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select only our lamp shade
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

# Use explicit path to the STLs directory
export_filepath = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/lamp_shade.stl"

# Apply the modifiers before export to ensure proper geometry in the STL
# Apply bevel first, then solidify
bpy.ops.object.modifier_apply(modifier=bevel_modifier.name)
bpy.ops.object.modifier_apply(modifier=solidify_modifier.name)

# Export the model
export_to_stl(lamp_shade, export_filepath)

print("Open-bottomed lamp shade with rounded bevels created in millimeters and exported to STL!")
print(f"Exported to: {export_filepath}")