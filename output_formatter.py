def create_output_files(filepath):
    token_count = 1
    path_count = 1
    token_dict = {}
    path_dict = {}
    token_dict["<PAD/>"] = 0
    path_dict["<PAD/>"] = 0

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
                    if len(pathContext) != 3:
                        continue

                    startToken = pathContext[0].strip()
                    path = pathContext[1].strip()
                    endToken = pathContext[2].strip()

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


create_output_files("C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\corpus_netdata.txt")