import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
results = pd.DataFrame()

# sample inductances
#L1 = np.arange(0, 20 + 2, 2)
L1 = list(range(0,11))
L2 = np.arange(0.5, 22, 2)
L3 = np.arange(.6, 22, 2)
freqs = [.1, .2, .5, 1,2,5,10,20,50, 100, 200]
temp = {}
#as returned from get_L_vs_freq():
temp['8Amps'] = L1
temp['9Amps'] = L2
temp['10Amps'] = L3

results = pd.DataFrame(temp, index=freqs)

axes_  = results.plot(kind='line', logx=True, title='Inductance vs Frequency')

plt.show()


