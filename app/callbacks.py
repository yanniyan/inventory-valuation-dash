from dash import Input, Output
from app.app_instance import app as dash_app
import os
import plotly.express as px
import pandas as pd

# Import helpers from utils
from app.utils import (
    normalize_filters,
    filter_df,
    split_latest_previous,
    compute_inventory_kpis,
    compute_turnover,
    compute_top_location,
    aggregate_valuation,
    prepare_monthly_summary
)

# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation.csv")

df = pd.read_csv(DATA_PATH)

df = df.rename(columns={
    "month": "date",
    "inventory_units": "quantity",
    "inventory_value": "value",
    "variation": "flavour"
})

df["date"] = pd.to_datetime(df["date"])

if "value" in df.columns:
    df = df.drop(columns=["value"])

df["value"] = df["quantity"] * df["unit_cost"]


# ---------------------------------------------------
# CALLBACKS
# ---------------------------------------------------

# --- VALUATION OVER TIME CHART ---
@dash_app.callback(
    Output("valuation-over-time", "figure"),
    Input("sku-dropdown", "value"),
    Input("location-dropdown", "value"),
)
def update_dashboard(selected_skus, selected_locations):

    # pass df into normalize_filters
    selected_skus, selected_locations = normalize_filters(
        selected_skus, selected_locations, df
    )

    df_filtered = filter_df(df, selected_skus, selected_locations)
    agg = aggregate_valuation(df_filtered)

    fig = px.line(
        agg,
        x="date",
        y="value",
        title="<b>Inventory Valuation Over Time</b>"
    )

    fig.update_layout(
        title=dict(y=0.95, x=0.5, xanchor="center", yanchor="top"),
        margin=dict(t=40)
    )

    return fig


# --- KPI CARDS CALLBACK ---
@dash_app.callback(
    Output("kpi-inventory-value", "children"),
    Output("kpi-total-units", "children"),
    Output("kpi-sku-count", "children"),
    Output("kpi-top-location", "children"),
    Output("kpi-month-change", "children"),
    Output("kpi-turnover", "children"),
    Input("sku-dropdown", "value"),
    Input("location-dropdown", "value"),
    Input("turnover-percent", "n_clicks"),
    Input("turnover-abs", "n_clicks"),
)
def update_kpis(selected_skus, selected_locations, percent_clicks, abs_clicks):

    percent_clicks = percent_clicks or 0
    abs_clicks = abs_clicks or 0
    mode = "percent" if percent_clicks >= abs_clicks else "absolute"

    # FIXED: pass df into normalize_filters
    selected_skus, selected_locations = normalize_filters(
        selected_skus, selected_locations, df
    )

    df_filtered = filter_df(df, selected_skus, selected_locations)
    df_latest, df_previous = split_latest_previous(df_filtered)

    total_value, total_units, sku_count, change_text = compute_inventory_kpis(
        df_latest, df_previous
    )

    top_location = compute_top_location(df_filtered)
    turnover_display = compute_turnover(df_latest, df_previous, mode)

    return (
        f"€{total_value:,.0f}",
        f"{total_units:,.0f}",
        f"{sku_count}",
        top_location,
        change_text,
        turnover_display,
    )


# --- MONTHLY SUMMARY TABLE ---
@dash_app.callback(
    Output("monthly-summary-table", "data"),
    Input("sku-dropdown", "value"),
    Input("location-dropdown", "value"),
)
def update_monthly_summary(selected_skus, selected_locations):

    # FIXED: pass df into normalize_filters
    selected_skus, selected_locations = normalize_filters(
        selected_skus, selected_locations, df
    )

    df_filtered = filter_df(df, selected_skus, selected_locations)
    return prepare_monthly_summary(df_filtered)
