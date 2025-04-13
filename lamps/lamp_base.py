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

# Constants
SHADE_SIZE = 200  # Size of the lamp shade (from simple_lamp_cube.py)
SHADE_THICKNESS = 3  # Thickness of the lamp shade
BASE_HEIGHT = SHADE_SIZE / 3  # 1/3rd the height of the lamp shade
WALL_THICKNESS = 3  # Thickness of the base walls (same as lamp shade)
NOTCH_HEIGHT = 15  # Height of the notches
NOTCH_DEPTH = 5  # Depth of the notches
BULB_CLEARANCE = 120  # Inner space for bulb

# Function to create lamp base with notches
def create_lamp_base(size=SHADE_SIZE, height=BASE_HEIGHT, location=(0, 0, 0)):
    # Create a new mesh and bmesh
    mesh = bpy.data.meshes.new("LampBase_Mesh")
    bm = bmesh.new()
    
    # Half of the size for vertex coordinates
    half_size = size / 2
    
    # Outer dimensions
    outer_verts = [
        # Bottom vertices (outer)
        bm.verts.new((-half_size, -half_size, 0)),         # 0 Bottom front left
        bm.verts.new((half_size, -half_size, 0)),          # 1 Bottom front right
        bm.verts.new((half_size, half_size, 0)),           # 2 Bottom back right
        bm.verts.new((-half_size, half_size, 0)),          # 3 Bottom back left
        
        # Top vertices (outer)
        bm.verts.new((-half_size, -half_size, height)),    # 4 Top front left
        bm.verts.new((half_size, -half_size, height)),     # 5 Top front right
        bm.verts.new((half_size, half_size, height)),      # 6 Top back right
        bm.verts.new((-half_size, half_size, height)),     # 7 Top back left
    ]
    
    # Inner dimensions for the hollow part (for the light bulb)
    inner_half_size = (size - 2 * WALL_THICKNESS) / 2
    inner_verts = [
        # Bottom vertices (inner)
        bm.verts.new((-inner_half_size, -inner_half_size, WALL_THICKNESS)),   # 8 Bottom front left
        bm.verts.new((inner_half_size, -inner_half_size, WALL_THICKNESS)),    # 9 Bottom front right
        bm.verts.new((inner_half_size, inner_half_size, WALL_THICKNESS)),     # 10 Bottom back right
        bm.verts.new((-inner_half_size, inner_half_size, WALL_THICKNESS)),    # 11 Bottom back left
        
        # Top vertices (inner)
        bm.verts.new((-inner_half_size, -inner_half_size, height)),          # 12 Top front left
        bm.verts.new((inner_half_size, -inner_half_size, height)),           # 13 Top front right
        bm.verts.new((inner_half_size, inner_half_size, height)),            # 14 Top back right
        bm.verts.new((-inner_half_size, inner_half_size, height)),           # 15 Top back left
    ]
    
    # Create faces for the outer shell
    # Bottom face
    bm.faces.new([outer_verts[0], outer_verts[1], outer_verts[2], outer_verts[3]])
    
    # Side faces (outer)
    bm.faces.new([outer_verts[0], outer_verts[4], outer_verts[5], outer_verts[1]])  # Front
    bm.faces.new([outer_verts[1], outer_verts[5], outer_verts[6], outer_verts[2]])  # Right
    bm.faces.new([outer_verts[2], outer_verts[6], outer_verts[7], outer_verts[3]])  # Back
    bm.faces.new([outer_verts[3], outer_verts[7], outer_verts[4], outer_verts[0]])  # Left
    
    # Create faces for the inner shell
    # Bottom face (inner)
    bm.faces.new([inner_verts[0], inner_verts[3], inner_verts[2], inner_verts[1]])
    
    # Side faces (inner)
    bm.faces.new([inner_verts[0], inner_verts[1], inner_verts[5], inner_verts[4]])  # Front
    bm.faces.new([inner_verts[1], inner_verts[2], inner_verts[6], inner_verts[5]])  # Right
    bm.faces.new([inner_verts[2], inner_verts[3], inner_verts[7], inner_verts[6]])  # Back
    bm.faces.new([inner_verts[3], inner_verts[0], inner_verts[4], inner_verts[7]])  # Left
    
    # Connect inner and outer at the top (horizontal rim)
    bm.faces.new([outer_verts[4], outer_verts[7], inner_verts[7], inner_verts[4]])  # Front
    bm.faces.new([outer_verts[5], outer_verts[4], inner_verts[4], inner_verts[5]])  # Right
    bm.faces.new([outer_verts[6], outer_verts[5], inner_verts[5], inner_verts[6]])  # Back
    bm.faces.new([outer_verts[7], outer_verts[6], inner_verts[6], inner_verts[7]])  # Left
    
    # Now create the notch system on top of the base
    notch_verts = []
    
    # Number of notches per side - adjust as needed for a secure fit
    num_notches = 4
    
    # Create notches on all four sides
    sides = [
        # Vertices defining each side's upper edge [start_vert, end_vert, direction vector]
        [outer_verts[4], outer_verts[5], (1, 0, 0)],  # Front edge
        [outer_verts[5], outer_verts[6], (0, 1, 0)],  # Right edge
        [outer_verts[6], outer_verts[7], (-1, 0, 0)], # Back edge
        [outer_verts[7], outer_verts[4], (0, -1, 0)]  # Left edge
    ]
    
    for side_idx, side in enumerate(sides):
        start_vert, end_vert, direction = side
        edge_length = size - 2 * NOTCH_DEPTH  # Leave space at corners
        
        # Calculate the edge vector
        start_point = start_vert.co.copy()
        start_point.x += direction[0] * NOTCH_DEPTH
        start_point.y += direction[1] * NOTCH_DEPTH
        
        # Spacing between notches
        spacing = edge_length / (num_notches * 2)
        
        # Create notches along this side
        for i in range(num_notches):
            # Calculate position for this notch
            notch_pos = start_point.copy()
            offset = spacing * (2 * i + 1)
            notch_pos.x += direction[0] * offset
            notch_pos.y += direction[1] * offset
            
            # Create notch vertices (outer and inner)
            notch_outer = bm.verts.new((notch_pos.x, notch_pos.y, height))
            notch_pos_inner = notch_pos.copy()
            notch_pos_inner.z += NOTCH_HEIGHT
            notch_inner = bm.verts.new((notch_pos_inner.x, notch_pos_inner.y, height + NOTCH_HEIGHT))
            
            # Store vertices
            notch_verts.append((notch_outer, notch_inner, side_idx, i))
    
    # Create the notch geometry - connecting with faces
    for i, (outer_v, inner_v, side_idx, notch_idx) in enumerate(notch_verts):
        # Find the next notch on the same side
        next_idx = (notch_idx + 1) % num_notches
        next_notches = [v for v in notch_verts if v[2] == side_idx and v[3] == next_idx]
        
        if next_notches:
            next_outer, next_inner, _, _ = next_notches[0]
            
            # Create faces connecting current notch to next notch
            # Check if they're adjacent
            if abs(notch_idx - next_idx) == 1 or (notch_idx == 0 and next_idx == num_notches - 1) or (notch_idx == num_notches - 1 and next_idx == 0):
                # Outer face (vertical)
                bm.faces.new([outer_v, inner_v, next_inner, next_outer])
                
                # Create triangular faces for the top instead of using duplicated vertices
                bm.faces.new([inner_v, next_inner, outer_v])  # First triangle
                bm.faces.new([next_inner, next_outer, outer_v])  # Second triangle
    
    # Write the bmesh to the mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Create object from mesh
    obj = bpy.data.objects.new("LampBase", mesh)
    
    # Link object to scene collection
    bpy.context.collection.objects.link(obj)
    
    # Position the object
    obj.location = location
    
    # Make the created object active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    return obj

# Create the lamp base
lamp_base = create_lamp_base(
    size=SHADE_SIZE,
    height=BASE_HEIGHT,
    location=(0, 0, 0)
)

# Add a material for the base
base_material = bpy.data.materials.new(name="LampBase_Material")
base_material.use_nodes = True
lamp_base.data.materials.append(base_material)

# Configure material
bsdf = base_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)  # Darker color for base
bsdf.inputs["Metallic"].default_value = 0.7  # Slightly metallic look
bsdf.inputs["Roughness"].default_value = 0.2  # Less rough (more smooth)

# Add solidify modifier for clean geometry
bpy.ops.object.modifier_add(type='SOLIDIFY')
solidify_modifier = lamp_base.modifiers["Solidify"]
solidify_modifier.thickness = 0.01  # Very small thickness for cleanup
solidify_modifier.offset = 0.0

# Add bevel modifier for rounded edges
bpy.ops.object.modifier_add(type='BEVEL')
bevel_modifier = lamp_base.modifiers["Bevel"]
bevel_modifier.width = 2.0  # 2mm smaller bevel than the shade
bevel_modifier.segments = 6  # Fewer segments than the shade
bevel_modifier.limit_method = 'ANGLE'
bevel_modifier.angle_limit = 0.785398  # 45 degrees in radians
bevel_modifier.profile = 0.5  # Rounded profile

# Smooth the base
bpy.ops.object.shade_smooth()

# Apply modifiers
bpy.ops.object.modifier_apply(modifier=bevel_modifier.name)
bpy.ops.object.modifier_apply(modifier=solidify_modifier.name)

# Export the lamp base to STL
export_filepath = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/lamp_base.stl"

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
export_to_stl(lamp_base, export_filepath)

print("Lamp base with notch connector system created in millimeters and exported to STL!")
print(f"Exported to: {export_filepath}")