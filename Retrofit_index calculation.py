import numpy as np
import os
import eppy
from eppy.modeleditor import IDF

# IDD of software
iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
IDF.setiddname(iddfile)

# links to IDFs of base case scenario and retrofit
base_case = "/original.idf"
retrofit = "/retrofit.idf"
IDF_links = []
IDF_links.append(base_case)
IDF_links.append(retrofit)

# specify output directory 
output_dir_csv = "_CSVs"

# path to weather files 
epwfile_2015 = "2015_EPW.epw"
epwfile_2050 = "2050_EPW.epw"
epwfile_2080 = "2080_EPW.epw"

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

    # specify EPW file to use -> iterate through weather files 
    idf = IDF(file_path, epwfile_2015)
    the_options = make_eplaunch_options(idf)
    idf.run(**the_options)


import csv
import pandas as pd
import re


filename_pattern = re.compile(r'^case-\d{2}\.csv$')
csv_files = [os.path.join(output_dir_csv, f) for f in os.listdir(output_dir_csv) if filename_pattern.match(f)]
print(csv_files)


#specify length of simulation period (here 1032 hours)
sim_period = 1032
sample_size = len(csv_files)

# Create an empty array to store SET results
results = np.zeros((sample_size, sim_period))


# SET calculation
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
            results[a, j] = SET


#create empty array for results of indices
indicators = np.zeros((sample_size, 3))


# give specification of heat wave(s) to analyse (as per heat wave definition and in the EPW file)
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

# define comfort thresholds
SETcomf=24.12


## index calculation

#resistance
for i in range(sample_size):
    resistance_HW1_temp = []

    for j in range(sim_period):
        resistance_HW1_temp.append(results[i, HW1_start+12])

    resistance_HW2_temp = []
    for j in range(sim_period):
        resistance_HW2_temp.append(results[i, HW2_start+12])

    resistance_HW1 = resistance_HW1_temp[0]-SETcomf
    resistance_HW2 = resistance_HW2_temp[0]-SETcomf

    resistance = resistance_HW1 + resistance_HW2

    indicators[i, 1] = resistance


#robustness
for i in range (sample_size):
    for j in range (sim_period):

        HW_period_SET = []
        for a in range(HWperiod_hours):
            HW_period_SET.append(results[i, a])

        y_above_set_alert = []
        for a in range (HWperiod_hours):
            if HW_period_SET[a] >= SETcomf:
                y_above_set_alert.append(HW_period_SET[a])

        robustness = np.trapz(y_above_set_alert, dx=1)

        indicators[i, 2] = robustness
       
    
#recoverability
for i in range(sample_size):
    for j in range (sim_period):

        HW1_period_SET = []
        for a in range(HW1_length_hours):
            HW1_period_SET.append(results[i, HW1_start + a])

        HW2_period_SET = []
        for a in range(HW2_length_hours):
            HW2_period_SET.append(results[i, HW2_start + a])

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



res = indicators[:, 0]
rob = indicators[:, 1]
rec = indicators[:, 2]

# give directory of output CSV
csv_2015 = '2015.csv'
csv_2050 = '2050.csv'
csv_2080 = '2080.csv'
# save results to CSV -> change per iteration of weather files 
pd.DataFrame(indicators).to_csv(csv_2015, index=False, header=False)
