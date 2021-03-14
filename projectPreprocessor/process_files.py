import os
import sys
from shutil import copy
from utils import extract_functions_from_file, preprocess_cfile

# Filter the C/C++ source files and copy to the Dataset folder.
def filter_files(in_path, out_path):
    projectDirs = [name for name in os.listdir(os.path.join(in_path)) if os.path.isdir(os.path.join(in_path, name)) and name != "_temp_file_dir_"]

    # For each project directory, extract all C files and save in corresponding project folder in out_path.
    for dir in projectDirs:
        for root, dirs, files in os.walk(os.path.join(in_path, dir)):
            for file in files:
                if file.endswith(".cc") or file.endswith(".cxx") or file.endswith(".cpp") or file.endswith(".c"):
                    in_file_path = os.path.join(root, file)                    

                    # Replicate the same folder structure in out_path.
                    # C:\Users\karthik chandra\Downloads\Dataset\C\borg-master\scripts\fuzz-cache-sync\main.c
                    out_file_path = out_path + in_file_path.replace(in_path, "")
                    os.makedirs(os.path.dirname(out_file_path), exist_ok=True)

                    # Get the path without the file name in the end. (For example, without \main.c in the above path.)
                    # C:\Users\karthik chandra\Downloads\Dataset\C\borg-master\scripts\fuzz-cache-sync
                    out_file_path = os.path.dirname(os.path.abspath(out_file_path))
                    
                    copy(in_file_path, out_file_path)

# Splits all the files in in_path directory to functions and outputs them in out_path folder.
def split_files_into_functions(in_path, out_path, maxFileSize):
    os.makedirs(out_path, exist_ok=True)
    i = 0
    for root, dirs, files in os.walk(in_path):
        for file in files:
            in_file_path = os.path.join(root, file)

            code = preprocess_cfile(in_file_path)
            functions = extract_functions_from_file(code)
            
            for function in functions:
                # print(i, in_file_path)
        
                # Filter files as per the max size requirement.
                if sys.getsizeof(function) > maxFileSize:
                    continue

                with open(os.path.join(out_path, str(i) + ".c"), "w", encoding='utf-8') as file:
                    file.write(function)
                i += 1
