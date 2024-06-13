"""
calculate time to generate 1000 nulls for each surface
"""

# load libraries
import numpy as np
from eigenstrapping import SurfaceEigenstrapping, VolumetricEigenstrapping
import time
import threadpoolctl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from parspin import simnulls
from dataclasses import asdict, make_dataclass
from pathlib import Path

OUTDIR = Path('results/supplementary/comp_time').resolve()

# global variables
nsurrs = 1000
nrepeats = 5 # number of times to repeat computation for average
SURFACES = ['fsaverage5', 'fs_LR_32k']

CompTime = make_dataclass(
    'CompTime', ('surface', 'modes', 'runtime')
)
USE_CACHED = True

def make_stripplot(fn):
    "cached.csv or uncached.csv"
    data = pd.read_csv(fn)
    fig, ax = plt.subplots(1,1)
    ax = sns.stripplot(x='runtime', y='surface', hue='modes', dodge=True, ax=ax,
                       data=data)
    ax.set_xscale('log')
    xl = (10**0, 10**6)
    ax.hlines(np.arange(0.5, 2.5), *xl, linestyle='dashed', linewidth=0.5,
              color=np.array([50, 50, 50]) / 255)
   
    ax.set(xlim=xl, ylim=(2.5, -0.5))
    plt.xticks(size=15)
    plt.yticks(size=15)
    plt.xlabel('Runtime (seconds)', size=20)
    plt.ylabel('Surface type', size=20)
    #ax.legend_.set_visible(False)
    sns.despine(ax=ax)

def output_exists(data, surface, nmode, repeat):
    if len(data) == 0:
        return False
    
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    present = data.query(f'surface == "{surface}" '
                         f'& modes == "{nmode}" ')
    return len(present) > (repeat)

def compute_runtimes():
    threadpoolctl.threadpool_limits(limits=1) # NO parallelization
    # output
    fn = OUTDIR / ('cached.csv' if USE_CACHED else 'uncached.csv')
    fn.parent.mkdir(exist_ok=True, parents=True)
    
    cols = ['surface', 'modes', 'runtime']
    data = pd.read_csv(fn).to_dict('records') if fn.exists() else []
    for SURFACE in SURFACES:
        x = np.loadtxt(f'datasets/brainmaps/{SURFACE}_data.txt')
        if USE_CACHED:
            emodes = np.loadtxt(f'results/{SURFACE}_emodes.txt')
            evals = np.loadtxt(f'results/{SURFACE}_evals.txt')
        else:
            emodes = None
            evals = None
        for nmode in [200, 1000, 2500, 5000]:
            for repeat in range(nrepeats):
                if output_exists(data, SURFACE, nmode, repeat):
                    continue
                data.append(get_surface_runtime(x, SURFACE, nmode, emodes, evals))
                pd.DataFrame(data)[cols].to_csv(fn, index=False)
                
    # vol - no caching necessary
    for nmode in [20, 200, 1000]:
        for repeat in range(nrepeats):
            if output_exists(data, 'volumetric', nmode, repeat):
                continue
            data.append(get_vol_runtime(nmode))
            pd.DataFrame(data)[cols].to_csv(fn, index=False)
                
    return fn

def get_surface_runtime(x, SURFACE, nmode, emodes=None, evals=None):
    start = time.time()
    
    surf = f'datasets/surfaces/standard/{SURFACE}.L.pial.surf.gii'
    medial = f'datasets/masks/{SURFACE}_medial_wall_lh_masked.txt'
    # calculate null
    eigen = SurfaceEigenstrapping(x, surf, evals=evals, emodes=emodes,
                                  num_modes=nmode, use_cholmod=True,
                                  medial=medial,
                                  )
    nulls = eigen(n=nsurrs)
    
    if nulls is not None:
        simnulls.calc_pval(x, x, nulls.T)
    
    end = time.time()
    ct = CompTime(SURFACE, nmode, end-start)
    print(ct)
    
    return asdict(ct)

def get_vol_runtime(nmode):
    start = time.time()
    
    vol = 'datasets/subcortical/hcp_striatum-lh_thr25.nii.gz'
    x = 'datasets/subcortical/hcp_striatum-lh_gradient_1.txt'
    eigen = VolumetricEigenstrapping(vol, x, num_modes=nmode)
    
    nulls = eigen(n=nsurrs)
    
    data = np.loadtxt(x)
    if nulls is not None:
        simnulls.calc_pval(data, data, nulls.T)
    
    end = time.time()
    ct = CompTime('volumetric', nmode, end-start)
    print(ct)
    
    return asdict(ct)


for cache in (True, False):
    globals()['USE_CACHED'] = False
    fn = compute_runtimes()
    make_stripplot(fn)