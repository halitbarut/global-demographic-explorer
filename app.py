"""Global Demographic Explorer -- Dash application entry point."""

import numpy as np
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# IMPORT THE PIPELINE
from data_pipeline import load_and_clean_data

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
# Fetches and cleans data once on application startup
df = load_and_clean_data()

YEAR_MIN = 1950
YEAR_MAX = 2023
SLIDER_MARKS = {yr: str(yr) for yr in range(YEAR_MIN, YEAR_MAX + 1, 10)}

# Initialize the Dash application
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Global Demographic Explorer",
)

# ---------------------------------------------------------------------------
# Helper Functions: Data Mapping and Formatting
# ---------------------------------------------------------------------------
def get_column_name(metric: str, sex: str, age: str) -> str:
    """
    Translates the UI dropdown selections into the exact UN dataset column name.
    """
    sex_suffix = "" if sex == "Both" else sex
    
    if metric == "Population": 
        return f"TPopulation{sex_suffix}1July"
    elif metric == "Deaths": 
        return f"Deaths{sex_suffix}"
    elif metric == "Life Expectancy":
        base = "LEx" if age == "0" else f"LE{age}"
        return f"{base}{sex_suffix}"
    elif metric == "Population Growth Rate": 
        return "PopGrowthRate"
    elif metric == "Median Age": 
        return "MedianAgePop"
    elif metric == "Total Fertility Rate": 
        return "TFR"
    elif metric == "Net Migration Rate": 
        return "CNMR"
    
    return "TPopulation1July"

def get_display_title(metric: str, sex: str, age: str) -> str:
    """
    Generates a clean, readable UI title based on the user's dropdown selections.
    """
    title = metric
    
    if sex != "Both" and metric in ["Population", "Deaths", "Life Expectancy"]:
        title += f" ({sex})"
        
    if metric == "Life Expectancy" and age != "0":
        title += f" at Age {age}"
        
    return title

# ---------------------------------------------------------------------------
# Application Layout
# ---------------------------------------------------------------------------
app.layout = dbc.Container(
    fluid=True, className="px-5 py-4",
    style={"fontFamily": "'Inter', sans-serif", "backgroundColor": "#f8fafc", "minHeight": "100vh"},
    children=[
        html.H1(
            "Global Demographic Explorer", 
            className="text-center mt-2 mb-4", 
            style={"fontWeight": "700", "letterSpacing": "0.5px", "color": "#1e293b"}
        ),
        
        # --- Filters ---
        dbc.Row([
            dbc.Col([
                html.Label("Indicator", style={"fontWeight": "600", "fontSize": "0.85rem", "color": "#64748b"}),
                dcc.Dropdown(id="metric-dropdown", value="Population", clearable=False, options=[
                    {"label": "Total Population", "value": "Population"},
                    {"label": "Total Deaths", "value": "Deaths"},
                    {"label": "Life Expectancy", "value": "Life Expectancy"},
                    {"label": "Population Growth Rate", "value": "Population Growth Rate"},
                    {"label": "Median Age", "value": "Median Age"},
                    {"label": "Total Fertility Rate", "value": "Total Fertility Rate"},
                    {"label": "Net Migration Rate", "value": "Net Migration Rate"},
                ])
            ], width=4),
            
            dbc.Col([
                html.Label("Sex", style={"fontWeight": "600", "fontSize": "0.85rem", "color": "#64748b"}),
                dcc.Dropdown(id="sex-dropdown", value="Both", clearable=False, options=[
                    {"label": "Both Sexes", "value": "Both"},
                    {"label": "Female", "value": "Female"},
                    {"label": "Male", "value": "Male"},
                ])
            ], width=4),
            
            dbc.Col([
                html.Label("Age Group", style={"fontWeight": "600", "fontSize": "0.85rem", "color": "#64748b"}),
                dcc.Dropdown(id="age-dropdown", value="0", clearable=False, options=[
                    {"label": "All Ages / At Birth", "value": "0"},
                    {"label": "Age 15", "value": "15"},
                    {"label": "Age 65", "value": "65"},
                    {"label": "Age 80", "value": "80"},
                ])
            ], width=4),
        ], className="mb-4"),

        # --- Main Content Area ---
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dcc.Graph(id="choropleth-map", style={"height": "520px"}, config={"displayModeBar": False}), 
                    style={"border": "none", "borderRadius": "12px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"}
                ),
                id="map-col", width=12, style={"transition": "width 0.3s ease-in-out"}
            ),
            dbc.Col(
                dbc.Card([
                    dbc.Button("✕", id="close-chart-btn", color="light", style={
                        "position": "absolute", "top": "15px", "right": "15px", "zIndex": 1000, "borderRadius": "50%",
                        "width": "32px", "height": "32px", "padding": "0", "display": "flex", "alignItems": "center", "justifyContent": "center", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)", "fontWeight": "bold"
                    }),
                    dcc.Graph(id="line-chart", style={"height": "520px"}, config={"displayModeBar": False})
                ], style={"border": "none", "borderRadius": "12px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)", "position": "relative"}),
                id="chart-col", width=4, style={"display": "none"}
            ),
        ], className="g-3 mb-2"),

        # --- Footer & Timeline ---
        dbc.Row(dbc.Col(html.Div([
            dbc.Button("Play", id="play-pause-btn", color="primary", size="sm", className="me-3", style={"width": "80px"}),
            html.Div(dcc.Slider(
                id="year-slider", min=YEAR_MIN, max=YEAR_MAX, step=1, value=YEAR_MIN, 
                marks=SLIDER_MARKS, tooltip={"placement": "bottom", "always_visible": True}
            ), style={"flex": "1"}),
        ], className="d-flex align-items-center")), className="mt-3"),
        
        # Interval component for the timeline playback feature
        dcc.Interval(id="play-interval", interval=500, n_intervals=0, disabled=True),
    ]
)

# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@dash.callback(
    Output("sex-dropdown", "disabled"), 
    Output("age-dropdown", "disabled"),
    Input("metric-dropdown", "value")
)
def manage_dropdown_states(metric: str) -> tuple[bool, bool]:
    """
    Disables the 'Sex' and 'Age' dropdowns dynamically if the selected 
    demographic indicator does not support those stratifications.
    """
    if metric in ["Population", "Deaths"]: 
        return False, True
    elif metric == "Life Expectancy": 
        return False, False
    else: 
        return True, True


@dash.callback(
    Output("map-col", "width"), 
    Output("chart-col", "style"),
    Input("choropleth-map", "clickData"), 
    Input("close-chart-btn", "n_clicks"), 
    prevent_initial_call=True
)
def toggle_layout(click_data: dict | None, close_clicks: int | None) -> tuple[int, dict]:
    """
    Dynamically switches between a full-width map view and a split-screen 
    layout when a country is selected or the close button is clicked.
    """
    triggered_id = dash.ctx.triggered_id
    if triggered_id == "close-chart-btn": 
        return 12, {"display": "none"}
    elif triggered_id == "choropleth-map" and click_data is not None: 
        return 8, {"display": "block"}
    return 12, {"display": "none"}

@dash.callback(
    Output("choropleth-map", "figure"),
    Input("metric-dropdown", "value"), 
    Input("sex-dropdown", "value"), 
    Input("age-dropdown", "value"), 
    Input("year-slider", "value"),
)
def update_choropleth(metric: str, sex: str, age: str, selected_year: int) -> go.Figure:
    """
    Generates and updates the global choropleth map figure based on the 
    user's demographic selections and the current timeline year.
    """
    dff = df[df["Year"] == selected_year].copy()
    col_name = get_column_name(metric, sex, age)
    
    tickvals, ticktext = None, None
    color_scale = "Turbo"
    color_range = None
    
    if metric in ["Population", "Deaths"]:
        dff["_color"] = np.log10(dff[col_name].clip(lower=1))
        target_col = "_color"
        if metric == "Population":
            tickvals, ticktext = [4, 5, 6, 7, 8, 9, 10], ["10K", "100K", "1M", "10M", "100M", "1B", "10B"]
            
    elif metric in ["Net Migration Rate", "Population Growth Rate"]:
        target_col = col_name
        # Wir ignorieren die extremsten 2% Ausreißer für die Farbskala
        v_min = dff[target_col].quantile(0.02)
        v_max = dff[target_col].quantile(0.98)
        
        limit = max(abs(v_min), abs(v_max))
        color_range = [-limit, limit]
        
    else:
        target_col = col_name
        v_min = dff[target_col].quantile(0.01)
        v_max = dff[target_col].quantile(0.99)
        color_range = [v_min, v_max]

    fig = px.choropleth(
        data_frame=dff, locations="ISO3", color=target_col, hover_name="Country",
        hover_data={col_name: True, "_color": False} if metric in ["Population", "Deaths"] else {col_name: True},
        projection="natural earth", 
        color_continuous_scale=color_scale,
        range_color=color_range
    )

    # Base Colorbar Config
    colorbar_config = {
        "title": "",
        "orientation": "h",
        "yanchor": "bottom", "y": 0.02,
        "xanchor": "center", "x": 0.5,
        "thickness": 12,
        "len": 0.6
    }
    
    if tickvals and ticktext:
        colorbar_config["tickvals"] = tickvals
        colorbar_config["ticktext"] = ticktext

    fig.update_layout(
        font_family="Inter", margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=colorbar_config, paper_bgcolor="rgba(0,0,0,0)", geo_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_geos(
        showframe=False, showcoastlines=True, coastlinecolor="#cccccc", 
        showland=True, landcolor="#f0f0f0", showocean=True, oceancolor="#fafafa", showlakes=False
    )
    
    return fig


@dash.callback(
    Output("line-chart", "figure"),
    Input("choropleth-map", "clickData"), 
    Input("metric-dropdown", "value"), 
    Input("sex-dropdown", "value"), 
    Input("age-dropdown", "value"), 
    Input("year-slider", "value"),
)
def update_line_chart(click_data: dict | None, metric: str, sex: str, age: str, selected_year: int) -> go.Figure:
    """
    Generates a historical trend line chart for the specifically selected country.
    """
    if click_data is None: 
        return go.Figure()

    iso3 = click_data["points"][0]["location"]
    dff = df[df["ISO3"] == iso3].sort_values("Year")
    country_name = str(dff["Country"].iloc[0])
    
    col_name = get_column_name(metric, sex, age)
    display_title = get_display_title(metric, sex, age)

    fig = px.line(
        data_frame=dff, x="Year", y=col_name, title=None, 
        labels={col_name: display_title, "Year": "Year"}
    )
    
    fig.add_vline(
        x=selected_year, line_dash="dash", line_color="#aaaaaa", line_width=1, 
        annotation_text=str(selected_year), annotation_position="top", 
        annotation_font_size=10, annotation_font_color="#888888"
    )
    
    fig.update_layout(
        font_family="Inter", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin={"r": 15, "t": 45, "l": 15, "b": 15}, yaxis_title=display_title, 
        xaxis=dict(gridcolor="#eeeeee"), yaxis=dict(gridcolor="#eeeeee")
    )
    
    return fig


@dash.callback(
    Output("play-interval", "disabled"), 
    Output("play-pause-btn", "children"), 
    Input("play-pause-btn", "n_clicks"), 
    State("play-interval", "disabled"), 
    prevent_initial_call=True
)
def toggle_play_pause(n_clicks: int | None, currently_disabled: bool) -> tuple[bool, str]:
    """
    Toggles the playback timer interval and updates the button text between Play and Pause.
    """
    return (False, "Pause") if currently_disabled else (True, "Play")


@dash.callback(
    Output("year-slider", "value"), 
    Input("play-interval", "n_intervals"), 
    State("year-slider", "value"), 
    prevent_initial_call=True
)
def advance_year(n_intervals: int | None, current_year: int) -> int:
    """
    Increments the timeline slider by one year upon each interval trigger, 
    looping back to the minimum year once the maximum is reached.
    """
    return YEAR_MIN if current_year >= YEAR_MAX else current_year + 1

if __name__ == "__main__":
    app.run(debug=True)