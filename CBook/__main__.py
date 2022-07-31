from api import CBPro
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import rcParams

rcParams['figure.autolayout'] = True

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

fig.tight_layout()

bg = 'black'
fg = 'cyan'

ticker = 'BTC-USD'

depth = 30
cb = CBPro(ticker=[ticker], depth=depth)
cb.start()

hold = []
limit = depth

fig.patch.set_facecolor(bg)
ax.set_facecolor(bg)

for i in ('x','y','z'):
    ax.tick_params(i, colors=fg)

for i in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    i.set_facecolor(bg)
    i.set_edgecolor(bg)


while True:
    if ticker in cb.priceline.keys():
        hold.append(cb.bidvol[ticker] + cb.askvol[ticker])
        xn, yn = np.array(hold).shape
        x, y = np.meshgrid(range(yn), range(xn))
        y = y[::-1]
        z = np.array(hold)
        
        if len(hold) > 6:
            ax.cla()
            ax.set_title('Ticker: {} | Bids Size: {} | Asks Size: {}'.format(ticker, len(cb.bids[ticker]), len(cb.asks[ticker])), color=fg)
            ax.plot_surface(x, y, z, cmap='hsv')
            ax.set_xlabel('Price', color=fg)
            ax.set_ylabel('Time', color=fg)
            ax.set_zlabel('Volume', color=fg)
            uk = cb.priceline[ticker]
            ax.set_xticks(range(len(uk)))
            ax.set_xticklabels([round(j, 2) if i % 5 == 0 else '' for i, j in enumerate(uk)], rotation=30)
            ax.grid(False)
            plt.pause(0.00001)
        
        if len(hold) > limit:
            del hold[0]



cb.join()
plt.show()
