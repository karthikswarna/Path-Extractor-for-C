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
    os.system("g++ -E _temp_%s > __temp_code__.cpp" %filename)
    
    if os.path.isfile("__temp_code__.cpp"):
        # Remove all lines that start with # from the preprocessed code
        with codecs.open("__temp_code__.cpp", 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not re.search('^#', line):
                    preproc_code += line
    
        os.remove("__temp_code__.cpp")
    
    os.remove("_temp_" + filename)

    # print(includes)
    # print(new_code)
    # print(preproc_code)

    return includes + preproc_code

def extract_functions_from_file(code):
    if code == "":
        return []

    # G1 - regex, G2 - static or const, G3 - return type, G4 - Function name, G5 - Argument list, G6 - const keyword
    rproc = r"((static|const)?\s+(\w+(?:\s*[*&]?\s+|\s+[*&]?\s*))(?:\w+::)?(\w+)\s*\(([\w\s,<>\[\].=&':/*]*?)\)\s*(const)?\s*(?={))"
    cppwords = ['if', 'while', 'do', 'for', 'switch', 'else', 'case', 'IF', 'WHILE', 'DO', 'FOR', 'SWITCH', 'ELSE', 'CASE']

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
                header = (match.group(2).strip() + ' ' if match.group(2) is not None else '') + \
                        (match.group(3).strip() + ' ' if match.group(3) is not None else '') + \
                        (match.group(4).strip() + ' ' if match.group(4) is not None else '') + \
                        ('(' + match.group(5).strip() + ') ' if match.group(5) is not None else '') + \
                        (match.group(6).strip() + ' ' if match.group(6) is not None else '') + '\n'
            
                # function = match.group(1) + body
                function = header + body        # This is done not to include the class name in function header (For C++ functions).
                functions.append(function)

    return functions