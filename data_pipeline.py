"""
data_pipeline.py — UN Population Data Pipeline

This module handles the extraction, transformation, and loading of raw 
UN World Population Prospects 2024 data into memory. It filters the dataset 
for the dashboard's requirements.
"""

import pandas as pd

# File path for the raw UN data
RAW_DATA_PATH = "data/WPP2024_Demographic_Indicators_Medium.csv"

# Relevant columns required for the dashboard visualizations
COLUMNS_TO_KEEP = [
    "Location", "ISO3_code", "Time",
    "TPopulation1July", "TPopulationMale1July", "TPopulationFemale1July",
    "Deaths", "DeathsMale", "DeathsFemale",
    "LEx", "LExMale", "LExFemale",
    "LE15", "LE15Male", "LE15Female",
    "LE65", "LE65Male", "LE65Female",
    "LE80", "LE80Male", "LE80Female",
    "PopGrowthRate", "MedianAgePop", "TFR", "CNMR"
]

# Historical timeframe boundaries (inclusive)
YEAR_MIN, YEAR_MAX = 1950, 2023


def load_and_clean_data() -> pd.DataFrame:
    """
    Loads raw UN demographic data and cleans it in-memory.

    Returns:
        pd.DataFrame: The cleaned and filtered dataset ready for Dash.
    """
    print(f"Loading raw UN data from '{RAW_DATA_PATH}'...")
    df = pd.read_csv(RAW_DATA_PATH, usecols=COLUMNS_TO_KEEP, low_memory=False)

    print("Cleaning data and filtering years...")
    # Keep only rows with valid 3-character ISO3 codes (removes aggregates/regions)
    df = df[df["ISO3_code"].notna() & (df["ISO3_code"].astype(str).str.strip().str.len() == 3)]
    
    # Filter dataset down to the specified historical timeframe
    df = df[(df["Time"] >= YEAR_MIN) & (df["Time"] <= YEAR_MAX)]

    # Convert metrics reported in thousands to absolute numbers
    abs_cols = [
        "TPopulation1July", "TPopulationMale1July", "TPopulationFemale1July", 
        "Deaths", "DeathsMale", "DeathsFemale"
    ]
    for col in abs_cols:
        df[col] = df[col] * 1_000

    # Rename base demographic identifiers for UI and code consistency
    df = df.rename(columns={
        "Location": "Country", 
        "ISO3_code": "ISO3", 
        "Time": "Year"
    })

    print("Data Pipeline finished successfully!")
    
    return df