import pandas as pd
import numpy as np
import statistics
from statistics import mean
import scipy.stats as stats

# load SA output
indices_output = np.loadtxt("/SA_output.csv", delimiter=',')


res = indices_output[:, 0]
rob = indices_output[:, 1]
rec = indices_output[:, 2]

sample_size = len(rec)

# calculate Z-scores of performance per resilience index
zscores_res = stats.zscore(res)
zscores_rob = stats.zscore(rob)
zscores_rec = stats.zscore(rec)

# create an array to store z-scores, each index one column
zscores_total = np.zeros((sample_size, 3))

zscores_total[:, 0] = zscores_res
zscores_total[:, 1] = zscores_rob
zscores_total[:, 2] = zscores_rec
print(zscores_total)




# 95th percentile calculation -> analysis of the 5% best performing scenarios per index
variance = 5
percentile_res = np.percentile(zscores_res, variance)
print("percentile res", percentile_res)
percentile_rob = np.percentile(zscores_rob, variance)
print("percentile res", percentile_rob)
percentile_rec = np.percentile(zscores_rec, variance)
print("percentile rec", percentile_rec)

# find best performing scenarios that score with a performance in the top 5% per index
av_performance = []
for i in range(sample_size):
    if zscores_total[i, 0] <= (percentile_res):
        if zscores_total[i, 1] <= (percentile_rob):
            if zscores_total[i, 2] <= (percentile_rec):
                av_performance[i] = np.mean(zscores_total[i])
    else:
        av_performance[i] = 0
print(av_performance)

# save resulting average Z-scores to CSV file -> lowest value means that this scenario performs the best overall 
csv_path='/SA_Z_average.csv'
pd.DataFrame(av_performance).to_csv(csv_path, index=False, header=False)

# find index of scenario within sample size
indices = []
for i, val in enumerate(av_performance):
    if val != 0:
        indices.append(i)
print('indices', indices)

# find lowest Z-value (scenario with best overall performance)
best_index = np.argmin(av_performance)
print(best_index)


# CSV file directory 
csv_path_av = '/SA_Z_average_best.csv'
# save to CSV
pd.Series(best_index).to_csv(csv_path_av, index=False, header=False)



