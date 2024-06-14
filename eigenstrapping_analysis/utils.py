import os
import warnings

import numpy as np
from sklearn.utils.validation import check_random_state

from neuromaps.datasets import fetch_fsaverage, fetch_fslr
import nibabel as nib

MSEED = 1234

def get_rootdir():
    """
    Get the top-level directory of the repository
    """
    return os.path.abspath(os.path.dirname(__file__))

def spat_perm(data, mask=None, nperm=1000, seed=None):
    rs = check_random_state(seed)
    return np.array([rs.permutation(data[mask.astype(np.bool_)]) for _ in range(nperm)]).squeeze()

def get_medial(atlas='fsaverage', data_dir=None):
    if atlas == 'fsaverage':
        medial = nib.load(
            str(getattr(getattr(fetch_fsaverage(density='10k', data_dir=data_dir), 'medial'), 'L'))
        ).agg_data()

    elif atlas == 'fsLR':
        medial = nib.load(
            str(getattr(getattr(fetch_fslr(density='32k', data_dir=data_dir), 'medial'), 'L'))
        ).agg_data()
    
    else:
        raise ValueError('unrecognized atlas, got {}'.format(atlas))
    
    return medial

def join(*args):
    """ wrapper because i'm not writing out os.path every time """
    return os.path.join(*args)

def save_npy(array, path):
    """ wrapper because ditto """
    return np.save(path, array)

def load_npy(path):
    """ same """
    return np.load(path)

def get_num_threads():
    nt = 1
    try:
        nt = os.environ['EIG_NTHREADS']
    except KeyError as e:
        warnings.warn('Could not find environment variable EIG_NTHREADS, defaulting to single cpu thread', category=UserWarning)
    
    return nt