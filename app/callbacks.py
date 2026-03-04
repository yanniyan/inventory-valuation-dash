from dash import Input, Output
import plotly.express as px
import pandas as pd
from app import app
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation.csv")

df = pd.read_csv(DATA_PATH)

@app.callback(
    [
        Output("valuation-over-time", "figure"),
        Output("total-valuation", "children"),
    ],
    [
        Input("SKU-filter", "value"),
        Input("Location-filter", "value"),
    ],
)
def update_dashboard(selected_SKUs, selected_Locations):
    dff = df.copy()

    if selected_SKUs:
        dff = dff[dff["sku"].isin(selected_SKUs)]
    if selected_Locations:
        dff = dff[dff["location"].isin(selected_Locations)]
        
    agg = (
    dff.groupby("month", as_index=False)["inventory_value"]
    .sum()
    .sort_values("month")
)

    fig = px.line(agg, x="month", y="inventory_value", title="Inventory Valuation Over Time")

    latest_month = dff["month"].max()
    total_val = dff[dff["month"] == latest_month]["inventory_value"].sum()
    total_text = f"€{total_val:,.0f}"

    return fig, total_text
