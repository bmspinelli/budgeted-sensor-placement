import collections
import functools32 as functools
import itertools
import networkx as nx

def prob_err_from_cardinalities(len_classes):
    e = 0
    n = float(sum(len_classes))
    for l in len_classes:
        e = e + (l-1)/n
    return e


def prob_err(tree, leaves, budget):
    
    assert budget >= 2
    
    distance_matrix = nx.floyd_warshall(tree)
    opt_err = 2
    opt_sensors = []
    for sensors in itertools.combinations(leaves, budget):
        (classes, cardinalities) = equivalence_classes(distance_matrix, sensors)
        err = prob_err_from_cardinalities(cardinalities)
        if err < opt_err:
            opt_err = err
            opt_sensors = sensors
    return (opt_err, opt_sensors)


def exp_dist_from_classes(distance_matrix, classes):
    e = 0
    n = len(distance_matrix)
    for c in classes:
        for u, v in itertools.combinations(c, 2):
            e += 2*distance_matrix[u][v]/float(len(c))
    return e/float(n)


def exp_dist(tree, leaves, budget):
    
    assert budget >= 2
    
    distance_matrix = nx.floyd_warshall(tree)
    opt_exp_dist = sum([sum(distance_matrix[u].values()) for u in
            distance_matrix])
    opt_sensors = []
    for sensors in itertools.combinations(leaves, budget):
        (classes, cardinalities) = equivalence_classes(distance_matrix, sensors)
        exp_dist = exp_dist_from_classes(distance_matrix, classes)
        if exp_dist < opt_exp_dist:
            opt_exp_dist = exp_dist
            opt_sensors = sensors
    return (opt_exp_dist, opt_sensors)


def equivalence_classes(distance_matrix, sensors):
    u = sensors[0]
    vector_to_n = collections.defaultdict(list)
    for n in distance_matrix.keys():
        vector_to_n[tuple(int((10**8)*(distance_matrix[n][v] - 
                distance_matrix[n][u])) for v in sensors[1:])].append(n)
    classes = vector_to_n.values()
    return classes, [len(c) for c in classes]


def find_leaves(graph): 
    """Find the leaves of a graph.
    If the graph has only a node, that node is considered a leaf
    
    """
    leaves=list()
    if len(graph) == 1:
        return graph.nodes()
    for n in graph.nodes():
        if graph.degree(n) == 1:
            leaves.extend([n])
    return leaves


@functools.lru_cache(maxsize=None)
def size_subtree(tree, u):
    """Find the the size of the subtree rooted at u by computing the size
    of those rooted at the children
    
    tree: networkx.Graph()
        a directed tree
    u: the root of the subtree whose cardinality we want to compute
    
    """
    children = tree.successors(u)
    #base case: u is a leaf
    if not children:
        return 1
    else:
        size = 1
        for c in children:
            size += size_subtree(tree, c)
        return size
