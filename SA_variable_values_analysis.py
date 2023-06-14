import pandas as pd
import numpy as np
import eppy
from eppy import modeleditor
from eppy.modeleditor import IDF
import csv
import os
import glob

# IDF output of Sensitivity analysis
folder_path = '/Output_IDF'

# IDD file of software
iddfile = "C:/EnergyPlusV22-2-0/Energy+.idd"
sample_size = len(glob.glob(os.path.join(folder_path, '*.idf')))

# create empty array for results of variable values 
var_output = np.zeros((sample_size, 7))

for j, file_path in enumerate(glob.glob(os.path.join(folder_path, '*.idf'))):
    print(file_path)
    IDF.setiddname(iddfile)
    idf = IDF(file_path)

    materials = idf.idfobjects["MATERIAL"]
    interior_finish_specific_heat = materials[18].Specific_Heat
    var_output[j, 0] = interior_finish_specific_heat

    glazing_object = idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
    shgc_glazing = glazing_object.Solar_Heat_Gain_Coefficient
    var_output[j, 1] = shgc_glazing

    infiltration_object = idf.idfobjects["ZoneInfiltration:DesignFlowRate"]
    infiltration = infiltration_object[0].Flow_Rate_per_Exterior_Surface_Area
    var_output[j, 2] = infiltration

    glazing_object = idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0]
    glazing_u_value = glazing_object.UFactor
    var_output[j, 3] = glazing_u_value

    insulation_conductivity = materials[14].Conductivity
    var_output[j, 4] = insulation_conductivity

    brick_exterior_specific_heat = materials[0].Specific_Heat
    var_output[j, 5] = brick_exterior_specific_heat

    exterior_finish_solar_absorptance = materials[17].Solar_Absorptance
    var_output[j, 6] = exterior_finish_solar_absorptance

    if j == sample_size - 1:
        break

# save variable values to CSV 
print(var_output)
csv_path='/SA_param_values.csv'
pd.DataFrame(param_output).to_csv(csv_path)
