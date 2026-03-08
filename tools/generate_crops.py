import sys
import random
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate a grid of lettuce crops in single_rigid_link.sdf")
    parser.add_argument("--rows", type=int, default=15, help="Number of rows (default: 15)")
    parser.add_argument("--cols", type=int, default=5, help="Number of columns (default: 5)")
    parser.add_argument("--spacing-x", type=float, default=0.4, help="Spacing between plants in x-direction (default: 0.4)")
    parser.add_argument("--spacing-y", type=float, default=0.4, help="Spacing between plants in y-direction (default: 0.4)")
    parser.add_argument("--start-x", type=float, default=1.0, help="Starting x coordinate (default: 1.0)")
    parser.add_argument("--noise-xy", type=float, default=0.05, help="Maximum random noise applied to x and y coordinates (default: 0.05)")
    parser.add_argument("--noise-yaw", type=float, default=3.14159, help="Maximum random noise applied to yaw rotation (default: 3.14159)")
    parser.add_argument("--plant-model", type=str, default="lettuce_bib", help="Plant model name (default: lettuce_bib)")
    parser.add_argument("--sdf-path", type=str, default="farm_single_drone.sdf", help="Path to the SDF file (default: single_rigid_link.sdf)")

    
    args = parser.parse_args()
    
    total_width = (args.cols - 1) * args.spacing_y
    start_y = -(total_width / 2.0)
    
    xml_output = ""
    count = 1
    
    for col in range(args.cols):
        y_base = start_y + col * args.spacing_y
        for row in range(1, args.rows + 1):
            x_base = args.start_x + (row - 1) * args.spacing_x
            
            x = x_base + random.uniform(-args.noise_xy, args.noise_xy)
            y = y_base + random.uniform(-args.noise_xy, args.noise_xy)
            yaw = random.uniform(-args.noise_yaw, args.noise_yaw)
            
            xml_output += f"""      <include>
        <uri>{args.plant_model}</uri>
        <name>{args.plant_model}_{count}</name>
        <pose>{x:.3f} {y:.3f} 0 0 0 {yaw:.3f}</pose>
      </include>\n"""
            count += 1

    sdf_path = f'repos/PX4-Autopilot/Tools/simulation/gz/worlds/{args.sdf_path}'
    
    with open(sdf_path, 'r') as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if f'<name>{args.plant_model}_1</name>' in line:
            start_idx = i - 2
            break

    if start_idx != -1:
        for i in range(start_idx, len(lines)):
            # Look for the end of the crop block. The next thing is either the commented out tether or the end of the model block.
            if '<!--' in lines[i] or '</model>' in lines[i]:
                # Step backward to find the last </include>
                for j in range(i, start_idx - 1, -1):
                    if '</include>' in lines[j]:
                        end_idx = j + 1
                        break
                break

    if start_idx != -1 and end_idx != -1:
        new_lines = lines[:start_idx] + [xml_output] + lines[end_idx:]
        with open(sdf_path, 'w') as f:
            f.writelines(new_lines)
        print(f"Successfully replaced {args.plant_model} block with {count-1} plants (Grid: {args.rows}x{args.cols}).")
    else:
        print(f"Could not find start or end index. start={start_idx}, end={end_idx}")
        print(f"Please ensure at least '{args.plant_model}_1' exists in the SDF file before running.")

if __name__ == "__main__":
    main()
