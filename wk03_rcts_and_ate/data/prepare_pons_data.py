"""Rebuild the teaching CSV from Pons's original analysis.dta.

For course maintainers; students use the supplied CSV.
Run: python prepare_pons_data.py /path/to/Data/Analysis/analysis.dta
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

source = pd.read_stata(sys.argv[1], convert_categoricals=False)

# The main analysis sample with matched 2012 election results (Analysis.do).
sample = source[(source['territory_in'] == 1) &
                (source['merge_results12'] == 1)].copy()

teaching = pd.DataFrame()
municipality_code = sample['municipality_code'].astype(int).astype(str)
teaching['area_id'] = np.where(
    sample['level_randomization'] == 1,
    'P_' + municipality_code + '_' + sample['precinct_code'],
    'M_' + municipality_code)
teaching['area_type'] = np.where(
    sample['level_randomization'] == 1, 'Precinct', 'Municipality')
teaching['municipality'] = sample['municipality'].values
teaching['block'] = sample['stratum_identifier'].astype(int).values
teaching['treatment'] = sample['treatment'].astype(int).values
teaching['registered'] = sample['nb_registered_pr12t1_an'].astype(int).values
teaching['turnout'] = sample['prop_turnout_pr12t1_an'].astype(float).values
teaching['hollande_share'] = sample['prop_hollande_pr12t1_an'].astype(float).values

destination = Path(__file__).with_name('pons_2018_teaching.csv')
teaching.to_csv(destination, index=False)
print('Saved', teaching.shape, 'to', destination)
