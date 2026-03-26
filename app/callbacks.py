from dash import Input, Output, State
from app.app_instance import app as dash_app
from app.components.kpi import kpi_card
import os

import plotly.express as px
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation.csv")

df = pd.read_csv(DATA_PATH)

# Normalize column names
df = df.rename(columns={
    "month": "date",
    "inventory_units": "quantity",
    "inventory_value": "value",
    "variation": "flavour"
})

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Drop precomputed value column if present
if "value" in df.columns:
    df = df.drop(columns=["value"])

# Compute value column
df["value"] = df["quantity"] * df["unit_cost"]

#---------------------------------------------------
# CALLBACKS: START OF CALLBACKS
#---------------------------------------------------

# VALUATION OVER TIME CHART 
# ---------------------------------------------------
@dash_app.callback(
        
    Output("valuation-over-time", "figure"),
    [
        Input("sku-dropdown", "value"),
        Input("location-dropdown", "value"),
    ],
)

def update_dashboard(selected_SKUs, selected_Locations):

    if not selected_SKUs:
        selected_SKUs = df["sku"].unique() # if no SKU is selected, include all SKUs

    if not selected_Locations:
        selected_Locations = df["location"].unique() # if no Location is selected, include all Locations
    
    #apply filters
    df_filtered = df[                                          # filtering the dataframe based on selected SKUs and Locations                              
    df["sku"].isin(selected_SKUs) &
    df["location"].isin(selected_Locations)           # logical AND to apply both filters simultaneously
]
    #aggregate for chart    
    agg = (                                             # aggregating the filtered dataframe by date and summing the value column to get total valuation per month
    df_filtered.groupby("date", as_index=False)["value"]
    .sum()
    .sort_values("date")
)
    fig = px.line(  
        agg, x="date", 
        y="value", 
        title="<b>Inventory Valuation Over Time</b>"    
    )
    fig.update_layout(
    title=dict(
        y=0.95,
        x=0.5,
        xanchor="center",
        yanchor="top"
    ),
    margin=dict(t=40)
)
    # Latest month total
    latest_month = df_filtered["date"].max()
    df_latest = df_filtered[df_filtered["date"] == latest_month]
    
    total_val = df_latest["value"].sum()
    
    return fig


# KPI CARD CALLBACK
# ---------------------------------------------------
@dash_app.callback(
    Output("kpi-inventory-value", "children"),
    Output("kpi-total-units", "children"),
    Output("kpi-sku-count", "children"),
    Output("kpi-top-location", "children"),
    Input("sku-dropdown", "value"),
    Input("location-dropdown", "value")
    
)

def update_kpis(selected_skus, selected_locations):

    if not selected_skus:
        selected_skus = df["sku"].unique()

    if not selected_locations:
        selected_locations = df["location"].unique()

    df_filtered = df[
        df["sku"].isin(selected_skus) &
        df["location"].isin(selected_locations)
    ]
    
    latest_month = df_filtered["date"].max()
    df_latest = df_filtered[df_filtered["date"] == latest_month]

    # --- KPI CALCULATIONS ---
    total_value = df_latest["value"].sum()
    total_units =df_latest["quantity"].sum()
    sku_count = df_latest["sku"].nunique()

    top_location = (
        df_filtered.groupby("location")["value"].sum().idxmax()
        if not df_latest.empty else "N/A"
    )

    return (
        f"€{total_value:,.0f}",
        f"{total_units:,.0f}",
        f"{sku_count}",
        top_location,
    )


# MONTHLY SUMMARY TABLE 
# ---------------------------------------------------
@dash_app.callback(
    Output("monthly-summary-table", "data"),
    [
        Input("sku-dropdown", "value"),
        Input("location-dropdown", "value"),
    ]
)
def update_monthly_summary(selected_skus, selected_locations):

    # Normalize empty filters
    if not selected_skus:
        selected_skus = df["sku"].unique()

    if not selected_locations:
        selected_locations = df["location"].unique()

    # Apply filters
    df_filtered = df[
        df["sku"].isin(selected_skus) &
        df["location"].isin(selected_locations)
    ]

    # datetime conversion and month extraction
    df_filtered["date"] = pd.to_datetime(df_filtered["date"])
    df_filtered["month"] = df_filtered["date"].dt.strftime("%Y-%m")
    
    summary = (
        df_filtered.groupby(["month", "location"])
        .agg(
            total_value=("value", "sum"),
            units=("quantity", "sum"),
            sku_count=("sku", "nunique"),
        )
        .reset_index()
        .sort_values(["month", "location"])
    )

    return summary.to_dict("records")


