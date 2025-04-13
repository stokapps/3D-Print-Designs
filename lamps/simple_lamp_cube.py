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

# Create an open-bottomed cube using BMesh with vertical lines
def create_open_bottom_cube_with_lines(size=200, location=(0, 0, 0), num_lines=8, line_depth=5):
    # Create a new mesh and bmesh
    mesh = bpy.data.meshes.new("OpenBottomCube_Mesh")
    bm = bmesh.new()
    
    # Half of the size for vertex coordinates
    half_size = size / 2
    
    # Create the base vertices (8 corners of a cube)
    corners = [
        bm.verts.new((-half_size, -half_size, -half_size)),  # 0 Bottom front left
        bm.verts.new((half_size, -half_size, -half_size)),   # 1 Bottom front right
        bm.verts.new((half_size, half_size, -half_size)),    # 2 Bottom back right
        bm.verts.new((-half_size, half_size, -half_size)),   # 3 Bottom back left
        bm.verts.new((-half_size, -half_size, half_size)),   # 4 Top front left
        bm.verts.new((half_size, -half_size, half_size)),    # 5 Top front right
        bm.verts.new((half_size, half_size, half_size)),     # 6 Top back right
        bm.verts.new((-half_size, half_size, half_size)),    # 7 Top back left
    ]
    
    # Create the top face (kept clean, no vertical lines)
    bm.faces.new([corners[4], corners[5], corners[6], corners[7]])
    
    # Create arrays to store all vertices for the sides
    # We'll use these to create faces with vertical lines
    front_verts_bottom = [corners[0]]
    front_verts_top = [corners[4]]
    right_verts_bottom = [corners[1]]
    right_verts_top = [corners[5]]
    back_verts_bottom = [corners[2]]
    back_verts_top = [corners[6]]
    left_verts_bottom = [corners[3]]
    left_verts_top = [corners[7]]
    
    # Calculate spacing between lines
    spacing = size / num_lines
    
    # Create vertices for the vertical lines on each face
    for i in range(1, num_lines):
        # Parameter 't' goes from 0 to 1 across each side
        t = i / num_lines
        
        # Front face vertices
        x_front = -half_size + (size * t)
        # Bottom edge
        front_verts_bottom.append(bm.verts.new((x_front, -half_size, -half_size)))
        # Top edge
        front_verts_top.append(bm.verts.new((x_front, -half_size, half_size)))
        
        # Right face vertices
        y_right = -half_size + (size * t)
        # Bottom edge
        right_verts_bottom.append(bm.verts.new((half_size, y_right, -half_size)))
        # Top edge
        right_verts_top.append(bm.verts.new((half_size, y_right, half_size)))
        
        # Back face vertices
        x_back = half_size - (size * t)
        # Bottom edge
        back_verts_bottom.append(bm.verts.new((x_back, half_size, -half_size)))
        # Top edge
        back_verts_top.append(bm.verts.new((x_back, half_size, half_size)))
        
        # Left face vertices
        y_left = half_size - (size * t)
        # Bottom edge
        left_verts_bottom.append(bm.verts.new((-half_size, y_left, -half_size)))
        # Top edge
        left_verts_top.append(bm.verts.new((-half_size, y_left, half_size)))
        
        # Add the vertical line indentations by creating vertices pushed inward
        # Only do this if line_depth > 0
        if line_depth > 0:
            # Front face line
            front_line_bottom = bm.verts.new((x_front, -half_size + line_depth, -half_size))
            front_line_top = bm.verts.new((x_front, -half_size + line_depth, half_size))
            
            # Create faces on either side of the line
            # Left side of the line
            if i > 1:
                bm.faces.new([front_verts_bottom[i-1], front_verts_top[i-1], 
                              front_line_top, front_line_bottom])
            
            # Right side of the line
            if i < num_lines - 1:
                bm.faces.new([front_line_bottom, front_line_top, 
                              front_verts_top[i], front_verts_bottom[i]])
            
            # Right face line
            right_line_bottom = bm.verts.new((half_size - line_depth, y_right, -half_size))
            right_line_top = bm.verts.new((half_size - line_depth, y_right, half_size))
            
            # Create faces on either side of the line
            # Left side of the line
            if i > 1:
                bm.faces.new([right_verts_bottom[i-1], right_verts_top[i-1], 
                              right_line_top, right_line_bottom])
            
            # Right side of the line
            if i < num_lines - 1:
                bm.faces.new([right_line_bottom, right_line_top, 
                              right_verts_top[i], right_verts_bottom[i]])
            
            # Back face line
            back_line_bottom = bm.verts.new((x_back, half_size - line_depth, -half_size))
            back_line_top = bm.verts.new((x_back, half_size - line_depth, half_size))
            
            # Create faces on either side of the line
            # Left side of the line
            if i > 1:
                bm.faces.new([back_verts_bottom[i-1], back_verts_top[i-1], 
                              back_line_top, back_line_bottom])
            
            # Right side of the line
            if i < num_lines - 1:
                bm.faces.new([back_line_bottom, back_line_top, 
                              back_verts_top[i], back_verts_bottom[i]])
            
            # Left face line
            left_line_bottom = bm.verts.new((-half_size + line_depth, y_left, -half_size))
            left_line_top = bm.verts.new((-half_size + line_depth, y_left, half_size))
            
            # Create faces on either side of the line
            # Left side of the line
            if i > 1:
                bm.faces.new([left_verts_bottom[i-1], left_verts_top[i-1], 
                              left_line_top, left_line_bottom])
            
            # Right side of the line
            if i < num_lines - 1:
                bm.faces.new([left_line_bottom, left_line_top, 
                              left_verts_top[i], left_verts_bottom[i]])
    
    # Add the last vertices for each side
    front_verts_bottom.append(corners[1])
    front_verts_top.append(corners[5])
    right_verts_bottom.append(corners[2])
    right_verts_top.append(corners[6])
    back_verts_bottom.append(corners[3])
    back_verts_top.append(corners[7])
    left_verts_bottom.append(corners[0])
    left_verts_top.append(corners[4])
    
    # Create the side faces between the vertical lines
    for i in range(num_lines):
        # Front face strip
        if i == 0 or i == num_lines - 1 or line_depth == 0:
            bm.faces.new([front_verts_bottom[i], front_verts_top[i], 
                          front_verts_top[i+1], front_verts_bottom[i+1]])
        
        # Right face strip
        if i == 0 or i == num_lines - 1 or line_depth == 0:
            bm.faces.new([right_verts_bottom[i], right_verts_top[i], 
                          right_verts_top[i+1], right_verts_bottom[i+1]])
        
        # Back face strip
        if i == 0 or i == num_lines - 1 or line_depth == 0:
            bm.faces.new([back_verts_bottom[i], back_verts_top[i], 
                          back_verts_top[i+1], back_verts_bottom[i+1]])
        
        # Left face strip
        if i == 0 or i == num_lines - 1 or line_depth == 0:
            bm.faces.new([left_verts_bottom[i], left_verts_top[i], 
                          left_verts_top[i+1], left_verts_bottom[i+1]])
    
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

# Create the open-bottomed cube with vertical lines
lamp_shade = create_open_bottom_cube_with_lines(
    size=200, 
    location=(0, 0, 0), 
    num_lines=12,  # Number of divisions (including corners)
    line_depth=3   # Depth of the vertical lines in mm
)

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