import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

##############################################################
#Specify if HCS-1 is being used, otherwise rewrite False if HCS-3 is being used
HCS_1 = False

#Specify file path of csv file
data_path = r'C:\Users\sango\Github\biomass_resources\HCS_Plotting\HCS_3_Sample.csv'

#Date and time that you started your trial
reference_date = pd.Timestamp('2025-01-14 00:00:00')
##############################################################

#moving average filter
window_size = 15
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

if HCS_1:
    cols = ['Day','H:M','Temp(C)','Humid(%rH)','CO2(PPM)']
    data = pd.read_csv(data_path,skiprows=4, usecols = cols, on_bad_lines='warn')
    
    data['H:M'] = data['H:M'].astype(str) + ':00'
    
    data['Datetime'] = reference_date + pd.to_timedelta(data['Day'].astype(int) - 1, unit='D') + pd.to_timedelta(data['H:M'])

    #convert data to numeric values
    data['Temp(C)'] = pd.to_numeric(data['Temp(C)'], errors='coerce')
    data['Humid(%rH)'] = pd.to_numeric(data['Humid(%rH)'], errors='coerce')
    data['CO2(PPM)'] = pd.to_numeric(data['CO2(PPM)'], errors='coerce')

    # Drop rows with any non-numeric values (NaN) after conversion
    original_count = len(data)
    data = data.dropna(subset=['Temp(C)', 'Humid(%rH)', 'CO2(PPM)'])
    dropped_count = original_count - len(data)

    if dropped_count > 0:
        print(f"Warning: Dropped {dropped_count} rows containing non-numeric values.")

    #apply moving average filter
    temp = moving_average(data['Temp(C)'])
    humidity = moving_average(data['Humid(%rH)'])
    CO2 = moving_average(data['CO2(PPM)'])
    time = data['Datetime']
else:
    data = pd.read_csv(data_path, on_bad_lines='warn')

    time_raw = data['Time']
    time = pd.to_datetime(time_raw)
    temperature_raw = data['Temp(F)']
    humidity_raw = data['Humid(%)']
    CO2_raw = data['CO2(PPM)']

    temp = []
    humidity = []
    CO2 = []
    error_count = 0

    for item in temperature_raw:
        try:
            numbers = item.split()
            values = [float(num.split(':')[1]) for num in numbers]
            values = [value / 10 for value in values]
            values = [(value - 32) * 5 / 9 for value in values]
            average_value = sum(values) / len(values)
            average_value = round(average_value, 2)
            temp.append(average_value)
        except (ValueError, IndexError, ZeroDivisionError):
            error_count += 1
            # Skip this row by appending None, will be removed later
            temp.append(None)
    
    for item in humidity_raw:
        try:
            numbers = item.split()
            values = [float(num.split(':')[1]) for num in numbers]
            values = [value / 10 for value in values]
            average_value = sum(values) / len(values)
            average_value = round(average_value, 2)
            humidity.append(average_value)
        except (ValueError, IndexError, ZeroDivisionError):
            error_count += 1
            humidity.append(None)
        
    for item in CO2_raw:
        try:
            numbers = item.split()
            values = [float(num.split(':')[1]) for num in numbers]
            average_value = sum(values) / len(values)
            average_value = round(average_value, 2)
            CO2.append(average_value)
        except (ValueError, IndexError, ZeroDivisionError):
            error_count += 1
            CO2.append(None)
    
    processed_data = pd.DataFrame({
        'Time': time,
        'Temperature': temp,
        'Humidity': humidity,
        'CO2': CO2
    })
    
    # Drop rows with any missing values
    original_count = len(processed_data)
    processed_data = processed_data.dropna()
    dropped_count = original_count - len(processed_data)
    
    if dropped_count > 0:
        print(f"Warning: Dropped {dropped_count} rows containing errors during processing.")
    
    # Extract the cleaned data
    time = processed_data['Time']
    temp = processed_data['Temperature'].tolist()
    humidity = processed_data['Humidity'].tolist()
    CO2 = processed_data['CO2'].tolist()


#plotting 
plt.plot(time, moving_average(humidity))
plt.xlabel('Time')
plt.ylabel('Humidity (RH)')
plt.title('Humidity vs Time')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks([])
plt.show()

plt.plot(time, moving_average(CO2))
plt.xlabel('Time')
plt.ylabel('CO₂ (ppm)')
plt.title('CO₂ vs Time')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks([])
plt.show()

plt.plot(time, moving_average(temp))
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Temperature vs Time')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks([])
plt.show()

#performance statistics
temp_mean = np.mean(temp)
temp_std = np.std(temp)
humidity_mean = np.mean(humidity)
humidity_std = np.std(humidity)
co2_mean = np.mean(CO2)
co2_std = np.std(CO2)

stats_table = [
    ["Parameter", "Mean", "Standard Deviation"],
    ["Temperature (°C)", f"{temp_mean:.2f}", f"{temp_std:.2f}"],
    ["Humidity (%RH)", f"{humidity_mean:.2f}", f"{humidity_std:.2f}"],
    ["CO₂ (ppm)", f"{co2_mean:.2f}", f"{co2_std:.2f}"]
]

print("\nEnvironmental Conditions Summary:")
print(tabulate(stats_table, headers="firstrow", tablefmt="grid"))