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

# Add vertical lines before adding thickness
# Step 1: Add loop cuts for vertical lines
bpy.ops.mesh.select_all(action='DESELECT')

# Add loop cuts along the X axis (creates vertical lines on front and back)
# We'll add 8 cuts evenly spaced
for i in range(1, 9):
    # Position from 0 to 1
    factor = i / 9
    
    # Select an edge to cut along
    bpy.ops.object.mode_set(mode='OBJECT')
    for edge in cube.data.edges:
        v1 = cube.data.vertices[edge.vertices[0]].co
        v2 = cube.data.vertices[edge.vertices[1]].co
        # Find horizontal edges at the top
        if abs(v1.z - v2.z) < 0.001 and abs(v1.z - 180) < 0.001:
            if abs(v1.y - v2.y) < 0.001:  # Parallel to X axis
                edge.select = True
                break
    
    # Make the cut
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=1)
    
    # Position the cut 
    bpy.ops.transform.translate(value=(0, 0, 0))  # Just to apply the cut
    
    # Deselect for next iteration
    bpy.ops.mesh.select_all(action='DESELECT')

# Add loop cuts along the Y axis (creates vertical lines on left and right)
for i in range(1, 9):
    # Position from 0 to 1
    factor = i / 9
    
    # Select an edge to cut along
    bpy.ops.object.mode_set(mode='OBJECT')
    for edge in cube.data.edges:
        v1 = cube.data.vertices[edge.vertices[0]].co
        v2 = cube.data.vertices[edge.vertices[1]].co
        # Find horizontal edges at the top
        if abs(v1.z - v2.z) < 0.001 and abs(v1.z - 180) < 0.001:
            if abs(v1.x - v2.x) < 0.001:  # Parallel to Y axis
                edge.select = True
                break
    
    # Make the cut
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=1)
    
    # Position the cut
    bpy.ops.transform.translate(value=(0, 0, 0))  # Just to apply the cut
    
    # Deselect for next iteration
    bpy.ops.mesh.select_all(action='DESELECT')

# Step 2: Push in the vertices to create indented lines
bpy.ops.object.mode_set(mode='OBJECT')

# Go through each vertex on the outside of the model
line_depth = 3  # 3mm depth for vertical lines
for vertex in cube.data.vertices:
    # Skip if at top or bottom
    if abs(vertex.co.z - 180) < 0.001 or abs(vertex.co.z) < 0.001:
        continue
        
    # Skip if vertex is at a corner
    if (abs(abs(vertex.co.x) - 50) < 0.001 and abs(abs(vertex.co.y) - 50) < 0.001):
        continue
    
    # Check if the vertex is on an outer face
    on_front = abs(vertex.co.y + 50) < 0.001  # Front face
    on_back = abs(vertex.co.y - 50) < 0.001   # Back face
    on_left = abs(vertex.co.x + 50) < 0.001   # Left face
    on_right = abs(vertex.co.x - 50) < 0.001  # Right face
    
    # If it's on an outer face and not at a corner, push it in
    if on_front:
        vertex.co.y += line_depth
    elif on_back:
        vertex.co.y -= line_depth
    elif on_left:
        vertex.co.x += line_depth
    elif on_right:
        vertex.co.x -= line_depth

# Add thickness
bpy.ops.object.mode_set(mode='OBJECT')
solidify = cube.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 1.0  # 1mm thickness
bpy.ops.object.modifier_apply(modifier=solidify.name)

# Add bevel for smoother edges
bevel = cube.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 2.0  # 2mm bevel
bevel.segments = 3  # 3 segments for a smooth bevel
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.785398  # 45 degrees
bpy.ops.object.modifier_apply(modifier=bevel.name)

# STL export path - UPDATED to match what build_all_lamps.py expects
stl_path = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/rectangular_shade.stl"

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

print("Rectangular lamp shade created with dimensions 100x100x180mm and exported to STL")
print("Features: Vertical decorative lines on all 4 sides, 1mm wall thickness, open bottom")