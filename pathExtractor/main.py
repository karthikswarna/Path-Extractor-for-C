import os
import sys
import math
import configparser
import multiprocess as mp
from store_paths import *
from generate_dataset import *

if __name__ == '__main__':
    # If the output files already exist, don't continue the execution.
    if os.path.isfile(os.path.join("..", "config.txt")) or os.path.isfile(os.path.join("..", "token_ids.txt")) or os.path.isfile(os.path.join("..", "path_ids.txt")):
        print("config.txt or token_ids.txt or path_ids.txt files already exist. Exiting..")
        sys.exit()

    # Reading the configuration parameters from config.ini file.
    config = configparser.ConfigParser()
    config.read(os.path.join("..", "config.ini"))
    in_path = config['pathExtractor']['inputPath']
    numOfProcesses = config['pathExtractor'].getint('numOfProcesses')
    maxPathContexts = config['pathExtractor'].getint('maxPathContexts')
    maxLength = config['pathExtractor'].getint('maxLength')
    maxWidth = config['pathExtractor'].getint('maxWidth')
    maxTreeSize = config['pathExtractor'].getint('maxTreeSize')
    separator = config['pathExtractor']['separator']
    splitToken = config['pathExtractor'].getboolean('splitToken')

    # Divide the work between processes.
    totalFiles = len(os.listdir(in_path))
    filesPerProcess = math.floor(totalFiles / numOfProcesses)
    leftOver = totalFiles % numOfProcesses

    # Calculate the start and end file indices for each process.
    processFileIndices = []
    for ProcessIndex in range(numOfProcesses):
        startIndex = filesPerProcess * ProcessIndex
        endIndex = startIndex + filesPerProcess - 1
        if ProcessIndex == numOfProcesses - 1:
            endIndex += leftOver
        processFileIndices.append([startIndex, endIndex])

    with mp.Manager() as manager:
        # Create shared dictionaries, count variables, and locks.
        token_count = manager.Value('i', 1)
        path_count = manager.Value('i', 1)
        token_dict = manager.dict()
        path_dict = manager.dict()
        token_dict["<PAD/>"] = 0
        path_dict["<PAD/>"] = 0
        i = manager.Value('i', 0)
        ilock = manager.Lock()
        count_lock = manager.Lock()
        
        # Create the argument collection, where each element contains the array of parameters for each process.
        ProcessArguments = ([in_path] + FileIndices + [token_count, path_count, token_dict, path_dict, i, ilock, count_lock] \
                            + [maxPathContexts, maxLength, maxWidth, maxTreeSize, splitToken, separator] for FileIndices in processFileIndices)
        
        # Start executing multiple processes.
        with mp.Pool(processes = numOfProcesses) as pool:
            pool.map(generate_dataset, ProcessArguments)
        
        # Store the path dictionary and token dictionary in files.
        store_tokens_paths(token_dict, path_dict)

        print("Token count : ", token_count.value)
        print("Path count : ", path_count.value)