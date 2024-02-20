import Light
import Ray
import Sphere
import sys

# List of all the spheres
objects = []
# List of all the lights
light_sources = []

# Main function
def main():
    # Dictionary of the file info
    file_info = {}

    # Get input
    input = sys.argv[1]

    # Open File and get first line
    fp = open(str(input), "r")
    line = fp.readline()

    # Parse through input file and extract all information
    while True:
        # Check if end of file
        if not line:
            break

        # Break up line
        split_line = line.split()
        key = split_line[0]
        # Get information
        if key == "SPHERE":
            objects.append(Sphere.Sphere(split_line[1], split_line[2:5], split_line[5:8], split_line[8:11], split_line[11:]))
        elif key == "LIGHT":
            light_sources.append(Light.Light(split_line[1], split_line[2:5], split_line[5:]))
        else:
            file_info.update({key : split_line[1:]})   

        # Get next line
        line = fp.readline()

    fp.close() # We are done with file so close it

    # Get scene dimensions
    width = int(file_info.get("RES")[0])
    height = int(file_info.get("RES")[1])
    
    # Get new file and write ppm header
    print("Saving image " + str(file_info.get("OUTPUT")[0]) + " " + str(width) + " x " + str(height))
    fp = open(str(file_info.get("OUTPUT")[0]), "w")
    if fp is None:
        print("Unable to open file " + str(file_info.get("OUTPUT")[0]))
        return
    fp.write("P3\n")
    fp.write(str(width) + " " + str(height) + "\n")
    fp.write("255\n")

    # for each pixel on the screen raytrace it and set its color in the ppm file
    for i in range(0, width):
        for j in range(0, height):

            # Calculate Ray then trace it
            ray = Ray.Ray(file_info, objects, light_sources)
            ray.update_eye_ray(j, i, width, height)
            col = ray.raytrace()

            # Clamp any colors that have exceeded 1.0
            col.clamp()

            # Write pixel to output file
            fp.write(str(col.r*255) + " " + str(col.g*255) + " " + str(col.b*255) + " ")
        fp.write("\n")
    fp.close() # We are done with this file so close it

# Run Main
main()
