def create_output_files_unofficial(filepath):
    token_count = 1
    path_count = 1
    token_dict = {}
    path_dict = {}
    token_dict["<PAD/>"] = 0
    path_dict["<PAD/>"] = 0

    startToken = ''
    path = ''
    endToken = ''
    flag = 0
    with open("corpus.txt", 'a', encoding="utf-8") as fout:
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    fout.write('\n' + line)

                elif line.startswith("label:") or line.startswith("path: "):
                    fout.write(line)

                elif not line.strip() or line.startswith("file:"):
                    continue

                elif line.startswith("paths:"):
                    fout.write(line.replace("paths:", "path: "))

                else:
                    pathContext = line.split('\t')

                    if len(pathContext) == 2:
                        if flag == 0:
                            startToken = pathContext[0].strip()
                            path = pathContext[1].strip()
                            flag = 1
                            continue
                        elif flag == 1:
                            path = path + pathContext[0].replace('\\n', '').strip()
                            endToken = pathContext[1].strip()
                            print(startToken, path, endToken)
                            print()
                            flag = 0

                    elif len(pathContext) == 3:
                        startToken = pathContext[0].strip()
                        path = pathContext[1].strip()
                        endToken = pathContext[2].strip()

                    else:
                        continue

                    if startToken not in token_dict:
                        token_dict[startToken] = token_count
                        token_count += 1

                    if path not in path_dict:
                        path_dict[path] = path_count
                        path_count += 1

                    if endToken not in token_dict:
                        token_dict[endToken] = token_count
                        token_count += 1

                    fout.write(str(token_dict[startToken]) + '\t' + str(path_dict[path]) + '\t' + str(token_dict[endToken]) + '\n')

    with open("path_idxs.txt", 'w', encoding="utf-8") as f:
        for path, path_id in path_dict.items():
            f.write(str(path_id) + '\t' + path + '\n')
    
    with open("terminal_idxs.txt", 'w', encoding="utf-8") as f:
        for token, token_id in token_dict.items():
            f.write(str(token_id) + '\t' + token + '\n')

def java_string_hashcode(s):
        """
        Imitating Java's String#hashCode, because the model is trained on hashed paths but we wish to
        Present the path attention on un-hashed paths.
        """
        h = 0
        for c in s:
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

def create_output_files_code2vec(filepath):
    hash_to_string_dict = {}

    startToken = ''
    path = ''
    endToken = ''
    flag = 0
    with open("corpus.c2v", 'a', encoding="utf-8") as fout:
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                if line.startswith("label:"):
                    fout.write('\n' + line.strip('label:\n\t ') + ' ')

                elif not line.strip() or line.startswith("#") or line.startswith("file:") or line.startswith("path: ast"):
                    continue

                elif line.startswith("path: cfg") or line.startswith("path: cdg") or line.startswith("path: ddg"):
                    fout.write('\t')

                else:
                    pathContext = line.split('\t')

                    if len(pathContext) == 2:
                        if flag == 0:
                            startToken = pathContext[0].strip()
                            path = pathContext[1].strip()
                            flag = 1
                            continue
                        elif flag == 1:
                            path = path + pathContext[0].replace('\\n', '').strip()
                            endToken = pathContext[1].strip()
                            print(startToken, path, endToken)
                            print()
                            flag = 0

                    elif len(pathContext) == 3:
                        startToken = pathContext[0].strip()
                        path = pathContext[1].strip()
                        endToken = pathContext[2].strip()

                    else:
                        continue
                    
                    hashed_path = str(java_string_hashcode(path))
                    fout.write(startToken + ',' + hashed_path + ',' + endToken + ' ')
                    hash_to_string_dict[hashed_path] = path

    with open("path_dict.c2v", 'w', encoding="utf-8") as f:
        for hashed_path, context_path in hash_to_string_dict.items():
            f.write(hashed_path + '\t' + context_path + '\n')

create_output_files_code2vec("C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\testdata.c2v")