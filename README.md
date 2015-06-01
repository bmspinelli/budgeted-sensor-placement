### Budgeted sensor placement for source localization on trees

This repository is a complement to the paper *Budgeted sensor placement for source localization on trees* [1] presented at LAGOS conference [3] in May 2015.
It contains a Python implementation of the algorithms described in
[1] together with some testing scripts. 

Also, an extended version of [1] is available in the present repository.  

For any question, suggestion or comment please write to Brunella Spinelli [3].

### Implementation
* sensor_placement/prob_err.py 
    >> algorithm to optimally allocate $k$ sensors in order to minimize the
    >> error probability in source localization, i.e., the probability of
    >> obtaining an estimated source different from the actual source of the
    >> diffusion 
* sensor_placement/exp_dist.py 
    >> algorithm to optimally allocate $k$ sensors in order to minimize (in
    >> expectation) the
    >> distance between the estimated source and the actual one
* test_prob_err.py, test_exp_dist.py
    >> scripts to test the above algorithms on randomly generated trees

### Dependencies
This implementation requires the following Python libraries: NetworkX,
functools32.

[1] L.E. Celis, F. Pavetic, B. Spinelli, P. Thiran, *Budgeted Sensor Placement for Source Localization on Trees*, LAGOS 2015 

[2] http://www.lia.ufc.br/lagos2015/index.php

[3] brunella.spinelli@epfl.ch
