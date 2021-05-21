import configparser
import pickle
import os

# This function is taken from code2vec (https://github.com/tech-srl/code2vec/blob/master/extractor.py)
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

def save_dictionaries(destination_dir, dataset_name, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict, num_training_examples):
    output_file_name = dataset_name + '.dict.c2v' 
    with open(os.path.join(destination_dir, output_file_name), 'wb') as f:
        pickle.dump(token_freq_dict, f)
        pickle.dump(path_freq_dict, f)
        pickle.dump(target_freq_dict, f)
        pickle.dump(num_training_examples, f)

    # with open("path_dict.c2v", 'w', encoding="utf-8") as f:
    #     for hashed_path, context_path in hash_to_string_dict.items():
    #         f.write(hashed_path + '\t' + context_path + '\n')

    print('Dictionaries saved to: {}'.format(os.path.join(destination_dir, output_file_name)))

def create_output_files_code2vec(filepath, destination_dir, dataset_name, data_role, include_paths, max_paths, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict):
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
    
    os.makedirs(destination_dir, exist_ok=True)
    with open(os.path.join(destination_dir, "{}.{}.c2v".format(dataset_name, data_role)), 'a', encoding="utf-8") as fout:
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
                            current_path_count[current_counter] = 0
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

                    current_path_count[current_counter] = 0
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
                current_path_count[current_counter] = 0

            fout.write(current_row + '\n')
            total_examples += 1

    print('File: ' + filepath)
    print('Valid examples: ' + str(total_examples))
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

    include_paths = {'ast':False, 'cfg':False, 'cdg':False, 'ddg':False}
    max_path_count = {'ast':0, 'cfg':0, 'cdg':0, 'ddg':0}

    config = configparser.ConfigParser()
    config.read("config.ini")
    input_dir = config['outputFormatter']['inputDirectory']
    datasets = config['outputFormatter']['datasets']
    datasets = [dataset.strip() for dataset in datasets.split(',')]
    output_dir = config['outputFormatter']['outputDirectory']
    dataset_name_ext = config['outputFormatter']['datasetNameExtension']

    include_paths['ast'] = config['outputFormatter'].getboolean('includeASTPaths')
    include_paths['cfg'] = config['outputFormatter'].getboolean('includeCFGPaths')
    include_paths['cdg'] = config['outputFormatter'].getboolean('includeCDGPaths')
    include_paths['ddg'] = config['outputFormatter'].getboolean('includeDDGPaths')

    max_path_count['ast'] = config['outputFormatter'].getint('maxASTPaths')
    max_path_count['cfg'] = config['outputFormatter'].getint('maxCFGPaths')
    max_path_count['cdg'] = config['outputFormatter'].getint('maxCDGPaths')
    max_path_count['ddg'] = config['outputFormatter'].getint('maxDDGPaths')

    ## For normal Train-Test-Val split. (Target dict is formed using only training, path and token dicts are formed using all splits)
    for dataset_name in datasets:
        num_training_examples = 0
        destination_dir = os.path.join(output_dir, dataset_name, dataset_name_ext)
        data_path = os.path.join(input_dir, dataset_name + ".c2v")

        num_examples = create_output_files_code2vec(data_path, destination_dir, dataset_name, 'full', \
                            include_paths, max_path_count, \
                            hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict)
        
        num_training_examples = round(num_examples * 0.89)
        print("num_training_examples: ", num_training_examples)

        ## Shuffle the output file of above step.
        os.system('./terashuf < {destination_dir}/{dataset_name}.full.c2v > {destination_dir}/{dataset_name}.full.shuffled.c2v'.format(destination_dir=destination_dir, dataset_name=dataset_name))

        ## Splitting the joined and shuffled file into Train-Test-Val sets.
        train_index = round(num_examples * 0.89)
        val_index = round(num_examples * 0.035) + train_index
        test_index = round(num_examples * 0.075) + val_index
        print("Train Examples: ", train_index)
        print("Val Examples: ", val_index - train_index)
        print("Test Examples: ", test_index - val_index)
        line_count = 0
        with open(os.path.join(destination_dir, '{}.train.c2v'.format(dataset_name + '_' + dataset_name_ext)), 'w') as fo0:
            with open(os.path.join(destination_dir, '{}.val.c2v'.format(dataset_name + '_' + dataset_name_ext)), 'w') as fo1:
                with open(os.path.join(destination_dir, '{}.test.c2v'.format(dataset_name + '_' + dataset_name_ext)), 'w') as fo2:
                    with open(os.path.join(destination_dir, '{}.full.shuffled.c2v'.format(dataset_name)), 'r', encoding="utf-8") as fin:
                        for line in fin:
                            line_count += 1
                            if line_count <= train_index:
                                fo0.write(line)
                            elif line_count > train_index and line_count <= val_index:
                                fo1.write(line)
                            elif line_count > val_index and line_count <= test_index:
                                fo2.write(line)

        # # Creating target dictionary using only Training data.
        # with open(os.path.join('processedDataset', dataset_name, dataset_name_ext, '{}.train.c2v'.format(dataset_name + dataset_name_ext)), 'r') as file:
        #     for line in file:
        #         parts = line.rstrip('\n').split(' ')
        #         target_name = parts[0]
        #         contexts = parts[1:]

        #         update_freq_dict(target_freq_dict, target_name)

        save_dictionaries(destination_dir, dataset_name + '_' + dataset_name_ext, hash_to_string_dict, token_freq_dict, path_freq_dict, target_freq_dict, num_training_examples)
        os.remove(os.path.join(destination_dir, dataset_name + '.full.c2v'))
        os.remove(os.path.join(destination_dir, dataset_name + '.full.shuffled.c2v'))