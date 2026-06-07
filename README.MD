# Global Demographic Explorer

**Team Members:** Apichan Mahenthrarasa, Mehmet Halit Barut

---

## 1. Project Description
This project is an interactive, standalone web dashboard built with Python, Plotly Dash, and Pandas. It enables exploration of the United Nations World Population Prospects (1950–2023) through a single unified interface. The app uses a custom in-memory ETL pipeline to process the raw CSV dynamically. The UI follows Ben Shneiderman's Information Seeking Mantra: "Overview first, zoom and filter, then details-on-demand."

## 2. Implemented Visualization Techniques
- **Interactive Choropleth Map:** Global spatial overview with tooltips and adaptive scaling. For extreme absolute values (e.g., total population) we apply Log10 scaling; for other indicators we use outlier-clamping (top/bottom 1–2%) and a high-contrast color scale to preserve visual discrimination.
- **Linked Historical Line Chart:** Clicking a country polygon triggers a responsive layout change from full-map to a 65%/35% split and displays a historical trend line for the selected nation.
- **Synchronized Temporal Animation:** A timeline slider with a playback control animates the map through years. A vertical time marker in the line chart synchronizes with the active map year.
- **Dynamic UI Filtering:** Cascading dropdowns disable or grey out incompatible options automatically for example, when an indicator does not support stratification by Sex or Age.

## 3. Usage & Installation

### Installation
We provide multiple setup options. We recommend using the `requirements.txt` to replicate the evaluation environment.

Option A — Standard (Recommended):
```bash
pip install -r requirements.txt
```

Option B — Modern package managers (alternative):
If you prefer a fast resolver and the repo contains a `pyproject.toml`, you can use modern tools (e.g., `uv`) or install the package in editable mode:
```bash
# Using uv (ultra-fast resolver):
uv sync

# Or install via pip from pyproject.toml:
pip install .
```

### Running the Application
Start the local server after dependencies are installed:
```bash
python app.py
```
Open your browser (Chrome or Firefox recommended) and navigate to `http://127.0.0.1:8050/`.

### User Interaction Flow
- **Filter:** Use the top control panel to choose an Indicator (e.g., "Life Expectancy"), select "Sex" (Both/Female/Male), and pick an Age Group (At Birth/15/65/80).
- **Playback:** Animate the map using the bottom slider or the "Play" button (1950 → 2023).
- **Zoom & Details:** Hover to view precise values in tooltips. Click a country to open the line chart on the right.
- **Reset:** Close the line chart via the ✕ button to return to the full-screen map.

## 4. Screenshots


## 5. Data & Sources
- **Data Source:** United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition.

  URL: [https://population.un.org/wpp/Download/Standard/CSV/](https://population.un.org/wpp/downloads?folder=Standard%20Projections&group=CSV%20format)

  (Bundled file: [data/WPP2024_Demographic_Indicators_Medium.csv](data/WPP2024_Demographic_Indicators_Medium.csv))

- **Libraries & Tools:**
  - Plotly Dash (UI & callbacks): https://dash.plotly.com/
  - Dash Bootstrap Components (layout & styling): https://dash-bootstrap-components.opensource.faculty.ai/
  - Pandas (data processing): https://pandas.pydata.org/
  - Plotly Express (map & chart generation): https://plotly.com/python/plotly-express/

---
