import os
from glob import glob
import pandas as pd

__all__ = ['datasets']
datasets = {}


for _folder in [f for f in os.scandir(os.path.dirname(__file__)) if f.is_dir()]:
    datasets[_folder.name] = {}
    for _csv in glob(os.path.join(_folder.path, '*.csv')):
        try:
            _name = os.path.basename(_csv)[:-4]
            _df = pd.read_csv(_csv, parse_dates=[0], index_col=0)
            datasets[_folder.name][_name] = _df
            globals()[f'{_folder.name}__{_name}'] = _df
            __all__.append(f'{_folder.name}__{_name}')
        except:
            pass


del os, glob, pd
