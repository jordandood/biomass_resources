# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 10:34:43 2024

@author: sango
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

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
#change these parameters
data_path = r'C:\Users\sango\Documents\McGill\Experimental Work\Data Collection\T6\Environmental_Trace_T6\T6_80.csv'
reference_date = pd.Timestamp('2025-01-14 00:00:00')
##############################################################

data = pd.read_csv(data_path,skiprows=4)
data['Datetime'] = reference_date + pd.to_timedelta(data['Day'].astype(int) - 1, unit='D') + pd.to_timedelta(data['H:M'] + ':00')
time = data['Datetime']    

data['Temp(C)'] = pd.to_numeric(data['Temp(C)'], errors='coerce')
data['Humid(%rH)'] = pd.to_numeric(data['Humid(%rH)'], errors='coerce')
data['CO2(PPM)'] = pd.to_numeric(data['CO2(PPM)'], errors='coerce')

temp = moving_average(data['Temp(C)'])
humidity = moving_average(data['Humid(%rH)'])
CO2 = moving_average(data['CO2(PPM)'])

#plotting 
plt.plot(time, moving_average(humidity))
plt.xlabel('Time')
plt.ylabel('Humidity (RH)')
plt.title('Humidity vs Time - T6')
plt.xticks([])
plt.show()

plt.plot(time, moving_average(CO2))
plt.xlabel('Time')
plt.ylabel('CO2 (ppm)')
plt.title('CO2 vs Time - T6')
plt.xticks([])
plt.show()

plt.plot(time, moving_average(temp))
plt.xlabel('Time')
plt.ylabel('Temperature (degC)')
plt.title('Temperature vs Time - T6')
plt.xticks([])
plt.show()