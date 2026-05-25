"""Global Demographic Explorer -- Dash application entry point."""

import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

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
# Callbacks
# ---------------------------------------------------------------------------


@dash.callback(
    Output("choropleth-map", "figure"),
    Input("metric-dropdown", "value"),
    Input("year-slider", "value"),
)
def update_choropleth(selected_metric, selected_year):
    """Return a choropleth figure filtered by year and coloured by metric."""
    dff = df[df["Year"] == selected_year]

    fig = px.choropleth(
        data_frame=dff,
        locations="ISO3",
        color=selected_metric,
        hover_name="Country",
        projection="natural earth",
        color_continuous_scale="Viridis",
        labels={selected_metric: selected_metric},
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={"title": selected_metric},
    )

    return fig


@dash.callback(
    Output("line-chart", "figure"),
    Input("choropleth-map", "clickData"),
    Input("metric-dropdown", "value"),
)
def update_line_chart(click_data, selected_metric):
    """Return a line chart for the clicked country, or an empty prompt."""
    if click_data is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Click on a country on the map to see its historical trend.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 14, "color": "grey"},
        )
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor="white",
            margin={"r": 10, "t": 10, "l": 10, "b": 10},
        )
        return fig

    iso3 = click_data["points"][0]["location"]
    dff = df[df["ISO3"] == iso3].sort_values("Year")
    country_name = dff["Country"].iloc[0]

    fig = px.line(
        data_frame=dff,
        x="Year",
        y=selected_metric,
        title=country_name,
        labels={selected_metric: selected_metric, "Year": "Year"},
    )

    fig.update_layout(
        plot_bgcolor="white",
        margin={"r": 10, "t": 40, "l": 10, "b": 10},
    )

    return fig


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
