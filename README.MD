# Global Demographic Explorer

**Team Members:** Apichan Mahenthrarasa, Mehmet Halit Barut

## Description
This project is an interactive, standalone web dashboard built with Python and Plotly Dash. It allows users to explore the United Nations World Population Prospects (1950-2023) through a unified interface based on Ben Shneiderman's "Overview first, zoom and filter, then details-on-demand" mantra.

## Implemented Visualization Techniques
1. **Interactive Choropleth Map:** Provides a global spatial overview of selected demographic metrics. Includes tooltips on hover and dynamic color scales (Log10 for absolute population, linear for other metrics).
2. **Linked Historical Line Chart:** Implementing "details-on-demand", clicking on any country polygon dynamically generates a historical trend line chart for that specific nation.
3. **Temporal Animation (Playback):** A timeline slider linked to a playback interval automatically animates the historical evolution of the data across the map and chart.

## Brief Description of Usage
1. Open a terminal in the project directory.
2. Install the required libraries using `pip install -r requirements.txt`.
3. Run the application via `python app.py`.
4. Open the provided local host address (e.g., `http://127.0.0.1:8050/`) in your browser (Chrome or Firefox).
5. **Interactions:**
   - Select a demographic metric from the top dropdown.
   - Use the bottom slider or the "Play" button to navigate through the years.
   - Click on any country on the map to reveal its historical trend on the right-side chart.

## Sources
- **Data Source:** United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition. 
  URL: https://population.un.org/wpp/downloads?folder=Standard%20Projections&group=CSV%20format
- **Code & Libraries:** 
  - Plotly Dash Framework: https://dash.plotly.com/
  - Dash Bootstrap Components: https://dash-bootstrap-components.opensource.faculty.ai/