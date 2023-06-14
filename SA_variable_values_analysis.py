import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from eppy import modeleditor
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs
import eppy
import csv

import os
import glob
from eppy.modeleditor import IDF


folder_path = 'C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/07_P3/04_Simulation/04_Sensitivity analysis/Sensitivity Analysis_Python/Output_IDF'

iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
sample_size = len(glob.glob(os.path.join(folder_path, '*.idf')))


param_output = np.zeros((sample_size, 7))

for j, file_path in enumerate(glob.glob(os.path.join(folder_path, '*.idf'))):
    print(file_path)
    IDF.setiddname(iddfile)
    idf = IDF(file_path)

    materials = idf.idfobjects["MATERIAL"]
    interior_finish_specific_heat = materials[18].Specific_Heat
    param_output[j, 0] = interior_finish_specific_heat

    glazing_object = idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
    shgc_glazing = glazing_object.Solar_Heat_Gain_Coefficient
    param_output[j, 1] = shgc_glazing

    infiltration_object = idf.idfobjects["ZoneInfiltration:DesignFlowRate"]
    infiltration = infiltration_object[0].Flow_Rate_per_Exterior_Surface_Area
    param_output[j, 2] = infiltration

    glazing_object = idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
    glazing_u_value = glazing_object.UFactor
    param_output[j, 3] = glazing_u_value

    insulation_conductivity = materials[14].Conductivity
    param_output[j, 4] = insulation_conductivity

    brick_exterior_specific_heat = materials[0].Specific_Heat
    param_output[j, 5] = brick_exterior_specific_heat

    exterior_finish_solar_absorptance = materials[17].Solar_Absorptance
    param_output[j, 6] = exterior_finish_solar_absorptance

    if j == sample_size - 1:
        break


print(param_output)
csv_path='C:/Users/walin/OneDrive - Delft University of Technology/Desktop/Delft/MyTHESIS/08_P4/01_Sensitivity analysis/SA_Plot/SA_param_values.csv'

"""
with open(csv_path, mode='w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(param_output)
"""

pd.DataFrame(param_output).to_csv(csv_path)
