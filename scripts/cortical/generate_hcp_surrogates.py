"""
Generate eigenstrapping nulls for S255 HCP functional data
"""

from pathlib import Path
import os.path as op
import numpy as np

from eigenstrapping_analysis.utils import get_rootdir, MSEED, spat_perm, get_medial

from eigenstrapping import SurfaceEigenstrapping
from eigenstrapping.fit import SampledSurrogateMaps

ROOTDIR = get_rootdir()
DATADIR = Path(ROOTDIR, 'datasets').resolve()
MASKDIR = Path(DATADIR, 'masks').resolve()
OUTDIR = Path(ROOTDIR, 'results', 'cortical', parents=True, exist_ok=True).resolve()

nsurrs = 1000
seed = MSEED

# get paths
D = op.join(DATADIR, 'distmat', 'distmat_32k.npy')
index = op.join(DATADIR, 'distmat', 'index_32k.npy')
hcp_data = np.load(op.join(DATADIR, 'HCP_functional', 'space-fsLR_den-32k_hemi-lh_S255-ALLTASKS.npy'))
medial_wall = np.loadtxt(op.join(MASKDIR, 'space-fsLR_den-32k_hemi-lh_medialwall.txt'))
emodes = np.loadtxt(op.join(DATADIR, 'eigenmodes', 'space-fsLR_den-32k_hemi-lh_emodes-6000.txt'))
evals = np.loadtxt(op.join(DATADIR, 'eigenmodes', 'space-fsLR_den-32k_hemi-lh_evals-6000.txt'))

# first and second subjects in EMOTION_FACES_SHAPES
hcp_data_source = hcp_data[0][0]
hcp_data_target = hcp_data[0][1]

# generate random surrogates
rand_nulls = spat_perm(hcp_data_source, mask=medial_wall, seed=seed, nperm=nsurrs)

# generate eigenstrapping surrogates
e = SurfaceEigenstrapping(
    data=hcp_data_source,
    emodes=emodes,
    evals=evals,
    num_modes=6000,
    seed=seed,
    resample=True,
    permute=True
)

eigen_nulls = e(n=nsurrs)

# Compute target & surrogate map variograms
generator = SampledSurrogateMaps(nh=40, seed=seed)
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

# save for plots
np.save(op.join(OUTDIR, 'hcp_u0.npy'), u0)
np.save(op.join(OUTDIR, 'hcp_emp_var.npy'), emp_var)
np.save(op.join(OUTDIR, 'hcp_rand_nulls_var.npy'), surr_rand)
np.save(op.join(OUTDIR, 'hcp_eigen_nulls_var.npy'), surr_eigen)