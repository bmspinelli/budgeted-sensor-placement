"""Optimal sensor placement for trees.

Provides an algorithm to compute a placement of sensors in a tree that
minimizes the error probability. It only works for trees and assumes that all
vertices have unit cost. 

A simple example:

   import networkx as nx
   tree = nx.barabasi_albert_graph(100, 1)
   nb_sensors = 10
   perr, sensors = optimal_placement(tree, nb_sensors)
   
"""

import functools32 as functools
import networkx as nx
import random
from sensor_placement import utilities



INFINITY = float('infinity')

def optimal_placement(tree, budget):
    """
    Place `budget` sensors on a tree in an optimal way.

    Parameters
    ----------
    tree : networkx.Graph
        A tree (undirected) on which to place the sensors.
    budget : int
        The sensor budget, i.e. the number of nodes that can be chosen as
        sensors

    Returns
    -------
    (perr, obs) : tuple
        `perr` is the error probability, and `obs` a tuple containing the
        sensors.
    """ 
    
    #one single sensor is useless
    assert budget >= 2

    assert nx.is_tree(tree)

    leaves = utilities.find_leaves(tree)
    if budget >= len(leaves):
        return (0, tuple(leaves))

    #define a non-leaf root arbitrarily
    root = random.choice(filter(lambda x: x not in leaves, tree.nodes()))
    directed = nx.dfs_tree(tree, source=root) #dir DFS tree from source

    #compute the subtree sizes
    for x in directed:
        directed.node[x]['size'] = utilities.size_subtree(directed, x)
    utilities.size_subtree.cache_clear()
    
    #add the budget and the root to the tree as an attribute
    directed.graph['root'] = root
    directed.graph['budget'] = budget
    
    #place the sensors using the DP algorithm
    err, obs = _opt(directed, root, budget)
    _optc.cache_clear()
    _opt.cache_clear()
    
    return (float(err) / len(tree), obs)


@functools.lru_cache(maxsize=None)
def _opt(tree, x, k):
    """
    Place `k` sensors on the subtree rooted at `x` in an optimal way.
    
    Parameters
    ----------
    tree : networkx.DiGraph
        A directed tree on which to place the sensors. Each node must contain
        an attribute `size` with the size of the subtree rooted at the node.
    x : node
        The root of the (sub)tree, i.e. the node below which the
        sensors will be placed
    k : int
        The sensor budget, i.e. the number of sensors to be placed and
        below 'x'
        
    Returns
    -------
    (err, obs) : tuple
        `err` is the (unscaled) error and `obs` is a tuple containing the
        sensors. To obtain the error probability, divide the unscaled error
        by the size of the tree.
    """
    
    assert k >= 0

    # First, we handle shortcuts and stopping conditions.
    if k == 0:
        # No more sensors in the budget.
            return (tree.node[x]['size'], ())
    elif tree.node[x]['size'] == 1:
        # We reached a leaf.
        if k > 1:
            return (INFINITY, ()) #some sensors are wasted
        else:
            return (0, (x,)) #NB (x)=x, (x,) is a tuple!
    # Otherwise, compute the error from that of the subtrees rooted at the
    # children.
    children = tuple(tree.successors(x))
    e, o = _optc(tree, x, k, children)
    #If a subtree (rooted at a node x != root) receives the whole budget, x
    #is not resolved and counts towards the error
    if tree.graph['root'] != x and tree.graph['budget'] == k:
         e += 1
    return e, o


@functools.lru_cache(maxsize=None)
def _optc(tree, x, k, children):
    """
    Place sensors in the children of `x` (or a subset thereof) in an optimal
    way, using a dynamic programming algorithm.

    The algorithm works by picking a child, sending k' sensors down the
    subtree rooted at this child, and sending the k - k' remaining sensors in
    the rest of the children. The optimal k' is chosen by trying all possible
    values between 0 and k.

    Parameters
    ----------
    tree : networkx.DiGraph
        See doc for `_opt`
    x : node
        See doc for `_opt`
    k : int
        See doc for `_opt`
    children : tuple
        The (subset of) children downstream of which we place the sensors

    Returns
    -------
    (err, obs) : tuple
        See doc for `_opt`
    """
    assert k >= 0

    #First, handle stopping conditions
    if len(children) == 0:
        #All the children have been processed
        if k > 0:
            return (INFINITY, ()) #some sensors are wasted
        else:
            return (0, ())
    elif k == 0:
        return (sum(tree.node[n]['size'] for n in children), ())
    #Otherwise, the error is composed of a part below (subtree rooted at first
    #child) and a part to the right (remaining children.)
    first, rest = children[0], children[1:]
    results = list()
    for l in xrange(k+1):
        e1, o1 = _opt(tree, first, l)
        e2, o2 = _optc(tree, x, k - l, rest)
        results.append((e1 + e2, o1 + o2))
    return min(results)
