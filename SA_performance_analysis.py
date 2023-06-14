import pandas as pd
import numpy as np

output = np.loadtxt("/SA_output.csv", delimiter=',')

res = output[:, 0]
rob = output[:, 1]
rec = output[:, 2]

# find best performing scenarios per index (output: lowest value of performance output and file number (within sample size))
def find_best_performance(output, best_results):
    sorted_output = np.argsort(output)
    indices_output = sorted_output[:best_results]
    lowest_output = output[indices_output]
    original_indices_output = indices_output[np.argsort(lowest_output)]
    return lowest_output, original_indices_output

lowest_rec, rec_indices = find_best_performance(rec, 5)
lowest_res, res_indices = find_best_performance(res, 5)
lowest_rob, rob_indices = find_best_performance(rob, 5)


# find worst performing scenarios per index (output: highest value of performance output and file number (within sample size))
def find_worst_performance(output, worst_results):
    sorted_output = np.argsort(output)[::-1]  # sort in descending order
    indices_output = sorted_output[:worst_results]
    highest_output = output[indices_output]
    original_indices_output = indices_output[np.argsort(highest_output)][::-1] # sort original indices in descending order
    return highest_output, original_indices_output

highest_rec, rec_worst_indices = find_worst_performance(rec, 5)
highest_res, res_worst_indices = find_worst_performance(res, 5)
highest_rob, rob_worst_indices = find_worst_performance(rob, 5)


indices = np.stack((res_indices, rob_indices, rec_indices), axis=1)
worst_indices = np.stack((res_worst_indices, rob_worst_indices, rec_worst_indices), axis=1)

# save scenario indices for further analysis
csv_path='/SA_performance_indices.csv'
csv_path_2='/SA_worst_performance_indices.csv'

pd.DataFrame(indices).to_csv(csv_path, index=False, header=False)
pd.DataFrame(worst_indices).to_csv(csv_path_2, index=False, header=False)





# plot performance distribution as histogramm
import seaborn as sns
import matplotlib.pyplot as plt

# give each index a colour
color_res = (39/255, 60/255, 44/255)
color_rob = (86/255, 137/255, 118/255)
color_rec = (107/255, 144/255, 179/255)


fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 9))
sns.histplot(res, ax=axes[0], bins=np.arange(1.0, 3.2, 0.1), color=color_res, alpha=0.8, edgecolor='white')
axes[0].axvline(mean_res, color='black', linestyle='--', linewidth=1)

sns.histplot(rob, ax=axes[1], bins=np.arange(17800, 20500, 125), color=color_rob, alpha=0.8, edgecolor='white')
axes[1].axvline(mean_rob, color='black', linestyle='--', linewidth=1)

sns.histplot(rec, ax=axes[2], bins=np.arange(5, 65, 2.5), color=color_rec, alpha=0.8, edgecolor='white')
axes[2].axvline(mean_rec, color='black', linestyle='--', linewidth=1)


# Add a grid to each subplot
for ax in axes:
    ax.grid(color='gray', alpha=0.6, linestyle='-', linewidth=0.1)
    ax.set_facecolor((0.95, 0.95, 0.95))

axes[0].set_title('resistance')
axes[0].set_xlabel('temperature (SET, °C)')
axes[1].set_title('robustness')
axes[1].set_xlabel('integral index')
axes[2].set_title('recoverability')
axes[2].set_xlabel('time (hours)')

 # adjust the horizontal spacing between subplots
plt.tight_layout()
plt.subplots_adjust(wspace=0.2)
plt.show()
