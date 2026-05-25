"""Global Demographic Explorer -- Dash application entry point."""

import numpy as np
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
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
    className="px-5 py-4",
    children=[
        # --- Header ---
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Global Demographic Explorer",
                        className="text-center mt-2 mb-3",
                        style={"fontWeight": "600", "letterSpacing": "0.5px"},
                    ),
                    dbc.Row(
                        dbc.Col(
                            dcc.Dropdown(
                                id="metric-dropdown",
                                options=METRIC_OPTIONS,
                                value="Population",
                                clearable=False,
                                placeholder="Select a metric",
                                style={
                                    "borderRadius": "6px",
                                    "fontSize": "0.95rem",
                                },
                            ),
                            width={"size": 4, "offset": 0},
                        ),
                        justify="center",
                        className="mb-4",
                    ),
                ]
            )
        ),
        # --- Main content: map + line chart ---
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="choropleth-map",
                        style={"height": "520px"},
                    ),
                    width=8,
                    className="pe-2",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="line-chart",
                        style={"height": "520px"},
                    ),
                    width=4,
                    className="ps-2",
                ),
            ],
            className="g-3 mb-2",
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
        # --- Interval timer for playback ---
        dcc.Interval(
            id="play-interval",
            interval=500,
            n_intervals=0,
            disabled=True,
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
    dff = df[df["Year"] == selected_year].copy()

    # Use a log-10 colour scale for Population to prevent outlier washout.
    if selected_metric == "Population":
        dff["_color"] = np.log10(dff["Population"].clip(lower=1))
        color_col = "_color"
        bar_title = "Population (log10)"
    else:
        color_col = selected_metric
        bar_title = selected_metric

    fig = px.choropleth(
        data_frame=dff,
        locations="ISO3",
        color=color_col,
        hover_name="Country",
        hover_data={selected_metric: True, "_color": False}
        if selected_metric == "Population"
        else {selected_metric: True},
        projection="natural earth",
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={"title": bar_title},
        paper_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#cccccc",
        showland=True,
        landcolor="#f0f0f0",
        showocean=True,
        oceancolor="#fafafa",
        showlakes=False,
    )

    return fig


@dash.callback(
    Output("line-chart", "figure"),
    Input("choropleth-map", "clickData"),
    Input("metric-dropdown", "value"),
    Input("year-slider", "value"),
)
def update_line_chart(click_data, selected_metric, selected_year):
    """Return a line chart for the clicked country, or an empty prompt."""
    if click_data is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Click on a country on the map<br>to see its historical trend.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 14, "color": "#999999"},
        )
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin={"r": 20, "t": 20, "l": 20, "b": 20},
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

    # Vertical indicator for the currently selected year on the slider.
    fig.add_vline(
        x=selected_year,
        line_dash="dash",
        line_color="#aaaaaa",
        line_width=1,
        annotation_text=str(selected_year),
        annotation_position="top",
        annotation_font_size=10,
        annotation_font_color="#888888",
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin={"r": 15, "t": 45, "l": 15, "b": 15},
        yaxis_title=selected_metric,
        xaxis=dict(gridcolor="#eeeeee"),
        yaxis=dict(gridcolor="#eeeeee"),
    )

    return fig


@dash.callback(
    Output("play-interval", "disabled"),
    Output("play-pause-btn", "children"),
    Input("play-pause-btn", "n_clicks"),
    State("play-interval", "disabled"),
    prevent_initial_call=True,
)
def toggle_play_pause(n_clicks, currently_disabled):
    """Toggle the interval timer and swap button label between Play/Pause."""
    if currently_disabled:
        return False, "Pause"
    return True, "Play"


@dash.callback(
    Output("year-slider", "value"),
    Input("play-interval", "n_intervals"),
    State("year-slider", "value"),
    prevent_initial_call=True,
)
def advance_year(n_intervals, current_year):
    """Increment the slider by one year, looping back to 1950 after 2023."""
    if current_year >= YEAR_MAX:
        return YEAR_MIN
    return current_year + 1


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
