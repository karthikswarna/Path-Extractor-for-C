import glob
import codecs
import os, re
import configparser
from shutil import copy, rmtree
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
def split_files_into_functions(in_path, out_path):
    os.makedirs(out_path, exist_ok=True)
    i = 0
    for root, dirs, files in os.walk(in_path):
        for file in files:
            in_file_path = os.path.join(root, file)

            code = preprocess_cfile(in_file_path)
            functions = extract_functions_from_file(code)
            
            for function in functions:
                # print(i, in_file_path)
                with open(os.path.join(out_path, str(i) + ".c"), "w", encoding='utf-8') as file:
                    file.write(function)
                i += 1


if __name__ == '__main__':
    # Reading the configuration parameters from config.ini file.
    config = configparser.ConfigParser()
    config.read(os.path.join("..", "config.ini"))
    in_path = config['projectPreprocessor']['inPath']
    out_path = config['projectPreprocessor']['outPath']

    intermediate_path = os.path.join(in_path, "_temp_file_dir_")
    os.mkdir(intermediate_path)

    try:    
        filter_files(in_path, intermediate_path)
        split_files_into_functions(intermediate_path, out_path)

    except Exception as e:
        raise Exception(e)

    finally:
        rmtree(intermediate_path)
        for filename in glob.glob("./_temp_*"):
            os.remove(filename) 