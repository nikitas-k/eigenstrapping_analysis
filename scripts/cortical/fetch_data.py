"""
Fetch HCP/Neurosynth/Allen Human Brain Atlas/etc cortical maps and distance matrices and eigenmodes
"""
from pathlib import Path
import os.path as op

import numpy as np

from eigenstrapping_analysis.datasets.data_fetcher import fetch_data
from eigenstrapping_analysis.utils import get_rootdir, get_medial
from eigenstrapping.datasets import txt2memmap

from neuromaps.transforms import mni152_to_fsaverage, fslr_to_fsaverage
from neuromaps.datasets import fetch_fsaverage, fetch_fslr
import nibabel as nib

OUTDIR = Path(get_rootdir(), 'datasets/cortical', parents=True, exist_ok=True).resolve()
MASKDIR = Path(OUTDIR, 'masks', parents=True, exist_ok=True).resolve()

# fetch HCP
fetch_data(name='HCP_functional', data_dir=OUTDIR)
fetch_data(name='HCP_structural', data_dir=OUTDIR)

# fetch others
fetch_data(name='neurosynth', data_dir=OUTDIR)
fetch_data(name='abagen_PC1', data_dir=OUTDIR)
fetch_data(name='margulies2016_PC1', data_dir=OUTDIR)
fetch_data(name='distmat', data_dir=OUTDIR)

# fetch fsaverage and fslr masks for medial wall masking (as neuromaps does not do this by default)
medial_mask_10k = nib.load(
    getattr(
        getattr(
            fetch_fsaverage(density='10k'),
            'medial'),
    'L')
).agg_data()
np.savetxt(op.join(MASKDIR, 'space-fsaverage_den-10k_hemi-lh_medialwall.txt'), medial_mask_10k, fmt='%d')

medial_mask_32k = nib.load(
    getattr(
        getattr(
            fetch_fslr(density='32k'),
            'medial'),
    'L')
).agg_data()
np.savetxt(op.join(MASKDIR, 'space-fsLR_den-32k_hemi-lh_medialwall.txt'), medial_mask_32k, fmt='%d')

# resample and save to arrays
HCP_thickness = fslr_to_fsaverage(
    data=op.join(OUTDIR, 'HCP_structural', 'space-fsLR_den-32k_hemi-lh_thickness.shape.gii'),
    target_density='10k',
    hemi='L'
)
HCP_thickness = HCP_thickness.agg_data()
HCP_thickness[np.logical_not(medial_mask)] = np.nan
np.save(op.join(OUTDIR, 'HCP_structural/HCP_thickness.npy'), HCP_thickness)

HCP_myelin = fslr_to_fsaverage(
    data=op.join(OUTDIR, 'HCP_structural', 'space-fsLR_den-32k_hemi-lh_myelin_average.func.gii'),
    target_density='10k',
    hemi='L'
)
HCP_myelin = HCP_myelin.agg_data()
HCP_myelin[np.logical_not(medial_mask)] = np.nan
np.save(op.join(OUTDIR, 'HCP_structural/HCP_myelin.npy'), HCP_myelin)

neurosynth = mni152_to_fsaverage(
    img=op.join(OUTDIR, 'neurosynth', 'space-MNI152_den-2mm_hemi-lh_neurosynth-gradient01.nii.gz'),
    fsavg_density='10k'
)[0] # we want L hemi only
neurosynth = neurosynth.agg_data()
neurosynth[np.logical_not(medial_mask)] = np.nan
np.save(op.join(OUTDIR, 'neurosynth/neurosynth_gradient01.npy'), neurosynth)

margulies_gradient = fslr_to_fsaverage(
    data=op.join(OUTDIR, 'margulies2016_PC1', 'space-fsLR_den-32k_hemi-lh_margulies-gradient01.shape.gii'),
    target_density='10k',
    hemi='L'
)
margulies_gradient = margulies_gradient.agg_data()
margulies_gradient[np.logical_not(medial_mask)] = np.nan
np.save(op.join(OUTDIR, 'margulies2016_PC1/margulies_gradient01.npy'), margulies_gradient)

genepc1 = nib.load(op.join(OUTDIR, 'abagen_PC1', 'space-fsaverage_den-10k_hemi-lh_abagen-PC1.shape.gii')).agg_data()
np.save(op.join(OUTDIR, 'abagen_PC1/abagen_PC1.npy'), genepc1)

# convert and save 10k and 32k distance matrices
distmat_10k = op.join(OUTDIR, 'distmat', 'space-fsaverage_den-10k_hemi-lh_distmat.txt')
_ = txt2memmap(
    distmat_10k,
    output_dir=op.join(OUTDIR, 'distmat'),
    suffix='_10k'
)

distmat_32k = op.join(OUTDIR, 'distmat', 'space-fsLR_den-32k_hemi-lh_distmat.txt')
_ = txt2memmap(
    distmat_32k,
    output_dir=op.join(OUTDIR, 'distmat'),
    suffix='_32k'
)

# fetch eigenmodes
fetch_data(name='eigenmodes', hemi='lh', data_dir=OUTDIR)

print('Preprocessing complete\n')
print('Arrays saved to {}\n'.format(OUTDIR))


