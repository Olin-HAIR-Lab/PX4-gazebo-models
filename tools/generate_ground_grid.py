import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate a grid of textured ground planes in single_rigid_link.sdf")
    parser.add_argument("--rows", type=int, default=10, help="Number of rows (default: 10)")
    parser.add_argument("--cols", type=int, default=10, help="Number of columns (default: 10)")
    parser.add_argument("--size-x", type=float, default=2.0, help="Size of each patch in x-direction (default: 2.0)")
    parser.add_argument("--size-y", type=float, default=2.0, help="Size of each patch in y-direction (default: 2.0)")
    parser.add_argument("--center-x", type=float, default=3.0, help="Center of the grid in x (default: 3.0)")
    parser.add_argument("--center-y", type=float, default=0.0, help="Center of the grid in y (default: 0.0)")
    parser.add_argument("--z-offset", type=float, default=0.005, help="Z offset to prevent z-fighting with main ground (default: 0.005)")
    parser.add_argument("--texture", type=str, default="brown_mud_dry_diff_4k.jpg", help="Texture file name (default: brown_mud_dry_diff_4k.jpg)")
    parser.add_argument("--texture-dir", type=str, default="ground_plane_textures", help="Directory containing the texture file (default: models/ground_plane_textures)")
    parser.add_argument("--sdf-path", type=str, default="single_rigid_link.sdf", help="Path to the SDF file (default: single_rigid_link.sdf)")
    
    args = parser.parse_args()
    
    total_width_x = args.rows * args.size_x
    total_width_y = args.cols * args.size_y
    
    start_x = args.center_x - (total_width_x / 2.0) + (args.size_x / 2.0)
    start_y = args.center_y - (total_width_y / 2.0) + (args.size_y / 2.0)
    
    xml_output = '    <model name="soil_grid">\n      <static>true</static>\n      <link name="link">\n'
    
    count = 1
    
    for row in range(args.rows):
        x = start_x + row * args.size_x
        for col in range(args.cols):
            y = start_y + col * args.size_y
            
            # Create a separate visual for each grid cell
            xml_output += f"""        <visual name="soil_patch_{count}">
          <pose>{x:.3f} {y:.3f} {args.z_offset} 0 0 0</pose>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{args.size_x:.3f} {args.size_y:.3f}</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
            <pbr>
              <metal>
                <albedo_map>models://{args.texture_dir}/{args.texture}</albedo_map>
                <roughness>0.9</roughness>
                <metalness>0.0</metalness>
              </metal>
            </pbr>
          </material>
        </visual>\n"""
            count += 1
            
    xml_output += '      </link>\n    </model>\n'

    sdf_path = f'repos/PX4-Autopilot/Tools/simulation/gz/worlds/{args.sdf_path}'
    
    with open(sdf_path, 'r') as f:
        content = f.read()

    # If the model already exists, replace it
    import re
    if '<model name="soil_grid">' in content:
        new_content = re.sub(
            r'    <model name="soil_grid">.*?</model>\n',
            xml_output,
            content,
            flags=re.DOTALL
        )
    else:
        # Insert before </world>
        new_content = content.replace('  </world>', xml_output + '\n  </world>')

    with open(sdf_path, 'w') as f:
        f.write(new_content)
        
    print(f"Successfully created a {args.rows}x{args.cols} soil grid ({count-1} patches) in {sdf_path}")

if __name__ == "__main__":
    main()
