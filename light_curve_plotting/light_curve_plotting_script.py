#plotting and ratio calculation of a given lighting spectra
#Need to resave the output file from the spectroradiometer as an .xlsx in order to properly read it

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

##############################################################
# import and read excel
file_path = r'C:\Users\sango\Github\biomass_resources\light_curve_plotting\sample_spectra.xlsx'

# Specify which columns correspond to intensity and spectral distribution
# Column 0 is for wavelength, so do not specify it here
intensity_columns = [1,2,3]  
spd_columns = [4,5,6]        

#titles for plotting in the same order as the column headers in the excel file
titles = ["Wide Amber + FR", "White Light + FR", "White Light"]

# define wavelength ranges. Can adjust as needed, but by default set to include ultraviolet and far-red (300-799.5 nm)
PAR = [300,799.5]
UV = [300,399]
B = [400,499]
G = [500,579]
Amber = [580,619]
R = [620,699]
FR = [700,799.5]
##############################################################

df_int = pd.read_excel(file_path, usecols=[0] + intensity_columns)
df_spd = pd.read_excel(file_path, usecols=[0] + spd_columns)

wavelength_ranges = {
    "PAR": PAR,
    "UV": UV,
    "B": B,
    "G": G,
    "Amber": Amber,
    "R": R,
    "FR": FR
}

# Normalize the data to a range of 0 to 1 (using SPD data)
df_normalize = df_spd.copy()
df_normalize.iloc[:, 1:] = (df_spd.iloc[:, 1:] - df_spd.iloc[:, 1:].min()) / (df_spd.iloc[:, 1:].max() - df_spd.iloc[:, 1:].min())

def calculate_percentage_and_ratios(df, wavelength_ranges):
    totals = {}
    percentages = {}
    
    # Function to apply trapezoidal rule for integration
    def trapz_integrate(x, y):
        return np.trapz(y, x)
    
    total_integrals = {}
    for col in df.columns[1:]:
        total_integrals[col] = trapz_integrate(df.iloc[:, 0], df[col])
    
    total_sum = pd.Series(total_integrals)

    for name, wavelength_range in wavelength_ranges.items():
        # Mask for the wavelength range
        mask = (df.iloc[:, 0] >= wavelength_range[0]) & (df.iloc[:, 0] <= wavelength_range[1])
        
        # Calculate integrals for each column in the range using trapz
        range_integrals = {}
        for col in df.columns[1:]:
            filtered_df = df[mask]
            range_integrals[col] = trapz_integrate(filtered_df.iloc[:, 0], filtered_df[col])
        
        range_sum = pd.Series(range_integrals)
        
        totals[f"{name} Total"] = range_sum

        if name == "PAR":
            percentages[f"{name}%"] = range_sum
        else:
            percentages[f"{name}%"] = (range_sum / total_sum) * 100

    # Calculate ratios
    percentages["R:B Ratio"] = percentages["R%"] / percentages["B%"]
    percentages["R:FR Ratio"] = percentages["R%"] / percentages["FR%"]

    # Convert dictionaries to DataFrames
    totals_df = pd.DataFrame(totals).T
    totals_df.columns = df.columns[1:]  # Set column names to match the data columns

    percentages_df = pd.DataFrame(percentages).T
    percentages_df.columns = df.columns[1:]

    return percentages_df, totals_df

percentages_df, totals_df = calculate_percentage_and_ratios(df_int, wavelength_ranges)

print("Percentages and Ratios:")
print(percentages_df)
print("\nTotal intensity per wavelength range (micromoles per m2 per s):")
print(totals_df)

#plotting of normalized SPD data
plt.figure(figsize=(10, 6))
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 1], color="orange")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Spectral Irradiance")
plt.title(titles[0])
plt.xticks(range(int(df_normalize.iloc[:, 0].min()), int(df_normalize.iloc[:, 0].max()) + 1, 50))  
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 2], color="red")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Spectral Irradiance")
plt.title(titles[1])
plt.xticks(range(int(df_normalize.iloc[:, 0].min()), int(df_normalize.iloc[:, 0].max()) + 1, 50))  
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 3], color="blue", linewidth=2)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Spectral Irradiance")
plt.title(titles[2])
plt.xticks(range(int(df_normalize.iloc[:, 0].min()), int(df_normalize.iloc[:, 0].max()) + 1, 50))  
plt.show()

#plot all three spectra on the same plot
plt.figure(figsize=(10, 6))
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 1], label = "Wide Amber + FR", color="orange")
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 2], label = "White Light + FR", color="red")
plt.plot(df_normalize.iloc[:, 0], df_normalize.iloc[:, 3], label = "White Light", color="blue")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Spectral Irradiance")
plt.title("All Spectra")
plt.xticks(range(int(df_normalize.iloc[:, 0].min()), int(df_normalize.iloc[:, 0].max()) + 1, 50))  
plt.legend()
plt.show()

