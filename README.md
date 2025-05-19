Several scripts that may prove helpful for processing data

# HCS_Plotting
Contains scripts for plotting environmental data exported from the HCS-1 and HCS-3 models utilized in the pilot plant growth chambers. Plots temperature (degC), humidity (RH), and CO2 (ppm).

growth_room_plotting.py: Plots data from all three growth chambers at once on the same graph.

![all](HCS_Plotting/all_growth_rooms.png)

single_growth_room_plot.py: Plots data from a single growth chamber.

![single](HCS_Plotting/single_growth_room.png)


# Light Spectral Quality
Plots and calculates lighting ratios from spectral data measured by PS-300 apogee spectroradiometer

light_curve_plotting_script.py: takes in data from an excel and automatically calculates ratios and plots normalized spectra

![all](light_curve_plotting/sample_spectrum.png)


# Gas Exchange
Basic framework and resources for gas exchange analysis using the Farquhar-von Caemmerer-Berry model of photosynthesis. Analyzes a single raw gas exchange file from the LI-6800, but the functions and steps can be easily adapted to suit your particular needs. Note that low quality data will fail to fit, so refer to documentation for more specific adjustments as needed.

https://remkoduursma.github.io/plantecophys/
