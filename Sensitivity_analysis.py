
import eppy
import statsmodels as stats
from eppy import modeleditor
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs
# import sensitivity analysis python libraries
import SALib.sample.sobol
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami



# import model file and software IDD
# specify here IDD file of your EnergyPLUS software
# select IDF and EPW weather file to analyse 
iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
fname1 = ".idf"
epwfile_2015 = "EPW.epw"

# read the file
IDF.setiddname(iddfile)
idf1 = IDF(fname1)

# call for materials
materials = idf1.idfobjects["MATERIAL"]

# access required variables
#infiltration
infiltration = idf1.idfobjects["ZoneInfiltration:DesignFlowRate"]
#glazing
glazing_object = idf1.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
glazing_u_value = glazing_object.UFactor
glazing_shgc_value = glazing_object.Solar_Heat_Gain_Coefficient


###SOBOL
# set up problem, specify number of variables, names, bounds and distribution ('unif' uniform, 'norm' normal etc.)
problem = {
    'num_vars': 7,
    'names': ['structure_specific_heat', 'interior_finish_specific_heat','exterior_finish_solar_absorptance', 'insulation_thermal_conductivity', 'glazing_u_value', 'glazing_shgc_value', 'infiltration'],
    'bounds': [[400, 1500], #structure_specific_heat
               [400, 1500], #interior_finish_specific_heat
               [0.2, 0.9], #exterior_finish_solar_absorptance
               [0.03, 0.1], #insulation_thermal_conductivity
               [0.6, 1.1], #glazing_u_value
               [0.1, 0.8], #glazing_shgc_value
               [0.0001, 0.0006]], #infiltration
    'dists': ['unif', 'unif', 'unif', 'unif', 'unif', 'unif', 'unif']
}

# Generate samples using Saltelli sampling
param_values = SALib.sample.sobol.sample(problem, 256, calc_second_order=True) #2^x as input for sample size N*(2D+2)
print (param_values.shape)
print (param_values)


#specify output directory
output_dir_idf = '/Output_IDF'
output_dir_csv = '/Output_CSV'


for i in range(param_values.shape[0]):
    # access variables through eppy -> change their properties according to the samples (follow order as in the "problem")
    materials[0].Specific_Heat = param_values[i][0]
    materials[18].Specific_Heat = param_values[i][1]
    materials[17].Solar_Absorptance = param_values[i][2]
    materials[14].Conductivity = param_values[i][3]
    glazing_object.UFactor = param_values[i][4]
    glazing_object.Solar_Heat_Gain_Coefficient = param_values[i][5]
    infiltration[0].Flow_Rate_per_Exterior_Surface_Area = param_values[i][6]

    # save IDF with variable combinations as given from the sample 
    filename = 'test-%04d.idf' % i
    idf1.saveas(output_dir_idf + "/" + filename)
    path = str('/Output_IDF/' + filename)
    output_file = 'test-%04d' % i

    # specify how to launch simulations (important to run in the given simulation period)
    def make_eplaunch_options(idf):
        """Make options for run, so that it runs like EPLaunch on Windows"""
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

    # run simulations
    idf = IDF(path, epwfile_2015)
    the_options = make_eplaunch_options(idf)
    idf.run(**the_options)


    
# calculation of resilience indices (resistance, robustness, recoverability) 
import os
import csv
import pandas as pd
import numpy as np
import re

# access simulation results (CSV directory)
filename_pattern = re.compile(r'^test-\d{4}\.csv$')
csv_files = [os.path.join(output_dir_csv, f) for f in os.listdir(output_dir_csv) if filename_pattern.match(f)]
print(csv_files)


# define basics
# sim_period as length of simulation output (here, 1032 hours)
sim_period = 1032
sample_size = len(csv_files)

# Create an empty array to store SET results
SET_results = np.zeros((sample_size,sim_period))
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
            results[a, j] = SET


# create empty array for results of indicators
indicators = np.zeros((sample_size, 3))

# define given heat wave characteristics (as per heat wave definition and given weather file)
HW1_days = 6
HW2_days = 5
inbetween = 18
preHW1_days = 7
preHW2_days= preHW1_days + HW1_days + inbetween
postHW2_days = 7

HW1_start = preHW1_days * 24
HW1_length_hours = HW1_days * 24
HW1_end = HW1_start + HW1_length_hours

HWperiod_days = sim_period / 24)
HWperiod_hours = HWperiod_days * 24
HW2_start = HWperiod_hours - ((postHW2_days + HW2_days) * 24)
HW2_length_hours = HW2_days * 24
HW2_end = HWperiod_hours - ((postHW2_days) * 24)


# set thermal comfort thresholds
SETcomf = 24.12

#resistance
for i in range(sample_size):
    resistance_HW1_temp = []

    for j in range(sim_period):
        resistance_HW1_temp.append(results[i, HW1_start])

    resistance_HW2_temp = []
    for j in range(sim_period):
        resistance_HW2_temp.append(results[i, HW2_start])

    resistance_HW1 = resistance_HW1_temp[0]-SETcomf
    resistance_HW2 = resistance_HW2_temp[0]-SETcomf

    resistance = resistance_HW1 + resistance_HW2

    indicators[i, 0] = resistance


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

        indicators[i, 1] = robustness


##recoverability
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
            indicators[i, 2] = recovery_count



# save indices to CSV file (not necessary, but helpful)            
print(indicators)
output_file_dir="/SA_output.csv"
np.savetxt(output_file_dir, indicators, delimiter=",")


# SOBOL sensitivity analysis per index 
Y_res = np.zeros((sample_size))
Y_rob = np.zeros((sample_size))
Y_rec = np.zeros((sample_size))
for i in range (sample_size):
    Y_res[i] = (indicators[i, 0])
    Y_rob[i] = (indicators[i, 1])
    Y_rec[i] = (indicators[i, 2])


res = sobol.analyze(problem, Y_res, calc_second_order=True, print_to_console=True)
print(res['S1'])

rob = sobol.analyze(problem, Y_rob, calc_second_order=True, print_to_console=True)
print(rob['S1'])

rec = sobol.analyze(problem, Y_rec, calc_second_order=True, print_to_console=True)
print(rec['S1'])


# save numerical output (S1, S2, ST) to CSV
results = [res, rob, rec]
for i, result in enumerate(results):
    total_result, first_result, second_result = result.to_df()
    dfs=result.to_df()
    for a, df in enumerate(dfs):
        df.to_csv(f"/SA_final_{i,a}.csv", index=True)


















