from dash import Input, Output
import plotly.express as px
import pandas as pd
from app import app
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation_12m.csv")

df = pd.read_csv(DATA_PATH)
#df = pd.read_csv("../data/inventory_valuation_12m.csv")

@app.callback(
    [
        Output("valuation-over-time", "figure"),
        Output("total-valuation", "children"),
    ],
    [
        Input("sku-filter", "value"),
        Input("location-filter", "value"),
    ],
)
def update_dashboard(selected_skus, selected_locations):
    dff = df.copy()

    if selected_skus:
        dff = dff[dff["sku"].isin(selected_skus)]
    if selected_locations:
        dff = dff[dff["location"].isin(selected_locations)]
        
    agg = (
        dff.groupby("month", as_index=False)["inventory_value"]
        .sum()
        .sort_values("month")
    )

    fig = px.line(agg, x="month", y="inventory_value", title="Inventory Valuation Over Time")
    total_val = dff["inventory_value"].sum()
    total_text = f"€{total_val:,.0f}"

    return fig, total_text
