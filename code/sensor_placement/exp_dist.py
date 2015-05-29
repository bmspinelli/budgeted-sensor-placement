#!/usr/bin/env python
"""Optimal sensor placement for trees.

Provides an algorithm to compute a placement of sensors in a tree that
minimizes the expected distance between the real and the estimates source. It
only works for trees and assumes that all vertices have unit cost.

A simple example:

   import networkx as nx
   tree = nx.barabasi_albert_graph(100, 1)
   nb_sensors = 10
   exp_dist, sensors = optimal_placement(tree, nb_sensors)

"""

import functools32 as functools
import random

import preprocess_exp_dist
import utilities

INFINITY = float('infinity')


def optimal_placement(tree, budget):
    """
    Place `budget` sensors on a tree in an optimal way.

    Parameters
    ----------
    tree : networkx.Graph
        A tree (undirected) on which to place the sensors.
    budget : int
        The sensor budget, i.e. the number of nodes that can be choosen
        as sensors.

    Returns
    -------
    (exp_dist, obs) : tuple
        `exp_dist` is the expected distance, and `obs` a tuple containing the 
        sensors.
    """

    #one single sensor is useless
    assert budget >= 2

    leaves = utilities.find_leaves(tree)
    if budget >= len(leaves):
        return (0, tuple(leaves))    

    #define a non-leaf root arbitrarily
    root = random.choice(filter(lambda x: x not in leaves, tree.nodes()))
    
    #preprocessing to precompute expected distance for every class
    directed = preprocess_exp_dist.preprocess(tree, root)
    
    #add the budget to the tree as an attribute
    directed.graph['budget'] = budget
    
    #place the sensors using the DP algorithm.
    exp_dist, obs = _opt(directed, root, budget)
    _optc.cache_clear()
    _opt.cache_clear()
    
    return (float(exp_dist) / len(tree), obs)



@functools.lru_cache(maxsize=None)
def _opt(tree, x, k):
    """
    Place `k` sensors on the subtree rooted at `x` in an optimal way.
    
    Parameters
    ----------
    tree : networkx.DiGraph
        A directed tree on which to place the sensors. Each node must contain
        an attribute `size` with the size of the subtree rooted at the node and
        an attribute `subtree`containing a tuple with all the nodes in the
        subtree rooted at that node. The tree itself has an attribute `dists`
        containing the dictionary of all the distances in the tree.
    x : node
        The root of the (sub)tree, i.e. the node starting from which the
        sensors will be placed
    k : int
        The sensor budget, i.e. the number of sensors to be placed in `x`
        and below.

    Returns
    -------
    (exp_dist, obs) : tuple
        `exp_dist` is the (unscaled) expected distance real-estimated source, 
        and `obs` a tuple containing the sensors. To obtain the expected
        distance, divide the unscaled error by the size of the tree.

    """
    assert k >= 0
    if tree.degree(x) == 1:
        # We reached a leaf.
        if k > 1:
            return (INFINITY, ())
        else:
            return (0, (x,))
    # Otherwise, compute the error from that of the subtrees rooted at the
    # children.
    children = tuple(tree.successors(x))
    if tree.graph['root'] != x and tree.graph['budget'] == k:
        non_sensored = (tree.predecessors(x)[0],)
    else: 
        non_sensored = tuple()
    exp_dist, obs = _optc(tree, x, k, children, non_sensored)
    return exp_dist, obs


@functools.lru_cache(maxsize=None)
def _optc(tree, x, k, children, non_sensored):
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
        The (subset of) children downstream of which to place the sensors
    non_sensored: tuple
        The (subset of) neighboring subtrees of x that have been assigned no
        sensor
    Returns
    -------
    (exp_dist, obs) : tuple
        See doc for `_opt`
    
    """
    assert k >= 0

    #First, handle stopping conditions
    if len(children) == 0:
        #All the children have been processed
        if k > 0:
            return (INFINITY, ()) #some sensors are wasted
    if k == 0:
        equiv_neighs = non_sensored + children
        #We sort the tuple to look it up in the dictionary 'exp_dist'
        #the node predecessor, if present, has to come first
        if len(equiv_neighs) > 1 and x!=tree.graph['root'] and \
                (equiv_neighs[0]==tree.predecessors(x)[0]):
            equiv_neighs = (equiv_neighs[0],) + tuple(sorted(equiv_neighs[1:]))
        else:
            equiv_neighs = tuple(sorted(equiv_neighs))
        return (tree.graph['exp_dist'][x][equiv_neighs], ())
    results = list()
    #if no other sensor has been placed and x is not the root we try to
    #allocate all the budget to each single subtrees
    if tree.graph['root'] != x and tree.graph['budget'] == k:
        for c in children:
             e_c, o_c = _opt(tree, c, k)
             results.append((e_c, o_c))
    #Otherwise, the error is composed of a part below (subtree rooted at first
    #child) and a part to the right (remaining children)
    first, rest = children[0], children[1:]
    #First the case in which we put 0 sensors in first and 
    #so we have to add it to the unobserved children
    e0, o0 = _optc(tree, x, k, rest, non_sensored + (first, ))
    results.append((e0, o0))
    #Otherwise split the budget
    h = min(k, tree.graph['budget']-1) #maximum budget sent to a single subtree
    for l in xrange(1, h+1):
        e1, o1 = _opt(tree, first, l)
        e2, o2 = _optc(tree, x, k - l, rest, non_sensored)
        results.append((e1 + e2, o1 + o2))
    return min(results)

