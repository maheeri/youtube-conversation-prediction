from __future__ import print_function
import numpy as np
from itertools import combinations, permutations

def kendalltau_dist(rank_a, rank_b):
    tau = 0
    n_candidates = len(rank_a)
    for i, j in combinations(range(n_candidates), 2):
        tau += (np.sign(rank_a[i] - rank_a[j]) ==
                -np.sign(rank_b[i] - rank_b[j]))
    return tau
	
if __name__ == "__main__":
	ranks = np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 9, 8, 2, 6, 3, 5, 0, 4, 7]])
	print(kendalltau_dist(ranks[0], ranks[1]))