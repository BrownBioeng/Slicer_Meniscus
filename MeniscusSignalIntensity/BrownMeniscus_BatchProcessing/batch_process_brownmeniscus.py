import glob
import os

# collect folder names 
folder_names = glob.glob(r"P:\DBarnes\Meniscus\Slicer_6mo_data\*")

# Remove any in the list that don't start with BEAR
folders = []
for i in folder_names:
    if 'BEAR' in i:
        folders.append(i)

for files in folders:
    folder = os.path.join(files,"*")
    folder_open = glob.glob(folder)
    # Save STLs
    for item in folder_open:
        if item.endswith('_MM.stl'):
            mm_stl = item
        elif item.endswith('_LM.stl'):
            lm_stl = item
    # Save Dicom Folder 
        for dirpath, dirnames, filenames in os.walk(item):
            if any(filename.lower().endswith('.dcm') for filename in filenames):
                dcm_folder = dirpath
    #Right or left 
    if "right" in files:
        anatomy = "right"
    else:
        anatomy = "left"
    