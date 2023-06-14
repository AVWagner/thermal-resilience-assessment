import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from eppy.modeleditor import IDF

best_indices = np.loadtxt('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_performance_indices.csv', delimiter=',')
param_values = np.loadtxt("C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_param_values.csv", delimiter=',', skiprows=1)
best_av = np.loadtxt('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_Z_average_best.csv', delimiter=',')


#variables and parameter
g_values = []
u_values = []
for row in best_indices:
    for i in row:
        g_values.append(param_values[int(i), 2])
        u_values.append(param_values[int(i), 4])

g_value = np.mean(g_values)
u_value = np.mean(u_values)
print('av g-value', g_value)
print('av u-value', u_value)


iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
IDF.setiddname(iddfile)

base_case = "C:/Users/walin/simulation/unnamed/openstudio/run/in.idf"
list_of_idf_numbers = [best_indices[0, 1], best_indices[0, 2], best_indices[0, 0], best_av]


folder_path = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_IDF'
output_dir_csv = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/04_Final Index calculation/01_Output_CSV'
output_dir_idf = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/04_Final Index calculation/02_Output_IDF'



IDF_links = []
for i in list_of_idf_numbers:
    file_name = 'test-%04d.idf' % i
    file_path_1 = os.path.join(folder_path, file_name)
    IDF_links.append(file_path_1)
IDF_links.append(base_case)
print(IDF_links)



epwfile_2015 = "C:/Users/walin/Downloads/01_Weather data/HW Data/Final/BothHWandBetween2015_finalEPW.epw"
epwfile_2050 = 'C:/Users/walin/Downloads/01_Weather data/HW Data/2050/DEU_MUNICH_HadCM3-A2-2050_finalEPW.epw'
epwfile_2080 = 'C:/Users/walin/Downloads/01_Weather data/HW Data/2080/DEU_MUNICH_HadCM3-A2-2080_finalEPW.epw'


for i, file_path in enumerate(IDF_links):
    print(file_path)
    idf = IDF(file_path)
    filename = 'test-%04d.idf' % i
    output_file = 'test-%04d' % i



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

    materials = idf.idfobjects["MATERIAL"]
    glazing_object = idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
    cooling_setpoint = idf.idfobjects["Schedule:Day:Interval"]
    cooling_setpoint[11].Value_Until_Time_1 = 60
    ventilation = idf.idfobjects["ZoneVentilation:WindandStackOpenArea"]
    for j in range(3):
        ventilation[j].Minimum_Outdoor_Temperature = -100
        ventilation[j].Maximum_Wind_Speed = 5

    materials[0].Specific_Heat = 840


    if i <= 3:
        glazing_object.UFactor = u_value
        glazing_object.Solar_Heat_Gain_Coefficient = g_value
        materials[17].Solar_Absorptance = 0.7

    idf.saveas(output_dir_idf + "/" + filename)

    idf = IDF(output_dir_idf + "/" + filename, epwfile_2080)
    print('file', output_dir_idf + "/" + filename)
    the_options = make_eplaunch_options(idf)
    idf.run(**the_options)


import csv
import pandas as pd
import re

DBT = np.loadtxt('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/03_KPIs/02_SET/Air temperature_output.csv', delimiter=',',skiprows=1)

filename_pattern = re.compile(r'^test-\d{4}\.csv$')
csv_files = [os.path.join(output_dir_csv, f) for f in os.listdir(output_dir_csv) if filename_pattern.match(f)]
print(csv_files)


#define basics
sim_period=len(DBT)
sample_size=len(csv_files)
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
print(results[1])
print(results[2])


csv_path_SET = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/04_Final Index calculation/04_Results/SET_2080.csv'
results_2D = results.transpose((1, 0, 2)).reshape((results.shape[1], -1))
pd.DataFrame(results_2D).to_csv(csv_path_SET, index=False, header=False)


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

HWperiod_days = int(len(DBT) / 24)
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


csv_patch_future_index = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/04_Final Index calculation/04_Results/indicator_results_2080.csv'
pd.DataFrame(indicators).to_csv(csv_patch_future_index, index=False, header=False)


