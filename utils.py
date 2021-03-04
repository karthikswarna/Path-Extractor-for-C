import re

def normalizeAst(ast, postOrder, splitToken=False, separator='|'):
    for currentNode in postOrder:
        attributes = ast.nodes[currentNode]['label'][2:-2].split(',')
        attributes = [attr.strip() for attr in attributes]

        if len(attributes) <= 1:
            continue

        if splitToken:
            normalizedToken = separator.join(splitToSubtokens(attributes[1]))
        else:
            normalizedToken = normalizeToken(attributes[1])
            
        attributes[1] = normalizedToken
        ast.nodes[currentNode]['label'] = '"(' + ",".join(attributes) + ')"'


def normalizeToken(token, defaultToken = ""):
    cleanToken = token.lower()
    cleanToken = re.sub("\s+", "", cleanToken)       # escaped new line, whitespaces
    cleanToken = re.sub("[\"',]", "", cleanToken)    # quotes, apostrophies, commas
    cleanToken = re.sub("P{Print}", "", cleanToken)  # unicode weird characters

    stripped = re.sub("[^A-Za-z]", "", cleanToken)

    if not stripped:                                   # stripped is empty
        carefulStripped = re.sub(" ", "_", cleanToken)
        if not carefulStripped:                        # carefulStripped is empty
            return defaultToken
        else:
            return carefulStripped

    return stripped


def splitToSubtokens(token):
    token = token.strip()
    tokens = re.compile("(?<=[a-z])(?=[A-Z])|_|[0-9]|(?<=[A-Z])(?=[A-Z][a-z])|\\s+").split(token)
    normalizedTokens = map(lambda x: normalizeToken(x), tokens)
    normalizedTokens = list(filter(lambda x: x, normalizedTokens))
    
    return normalizedTokens

def toPathContext(ast, upPiece, topNode, downPiece):
    # Creating upPath (list of type labels) from upPiece (list of ids) 
    upPath = []
    for index, currentNode in enumerate(upPiece):
        attributes = ast.nodes[currentNode]['label'][2:-2].split(',')
        attributes = [attr.strip() for attr in attributes]
        upPath.append(attributes[0])
        
        if index == 0:
            startToken = attributes[1]
    

    # Creating downPath (list of type labels) from downPiece (list of ids) 
    downPath = []
    for index, currentNode in enumerate(downPiece):
        attributes = ast.nodes[currentNode]['label'][2:-2].split(',')
        attributes = [attr.strip() for attr in attributes]
        downPath.append(attributes[0])
        
        if index == 0:
            endToken = attributes[1]

    # Exxtracting topNode's label using its id. 
    attributes = ast.nodes[topNode]['label'][2:-2].split(',')
    attributes = [attr.strip() for attr in attributes]
    topNode = attributes[0]
    
    # Creating pathContext from the path using (upPath, topNode, downPath). Also, adds arrows to store in file.
    upOrientedPath = ''.join([node + '↑' for node in upPath])
    downOrientedPath = ''.join(['↓' + node for node in downPath[::-1]])
    orientedPath = upOrientedPath + topNode + downOrientedPath
    
    return (startToken, orientedPath, endToken)