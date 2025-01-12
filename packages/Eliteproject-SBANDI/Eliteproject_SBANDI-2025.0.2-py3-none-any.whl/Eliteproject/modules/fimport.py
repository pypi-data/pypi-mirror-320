import os
import tarfile
import bz2
from tkinter import filedialog

# Select compress log file 
filename = filedialog.askopenfilename(filetypes=(("gz Files", ("*.gz", "*.bz2")), ("All Files", "*.*")))
path_base = os.path.expanduser("~/Documents/Elite_Log_output") # try eventualy with os.path.expanduser("~/") 
# print(path_base)
folder_output = os.path.splitext(os.path.splitext(filename)[0])[0]
# print(folder_output)
folder_name = os.path.basename(folder_output)  # Extract folder name
# print(folder_name)
path_output = os.path.join(path_base, folder_name)
# print(path_output)

if not filename:  # verify if file is selected
    print('No file selected.')
else:
    # output path
    print(path_output)
    if not os.path.exists(path_output):
        os.makedirs(path_output, exist_ok=True)
        print(f"Output folder: {path_output}")
        print(f"File selected: {filename}")
    else:
        print(f"Folder {path_output} already exist.")
        # path_output = os.path.expanduser("~/Documents/Elite_Log_output")+folder_output
        # print(path_output)

    try:
        # Estrazione dei file
        if filename.endswith('tar.gz'):
            with tarfile.open(filename, 'r:gz') as tar:
                tar.extractall(path=path_output, numeric_owner=False, filter='data')
        elif filename.endswith('tar'):
            with tarfile.open(filename, 'r:') as tar:
                tar.extractall(path=path_output, numeric_owner=False, filter='data')    
        else:
            print("File not supported.")
            
        for root, _, files in os.walk(path_output):
            for file in files:
                if file.endswith('.bz2'):
                    bz2_file_path = os.path.join(root, file)
                    decompressed_file_path = os.path.splitext(bz2_file_path)[0]
                    with bz2.BZ2File(bz2_file_path, 'rb') as bz2_file:
                        with open(decompressed_file_path, 'wb') as decompressed_file:
                            decompressed_file.write(bz2_file.read())
                    print(f"File expand: {decompressed_file_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Generic error : {e}")
        