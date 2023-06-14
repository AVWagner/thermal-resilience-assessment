import SALib.sample.sobol
import eppy
import os
import numpy as np
import statsmodels as stats
from eppy import modeleditor
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs
import eppy


# import model file and software IDD
iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
fname1 = "C:/Users/walin/simulation/unnamed/openstudio/run/in.idf"
epwfile_2015 = "C:/Users/walin/Downloads/01_Weather data/HW Data/Final/BothHWandBetween2015_finalEPW.epw"

# read the file
IDF.setiddname(iddfile)
idf1 = IDF(fname1)

# call for materials
materials = idf1.idfobjects["MATERIAL"]


# brick_exterior
brick_exterior_specific_heat = materials[0].Specific_Heat

# plaster exterior
plaster_exterior_roughness = materials[17].Roughness
plaster_exterior_thermal_absorptance = materials[17].Thermal_Absorptance
plaster_exterior_solar_absorptance = materials[17].Solar_Absorptance

#insulation
insulation_conductivity = materials[14].Conductivity

plaster_interior_solar_absorptance = materials[18].Solar_Absorptance

#infiltration
infiltration = idf1.idfobjects["ZoneInfiltration:DesignFlowRate"]

#glazing
glazing_object = idf1.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
glazing_u_value = glazing_object.UFactor
glazing_shgc_value = glazing_object.Solar_Heat_Gain_Coefficient



# import sensitivity analysis python libraries
import matplotlib.pyplot as plt
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami



###SOBOL
"""
i = 2
print ('test-%02d.csv'%i)
#for float: %.2f
#for string: %s
"""
from scipy.stats import norm

problem = {
    'num_vars': 7,
    'names': ['structure_specific_heat', 'interior_finish_specific_heat','exterior_finish_solar_absorptance', 'insulation_thermal_conductivity', 'glazing_u_value', 'glazing_shgc_value', 'infiltration'],
    'bounds': [[400, 1500], #structure_specific_heat
               [400, 1500], #interior_finish_specific_heat
               #[300, 50], #structure_thickness
               #insulation_thickness
               #interior_finish_plaster
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

# Run simulations for each set of input parameters
output_dir_idf = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_IDF'
output_dir_csv = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_CSV'



print(param_values.shape[0])
for i in range(param_values.shape[0]):
    materials[0].Specific_Heat = param_values[i][0]
    materials[18].Specific_Heat = param_values[i][1]
    materials[17].Solar_Absorptance = param_values[i][2]
    materials[14].Conductivity = param_values[i][3]
    glazing_object.UFactor = param_values[i][4]
    glazing_object.Solar_Heat_Gain_Coefficient = param_values[i][5]
    infiltration[0].Flow_Rate_per_Exterior_Surface_Area = param_values[i][6]

    filename = 'test-%04d.idf' % i
    idf1.saveas(output_dir_idf + "/" + filename)
    path = str('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_IDF/' + filename)
    output_file = 'test-%04d' % i

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

    idf = IDF(path, epwfile_2015)
    the_options = make_eplaunch_options(idf)
    idf.run(**the_options)


import os
import csv
import pandas as pd
import numpy as np
import re

DBT = np.loadtxt('C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/03_KPIs/02_SET/Air temperature_output.csv', delimiter=',',skiprows=1)

output_dir_csv = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_CSV'
filename_pattern = re.compile(r'^test-\d{4}\.csv$')
csv_files = [os.path.join(output_dir_csv, f) for f in os.listdir(output_dir_csv) if filename_pattern.match(f)]
print(csv_files)


#define basics
sim_period=len(DBT)
sample_size=len(csv_files)
print('sample size', sample_size)

# Create an empty array to store HI and SET results
results = np.zeros((sample_size,sim_period, 2))
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
        resistance_HW1_temp.append(results[i, HW1_start, 1])

    resistance_HW2_temp = []
    for j in range(sim_period):
        resistance_HW2_temp.append(results[i, HW2_start, 1])

    resistance_HW1 = resistance_HW1_temp[0]-SETcomf
    resistance_HW2 = resistance_HW2_temp[0]-SETcomf

    resistance = resistance_HW1 + resistance_HW2

    indicators[i, 1] = resistance


    """
    for j in range (sim_period):

        HW1_period_SET = []
        for a in range(HW1_length_hours):
            HW1_period_SET.append(results[i, HW1_start + a, 1])

        HW2_period_SET = []
        for a in range(HW2_length_hours):
            HW2_period_SET.append(results[i, HW2_start + a, 1])

        resistance_count_HW1=0
        for a in HW1_period_SET:
            if a < SETcomf:
                resistance_count_HW1+=1
            else:
                break


        resistance_count_HW2 = 0
        for a in HW1_period_SET:
            if a < SETcomf:
                resistance_count_HW2 += 1
            else:
                break

        resistance_count=resistance_count_HW1+resistance_count_HW2
        #print(resistance_count)

        if resistance_count == []:
            indicators[i, 1] = 0
        else:
            indicators[i, 1] = resistance_count
        """



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
print(indicators.shape)
output_file_dir="C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_output/SA_output.csv"

np.savetxt(output_file_dir, indicators, delimiter=",")




# import sensitivity analysis python libraries
import matplotlib.pyplot as plt
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
import numpy as np
import pandas as pd


Y1 = np.zeros((sample_size))
Y2 = np.zeros((sample_size))
Y3 = np.zeros((sample_size))
for i in range (sample_size):
    Y1[i] = (indicators[i, 0])
    Y2[i] = (indicators[i, 1])
    Y3[i] = (indicators[i, 2])


rec = sobol.analyze(problem, Y1, calc_second_order=True, print_to_console=True)
print(problem)
print(rec['S1'])
"""
print("x1-x2:", rec['ST'][0, 1])
print("x1-x3:", rec['ST'][0, 2])
print("x2-x3:", rec['ST'][1, 2])
"""
res = sobol.analyze(problem, Y2, calc_second_order=True, print_to_console=True)
print(res['S1'])
rob = sobol.analyze(problem, Y3, calc_second_order=True, print_to_console=True)
print(rob['S1'])


"""
rec_data = rec.to_df()
res_data = res.to_df()
rob_data = rob.to_df()
"""

results = [rec, res, rob]
for i, result in enumerate(results):
    total_result, first_result, second_result = result.to_df()
    dfs=result.to_df()
    for a, df in enumerate(dfs):
        df.to_csv(f"C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_output/SA_final_{i,a}.csv", index=True)



"""
import matplotlib.pyplot as plt
#SA_output_file_dir="C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_output/SA_sensitivities.csv"
#Si.to_csv(SA_output_file_dir, index=True)
fig = plt.figure(figsize=(20, 10))
rec.plot()
plt.subplots_adjust(bottom=0.5)
plt.show()
"""















