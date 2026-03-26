from dash import html, dcc
from dash import dash_table
from dash.dash_table.Format import Format, Group
from app.components.kpi import kpi_card

import dash_bootstrap_components as dbc
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation.csv")

df = pd.read_csv(DATA_PATH)

# Normalize column names
df = df.rename(columns={
    "month": "date",
    "inventory_units": "quantity",
    "variation": "flavour"
})

# Drop precomputed value column if present
if "value" in df.columns:
    df = df.drop(columns=["value"])

# Compute value column
df["value"] = df["quantity"] * df["unit_cost"]

# ---------------------------------------------------
# DASHBOARD LAYOUT
# ---------------------------------------------------

layout = dbc.Container(
    [
        html.H4("Inventory Valuation Dashboard"),        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="sku-dropdown",
                        options=[{"label": s, "value": s} for s in sorted(df["sku"].unique())],
                        multi=True,
                        placeholder="Select SKU(s)",
                        style={"height": "32x", "fontSize": "13px", "padding": "0px"}
                    ),
                    md=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="location-dropdown",
                        options=[{"label": l, "value": l} for l in sorted(df["location"].unique())],
                        multi=True,
                        placeholder="Select Location(s)",
                        style={"height": "28px", "fontSize": "13px", "padding": "0px"}
                    ),
                    md=4,
                ),
            ],
            className="mt-0",
        ),

        #html.Div(style={"height": "8px"}),  # Spacer   

        # -------------------------
        # KPI ROW
        # -------------------------
        dbc.Row(
            [
                dbc.Col(kpi_card("kpi-inventory-value", "Current Inventory Value"), md=3),
                dbc.Col(kpi_card("kpi-total-units", "Total Units"), md=3),
                dbc.Col(kpi_card("kpi-sku-count", "SKU Count"), md=3),
                dbc.Col(kpi_card("kpi-top-location", "Top Location"), md=3),
            ],
            className="mt-2",
        ),

        # ---------------------------------------------------
        # VALUATION OVER TIME CHART
        # ---------------------------------------------------
    
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="valuation-over-time"), md=12),
            ],
            className="mt-0",
        ),

    # ---------------------------------------------------
    # Monthly Summary Table
    # ---------------------------------------------------
    # this section adds a new table to the dashboard that shows a monthly summary of inventory valuation, units, and SKU count by location. The table updates based on the same SKU and Location filters as the line chart.        
        
        html.Div(style={"height": "4px"}), 
        html.H4("Monthly Summary"),
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id="monthly-summary-table",
                        columns=[
                            {"name": "Month", "id": "month", "type": "datetime"},
                            {"name": "Location", "id": "location"},
                            {"name": "Total Value", "id": "total_value", "type": "numeric"},
                            {"name": "Units", "id": "units", "type": "numeric"},
                            {"name": "SKUs", "id": "sku_count", "type": "numeric"},
                        ],
                         style_table={
                                    "overflowX": "auto",
                                    "maxHeight": "260px",
                                    "overflowY": "auto",
                                    "border": "1px solid #e1e1e1",
                                },
                        style_cell={
                            "padding": "3px",
                            "fontSize": "12px",
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "400",
                            "padding": "2px",
                            "borderBottom": "1px solid #dcdcdc",
                        },
                        page_size=10,
                        data=[],
                    ),
                    md=6,
                )
            ],
            className="mt-0",
        ),
    ],
    fluid=True,
)

