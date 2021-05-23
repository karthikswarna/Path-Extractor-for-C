import networkx as nx
from utils import *
import os

def extract_ast_paths(ast_path, maxLength=8, maxWidth=2, maxTreeSize=200, splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    try:
        ast = nx.DiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(ast_path, "0-ast.dot")))
    except:
        return ("", [])

    if (ast.number_of_nodes() > maxTreeSize or ast.number_of_nodes() == 0):
        return ("", [])

    nx.set_node_attributes(ast, [], 'pathPieces')

    source = "1000101" if "1000101" in ast else min(ast.nodes)
    postOrder = list(nx.dfs_postorder_nodes(ast, source=source))

    normalizedLabel = normalizeAst(ast, postOrder, splitToken, separator, labelPlaceholder, useParentheses)

    paths = []    
    for currentNode in postOrder:
        if not list(ast.successors(currentNode)):    # List is empty i.e node is leaf
            attributes = ast.nodes[currentNode]['label'][2:-2].split(',')
            attributes = [attr.strip() for attr in attributes]
            if len(attributes) > 1 and attributes[1]:  # attribute[1] is token of the leaf node. If the token is not empty.
                ast.nodes[currentNode]['pathPieces'] = [[currentNode]]
        else:
            # Creates a list of pathPieces per child i.e. list(list(list(nodes))) <--> list(list(pathPieces)) <--> list(PathPieces per child)
            pathPiecesPerChild = list(map(lambda x: ast.nodes[x]['pathPieces'], list(ast.successors(currentNode))))

            # Append current node to all the pathPieces. And flatten the list(list(pathPieces)) to list(pathPieces).
            currentNodePathPieces = [pathPiece + [currentNode] for pathPieceList in pathPiecesPerChild for pathPiece in pathPieceList if maxLength == None or len(pathPiece) <= maxLength]            
            ast.nodes[currentNode]['pathPieces'] = currentNodePathPieces
            
            # Find list of paths that pass through the current node (leaf -> currentNode -> leaf). Also, filter as per maxWidth and maxLength
            for index, leftChildsPieces in enumerate(pathPiecesPerChild):
                if maxWidth is None:
                    maxIndex = len(pathPiecesPerChild)
                else:
                    maxIndex = min(index + maxWidth + 1, len(pathPiecesPerChild))
                
                for rightChildsPieces in pathPiecesPerChild[index + 1 : maxIndex]:
                    for upPiece in leftChildsPieces:
                        for downPiece in rightChildsPieces:
                            if ((maxLength == None) or (len(upPiece) + 1 + len(downPiece) <= maxLength)):
                                paths.append(toPathContext(ast, upPiece, currentNode, downPiece, upSymbol, downSymbol))

    # print('\n')
    # for path in paths:
    #     print(path)
        
    return (normalizedLabel, paths)

def extract_cfg_paths(cfg_path, splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    try:
        cfg = nx.DiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(cfg_path, "0-cfg.dot")))
        source = "1000101" if "1000101" in cfg else min(cfg.nodes)
    except:
        return []

    paths = []
    Visited = []
    paths = traverse_cfg_paths(cfg, source, paths.copy(), Visited.copy(), "", splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)

    # print('\ncfg:')
    # for path in paths:
    #     print(path)
        
    return paths

def traverse_cfg_paths(cfg, node, path, Visited, start_token = "", splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    attributes = normalizeNode(cfg, node, splitToken, separator, labelPlaceholder, useParentheses)
    if path:
        path.append(downSymbol + attributes[0])
    else:
        path.append(attributes[0])
        start_token = attributes[1]

    Visited.append(node)
    children = list(cfg.successors(node))
    child_paths = []

    if children:
        for child in children:
            if child not in Visited:
                child_paths += traverse_cfg_paths(cfg, child, path.copy(), Visited.copy(), start_token, splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)
            else:
                attributes = normalizeNode(cfg, child, splitToken, separator, labelPlaceholder, useParentheses)
                child_paths.append(  (start_token, ''.join(path + [upSymbol + attributes[0]]), attributes[1])  )
    else:
        return [(start_token, ''.join(path), attributes[1])]

    return child_paths

def extract_cdg_paths(cdg_path, splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    try:
        cdg = nx.DiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(cdg_path, "0-cdg.dot")))
        root = min(cdg.nodes)
    except:
        return []

    if nx.is_empty(cdg):
        return []
    
    # Removing self-loops and finding the root of the CDG (which is a tree, if self-loops are removed).
    # cdg.remove_edges_from(nx.selfloop_edges(cdg))
    # root = [node for node, degree in cdg.in_degree() if degree == 0]
    paths = []
    Visited = []
    paths = traverse_cdg_paths(cdg, root, paths, Visited, "", splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)

    # print("\ncdg:")
    # for path in paths:
    #     print(path)

    return paths

def traverse_cdg_paths(cdg, node, path, Visited, start_token = "", splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    attributes = normalizeNode(cdg, node, splitToken, separator, labelPlaceholder, useParentheses)
    if path:
        path.append(downSymbol + attributes[0])
    else:
        path.append(attributes[0])
        start_token = attributes[1]

    Visited.append(node)
    children = list(cdg.successors(node))
    child_paths = []

    if children:
        for child in children:
            if child not in Visited:
                child_paths += traverse_cdg_paths(cdg, child, path.copy(), Visited.copy(), start_token, splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)
            else:
                attributes = normalizeNode(cdg, child, splitToken, separator, labelPlaceholder, useParentheses)
                child_paths.append(  (start_token, ''.join(path + [upSymbol + attributes[0]]), attributes[1])  )
    else:
        return [(start_token, ''.join(path), attributes[1])]

    return child_paths

def extract_ddg_paths(ddg_path, splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    try:
        ddg = nx.MultiDiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(ddg_path, "0-ddg.dot")))
        source = "1000101" if "1000101" in ddg else min(ddg.nodes)
    except:
        return []

    paths = []
    Visited = []
    paths = traverse_ddg_paths(ddg, source, paths.copy(), Visited.copy(), "", "", splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)
    paths = list(set([path for path in paths]))

    # print('\nddg:')
    # for path in paths:
    #     print(path)
        
    return paths

def traverse_ddg_paths(ddg, node, path, Visited, start_token = "", edge_label="", splitToken=False, separator='|', upSymbol='↑', downSymbol='↓', labelPlaceholder='<SELF>', useParentheses=True):
    attributes = normalizeNode(ddg, node, splitToken, separator, labelPlaceholder, useParentheses)
    if path:
        path.append(downSymbol + attributes[0])
    else:
        path.append(attributes[0])
        start_token = attributes[1]

    Visited.append(node)
    edges = ddg.edges(node, data='label')
    child_paths = []

    if edges:
        for edge in edges:
            if edge_label == "" or edge_label == None or edge_label in edge[2] or edge[2] in edge_label:
                if edge[1] not in Visited:
                    if edge_label == "" or edge_label == None or edge[2] in edge_label:
                        child_paths += traverse_ddg_paths(ddg, edge[1], path.copy(), Visited.copy(), start_token, edge[2], splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)
                    elif edge_label in edge[2]:
                        child_paths += traverse_ddg_paths(ddg, edge[1], path.copy(), Visited.copy(), start_token, edge_label, splitToken, separator, upSymbol, downSymbol, labelPlaceholder, useParentheses)
                else:
                    attributes = normalizeNode(ddg, edge[1], splitToken, separator, labelPlaceholder, useParentheses)
                    child_paths.append(  (start_token, ''.join(path + [upSymbol + attributes[0]]), attributes[1])  )
    else:
        return [(start_token, ''.join(path), attributes[1])]

    return child_paths