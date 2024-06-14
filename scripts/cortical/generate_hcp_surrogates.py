"""
Generate eigenstrapping nulls for S255 HCP functional data
"""

from pathlib import Path
import numpy as np

from eigenstrapping_analysis.utils import (
    get_rootdir, MSEED, spat_perm, get_num_threads, get_medial,
    save_npy, load_npy, join
)

from eigenstrapping import SurfaceEigenstrapping

ROOTDIR = get_rootdir()
DATADIR = Path(ROOTDIR, 'datasets', 'cortical').resolve()
MASKDIR = Path(DATADIR, 'masks').resolve()
OUTDIR = Path(ROOTDIR, 'results', 'cortical', parents=True, exist_ok=True).resolve()

nsurrs = 1000
seed = MSEED
n_procs = get_num_threads()

# get paths
hcp_data = load_npy(join(DATADIR, 'HCP_functional', 'space-fsLR_den-32k_hemi-lh_S255-ALLTASKS.npy'))
medial_wall = get_medial(atlas='fsaverage')
emodes = load_npy(join(DATADIR, 'eigenmodes', 'space-fsLR_den-32k_hemi-lh_emodes-6000.npy'))
evals = load_npy(join(DATADIR, 'eigenmodes', 'space-fsLR_den-32k_hemi-lh_evals-6000.npy'))

# first and second subjects in EMOTION_FACES_SHAPES
hcp_data_source = hcp_data[0][0]

# generate random surrogates
rand_nulls = spat_perm(hcp_data_source, mask=medial_wall, seed=seed, nperm=nsurrs)

# generate eigenstrapping surrogates
eigen = SurfaceEigenstrapping(
    data=hcp_data_source,
    emodes=emodes,
    evals=evals,
    num_modes=6000,
    seed=seed,
    resample=True,
    permute=True
)

eigen_nulls = eigen(n=nsurrs)

# save files
save_npy(join(OUTDIR, 'hcp_random_nulls.npy'), rand_nulls)
save_npy(join(OUTDIR, 'hcp_eigen_nulls.npy'), eigen_nulls)
print('saved HCP surrogates to {}\n'.format(OUTDIR))