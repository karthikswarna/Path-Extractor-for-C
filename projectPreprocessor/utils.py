import codecs
import os, re

def preprocess_cfile(filepath):
    includes = ''
    new_code = ''
    preproc_code = ''
    
    # Separating the #includes from remaining code
    with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if re.search('^[ \t]*#[ \t]*include', line):
                includes += line
            else:
                new_code += line

        filename = os.path.basename(filepath)
        f1 = open("_temp_" + filename, "w", encoding='utf-8')
        f1.write(new_code)
        f1.close()
    
    # Preprocessing using gcc (removes comments, and resolves preprocessor directives other than #include)
    os.system("gcc -E _temp_%s > _temp_code.cpp" %filename)
    
    # Remove all lines that start with # from the preprocessed code
    with codecs.open("_temp_code.cpp", 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not re.search('^#', line):
                preproc_code += line
                
    # print(includes)
    # print(new_code)
    # print(preproc_code)
    
    os.remove("_temp_" + filename)
    os.remove("_temp_code.cpp")

    return includes + preproc_code

def extract_functions_from_file(code):
    # G1 - regex, G2 - static or const, G3 - return type, G4 - Function name, G5 - Argument list, G6 - const keyword
    rproc = r"((static|const)?\s+(\w+(?:\s*[*&]?\s+|\s+[*&]?\s*))(\w+)\s*\(([\w\s,<>\[\].=&':/*]*?)\)\s*(const)?\s*(?={))"
    cppwords = ['if', 'while', 'do', 'for', 'switch', 'else']

    functions = []
    for match in re.finditer(rproc, code, re.DOTALL):
        if match.group(4) not in cppwords:
            wait_char = ''
            wait_for_char = False     # For handling {,} in strings. No need to handle comments, as we are dealing with preprocessed files.
            brac_count = 0
            opening_brac_found = False
            start_index = 0
            end_index = 0

            for index in range(match.end(), len(code)):
                if (code[index] == '"' or code[index] == "'") and wait_for_char == False:
                    wait_for_char = True
                    wait_char = code[index]
                    continue

                if wait_for_char == True:
                    if code[index] == wait_char:
                        wait_for_char == False
                        wait_char = ''
                    continue

                if opening_brac_found == True and brac_count == 0:    # Closing bracket found.
                    end_index = index
                    break

                if code[index] == '{':
                    if opening_brac_found == False and brac_count == 0:  # Opening bracket found.
                        opening_brac_found = True
                        start_index = index

                    brac_count += 1
                elif code[index] == '}':
                    brac_count -= 1
                    
            body = code[start_index : end_index + 1].strip()
            if body != '':
                function = match.group(1) + body
                functions.append(function)

    return functions