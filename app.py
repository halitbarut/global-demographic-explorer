"""Global Demographic Explorer -- Dash application entry point."""

import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
df = pd.read_csv("data/cleaned_un_data.csv")

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
    title="Global Demographic Explorer",
)

# ---------------------------------------------------------------------------
# Metric dropdown options
# ---------------------------------------------------------------------------
METRIC_OPTIONS = [
    {"label": "Population", "value": "Population"},
    {"label": "Population Growth Rate", "value": "Population Growth Rate"},
    {"label": "Life Expectancy", "value": "Life Expectancy"},
    {"label": "Median Age", "value": "Median Age"},
    {"label": "Total Fertility Rate", "value": "Total Fertility Rate"},
    {"label": "Net Migration Rate", "value": "Net Migration Rate"},
]

# ---------------------------------------------------------------------------
# Year slider configuration
# ---------------------------------------------------------------------------
YEAR_MIN = 1950
YEAR_MAX = 2023
SLIDER_MARKS = {yr: str(yr) for yr in range(YEAR_MIN, YEAR_MAX + 1, 10)}

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = dbc.Container(
    fluid=True,
    className="px-4 py-3",
    children=[
        # --- Header ---
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Global Demographic Explorer",
                        className="text-center my-2",
                    ),
                    dbc.Row(
                        dbc.Col(
                            dcc.Dropdown(
                                id="metric-dropdown",
                                options=METRIC_OPTIONS,
                                value="Population",
                                clearable=False,
                                placeholder="Select a metric",
                            ),
                            width=4,
                        ),
                        justify="center",
                        className="mb-3",
                    ),
                ]
            )
        ),
        # --- Main content: map + line chart ---
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="choropleth-map"),
                    width=8,
                ),
                dbc.Col(
                    dcc.Graph(id="line-chart"),
                    width=4,
                ),
            ],
            className="g-3",
        ),
        # --- Footer / Timeline ---
        dbc.Row(
            dbc.Col(
                [
                    html.Div(
                        [
                            dbc.Button(
                                "Play",
                                id="play-pause-btn",
                                color="primary",
                                size="sm",
                                className="me-3",
                            ),
                            html.Div(
                                dcc.Slider(
                                    id="year-slider",
                                    min=YEAR_MIN,
                                    max=YEAR_MAX,
                                    step=1,
                                    value=YEAR_MIN,
                                    marks=SLIDER_MARKS,
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                                style={"flex": "1"},
                            ),
                        ],
                        className="d-flex align-items-center",
                    )
                ]
            ),
            className="mt-3",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
