import os

import numpy as np
from sklearn.utils.validation import check_random_state

from neuromaps.datasets import fetch_fsaverage, fetch_fslr

MSEED = 1234

def get_rootdir():
    """
    Get the top-level directory of the repository
    """
    return os.path.abspath(os.path.dirname(__file__))

def spat_perm(data, mask=None, nperm=1000, seed=None):
    rs = check_random_state(seed)
    return np.array([rs.permutation(data[mask.astype(np.bool_)]) for _ in range(nperm)]).squeeze()

def get_medial(density='10k', hemi='lh', data_dir=None):
    if density == '10k':
        medial = fetch_fsaverage()