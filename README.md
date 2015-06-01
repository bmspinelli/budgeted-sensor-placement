### Budgeted sensor placement for source localization on trees

This repository is a complement to the paper *Budgeted sensor placement for source localization on trees* [1] presented at [LAGOS conference](http://www.lia.ufc.br/lagos2015/index.php) in May 2015.
It contains a Python implementation of the algorithms described in the paper, together with testing scripts. 

Also, the repository contains the extended version of [1].  

For any question, suggestion or comment please write to Brunella Spinelli [2].

### Implementation
* __sensor_placement/prob_err.py__  
   >> algorithm to optimally allocate *k* sensors in order to minimize the error probability in source localization, i.e., the probability of obtaining an estimated source different from the actual source of the diffusion 
* __sensor_placement/exp_dist.py__  
   >> algorithm to optimally allocate *k* sensors in order to minimize (in expectation) the distance between the estimated source and the actual one
* __test_prob_err.py, test_exp_dist.py__  
    >> scripts to test the above algorithms on randomly generated trees

### Dependencies
This implementation requires Python 2.7 and the following third-party libraries: NetworkX,
functools32.

### References
[1] L. E. Celis, F. Pavetić, B. Spinelli, P. Thiran, *Budgeted Sensor Placement for Source Localization on Trees*, LAGOS 2015 

[2] brunella.spinelli@epfl.ch
