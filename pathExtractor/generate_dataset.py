import os
import random
from utils import *
from store_paths import *
from extract_paths import *
from shutil import copy, rmtree

def generate_dataset(params):
    in_path, startIndex, endIndex, i, ilock, \
    maxPathContexts, maxLength, maxWidth, maxTreeSize, maxFileSize, splitToken, separator = params

    # try:
    # Create temporary working directories.
    workingDir = os.path.abspath("_temp_dir_" + str(os.getpid()))
    if not os.path.exists(os.path.join(workingDir, "workspace")):
        os.makedirs(os.path.join(workingDir, "workspace"))

    if not os.path.exists(os.path.join(workingDir, "outdir")):
            os.mkdir(os.path.join(workingDir, "outdir"))

    # Process each file in the dataset one-by-one.
    for fileIndex in range(startIndex, endIndex + 1):
        # Create environment for joern.
        file_name = str(fileIndex) + ".c"
        in_file_path = os.path.join(in_path, file_name)

        # Filter files as per the max size requirement.
        statinfo = os.stat(in_file_path)
        if statinfo.st_size > maxFileSize:
            continue

        copy(in_file_path, os.path.join(workingDir, "workspace"))

        # Use joern to create AST, CFG, PDG.
        os.chdir(workingDir)
        os.system(os.path.join("..", "joern-cli", "bin", "joern-parse") + " workspace")
        os.system(os.path.join("..", "joern-cli", "bin", "joern-export") + " --repr ast --out " + os.path.join("outdir", "ast"))
        os.system(os.path.join("..", "joern-cli", "bin", "joern-export") + " --repr cfg --out " + os.path.join("outdir", "cfg"))
        os.system(os.path.join("..", "joern-cli", "bin", "joern-export") + " --repr cdg --out " + os.path.join("outdir", "cdg"))
        os.system(os.path.join("..", "joern-cli", "bin", "joern-export") + " --repr ddg --out " + os.path.join("outdir", "ddg"))
        os.chdir("..")

        # Extract paths from AST, CFG, DDG, CDG.
        label, ast_paths = extract_ast_paths(os.path.relpath(os.path.join(workingDir, "outdir", "ast")), maxLength, maxWidth, maxTreeSize, splitToken, separator)
        label = normalizeToken(label)

        # If no paths are generated, Reset and continue. 
        if not ast_paths or label == None or label == "":
            os.remove(os.path.join(workingDir, "workspace", file_name))
            for folder in os.listdir(os.path.join(workingDir, "outdir")):
                rmtree(os.path.join(workingDir, "outdir", folder))
            continue
        
        # Select maxPathContexts number of path contexts randomly.
        if len(ast_paths) > maxPathContexts:
            random.sample(ast_paths, maxPathContexts)

        cfg_paths = extract_cfg_paths(os.path.relpath(os.path.join(workingDir, "outdir", "cfg")))
        cdg_paths = extract_cdg_paths(os.path.relpath(os.path.join(workingDir, "outdir", "cdg")))
        ddg_paths = extract_ddg_paths(os.path.relpath(os.path.join(workingDir, "outdir", "ddg")))

        # Storing the extracted paths in files.
        # token_count, path_count = store_paths(label, ast_paths, cfg_paths, cdg_paths, ddg_paths, i)
        store_paths(label, file_name, ast_paths, cfg_paths, cdg_paths, ddg_paths, i)
        with ilock:
            i.value += 1

        # Remove the current file, and ast, cfg, pdg folder after processing current sample. Otherwise, joern will bail out. 
        os.remove(os.path.join(workingDir, "workspace", file_name))
        for folder in os.listdir(os.path.join(workingDir, "outdir")):
            rmtree(os.path.join(workingDir, "outdir", folder))

    rmtree(workingDir)

    # except KeyboardInterrupt:
    #     print("Keyboard Interrupt at %i'th file." %i.value)

    # finally:
        # Remove the temporary directory created by me.
        # rmtree(workingDir)