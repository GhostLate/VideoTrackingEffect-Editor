import numpy as np
from scipy.ndimage import gaussian_filter1d
from matplotlib import pyplot as plt

import pandas as pd
data = pd.read_csv('data.csv')

start = 0
slice = data['x1'].size
x = range(start, slice)

x1 = data['x1'][start:slice].values
y1 = data['y1'][start:slice].values
x2 = data['x2'][start:slice].values
y2 = data['y2'][start:slice].values

x_c = np.round((x1 + x2) / 2).astype(int)
y_c = np.round((y1 + y2) / 2).astype(int)
x_l = np.round(x2 - x1).astype(int)
y_l = np.round(y2 - y1).astype(int)
len = slice - start

y_g = gaussian_filter1d(y_c, 10)
x_g = gaussian_filter1d(x_c, 10)
y_g1 = gaussian_filter1d(gaussian_filter1d(y_c, 5), 5)
x_g1 = gaussian_filter1d(gaussian_filter1d(x_c, 5), 5)
y_lg = gaussian_filter1d(y_l, 15)
x_lg = gaussian_filter1d(x_l, 15)
y_lg1 = gaussian_filter1d(gaussian_filter1d(y_l, 10), 10)
x_lg1 = gaussian_filter1d(gaussian_filter1d(x_l, 10), 10)

n_x1 = list(x_g - x_lg / 2)
n_y1 = list(y_g - y_lg / 2)
n_x2 = list(x_g + x_lg / 2)
n_y2 = list(y_g + y_lg / 2)

plt.plot(x_c, y_c, 'b')
plt.plot(x_g, y_g, 'r')
plt.plot(x_g1, y_g1, 'g')
plt.show()

plt.plot(x_l, y_l, 'b')
plt.plot(x_lg, y_lg, 'r')
plt.plot(x_lg1, y_lg1, 'g')
plt.show()

plt.plot(x1, y1, 'b')
plt.plot(n_x1, n_y1, 'r')
plt.show()

plt.plot(x2, y2, 'b')
plt.plot(n_x2, n_y2, 'r')
plt.show()