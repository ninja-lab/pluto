import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import instrument_strings

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'

results1 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization2017-05-01_16_21.csv')
results2 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization2017-05-01_14_08.csv')

results = pd.concat([results1, results2], axis=1) 
filename = save_loc + 'PVC1001_Characterization2017-05-01.csv'
results.to_csv(path_or_buf=filename)

results1 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization_varying_current2017-05-02_15_34.csv')
results2 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization_varying_current2017-05-03_09_03.csv')

results = pd.concat([results1, results2], axis=1) 
filename = save_loc + 'PVC1001_Characterization_varying_current2017-05-02.csv'
results.to_csv(path_or_buf=filename)