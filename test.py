import matplotlib.pyplot as plt
import numpy as np

t = np.arange(0,5,0.2)

plt.plot(t, t**2, linewidth=2.0)
plt.show()