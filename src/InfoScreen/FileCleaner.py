'''
Created on Mar 25, 2025
This code may be executed on the embedded impressive device that contains the data.
It removes all files and thumbs not included in the slidelist.txt file
This is NOT client code! 
@author: matze
'''

import os

# Define directories
slideDir = "/home/jim/slides"
thumbDir = "/home/jim/slides/thumbs"
slidelistFile = "slidelist.txt"
slideListPath = os.path.join(slideDir,slidelistFile)


# Read allowed filenames from slidelist.txt
with open(slideListPath, "r") as f:
    allowed_files = {line.strip() for line in f}
#allowed_files is a set. add on, update many
immutables = []
for file in os.listdir(slideDir):
    if file.endswith(".txt"):
        immutables.append(file)

allowed_files.update(immutables)

# Task 1: Remove files in "a" that are not in slidelist.txt
for file in os.listdir(slideDir):
    file_path = os.path.join(slideDir, file)
    if os.path.isfile(file_path) and file not in allowed_files:
        print(f"Deleting: {file_path}")
        os.remove(file_path)
# Task 2: Remove files in "b" that match a filename in slidelist.txt but have a different extension
allowed_basenames = {os.path.splitext(file)[0] for file in allowed_files}

for file in os.listdir(thumbDir):
    file_path = os.path.join(thumbDir, file)
    base_name, _ = os.path.splitext(file)
    #if os.path.isfile(file_path) and base_name in allowed_basenames and file not in allowed_files:
    if os.path.isfile(file_path) and base_name not in allowed_basenames:
        print(f"Deleting: {file_path}")
        os.remove(file_path)


if __name__ == '__main__':
    pass
