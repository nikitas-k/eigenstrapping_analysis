import os.path as op
from pathlib import Path
import numpy as np

from eigenstrapping.fit import SampledSurrogateMaps
from eigenstrapping_analysis.utils import (
    get_rootdir, MSEED, join, save_npy, load_npy
)

from eigenstrapping.stats import compare_maps

ROOTDIR = get_rootdir()
DATADIR = Path(ROOTDIR, 'datasets', 'cortical').resolve()
MASKDIR = Path(DATADIR, 'masks').resolve()
OUTDIR = Path(ROOTDIR, 'results', 'cortical').resolve()

nsurrs = 1000
ncorrs = 4 # number of correlation sets
ntypes = 3 # number of null types
seed = MSEED

# necessary files
genepc1 = load_npy(join(DATADIR, 'abagen_PC1', 'abagen_PC1.npy'))
neurosynth = load_npy(join(DATADIR, 'neurosynth', 'neurosynth_gradient01.npy'))
HCP_thickness = load_npy(join(DATADIR, 'HCP_structural', 'HCP_thickness.npy'))
HCP_myelin = load_npy(join(DATADIR, 'HCP_structural', 'HCP_myelin.npy'))
margulies_gradient = load_npy(join(DATADIR, 'margulies2016_PC1', 'margulies_gradient01.npy'))
spin_nulls_all = load_npy(join(OUTDIR, 'annotations_spin_nulls.npy'))
brainsmash_nulls_all = load_npy(join(OUTDIR, 'annotations_brainsmash_nulls.npy'))
eigen_nulls_all = load_npy(join(OUTDIR, 'annotations_eigen_nulls.npy'))

# correlate target & surrogates
corrs = np.empty((ncorrs, ntypes))
zscores = np.empty((ncorrs, ntypes))
pvals = np.empty((ncorrs, ntypes))
spin_corrs, brainsmash_corrs, eigen_corrs = np.empty((ncorrs, ntypes, nsurrs))
for i, map in enumerate(zip([neurosynth, HCP_thickness, HCP_myelin, margulies_gradient])):
    for ii, (nulls, corrs) in enumerate(zip([spin_nulls_all, brainsmash_nulls_all, eigen_nulls_all], [spin_corrs, brainsmash_corrs, eigen_corrs])):
        curr_nulls = nulls[i]
        corrs[i, ii], pvals[i, ii], corrs[i, ii] = compare_maps(genepc1, map, nulls=curr_nulls, return_nulls=True)
        zscores[i, ii] = (corrs[i, ii] - np.mean(corrs[i, ii])) / np.std(corrs[i, ii])

# save for plotting
save_npy(join(OUTDIR, 'annotations_source_target_corrs.npy'), corrs)
save_npy(join(OUTDIR, 'annotations_source_target_zscores.npy'), zscores)
save_npy(join(OUTDIR, 'annotations_source_target_pvals.npy'), pvals)
save_npy(join(OUTDIR, 'annotations_source_target_corrs_allnulls.npy'), corrs)

print('saved brainmap annotation analysis files to {}\n'.format(OUTDIR))