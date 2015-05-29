import itertools
import functools32 as functools
import networkx as nx

import utilities

def preprocess(tree, root):
    """Compute the expected distance of all possible equivalence
    classes in the tree

    Parameters
    ----------
    tree : networkx.Graph()
        an undirected tree
    root : integer
        the non-leaf node at which we root the tree to run the algorithm

    Returns
    ------
    directed : networkx.Graph()
         a directed tree with the following attributes
         - 'dists': dictionary, distances in the (undirected) tree
         - 'root': integer, the non-leaf node at which we root the tree to run 
                the algorithm
         - 'exp dist': dictionary of dictionaries, associates to a node and a
           tuple of neighbors the expected distance of the corresponding
           equivalence class. The parent of the node, if present, is always the
           first element in the tuple
         Moreover, every node has the following attributes:
         - 'size': integer, size of the subtree rooted at the node
         - 'sum_below': integer, sum of the distances from the node to all
           nodes in the subtree 
         - 'sum_above': integer, sum of the distances from the node to all
           nodes NOT in the subtree
    """
    
    assert root in tree.nodes()
    assert nx.is_tree(tree)

    directed = nx.dfs_tree(tree, source=root) #dir DFS tree from source
    directed.graph['dists'] =  nx.all_pairs_dijkstra_path_length(tree)
    directed.graph['root'] = root

    size = {}
    sum_above = {}
    sum_below = {}
    exp_dist = {u: {} for u in directed}
    
    #SUBTREES SIZES
    for x in directed:
        size[x] = utilities.size_subtree(directed, x)
    utilities.size_subtree.cache_clear()
    #attach subtree size to nodes 
    for x in directed:
        directed.node[x]['size'] = size[x]

    #SUM DISTANCES FROM NODE TO NODES BELOW
    for x in directed:
        sum_below[x] = sum_dist_below(directed, x)
    sum_dist_below.cache_clear()
    #attach sum dists below to nodes 
    for x in directed:
        directed.node[x]['sum_below'] = sum_below[x]
    
    #SUM DISTANCES FROM NODE TO NODES ABOVE
    for x in directed:
        sum_above[x] = sum_dist_above(directed, x)
    sum_dist_above.cache_clear()
    #attach sum dists above to nodes 
    for x in directed:
        directed.node[x]['sum_above'] = sum_above[x]
    
    #ORDERED TUPLES OF CHILDREN FOER EVERY NODE
    ordered_tuples = {}
    for x in directed:
        ordered_tuples[x] = ordered_tuples_children(directed, x)
    
    #EXP DISTANCE FOR NODE AND SUBSET OF CHILDREN
    for x in directed:
        for sel_children in ordered_tuples[x]:
            exp_dist[x][sel_children] =\
                 exp_distance(directed, x, sel_children)
    exp_distance.cache_clear()
    #attach exp_dist to the graph
    directed.graph['exp_dist'] = exp_dist
    
    #SIZES OF EQUIVALENCE CLASSES
    size_classes = {x: {} for x in directed} 
    for x in directed:
        for sel_tuple in ordered_tuples[x]:
            size_classes[x][sel_tuple] = 0
            for c in sel_tuple:
                size_classes[x][sel_tuple] += directed.node[c]['size']
            if size_classes[x][sel_tuple]:
                #add node x itself
                size_classes[x][sel_tuple] += 1
            if x !=  directed.graph['root']:
                p = directed.predecessors(x)[0]
                #the class is composed by all nodes above and x (if no children
                #are in the class) or all nodes above and the class computed
                #before for the set of selected children
                size_classes[x][(p, ) + sel_tuple] = len(directed) -\
                        directed.node[x]['size'] +\
                        max(size_classes[x][sel_tuple], 1)
    
    #NORMALIZED EXP DISTANCE FOR NODE AND SUBSET OF CHILDREN INCLUDING PART OF THE TREE
    #ABOVE
    for x in directed:
        if x == directed.graph['root']:
            for sel_children in ordered_tuples[x][1:]:
                
                exp_dist[x][sel_children] =\
                    exp_distance_parent(directed, x,
                    sel_children)/float(size_classes[x][sel_children])
        else:
            p = directed.predecessors(x)[0]
            for sel_children in ordered_tuples[x]:
                exp_dist[x][(p, ) + sel_children] =\
                    exp_distance_parent(directed, x,
                    sel_children)/float(size_classes[x][(p, ) + sel_children])
                #also normalize the expected distance of the class without
                #nodes above (if it is not empty)
                if sel_children:
                    exp_dist[x][sel_children] = exp_dist[x][sel_children]\
                            /float(size_classes[x][sel_children])
    exp_distance_parent.cache_clear()

    #update exp_dist as an attribute to the graph
    directed.graph['exp_dist'] = exp_dist
    
    return directed


@functools.lru_cache(maxsize=None)
def exp_distance(tree, u, sel_children):
    """Computes the expected distance of a class composed by a vertex and a
    subset of its children recursively

    tree: networkx.Graph()
        a directed tree
    u: integer
        the vertex which is the 'center' of the quivalence class
    sel_children: tuple
        subtrees of T_u whose nodes are equivalent to u

    """
    exp_dist = 0
    #base case: if u is a leaf 
    if tree.degree(u)==1 or len(sel_children)==0:
        return exp_dist
    #compute the total number of nodes below u
    size_below = sum(tree.node[c]['size'] for c in sel_children)
    for c in sel_children:
        ordered_successors = tuple(sorted(tree.successors(c)))
        exp_dist += exp_distance(tree, c, ordered_successors)
    #between subtrees terms
    for c in sel_children:
        exp_dist += 2*(tree.node[c]['sum_below'] + tree.graph['dists'][u][c]* \
        tree.node[c]['size'])*(size_below - tree.node[c]['size'])
    #add distances from u to all nodes in the selected subtrees 
    for c in sel_children:
        exp_dist += 2*(tree.node[c]['sum_below'] + tree.graph['dists'][u][c]*\
                tree.node[c]['size'])
    return exp_dist


@functools.lru_cache(maxsize=None)
def exp_distance_parent(tree, u, sel_children):
    """Computes the expected distance above a node and in a subset of the
    children recursively

    tree: networkx.Graph()
        a directed tree
    u: integer
        the vertex which is the 'center' of the quivalence class
    sel_children: tuple
        subtrees of T_u whose nodes are equivalent to u

    """
    #initialize with the expected distance inside the selected children
    exp_dist_par = tree.graph['exp_dist'][u][sel_children]
    #if u is the root there is nothing above, this is the base case
    if u == tree.graph['root']:
        return exp_dist_par
    parent = tree.predecessors(u)[0] 
    #other children of parent, different from u
    other_children = tuple(sorted(filter(lambda x: x != u, tree.successors(parent))))
    #add the expected distance of nodes above the parent and in all other
    #subtrees rooted at the father
    exp_dist_par += exp_distance_parent(tree, parent, other_children)
    #Now distances from nodes in sel_children and u to all nodes above and viceversa
    #first compute the sum of distances from u to the nodes in the selected
    #children
    sum_below_sel = sum(tree.node[c]['sum_below'] + tree.graph['dists'][u][c]\
            *(tree.node[c]['size']) for c in sel_children)
    #number of nodes above, excluding u
    size_above = len(tree) - tree.node[u]['size']
    #number of nodes below, counting also u
    size_below = sum(tree.node[c]['size'] for c in sel_children) + 1
    exp_dist_par += 2* (sum_below_sel * (size_above) +tree.node[u]['sum_above']*\
            size_below)
    return exp_dist_par


@functools.lru_cache(maxsize=None)
def sum_dist_below(tree, u):
    """Computes the sum of distances from u to all nodes below recursively
    
    tree: networkx.Graph()
        a directed tree
    size: dictionary
        associates each node to the size of the subtree rooted at it
    u: integer
        identifies the node from which we want to compute distances below
    
    """
    #base case: if u is a leaf
    if not tree.successors(u):
        return 0
    sum_below = 0
    for c in tree.successors(u):
        sum_below += sum_dist_below(tree, c) + tree.graph['dists'][u][c] *\
                tree.node[c]['size']
    return sum_below


@functools.lru_cache(maxsize=None)
def sum_dist_above(tree, u):
    """Computes the sum of distances from u to all nodes that are not in the
    subtree rooted at u
    
    tree: networkx.Graph()
        a directed tree
    size: dictionary
        associates each node to the size of the subtree rooted at it
    u: integer
        identifies the node from which I want to compute distances below
    
    """
    #base_case: if u is the root
    if u == tree.graph['root']:
        return 0
    p = tree.predecessors(u)[0]
    above_predecessor = sum_dist_above(tree, p) 
    other_children_p = tree.node[p]['sum_below'] - tree.node[u]['sum_below'] -\
            tree.graph['dists'][u][p] * tree.node[u]['size']
    from_u_to_p = tree.graph['dists'][u][p] * (len(tree) - tree.node[u]['size'])
    sum_above = above_predecessor + other_children_p + from_u_to_p
    return sum_above
        

def ordered_tuples_children(tree, x):
    """generate all possible subsets of children as a list of tuples
    
    tree: networkx.Graph()
        a directed tree
    u: the nodes for which compute all possible tuples of children
    
    """
    children = sorted(tree.successors(x))
    tuples = []
    #generate all possible words on "01" with length len(children)
    combinations = [''.join(i) for i in itertools.product("01", repeat=len(children))]
    for comb in combinations:
        t = tuple()
        for i in range(len(children)):
            if comb[i] == '1':
                t += (children[i],)
        tuples.append(t)
    assert len(tuples[0]) == 0
    
    return tuples
