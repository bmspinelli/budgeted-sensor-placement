# This script generates random trees and compares the optimal
# probability of error computed by the dynamic programming algorithm
# described in the paper vs. the brute-force algorithm which tries
# out all possible combinations of placing the sensors on the tree
# leaves.

import networkx as nx
import random
from sensor_placement import prob_err
from sensor_placement import utilities

COMPARE_EPSILON = 0.000000001
TEST_CASES = 100000
MIN_NUMBER_OF_NODES = 10
MAX_NUMBER_OF_NODES = 25
RANDOM_SEED = 14052015

random.seed(RANDOM_SEED)

for test_case in xrange(TEST_CASES):
    n = random.randint(MIN_NUMBER_OF_NODES, MAX_NUMBER_OF_NODES)

    try:
        tree = nx.random_powerlaw_tree(n, seed=test_case, tries=100)
    except:
        print "Generating tree failed (this is due to how networkx.random_powerlaw_tree works and is OK), skipping test #%d." % test_case
        continue
        
    leaves = utilities.find_leaves(tree)
    k = random.randint(2, len(leaves))
    
    (perr, sensors) = prob_err.optimal_placement(tree, k)
    (brute_perr, brute_sensors) = utilities.prob_err(tree, leaves, k)

    assert abs(perr - brute_perr) < COMPARE_EPSILON
    print "Test #%d passed!" % test_case
    
    
