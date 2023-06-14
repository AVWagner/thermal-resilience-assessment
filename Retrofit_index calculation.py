import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from eppy.modeleditor import IDF

iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
IDF.setiddname(iddfile)

base_case = "C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/09_P5/01_Design/02_Index calculation/01_IDFs/original.idf"
retrofit = "C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/09_P5/01_Design/02_Index calculation/01_IDFs/retrofit.idf"
IDF_links = []
IDF_links.append(base_case)
IDF_links.append(retrofit)

output_dir_csv = "C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/09_P5/01_Design/02_Index calculation/02_CSVs"

epwfile_2015 = "C:/Users/walin/Downloads/01_Weather data/HW Data/Final/BothHWandBetween2015_finalEPW.epw"
epwfile_2050 = 'C:/Users/walin/Downloads/01_Weather data/HW Data/2050/DEU_MUNICH_HadCM3-A2-2050_finalEPW.epw'
epwfile_2080 = 'C:/Users/walin/Downloads/01_Weather data/HW Data/2080/DEU_MUNICH_HadCM3-A2-2080_finalEPW.epw'

for i, file_path in enumerate(IDF_links):

    output_file = 'case-%02d' % i


    def make_eplaunch_options(idf):
        #Make options for run, so that it runs like EPLaunch on Windows
        idfversion = idf.idfobjects['version'][0].Version_Identifier.split('.')
        idfversion.extend([0] * (3 - len(idfversion)))
        idfversionstr = '-'.join([str(item) for item in idfversion])
        fname = idf.idfname
        options = {
            'output_prefix': output_file,
            'output_suffix': 'C',
            'output_directory': output_dir_csv,
            'readvars': True,
            'expandobjects': True
        }
        return options

    idf = IDF(file_path, epwfile_2015)
    the_options = make_eplaunch_options(idf)
    idf.run(**the_options)






import csv
import pandas as pd
import re

CSV = np.loadtxt('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/03_KPIs/04_Outside Temp/Outside Temp_2015.csv', delimiter=',',skiprows=1)

filename_pattern = re.compile(r'^case-\d{2}\.csv$')
csv_files = [os.path.join(output_dir_csv, f) for f in os.listdir(output_dir_csv) if filename_pattern.match(f)]
print(csv_files)


#define basics
sim_period = len(CSV)
sample_size = len(csv_files)
print('sample size', sample_size)

# Create an empty array to store HI and SET results
results = np.zeros((sample_size, sim_period, 2))
print('shape', results.shape)




from pythermalcomfort.models import set_tmp
def calculate_set (tdb, tr, rh):
    return set_tmp(tdb=tdb, tr=tr, v=0.1, rh=rh, met=1.2, clo=0.35)

for i in csv_files:
    with open(i, 'r') as csvfile:
        #next(csvfile)
        reader = csv.DictReader(csvfile)
        data = pd.read_csv(str(i))
        tdb = data.iloc[:, 2]
        rh = data.iloc[:, 4]
        tr = data.iloc[:, 1]
        print(tdb)
        a = csv_files.index(i)
        print(a)
        for j in range(sim_period):
            SET = calculate_set(tdb[j], tr[j], rh[j])
            #print(SET)
            results[a, j, 1] = SET

print(results[0])



#create empty array for results of indicators
indicators = np.zeros((sample_size, 3))


#define HWs
HW1_days = 6
HW2_days = 5
inbetween = 18
preHW1_days = 7
preHW2_days= preHW1_days + HW1_days + inbetween
postHW2_days = 7

HW1_start = preHW1_days * 24
HW1_length_hours = HW1_days * 24
HW1_end = HW1_start + HW1_length_hours

HWperiod_days = int(len(CSV) / 24)
HWperiod_hours = HWperiod_days * 24
HW2_start = HWperiod_hours - ((postHW2_days + HW2_days) * 24)
HW2_length_hours = HW2_days * 24
HW2_end = HWperiod_hours - ((postHW2_days) * 24)

#thresholds
SETcomf=24.12
SETalert=28.12
SETemer=32.12




##recoverability
for i in range(sample_size):
    for j in range (sim_period):

        HW1_period_SET = []
        for a in range(HW1_length_hours):
            HW1_period_SET.append(results[i, HW1_start + a, 1])

        HW2_period_SET = []
        for a in range(HW2_length_hours):
            HW2_period_SET.append(results[i, HW2_start + a, 1])

        max_SET_HW1 = max(HW1_period_SET)
        maxSET_HW1_hour = HW1_period_SET.index(max_SET_HW1)

        recovery_count_HW1 = 0
        for a in HW1_period_SET[maxSET_HW1_hour:]:
            if a < SETcomf:
                break
            recovery_count_HW1 += 1
        #print (recovery_count_HW1)

        max_SET_HW2 = max(HW2_period_SET)
        maxSET_HW2_hour = HW2_period_SET.index(max_SET_HW2)

        recovery_count_HW2 = 0
        for a in HW2_period_SET[maxSET_HW2_hour:]:
            if a < SETcomf:
                break
            recovery_count_HW2 += 1
        #print(recovery_count_HW2)

        recovery_count=recovery_count_HW1+recovery_count_HW2

        if recovery_count == []:
            indicators[i, 0] = 0
        else:
            indicators[i, 0] = recovery_count



#resistance
for i in range(sample_size):
    resistance_HW1_temp = []

    for j in range(sim_period):
        resistance_HW1_temp.append(results[i, HW1_start+12, 1])

    resistance_HW2_temp = []
    for j in range(sim_period):
        resistance_HW2_temp.append(results[i, HW2_start+12, 1])

    resistance_HW1 = resistance_HW1_temp[0]-SETcomf
    resistance_HW2 = resistance_HW2_temp[0]-SETcomf

    resistance = resistance_HW1 + resistance_HW2

    indicators[i, 1] = resistance


#robustness
for i in range (sample_size):
    for j in range (sim_period):

        HW_period_SET = []
        for a in range(HWperiod_hours):
            HW_period_SET.append(results[i, a, 1])

        y_above_set_alert = []
        for a in range (HWperiod_hours):
            if HW_period_SET[a] >= SETcomf:
                y_above_set_alert.append(HW_period_SET[a])

        robustness = np.trapz(y_above_set_alert, dx=1)

        indicators[i, 2] = robustness



print(indicators)


rec = indicators[:, 0]
res = indicators[:, 1]
rob = indicators[:, 2]


csv_patch_future_index = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/09_P5/01_Design/02_Index calculation/03_Results/indicator_results_2015.csv'
pd.DataFrame(indicators).to_csv(csv_patch_future_index, index=False, header=False)