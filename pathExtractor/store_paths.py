import os
from filelock import FileLock

def store_paths(label, file_name, ast_paths, cfg_paths, cdg_paths, ddg_paths, i):
    with FileLock(os.path.join("..", "corpus.txt.lock")):
        with open(os.path.join("..", "corpus.txt"), 'a', encoding="utf-8") as f:
            f.write("#" + str(i.value) + '\n')
            f.write("label:" + label + '\n')
            f.write("file:" + file_name + '\n')
            f.write("path: ast\n")
            for path in ast_paths:
                f.write(path[0] + '\t' + path[1] + '\t' + path[2] + '\n')

            f.write("path: cfg\n")
            for path in cfg_paths:
                f.write(path[0] + '\t' + path[1] + '\t' + path[2] + '\n')

            f.write("path: cdg\n")
            for path in cdg_paths:
                f.write(path[0] + '\t' + path[1] + '\t' + path[2] + '\n')

            f.write("path: ddg\n")
            for path in ddg_paths:
                f.write(path[0] + '\t' + path[1] + '\t' + path[2] + '\n')
            f.write('\n')