import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
from statistics import mean
import scipy.stats as stats

indicator_output = np.loadtxt("C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_output/SA_output.csv", delimiter=',')

rec = indicator_output[:, 0]
res = indicator_output[:, 1]
rob = indicator_output[:, 2]

sample_size = len(rec)

mean_rec = mean(rec)
print("mean rec", mean_rec)
mean_res = mean(res)
print("mean res", mean_res)
mean_rob = mean(rob)
print("mean rob", mean_rob)

dev_rec = statistics.stdev(rec)
print("standard deviation of rec", dev_rec)
dev_res = statistics.stdev(res)
print("standard deviation of res", dev_res)
dev_rob = statistics.stdev(rob)
print("standard deviation of res", dev_rob)

zscores_rec = stats.zscore(rec)
zscores_res = stats.zscore(res)
zscores_rob = stats.zscore(rob)

min_z_rec = min(zscores_rec)
print("min z rec", min_z_rec)
min_z_res = min(zscores_res)
print("min z res", min_z_res)
min_z_rob = min(zscores_rob)
print("min z rob", min_z_rob)

color_rec = (107/255, 144/255, 179/255)
color_res = (39/255, 60/255, 44/255)
color_rob = (86/255, 137/255, 118/255)


zscores_total = np.zeros((sample_size, 3))

zscores_total[:, 0] = zscores_rec
zscores_total[:, 1] = zscores_res
zscores_total[:, 2] = zscores_rob

print(zscores_total)

av_performance = np.zeros((sample_size))

variance = 5

percentile_rec = np.percentile(zscores_rec, variance)
print("percentile rec", percentile_rec)

percentile_res = np.percentile(zscores_res, variance)
print("percentile res", percentile_res)

percentile_rob = np.percentile(zscores_rob, variance)
print("percentile res", percentile_rob)


for i in range(sample_size):
    if zscores_total[i, 0] <= (percentile_rec):
        if zscores_total[i, 1] <= (percentile_res):
            if zscores_total[i, 2] <= (percentile_rob):
                av_performance[i] = np.mean(zscores_total[i])
    else:
        av_performance[i] = 0

"""
for i in range(sample_size):
    if all(zscores_total[i] < 0):
        av_performance[i] = np.mean(zscores_total[i])
    else:
        av_performance[i] = 0
"""
print(av_performance)

csv_path='C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_Z_average.csv'

pd.DataFrame(av_performance).to_csv(csv_path, index=False, header=False)

best_av = min(av_performance)
print(best_av)

indices = []
for i, val in enumerate(av_performance):
    if val != 0:
        indices.append(i)
print('indices', indices)

best_index = np.argmin(av_performance)
print(best_index)



values_best_av = zscores_total[best_index]
print(values_best_av)

values_best_overall =zscores_total[indices]
print(values_best_overall)

csv_path_av = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_Z_average_best.csv'
csv_path_overall = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_Z_overall_best.csv'

pd.Series(best_index).to_csv(csv_path_av, index=False, header=False)

pd.DataFrame(indices).to_csv(csv_path_overall, index=False, header=False)



from scipy.stats import norm

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 8), sharey=True)

sns.kdeplot(zscores_rec, ax=axes[0], color=color_res)
sns.kdeplot(zscores_res, ax=axes[1], color=color_rob)
sns.kdeplot(zscores_rob, ax=axes[2], color=color_rec)

# Add vertical lines at x=0 for each subplot
for ax in axes:
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1.2, zorder=2000)

# Add a grid to each subplot
for ax in axes:
    ax.grid(color='gray', alpha=0.6, linestyle='-', linewidth=0.1)
    ax.set_facecolor((0.95, 0.95, 0.95))

axes[0].axvline(x=percentile_rec, c="gray", linestyle='--', linewidth=1.5)
axes[1].axvline(x=percentile_res, c="gray", linestyle='--', linewidth=1.5)
axes[2].axvline(x=percentile_rob, c="gray", linestyle='--', linewidth=1.5)

axes[0].set_title('recoverability')
axes[0].set_xlabel('z-factor')
axes[1].set_title('resistance')
axes[1].set_xlabel('z-factor')
axes[2].set_title('robustness')
axes[2].set_xlabel('z-factor')

# adjust the horizontal spacing between subplots
plt.tight_layout()
for ax in axes:
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

plt.subplots_adjust(wspace=0.2)
plt.show()


