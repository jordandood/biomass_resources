# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 13:44:04 2024

@author: sango
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

window_size = 15

#moving average filter
def moving_average(data):
    filter_data = []
    
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        filter_data.append(sum(window) / window_size)
    
    #appending a few dummy points at the end to maintain (x,y) length consistency
    last_window = data[-window_size:]
    dummy_value = sum(last_window) / window_size
    filter_data.extend([dummy_value] * (window_size - 1))  # Append (window_size - 1) dummy points
        
    return filter_data

##############################################################
#You should only need to change these parameters
base_path = r'C:\Users\sango\Documents\McGill\Experimental Work\Data Collection\T5\Environment_Trace_T5'
trial = "T5";

#Date and time that you started your trial
reference_date = pd.Timestamp('2024-11-15 00:00:00')
##############################################################

#define file paths
data_70_path = os.path.join(base_path, f'70_{trial}.csv')
data_80_path = os.path.join(base_path, f'80_{trial}.csv')
data_90_path = os.path.join(base_path, f'90_{trial}.csv')

#80 and 90 data processing
#The HCS-1 controller (80 and 90) exports data differently than the HCS-3 (70), 
#Needs a starting reference date
cols = ['Day','H:M','Temp(C)','Humid(%rH)','CO2(PPM)']
data_80 = pd.read_csv(data_80_path,skiprows=4, usecols = cols, on_bad_lines='warn')
data_90 = pd.read_csv(data_90_path,skiprows=4, usecols = cols, on_bad_lines='warn')

# Ensure 'H:M' is a string and concatenate ':00' to it
data_80['H:M'] = data_80['H:M'].astype(str) + ':00'
data_90['H:M'] = data_90['H:M'].astype(str) + ':00'

# Combine the 'Day' and 'H:M' columns into a single datetime column for 80 and 90 rooms
data_80['Datetime_80'] = reference_date + pd.to_timedelta(data_80['Day'].astype(int) - 1, unit='D') + pd.to_timedelta(data_80['H:M'])
data_90['Datetime_90'] = reference_date + pd.to_timedelta(data_90['Day'].astype(int) - 1, unit='D') + pd.to_timedelta(data_90['H:M'])

time_80 = data_80['Datetime_80']
time_80 = pd.to_datetime(time_80, format='%m/%d/%Y %H:%M')    
time_90 = data_90['Datetime_90']
time_90 = pd.to_datetime(time_90, format='%m/%d/%Y %H:%M')    

#debugging in case some rows are not numeric or N/A
print(data_80.dtypes)
#invalid_rows = data_80[pd.to_numeric(data_90['Temp(C)'], errors='coerce').isna()]
data_80['Temp(C)'] = pd.to_numeric(data_80['Temp(C)'], errors='coerce')

#print(data_90.dtypes)
#invalid_rows = data_90[pd.to_numeric(data_90['CO2(PPM)'], errors='coerce').isna()]
#print(invalid_rows)

temp_80 = moving_average(data_80['Temp(C)'])
humidity_80 = moving_average(data_80['Humid(%rH)'])
CO2_80 = moving_average(data_80['CO2(PPM)'])

temp_90 = moving_average(data_90['Temp(C)'])
humidity_90 = moving_average(data_90['Humid(%rH)'])
CO2_90 = moving_average(data_90['CO2(PPM)'])

#70 room data processing
data_70 = pd.read_csv(data_70_path)
time_70_raw = data_70['Time']
time_70 = pd.to_datetime(time_70_raw)

temperature_70_raw = data_70['Temp(F)']
humidity_70_raw = data_70['Humid(%)']
CO2_70_raw = data_70['CO2(PPM)']

temp_70 = []
humidity_70 = []
CO2_70 = []

for item in temperature_70_raw:
    numbers = item.split()
    values = [float(num.split(':')[1]) for num in numbers]
    values = [value / 10 for value in values]
    values = [(value - 32) * 5 / 9 for value in values]
    average_value = sum(values) / len(values)
    average_value = round(average_value, 2)
    temp_70.append(average_value)
    
for item in humidity_70_raw:
    numbers = item.split()
    values = [float(num.split(':')[1]) for num in numbers]
    values = [value / 10 for value in values]
    average_value = sum(values) / len(values)
    average_value = round(average_value, 2)
    humidity_70.append(average_value)
    
for item in CO2_70_raw:
    numbers = item.split()
    values = [float(num.split(':')[1]) for num in numbers]
    average_value = sum(values) / len(values)
    average_value = round(average_value, 2)
    CO2_70.append(average_value)


days_70 = list(range(1, 30))
days_80 = list(range(1, 30))
days_90 = list(range(1, 30))


#plotting 
plt.plot(time_70, moving_average(humidity_70))
plt.plot(time_80, humidity_80)
plt.plot(time_90, humidity_90)
plt.xlabel('Time')
plt.ylabel('Humidity (RH)')
plt.title(f'Humidity vs Time - {trial}')
plt.legend(['70', '80', '90'])
plt.xticks([])
plt.show()

plt.plot(time_70, moving_average(temp_70))
plt.plot(time_80, temp_80)
plt.plot(time_90, temp_90)
plt.xlabel('Time')
plt.ylabel('Temperature (degC)')
plt.title(f'Temperature vs Time - {trial}')
plt.legend(['70', '80', '90'])
plt.xticks([])
plt.show()

plt.plot(time_70, moving_average(CO2_70))
plt.plot(time_80, CO2_80)
plt.plot(time_90, CO2_90)
plt.xlabel('Time')
plt.ylabel('CO2 (ppm)')
plt.title(f'CO2 vs Time - {trial}')
plt.legend(['70', '80', '90'])
plt.xticks([])
plt.show()