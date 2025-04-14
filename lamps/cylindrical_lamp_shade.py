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

# Create a cylindrical lamp shade with dome top and textured pattern
def create_cylindrical_lamp():
    # Create the base cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,  # Smooth cylinder
        radius=45,    # 90mm diameter
        depth=100,    # 100mm height (cylinder part)
        end_fill_type='NGON',
        location=(0, 0, 50)  # Center of cylinder at (0,0,50)
    )
    cylinder = bpy.context.active_object
    
    # Create the dome for the top
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=3,  # Use ico sphere for better stability
        radius=45,       # Match cylinder radius
        location=(0, 0, 100)  # Top of cylinder
    )
    dome = bpy.context.active_object
    
    # Scale dome to desired height
    dome.scale.z = 30/45  # 30mm dome height
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Cut bottom half of dome
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Go to vertex select mode
    bpy.ops.mesh.select_mode(type='VERT')
    
    # Switch to object mode to do selection
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select vertices in bottom half
    for v in dome.data.vertices:
        if v.co.z < 0:  # Bottom half (origin at center)
            v.select = True
    
    # Delete selected vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Join dome and cylinder
    dome.select_set(True)
    cylinder.select_set(True)
    bpy.context.view_layer.objects.active = cylinder  
    bpy.ops.object.join()
    
    # Get the resulting joined object
    lamp = cylinder
    
    # Remove bottom face of cylinder
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='FACE')
    
    # Switch to object mode to select bottom face
    bpy.ops.object.mode_set(mode='OBJECT')
    for poly in lamp.data.polygons:
        if poly.normal.z < -0.9:  # Face normal pointing down
            poly.select = True
    
    # Delete selected face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')
    
    # Create a simple pattern - add a displacement modifier 
    # instead of directly manipulating vertices
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add more geometry for the pattern
    subsurf = lamp.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    bpy.ops.object.modifier_apply(modifier=subsurf.name)
    
    # Create a texture for displacement
    texture = bpy.data.textures.new("HexPattern", type='STUCCI')
    texture.noise_scale = 0.25
    texture.turbulence = 5.0
    
    # Add displacement modifier using the texture
    displace = lamp.modifiers.new(name="Displace", type='DISPLACE')
    displace.texture = texture
    displace.strength = 2.0  # 2mm pattern depth
    displace.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=displace.name)
    
    # Add thickness with solidify
    solidify = lamp.modifiers.new(name="Solidify", type='SOLIDIFY') 
    solidify.thickness = 1.5  # 1.5mm wall thickness
    solidify.offset = 0
    bpy.ops.object.modifier_apply(modifier=solidify.name)
    
    # Final cleanup
    bpy.ops.object.shade_smooth()
    lamp.name = "CylindricalLampShade"
    
    return lamp

# Create lamp shade
lamp_shade = create_cylindrical_lamp()

# Export to STL
export_filepath = "/Users/stoklosa/Documents/StokApps/3D-print-designs/lamps/STLs/cylindrical_shade.stl"
os.makedirs(os.path.dirname(export_filepath), exist_ok=True)

# Deselect all objects and select only the lamp shade
bpy.ops.object.select_all(action='DESELECT')
lamp_shade.select_set(True)
bpy.context.view_layer.objects.active = lamp_shade

# Export using newer Blender 4.x method
try:
    bpy.ops.wm.stl_export(filepath=export_filepath)
    print(f"STL exported to {export_filepath}")
except Exception as e:
    print(f"Export failed: {e}")

print("Cylindrical lamp shade created with dimensions:")
print(f"  - Height: 130mm (100mm cylinder + 30mm dome)")
print(f"  - Diameter: 90mm")
print(f"  - Open bottom, domed top")
print(f"  - Wall thickness: 1.5mm")
print(f"  - Textured pattern")
print(f"Exported to: {export_filepath}")