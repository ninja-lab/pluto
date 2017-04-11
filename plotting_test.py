import plotting
import numpy as np


testR1 = np.arange(100, 200, 10)
testR2 = np.arange(110, 210, 10)
xvals = np.arange (1, 2, .1)
legend_strs = ['R1', 'R2']
xlabel = 'current'
ylabel = 'resistance'
title_str = 'Sample Plot'

plotting.easy_plot([testR1, testR2], xvals, legend_strs, xlabel, ylabel, title_str)

