import os
from filelock import FileLock

def store_paths(label, ast_paths, cfg_paths, cdg_paths, ddg_paths, token_count, path_count, token_dict, path_dict, i, count_lock):
    with count_lock:
        for path in ast_paths:
            if path[0] not in token_dict:
                token_dict[path[0]] = token_count.value
                token_count.value += 1

            if path[1] not in path_dict:
                path_dict[path[1]] = path_count.value
                path_count.value += 1

            if path[2] not in token_dict:
                token_dict[path[2]] = token_count.value
                token_count.value += 1

    with count_lock:
        for path in cfg_paths:
            if path[0] not in token_dict:
                token_dict[path[0]] = token_count.value
                token_count.value += 1

            if path[1] not in path_dict:
                path_dict[path[1]] = path_count.value
                path_count.value += 1

            if path[2] not in token_dict:
                token_dict[path[2]] = token_count.value
                token_count.value += 1

    with count_lock:
        for path in cdg_paths:
            if path[0] not in token_dict:
                token_dict[path[0]] = token_count.value
                token_count.value += 1

            if path[1] not in path_dict:
                path_dict[path[1]] = path_count.value
                path_count.value += 1

            if path[2] not in token_dict:
                token_dict[path[2]] = token_count.value
                token_count.value += 1
    
    with count_lock:
        for path in ddg_paths:
            if path[0] not in token_dict:
                token_dict[path[0]] = token_count.value
                token_count.value += 1

            if path[1] not in path_dict:
                path_dict[path[1]] = path_count.value
                path_count.value += 1

            if path[2] not in token_dict:
                token_dict[path[2]] = token_count.value
                token_count.value += 1
    
    with FileLock(os.path.join("..", "corpus.txt.lock")):
        with open(os.path.join("..", "corpus.txt"), 'a', encoding="utf-8") as f:
            f.write("#" + str(i.value) + '\n')
            f.write("label:" + label + '\n')
            f.write("paths:ast\n")
            for path in ast_paths:
                f.write(str(token_dict[path[0]]) + '\t' + str(path_dict[path[1]]) + '\t' + str(token_dict[path[2]]) + '\n')

            f.write("paths:cfg\n")
            for path in cfg_paths:
                f.write(str(token_dict[path[0]]) + '\t' + str(path_dict[path[1]]) + '\t' + str(token_dict[path[2]]) + '\n')

            f.write("paths:cdg\n")
            for path in cdg_paths:
                f.write(str(token_dict[path[0]]) + '\t' + str(path_dict[path[1]]) + '\t' + str(token_dict[path[2]]) + '\n')

            f.write("paths:ddg\n")
            for path in ddg_paths:
                f.write(str(token_dict[path[0]]) + '\t' + str(path_dict[path[1]]) + '\t' + str(token_dict[path[2]]) + '\n')
            f.write('\n')
    
    return (token_count, path_count)


def store_tokens_paths(token_dict, path_dict):
    with FileLock(os.path.join("..", "path_ids.txt.lock")):
        with open(os.path.join("..", "path_ids.txt"), 'a', encoding="utf-8") as f:
            for path, path_id in path_dict.items():
                f.write(str(path_id) + '\t' + path + '\n')

    with FileLock(os.path.join("..", "terminal_ids.txt.lock")):
        with open(os.path.join("..", "terminal_ids.txt"), 'a', encoding="utf-8") as f:
            for token, token_id in token_dict.items():
                f.write(str(token_id) + '\t' + token + '\n')