"""
data_pipeline.py — UN Population Data Cleaning Pipeline

Reads raw UN World Population Prospects 2024 CSV, filters, transforms,
and exports a cleaned dataset optimized for the Plotly Dash dashboard.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DATA_PATH = "data/WPP2024_Demographic_Indicators_Medium.csv"
CLEANED_DATA_PATH = "data/cleaned_un_data.csv"

# Columns to retain from the raw dataset
COLUMNS_TO_KEEP = [
    "Location",
    "ISO3_code",
    "Time",
    "TPopulation1July",
    "PopGrowthRate",
    "LEx",
    "MedianAgePop",
    "TFR",
    "CNMR",
]

# Human-readable column names for UI consumption
COLUMN_RENAME_MAP = {
    "Location": "Country",
    "ISO3_code": "ISO3",
    "Time": "Year",
    "TPopulation1July": "Population",
    "PopGrowthRate": "Population Growth Rate",
    "LEx": "Life Expectancy",
    "MedianAgePop": "Median Age",
    "TFR": "Total Fertility Rate",
    "CNMR": "Net Migration Rate",
}

# Metric columns (after rename) where NaN should be filled with 0
METRIC_COLUMNS = [
    "Population",
    "Population Growth Rate",
    "Life Expectancy",
    "Median Age",
    "Total Fertility Rate",
    "Net Migration Rate",
]

# Year range filter (inclusive)
YEAR_MIN, YEAR_MAX = 1950, 2023


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_pipeline() -> pd.DataFrame:
    """Execute the full data-cleaning pipeline and return the result."""

    # Step 1: Read only the columns we need (reduces memory footprint)
    print(f"[1/7] Reading raw CSV from '{RAW_DATA_PATH}' ...")
    df = pd.read_csv(RAW_DATA_PATH, usecols=COLUMNS_TO_KEEP, low_memory=False)
    print(f"      Loaded {len(df):,} rows × {df.shape[1]} columns.")

    # Step 2: Filter by country — keep rows with a valid 3-character ISO3 code
    #         This drops aggregate regions, continents, and income groups.
    print("[2/7] Filtering by valid ISO3 country codes ...")
    df = df[df["ISO3_code"].notna() & (df["ISO3_code"].str.len() == 3)]
    print(f"      {len(df):,} rows remaining after country filter.")

    # Step 3: Filter by year — retain only 1950–2023 (historical data)
    print(f"[3/7] Filtering years {YEAR_MIN}–{YEAR_MAX} ...")
    df = df[(df["Time"] >= YEAR_MIN) & (df["Time"] <= YEAR_MAX)]
    print(f"      {len(df):,} rows remaining after year filter.")

    # Step 4: Transform population — raw values are in thousands
    print("[4/7] Converting population from thousands to absolute ...")
    df["TPopulation1July"] = df["TPopulation1July"] * 1_000

    # Step 5: Rename columns for clean UI labels
    print("[5/7] Renaming columns for dashboard UI ...")
    df = df.rename(columns=COLUMN_RENAME_MAP)

    # Step 6: Fill NaN values in metric columns with 0
    print("[6/7] Filling NaN values in metric columns with 0 ...")
    df[METRIC_COLUMNS] = df[METRIC_COLUMNS].fillna(0)

    # Step 7: Export the cleaned dataset
    print(f"[7/7] Export ing cleaned data to '{CLEANED_DATA_PATH}' ...")
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"      Saved {len(df):,} rows × {df.shape[1]} columns.")

    return df


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    result = run_pipeline()
    print(f"\n Pipeline complete. Output: {CLEANED_DATA_PATH}")
    print(result.head())
