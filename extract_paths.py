import networkx as nx
from utils import *
import os

def extract_ast_paths(ast_path, maxLength=8, maxWidth=3, maxTreeSize=50, splitToken=False, separator='|'):
    if not os.path.exists(os.path.join(ast_path, "0-ast.dot")):
        return ("", [])

    ast = nx.DiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(ast_path, "0-ast.dot")))
    if (ast.number_of_nodes() > maxTreeSize):
        return ("", [])

    nx.set_node_attributes(ast, [], 'pathPieces')
    postOrder = list(nx.dfs_postorder_nodes(ast, source="1000101"))
    normalizeAst(ast, postOrder, splitToken, separator)
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
                                paths.append(toPathContext(ast, upPiece, currentNode, downPiece))

    # for start_node, edge_list in ast.adj.items():
    #     print(start_node, ast.nodes[start_node])
    #     print()
        
    # print('\n')
    # for path in paths:
    #     print(path)
        
    return (ast.name, paths)

def extract_cfg_paths(cfg_path):
    if not os.path.exists(os.path.join(cfg_path, "0-cfg.dot")):
        return []

    cfg = nx.DiGraph(nx.drawing.nx_pydot.read_dot(os.path.join(cfg_path, "0-cfg.dot")))
    paths = []
    Visited = []
    paths = traverse_paths(cfg, '1000101', paths.copy(), Visited.copy())

    # print('\n')
    # for path in paths:
    #     print(path)
        
    return paths

def traverse_paths(cfg, node, path, Visited):
    attributes = cfg.nodes[node]['label'][2:-2].split(',')
    attributes = [attr.strip() for attr in attributes]
    if path:
        path.append('↓' + attributes[0])
    else:
        path.append(attributes[0])

    Visited.append(node)
    children = list(cfg.successors(node))
    child_paths = []

    if children:
        for child in children:
            if child not in Visited:
                child_paths += traverse_paths(cfg, child, path.copy(), Visited.copy())
            else:
                attributes = cfg.nodes[child]['label'][2:-2].split(',')
                attributes = [attr.strip() for attr in attributes]
                child_paths.append(  (normalizeToken(path[0]), ''.join(path + ['↑' + attributes[0]]), normalizeToken(attributes[0]))  )
    else:
        return [(normalizeToken(path[0]), ''.join(path), normalizeToken(path[-1]))]

    return child_paths

def extract_pdg_paths(pdg_path):
    return None