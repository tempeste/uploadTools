# Usage: python script_name.py --source /path/to/source/directory --destination /path/to/destination/directory --extension jpg
import os
import glob
import shutil
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description='Aggregate images of a specific type from one directory and copy them to another.')
parser.add_argument('--source', required=True, help='Source directory containing images')
parser.add_argument('--destination', required=True, help='Destination directory to copy images to')
parser.add_argument('--extension', required=True, help='Image file extension to copy (e.g., png, jpg)')

# Parse arguments
args = parser.parse_args()

# Assign directories and extension from parsed arguments
source_dir = args.source
destination_dir = args.destination
image_extension = args.extension

# Validate and format the image extension
if not image_extension.startswith('.'):
    image_extension = '.' + image_extension

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Copy files with the specified extension
counter = 1
for image_file in glob.glob(os.path.join(source_dir, '*' + image_extension)):
    # Generate new file name with counter
    new_file_name = f"{counter:03d}{os.path.splitext(image_file)[1]}"
    destination_file_path = os.path.join(destination_dir, new_file_name)
    
    shutil.copy(image_file, destination_file_path)
    print(f"Copied {image_file} to {destination_file_path}")
    
    counter += 1

print("Image aggregation complete.")
