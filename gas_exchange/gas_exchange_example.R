library(readxl)
library(plantecophys)
library(ggplot2)
library(dplyr)

###########################################################################
#Designed for excel sheets directly exported from LI-6800
#excel sheet need to be saved as values only, as read_excel will evaluate formulas as zero

#Documentation:
#https://www.rdocumentation.org/packages/plantecophys/versions/1.4-6/topics/fitaci
#https://remkoduursma.github.io/plantecophys//index.html

setwd("C:/Users/sango/Documents/McGill/biomass_resources/gas_exchange")
sample <- as.data.frame(read_excel("gas_exchange_sample_dataset.xlsx", skip = 16))
sample <- sample[-1, ]

PPFD <- 200
###########################################################################

#cleans data 
clean_data <- function(df) {
  # Rename columns for consistency
  colnames(df)[colnames(df) == "A"] <- "ALEAF"  # Net Photosynthesis (Pn)
  colnames(df)[colnames(df) == "elapsed"] <- "Time"

  # Ensure Time is in minutes
  if ("Time" %in% colnames(df)) {
    df$Time <- as.numeric(df$Time) / 60  
  }
  
  if ("ALEAF" %in% colnames(df)) {
    df$ALEAF <- as.numeric(df$ALEAF)
  }
  if ("Ci" %in% colnames(df)) {
    df$Ci <- as.numeric(df$Ci)
  }
  if ("Tleaf" %in% colnames(df)) {
    df$Tleaf <- as.numeric(df$Tleaf)
  }
  
  # Ensure PPFD exists and fill with default value if missing
  if (!"PARi" %in% colnames(df)) {
    df$PARi <- PPFD  # Assign a default value if PPFD is missing
  }
  
  # Clean data (filter valid rows and ensure necessary columns exist)
  df_clean <- df %>%
    filter(
      !is.na(ALEAF), !is.na(E), !is.na(gsw),
      ALEAF > 0, Ci > 50
    )
  
  return(df_clean)
}

#plotting function
plot_variable <- function(df, x_var, y_var, plot_title, y_label, x_label = NULL) {
  if (is.null(x_label)) x_label <- x_var
  plot <- ggplot(df, aes(x = .data[[x_var]], y = .data[[y_var]])) +
    geom_point() +
    theme_minimal() +
    labs(
      title = plot_title,
      x = x_label,
      y = y_label
    ) +
    scale_y_continuous(breaks = scales::pretty_breaks(n = 6), labels = scales::number_format(accuracy = 0.1)) +
    scale_x_continuous(breaks = scales::pretty_breaks(n = 6)) +  
    theme(legend.position = "bottom")
  print(plot) 
}


cleaned_sample <- clean_data(sample)
fitaci_data <- cleaned_sample %>%
  select(ALEAF, Tleaf, Ci, PARi) %>%
  rename(
    Photo = ALEAF
  )

plot_variable(cleaned_sample, "Time" ,"ALEAF", "Net Photosynthesis Over Time", "ALEAF (umol m-2 s-1)")
plot_variable(cleaned_sample,"Ci","ALEAF", "ALEAF vs Ci", "ALEAF (umol m-2 s-1)")


#fit will fail if data is low quality; refer to documentation for further adjustment
#of fitting parameters
#fit <- fitaci(fitaci_data, fitmethod = 'bilinear')



