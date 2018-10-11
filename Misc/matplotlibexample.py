'''
import matplotlib.pyplot as plt
plt.ion()
plt.plot([1.6, 2.7])
plt.title("interactive test")
plt.xlabel("index")
ax = plt.gca()
ax.plot([3.1, 2.2])
plt.draw()
'''

import matplotlib.pyplot as plt
plt.ioff()
plt.plot([1.6, 2.7])