# <div align="center">**Path Extractor for C**</div>

## **Contents**
  * [Introduction](#introduction)
  * [Installing Dependencies](#installing-dependencies)
  * [Extracting paths from a set of projects](#extracting-paths-from-a-set-of-projects)
  * [Similar tools that inspired our implementation](#similar-tools-that-inspired-our-implementation)
  * [Sample Datasets](#sample-datasets)
  * [Team](#team)



## **Introduction**
* The idea of extracting paths from code to capture properties is inspired by [A general path-based representation for predicting program properties](https://doi.org/10.1145/3296979.3192412). We have extended the path-based representation to include CFG and PDG paths.

* This tool is developed as part of my and [Dheeraj's](https://github.com/dheerajrox) bachelor thesis.



## **Installing Dependencies**
**STEP-0:** Recommended OS is Linux. Joern is not tested on Windows but still seems to work fine.


**STEP-1:** Install [Joern](https://github.com/joernio/joern)

* This library is used to extract AST, CFG, and PDG from C code snippets.

* Follow the instructions given on Joern's GitHub page to install it. Then place the ```joern-cli``` folder inside the ```pathExtractor``` folder. 

* Alternatively, you can use the ```joern-cli``` folder in this repository without making a new Joern installation. Please note that Java Virtual Machine (version 8 or higher) is required to run Joern.

* Please make sure that the Joern scripts have the necessary execute permissions before running the tool.


**STEP-2:** Install [terashuf](https://github.com/alexandres/terashuf)

* This is used to shuffle large dataset files.

* Follow the instructions given on terashuf's GitHub page to download and compile it. Then place the terashuf executable parallel to the ```output_formatter.py``` file.

* Please do not use the executable provided in this repository as it is platform-specific.


**STEP-3:** Install required python libraries
```
pip3 install requirements.txt
```


## **Extracting paths from a set of projects**
Both the ```projectPreprocessor``` and ```pathExtractor``` modules and ```output_formatter.py``` script take the input parameters from the ```config.ini``` file. The input parameters for each of the modules are explained below.

**STEP-1:** Use the ```projectPreprocessor``` module to extract the functions/methods from all the projects.

* If outputType is 'single':

    - The inPath must point to a project directory.
    - The directory will be filled with methods extracted from inPath.

  If outputType is 'multiple':

    - The inputPath must point to a directory that contains a set of project directories.
    - For each project directory, all C functions are extracted and saved in the corresponding project directory in outPath.

* The maxFileSize parameter can be used to limit the size of the functions extracted from the projects.

* Run the ```projectPreprocessor/main.py``` script to extract the methods.
```
python3 projectPreprocessor/main.py
```


**STEP-2:** Use the ```pathExtractor``` module to extract paths from the functions.

* Set the following parameters in ```config.ini```:

Configuration Parameter  | Default Value | Description
------------------------ | ------------- | ------------
inputPath                | -             | Path to the directory that has all the methods extracted from a project.
datasetName              | -             | Name of the dataset to be created. This is used to name the output files generated by the tool.
numOfProcesses           | -             | Number of processes to be launched to extract paths. Use the value of the number of processors available.
maxPathContexts          | -             | Maximum number of each type of path context to be extracted from a method.
maxLength                | 8             | Maximum length of paths to be extracted from a method. This parameter applies only to AST paths.
maxWidth                 | 2             | Maximum width of paths to be extracted from a method. This parameter applies only to AST paths.
maxTreeSize              | 200           | Maximum number of AST nodes allowed. If a method has more nodes, it will not be included in the dataset.
separator                | \|            | Special character used to separate subwords in the method names (labels) and context words.
splitToken               | False         | This flag specifies whether to split the context words into subwords.
maxFileSize              | -             | Maximum filesize of the method. If a file has more size, it will not be included in the dataset.
upSymbol                 | ↑             | Special character used to indicate the upward movement in the path.
downSymbol               | ↓             | Special character used to indicate the downward movement in the path.
labelPlaceholder         | \<SELF\>      | Special token used to replace the method name in paths and context words.
useParentheses           | True          | This flag specifies whether to place path's nodes inside parenthesis.
useCheckpoint            | -             | This flag specifies whether to use the existing dataset file and resume the path extraction process. If this is true, make sure that all the parameters are unchanged from the previous run.

* Run the ```pathExtractor/main.py``` script to extract the paths from methods.
```
python3 pathExtractor/main.py
```


**STEP-3:** Use the ```output_formatter.py``` script to convert the dataset into the [model](https://github.com/karthikswarna/Extended-code2vec-model) input format, and split it into train-test-val sets.

* Set the following parameters in ```config.ini```:

Configuration Parameter  | Default Value | Description
------------------------ | ------------- | ------------
inputDirectory           | -             | Path to the directory that contains dataset files generated by the pathExtractor tool.
datasets                 | -             | Comma-separated list of names of the dataset files to be read from the inputDirectory.
outputDirectory          | -             | Path to the destination directory where the output datasets should be saved.
datasetNameExtension     | -             | An additional extension to the dataset name (Used to distinguish between different datasets.)
notIncludeMethods        | -             | Comma-separated list of method names that should not be included in the dataset. For example, some method names like 'f' may not represent the method's meaning, and hence we can remove such methods from the dataset.
includeASTPaths          | False         | This flag specifies whether to include AST paths in the output dataset.
includeCFGPaths          | False         | This flag specifies whether to include CFG paths in the output dataset.
includeCDGPaths          | False         | This flag specifies whether to include CDG paths in the output dataset.
includeDDGPaths          | False         | This flag specifies whether to include DDG paths in the output dataset.
maxASTPaths              | 0             | Maximum number of AST paths to be included from each method in the dataset.
maxCFGPaths              | 0             | Maximum number of CFG paths to be included from each method in the dataset.
maxCDGPaths              | 0             | Maximum number of CDG paths to be included from each method in the dataset.
maxDDGPaths              | 0             | Maximum number of DDG paths to be included from each method in the dataset.

* Run the ```output_formatter.py``` script to convert the dataset file into code2vec's format.
```
python3 output_formatter.py
```



## **Similar tools that inspired our implementation**
1. [astminer](https://github.com/JetBrains-Research/astminer)
2. [code2vec's Java extractor](https://github.com/tech-srl/code2vec/tree/master/JavaExtractor)



## **Sample Datasets**
The datasets we have created for our project can be found [here](https://drive.google.com/file/d/1CmQSOVvoR8zObc-Rbh8Un5d3dNFvCfbF/view?usp=sharing).



## **Team**
In case of any queries or if you would like to give any suggestions, please feel free to contact:

- Karthik Chandra (cs17b026@iittp.ac.in) 

- Dheeraj Vagavolu (cs17b028@iittp.ac.in) 

- Sridhar Chimalakonda (ch@iittp.ac.in)
