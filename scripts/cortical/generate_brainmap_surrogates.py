"""
Generate all nulls for annotations
"""

from pathlib import Path
import numpy as np

from eigenstrapping_analysis.utils import (
    get_rootdir, MSEED, get_medial, join, save_npy, load_npy,
    get_num_threads
)

from eigenstrapping import SurfaceEigenstrapping
from neuromaps.nulls import alexander_bloch, burt2020

ROOTDIR = get_rootdir()
DATADIR = Path(ROOTDIR, 'datasets', 'cortical').resolve()
MASKDIR = Path(DATADIR, 'masks').resolve()
OUTDIR = Path(ROOTDIR, 'results', 'cortical', parents=True, exist_ok=True).resolve()

nsurrs = 1000
seed = MSEED
nverts = 10242
n_procs = get_num_threads()

# get paths
genepc1 = load_npy(join(DATADIR, 'abagen_PC1', 'abagen_PC1.npy'))
neurosynth = load_npy(join(DATADIR, 'neurosynth', 'neurosynth_gradient01.npy'))
HCP_thickness = load_npy(join(DATADIR, 'HCP_structural', 'HCP_thickness.npy'))
HCP_myelin = load_npy(join(DATADIR, 'HCP_structural', 'HCP_myelin.npy'))
margulies_gradient = load_npy(join(DATADIR, 'margulies2016_PC1', 'margulies_gradient01.npy'))

medial_wall = get_medial(density='10k')
emodes = load_npy(join(DATADIR, 'eigenmodes', 'space-fsaverage_den-10k_hemi-lh_emodes-2500.npy'))
evals = load_npy(join(DATADIR, 'eigenmodes', 'space-fsaverage_den-10k_hemi-lh_evals-2500.npy'))

# generate spin resamples
spin_nulls_all = np.empty((4, nsurrs, nverts))
for i, map in enumerate([neurosynth, HCP_thickness, HCP_myelin, margulies_gradient]):
    map = np.concatenate((map, np.zeros(nverts)))
    spin_nulls = alexander_bloch(
        data=map,
        atlas='fsaverage',
        density='10k',
        n_perm=nsurrs,
        seed=seed
    )[:nverts] # only want the left hemisphere
    spin_nulls_all[i] = spin_nulls.T

save_npy(join(OUTDIR, 'annotations_spin_nulls.npy'), spin_nulls_all)
del spin_nulls_all # clear memory because BIG

# generate brainsmash surrogates
brainsmash_nulls_all = np.empty((4, nsurrs, nverts))
for i, map in enumerate([neurosynth, HCP_thickness, HCP_myelin, margulies_gradient]):
    map = np.concatenate()
    brainsmash_nulls = burt2020(
        data=map,
        atlas='fsaverage',
        density='10k',
        n_perm=nsurrs,
        seed=seed,
        n_proc=n_procs
    )[:nverts]
    brainsmash_nulls_all[i] = brainsmash_nulls.T

save_npy(join(OUTDIR, 'annotations_brainsmash_nulls.npy'), brainsmash_nulls_all)
del brainsmash_nulls_all # clear memory because BIG

# generate eigenstrapping surrogates
eigen_nulls_all = np.empty((4, nsurrs, nverts))
for i, map in enumerate([neurosynth, HCP_thickness, HCP_myelin, margulies_gradient]):
    eigen = SurfaceEigenstrapping(
        data=map,
        emodes=emodes,
        evals=evals,
        num_modes=6000,
        seed=seed,
        resample=True,
        permute=True,
        n_jobs=n_procs
    )
    eigen_nulls = eigen(n=nsurrs)
    eigen_nulls_all[i] = eigen_nulls

save_npy(join(OUTDIR, 'annotations_eigen_nulls.npy'), eigen_nulls_all)
del eigen_nulls_all # clear memory because BIG

print('saved all brainmap surrogates to {}\n'.format(OUTDIR))