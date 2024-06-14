"""
data fetchers
"""

import os.path as op
from pathlib import Path
import shutil
from pkg_resources import resource_filename

from eigenstrapping.datasets import utils

import numpy as np
from neuromaps import datasets, images
import nibabel as nib
from nilearn.datasets.utils import _fetch_file


def fetch_data(*, name=None, space=None, den=None, res=None, hemi=None,
                   tags=None, format=None, data_dir=None, verbose=1):
    """
    Downloads files for brain surfaces and eigenmodes matching requested variables

    Parameters
    ----------
    name, space, den, res, hemi, tags, format : str or list-of-str
        Values on which to match surfaces. If not specified surfaces with
        any value for the relevant key will be matched. Default: None
    data_dir : str, optional
        Path to use as data directory. If not specified, will
        use `~/eigenstrapping-data` instead. Default: None
    verbose : int, optional
        Modifies verbosity of download, where higher numbers mean more updates.
        Default: 1

    Returns
    -------
    data : dict
        Dictionary of downloaded annotations where dictionary keys are tuples
        (space, den/res) and values are lists of corresponding
        filenames
    """

    # check input parameters to ensure we're fetching _something_
    supplied = False
    for val in (space, den, res, hemi, tags, format):
        if val is not None:
            supplied = True
            break
    if not supplied:
        raise ValueError('Must provide at least one parameters on which to '
                         'match files. If you want to fetch all '
                         'annotations set any of the parameters to "all".')

    # get info on datasets we need to fetch
    if name == 'HCP_structural':
        data_dir = Path('datasets', 'cortical', 'HCP_structural', parents=True, exist_ok=True).resolve()
        datasets.fetch_annotation(desc='myelinmap', return_single=True, data_dir=data_dir)
        datasets.fetch_annotation(desc='thickness', return_single=True, data_dir=data_dir)
    elif name == 'abagen_PC1':
        data_dir = Path('datasets', 'cortical', 'abagen_PC1', parents=True, exist_ok=True).resolve()
        datasets.fetch_annotation(desc='abagen', return_single=True, data_dir=data_dir)
    elif name == 'margulies2016_gradient01':
        data_dir = Path('datasets', 'cortical', 'margulies2016_gradient01', parents=True, exist_ok=True).resolve()
        datasets.fetch_annotation(desc='fcgradient01', return_single=True, data_dir=data_dir)
    elif name == 'neurosynth':
        data_dir = Path('datasets', 'cortical', 'neurosynth', parents=True, exist_ok=True).resolve()
        datasets.fetch_annotation(source='neurosynth', return_single=True, data_dir=data_dir)

    data_dir = utils.get_data_dir(data_dir=data_dir)
    info = utils._match_files(get_dataset_info(name),
                        space=space, den=den, res=res,
                        hemi=hemi, tags=tags, format=format)
    if verbose > 1:
        print(f'Identified {len(info)} datasets matching specified parameters')

    # TODO: current work-around to handle that _fetch_files() does not support
    # session instances. hopefully a future version will and we can just use
    # that function to handle this instead of calling _fetch_file() directly
    data = []
    for dset in info:
        fn = Path(data_dir) / dset['rel_path'] / dset['fname']
        if not fn.exists():
            dl_file = _fetch_file(dset['url'], str(fn.parent), verbose=verbose,
                                  md5sum=dset['checksum'])
            shutil.move(dl_file, fn)
        data.append(str(fn))
    
    if len(data) == 1:
        return data[0]
    
    return utils._groupby_match(data)

def get_dataset_info(name):
    """
    Returns information for requested dataset `name`

    Parameters
    ----------
    name : str
        Name of dataset

    Returns
    -------
    dataset : dict or list-of-dict
        Information on requested data
    """

    fn = resource_filename('eigenstrapping_analysis',
                           op.join('datasets', 'osf.json'))
    with open(fn) as src:
        osf_resources = utils._osfify_urls(json.load(src))

    try:
        resource = osf_resources[name]
    except KeyError:
        raise KeyError("Provided dataset '{}' is not valid. Must be one of: {}"
                       .format(name, sorted(osf_resources.keys())))

    return resource