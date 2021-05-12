import pickle

def java_string_hashcode(s):
        """
        Imitating Java's String#hashCode, because the model is trained on hashed paths but we wish to
        Present the path attention on un-hashed paths.
        """
        h = 0
        for c in s:
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

def update_freq_dict(freq_dict, word):
    if word in freq_dict:
        freq_dict[word] += 1
    else:
        freq_dict[word] = 1

def save_dictionaries(dataset_name, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict, num_training_examples):
    output_file_name = dataset_name + '.dict.c2v' 
    with open(dataset_name + '.dict.c2v', 'wb') as f:
        pickle.dump(token_freq_dict, f)
        pickle.dump(path_freq_dict, f)
        pickle.dump(target_freq_dict, f)
        pickle.dump(num_training_examples, f)

    # with open("path_dict.c2v", 'w', encoding="utf-8") as f:
    #     for hashed_path, context_path in hash_to_string_dict.items():
    #         f.write(hashed_path + '\t' + context_path + '\n')

    print('Dictionaries saved to: {}'.format(output_file_name))

def create_output_files_code2vec(filepath, dataset_name, data_role, include_paths, max_paths, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict):
    total_examples = 0      # Total Valid examples
    empty_examples = 0
    startToken = ''
    path = ''
    endToken = ''
    flag = 0
    current_row = ''
    first_example = True
    valid_example = False

    total_path_count = {'ast':0, 'cfg':0, 'cdg':0, 'ddg':0}
    current_path_count = {'ast':0, 'cfg':0, 'cdg':0, 'ddg':0}
    current_counter = 'ast'
    
    with open("{}.{}.c2v".format(dataset_name, data_role), 'a', encoding="utf-8") as fout:
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                if line.startswith("label:"):
                    if current_counter == 'ddg':
                        if include_paths['ddg']:
                            current_row += (' ' * (max_paths['ddg'] - current_path_count['ddg'] - 1))

                            if current_path_count['ddg'] > 0:
                                fout.write(current_row)
                                total_examples += 1
              
                            total_path_count['ddg'] += current_path_count['ddg']
                            path_count[current_counter] = 0
                        else:
                            fout.write(current_row)                    
                            total_examples += 1

                    current_row = ''
                    label = line[6:].strip('\n\t ')
                    if not label:
                        valid_example = False
                        empty_examples += 1
                        continue
                    else:
                        valid_example = True
                        update_freq_dict(target_freq_dict, label)
                        if first_example:
                            current_row += (label + ' ')
                            first_example = False
                        else:
                            current_row += ('\n' + label + ' ')     # \t or ' '

                elif not line.strip() or line.startswith("#") or line.startswith("file:"):
                    continue
                
                elif line.startswith("path: ast") and valid_example:
                    current_counter = 'ast'

                elif (line.startswith("path: cfg") or line.startswith("path: cdg") or line.startswith("path: ddg")) and valid_example:
                    if include_paths[current_counter]:
                        if current_path_count[current_counter] == 0:
                            valid_example = False
                            empty_examples += 1
                            current_row = ''
                            continue

                        current_row += (' ' * (max_paths[current_counter] - current_path_count[current_counter] - 1))
                        total_path_count[current_counter] += current_path_count[current_counter]

                    path_count[current_counter] = 0
                    current_counter = line.lstrip('path: \n\t').rstrip(' \n\t')
                    if include_paths[current_counter]:
                        current_row += ' '      # \t or ' '

                else:
                    if (not valid_example) or (not include_paths[current_counter]) or (current_path_count[current_counter] >= max_paths[current_counter]):
                        continue

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
                    
                    if (not startToken) or (not path) or (not endToken):
                        continue
                    current_path_count[current_counter] += 1
                    hashed_path = str(java_string_hashcode(path))
                    current_row += (startToken + ',' + hashed_path + ',' + endToken)
                    if current_path_count[current_counter] < max_paths[current_counter]:
                        current_row += ' '
                    hash_to_string_dict[hashed_path] = path
                    update_freq_dict(token_freq_dict, startToken)
                    update_freq_dict(path_freq_dict, hashed_path)
                    update_freq_dict(token_freq_dict, endToken)

        if valid_example:
            if include_paths[current_counter]:
                current_row += (' ' * (max_paths[current_counter] - current_path_count[current_counter] - 1))
                total_path_count[current_counter] += current_path_count[current_counter]
                path_count[current_counter] = 0

            fout.write(current_row + '\n')
            total_examples += 1

    print('File: ' + filepath)
    print('Total examples: ' + str(total_examples))
    print('Invalid examples: ' + str(empty_examples))
    print('Average Path Count: ')
    for rep, count in total_path_count.items():
        print(rep, count/total_examples)
    return total_examples


if __name__ == '__main__':
    hash_to_string_dict = {}
    token_freq_dict = {}
    path_freq_dict = {}
    target_freq_dict = {}
    
    ## For Cross-Project Evaluation
    # dataset_name = 'c'
    # num_training_examples = 0
    # train_data_path = "C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\processedDataset\\c.train.c2v"
    # test_data_path = "C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\processedDataset\\c.test.c2v"
    # val_data_path = "C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\processedDataset\\c.val.c2v"

    # for data_file_path, data_role in zip([test_data_path, val_data_path, train_data_path], ['test', 'val', 'train']):
    #     num_examples = create_output_files_code2vec(data_file_path, dataset_name, data_role, \
    #                         {'ast':True, 'cfg':False, 'cdg':False, 'ddg':False}, {'ast':200, 'cfg':10, 'cdg':50, 'ddg':100}, \
    #                         hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict)
        
    #     if data_role == 'train':
    #         num_training_examples = num_examples

    # save_dictionaries(dataset_name, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict, num_training_examples)


    ## For normal Train-Test-Val split. (Dictionary is formed using all splits)
    dataset_name = 'c'
    num_training_examples = 0
    train_data_path = "C:\\Users\\karthik chandra\\Desktop\\CS\\Research Work\\c2cpg\\processedDataset\\c_joined.c2v"

    num_examples = create_output_files_code2vec(train_data_path, dataset_name, 'train', \
                        {'ast':True, 'cfg':True, 'cdg':False, 'ddg':True}, {'ast':200, 'cfg':10, 'cdg':50, 'ddg':100}, \
                        hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict)
    
    num_training_examples = round(num_examples * 0.89)
    print("num_training_examples: ", num_training_examples)
    save_dictionaries(dataset_name, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict, num_training_examples)

    # Shuffle the output file of above step.

    # Splitting the joined and shuffled file into Train-Test-Val sets.
    # train_count = round(num_examples * 0.89)
    # val_count = round(num_examples * 0.035) + train_count
    # test_count = round(num_examples * 0.075) + val_count
    # print("Train Examples: ", train_count)
    # print("Val Examples: ", val_count)
    # print("Test Examples: ", test_count)
    # line_count = 0
    # with open('processedDataset\\c_ast_cfg_ddg\\c.train.c2v', 'w') as fo0:
    #     with open('processedDataset\\c_ast_cfg_ddg\\c.val.c2v', 'w') as fo1:
    #         with open('processedDataset\\c_ast_cfg_ddg\\c.test.c2v', 'w') as fo2:
    #             with open('processedDataset\\c_full_shuffled.c2v', 'r', encoding="utf-8") as fin:
    #                 for line in fin:
    #                     line_count += 1
    #                     if line_count <= train_count:
    #                         fo0.write(line)
    #                     elif line_count > train_count and line_count <= val_count:
    #                         fo1.write(line)
    #                     elif line_count > val_count and line_count <= test_count:
    #                         fo2.write(line)