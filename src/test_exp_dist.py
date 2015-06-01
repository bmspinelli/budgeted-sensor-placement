# This script generates random trees and compares the optimal
# probability of error computed by the dynamic programming algorithm
# described in the paper vs. the brute-force algorithm which tries
# out all possible combinations of placing the sensors on the tree
# leaves.

import networkx as nx
import random
from sensor_placement import exp_dist
from sensor_placement import utilities

COMPARE_EPSILON = 0.000000001
TEST_CASES = 100000
MIN_NUMBER_OF_NODES = 5
MAX_NUMBER_OF_NODES = 25
RANDOM_SEED = 14052015

random.seed(RANDOM_SEED)

for test_case in xrange(TEST_CASES):
    n = random.randint(MIN_NUMBER_OF_NODES, MAX_NUMBER_OF_NODES)

    try:
        tree = nx.random_powerlaw_tree(n, seed=test_case, tries=100)
    except:
        print "Generating tree failed" 
        print "(this is due to how networkx.random_powerlaw_tree works, OK)"
        print "skipping test #%d." % test_case
        continue
        
    leaves = utilities.find_leaves(tree)
    k = random.randint(2, len(leaves))
    
    (dist, sensors) = exp_dist.optimal_placement(tree, k)
    (brute_expdist, brute_sensors) = utilities.exp_dist(tree, leaves, k)
    assert abs(dist - brute_expdist) < COMPARE_EPSILON
    print "Test #%d passed!" % test_case 
