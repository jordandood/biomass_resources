import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from datetime import datetime

##############################################################
#Specify folder containing csv file(s)
folder_path = r'C:\Users\sango\Github\biomass_resources\HCS_Plotting'

#Date and time that you started your trial
reference_date = pd.Timestamp('2024-11-15 04:00:00')
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

#process all csv files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
data_frames = {}
processed_data = {}

for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    
    # Determine file type based on HCS_1 or HCS_3 in the filename
    if "HCS_3" in csv_file:
        # HCS-3 format
        try:
            df = pd.read_csv(file_path)
            data_frames[csv_file] = {
                'data': df,
                'type': 'HCS_3',
            }
            print(f"Loaded HCS-3 format file: {csv_file}")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    elif "HCS_1" in csv_file:
        # HCS-1 format
        cols = ['Day','H:M','Temp(C)','Humid(%rH)','CO2(PPM)']
        try:
            df = pd.read_csv(file_path, skiprows=4, usecols=cols, on_bad_lines='warn')
            data_frames[csv_file] = {
                'data': df,
                'type': 'HCS_1',
            }
            print(f"Loaded HCS-1 format file: {csv_file}")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

#run through dictionary and process data in each file for plotting
for file_name, file_info in data_frames.items():
    df = file_info['data']
    file_type = file_info['type']
    
    try:
        if file_type == 'HCS_1':
            # HCS-1 processing logic
            df['H:M'] = df['H:M'].astype(str) + ':00'
            
            df['Datetime'] = reference_date + pd.to_timedelta(df['Day'].astype(int) - 1, unit='D') + pd.to_timedelta(df['H:M'])
            
            # Convert data to numeric values
            df['Temp(C)'] = pd.to_numeric(df['Temp(C)'], errors='coerce')
            df['Humid(%rH)'] = pd.to_numeric(df['Humid(%rH)'], errors='coerce')
            df['CO2(PPM)'] = pd.to_numeric(df['CO2(PPM)'], errors='coerce')
            
            # Drop rows with any non-numeric values (NaN) after conversion
            original_count = len(df)
            df = df.dropna(subset=['Temp(C)', 'Humid(%rH)', 'CO2(PPM)'])
            dropped_count = original_count - len(df)
            
            if dropped_count > 0:
                print(f"Warning: Dropped {dropped_count} rows containing non-numeric values in {file_name}")
            
            # Apply moving average filter and store processed data
            processed_data[file_name] = {
                'time': df['Datetime'],
                'temp': moving_average(df['Temp(C)']),
                'humidity': moving_average(df['Humid(%rH)']),
                'co2': moving_average(df['CO2(PPM)']),
                'type': file_type,
                'raw_data': df
            }
            
        elif file_type == 'HCS_3':
            # HCS-3 processing logic
            time_raw = df['Time']
            time = pd.to_datetime(time_raw)
            temperature_raw = df['Temp(F)']
            humidity_raw = df['Humid(%)']
            CO2_raw = df['CO2(PPM)']
            
            temp = []
            humidity = []
            CO2 = []
            error_count = 0
            
            # Process temperature
            for item in temperature_raw:
                try:
                    numbers = item.split()
                    values = [float(num.split(':')[1]) for num in numbers]
                    values = [value / 10 for value in values]
                    values = [(value - 32) * 5 / 9 for value in values]  # Convert F to C
                    average_value = sum(values) / len(values)
                    average_value = round(average_value, 2)
                    temp.append(average_value)
                except (ValueError, IndexError, ZeroDivisionError):
                    error_count += 1
                    temp.append(None)
            
            # Process humidity
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
            
            # Process CO2
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
            
            # Create a DataFrame with the processed data
            processed_df = pd.DataFrame({
                'Time': time,
                'Temperature': temp,
                'Humidity': humidity,
                'CO2': CO2
            })
            
            # Drop rows with any missing values
            original_count = len(processed_df)
            processed_df = processed_df.dropna()
            dropped_count = original_count - len(processed_df)
            
            if dropped_count > 0:
                print(f"Warning: Dropped {dropped_count} rows containing errors during processing in {file_name}")
            
            # Store the processed data
            processed_data[file_name] = {
                'time': processed_df['Time'],
                'temp': moving_average(processed_df['Temperature'].tolist()),
                'humidity': moving_average(processed_df['Humidity'].tolist()),
                'co2': moving_average(processed_df['CO2'].tolist()),
                'type': file_type,
                'raw_data': processed_df
            }
    
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Print summary of processed files
print(f"\nSuccessfully processed {len(processed_data)} files:")
for file_name in processed_data.keys():
    print(f"  - {file_name}")


#plot all data together
plt.figure(figsize=(12, 6))
for file_name, data in processed_data.items():
    plt.plot(data['time'], data['temp'], label=file_name)
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Temperature vs Time - All Growth Rooms')
plt.legend(loc='best', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.xticks([])
plt.show()

plt.figure(figsize=(12, 6))
for file_name, data in processed_data.items():
    plt.plot(data['time'], data['humidity'], label=file_name)
plt.xlabel('Time')
plt.ylabel('Humidity (%RH)')
plt.title('Humidity vs Time - All Growth Rooms')
plt.legend(loc='best', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.xticks([])
plt.show()

plt.figure(figsize=(12, 6))
for file_name, data in processed_data.items():
    plt.plot(data['time'], data['co2'], label=file_name)
plt.xlabel('Time')
plt.ylabel('CO₂ (ppm)')
plt.title('CO₂ vs Time - All Growth Rooms')
plt.legend(loc='best', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.xticks([])
plt.show()

# Generate summary statistics for all files
print("\nEnvironmental Conditions Summary:")
stats_table = [["File", "Parameter", "Mean", "Standard Deviation"]]

for file_name, data in processed_data.items():
    # Calculate statistics for each parameter
    temp_mean = np.mean(data['temp'])
    temp_std = np.std(data['temp'])
    humidity_mean = np.mean(data['humidity'])
    humidity_std = np.std(data['humidity'])
    co2_mean = np.mean(data['co2'])
    co2_std = np.std(data['co2'])
    
    # Add to the table
    stats_table.append([file_name, "Temperature (°C)", f"{temp_mean:.2f}", f"{temp_std:.2f}"])
    stats_table.append([file_name, "Humidity (%RH)", f"{humidity_mean:.2f}", f"{humidity_std:.2f}"])
    stats_table.append([file_name, "CO₂ (ppm)", f"{co2_mean:.2f}", f"{co2_std:.2f}"])

# Print the table
print(tabulate(stats_table, headers="firstrow", tablefmt="grid"))