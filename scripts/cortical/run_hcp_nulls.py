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
OUTDIR = Path(ROOTDIR, 'results', 'cortical', parents=True, exist_ok=True).resolve()

nsurrs = 1000
seed = MSEED

# necessary files
D = join(DATADIR, 'distmat', 'distmat_32k.npy')
index = join(DATADIR, 'distmat', 'index_32k.npy')
hcp_data = load_npy(join(DATADIR, 'HCP_functional', 'space-fsLR_den-32k_hemi-lh_S255-ALLTASKS.npy'))
rand_nulls = load_npy(join(OUTDIR, 'hcp_random_nulls.npy'))
eigen_nulls = load_npy(join(OUTDIR, 'hcp_eigen_nulls.npy'))

# first and second subjects in EMOTION_FACES_SHAPES
hcp_data_source = hcp_data[0][0]
hcp_data_target = hcp_data[0][1]

# correlate target & surrogates
corr, _, rand_corrs = compare_maps(hcp_data_source, hcp_data_target, nulls=rand_nulls, return_nulls=True)
_, _, eigen_corrs = compare_maps(hcp_data_source, hcp_data_target, nulls=eigen_nulls, return_nulls=True)

# Compute target & surrogate map variograms
generator = SampledSurrogateMaps(nh=40, seed=seed) # nh = 40, default otherwise
generator.fit(D, index)

# compute random surrogates
surr_rand = np.empty((nsurrs, generator.nh))
surr_eigen = np.empty((nsurrs, generator.nh))
emp_var_samples = np.empty((nsurrs, generator.nh))
u0_samples = np.empty((nsurrs, generator.nh))
for i in range(nsurrs):
    xi = generator._check_map(hcp_data_source)
    idx = generator.sample(xi.size)  # Randomly sample a subset of brain areas
    v = generator.compute_variogram(xi, idx)
    u = generator._dist[idx, :]
    umax = np.percentile(u, generator.pv)
    uidx = np.where(u < umax)
    emp_var_i, u0i = generator.smooth_variogram(
        u=u[uidx], v=v[uidx], return_h=True)
    emp_var_samples[i], u0_samples[i] = emp_var_i, u0i
    # Random Surrogate
    surri = generator._check_map(rand_nulls[i])
    v_rand = generator.compute_variogram(surri, idx)
    surr_rand[i] = generator.smooth_variogram(
        u=u[uidx], v=v_rand[uidx], return_h=False
    )
    
    # Eigen surrogate
    surri = generator._check_map(eigen_nulls[i])
    v_eigen = generator.compute_variogram(surri, idx)
    surr_eigen[i] = generator.smooth_variogram(
        u=u[uidx], v=v_eigen[uidx], return_h=False
    )

u0 = u0_samples.mean(axis=0)
emp_var = emp_var_samples.mean(axis=0)

# save for later
save_npy(join(OUTDIR, 'hcp_source_target_corr.npy'), corr)
save_npy(join(OUTDIR, 'hcp_random_corrs.npy'), rand_corrs)
save_npy(join(OUTDIR, 'hcp_eigen_corrs.npy'), eigen_corrs)
save_npy(join(OUTDIR, 'hcp_u0.npy'), u0)
save_npy(join(OUTDIR, 'hcp_emp_var.npy'), emp_var)
save_npy(join(OUTDIR, 'hcp_rand_nulls_var.npy'), surr_rand)
save_npy(join(OUTDIR, 'hcp_eigen_nulls_var.npy'), surr_eigen)

print('saved HCP analysis files to {}\n'.format(OUTDIR))