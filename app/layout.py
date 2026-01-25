from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_valuation_12m.csv")

df = pd.read_csv(DATA_PATH)

#df = pd.read_csv("../data/inventory_valuation_12m.csv")

layout = dbc.Container(
    [
        html.H2("Inventory Valuation Dashboard"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="sku-filter",
                        options=[{"label": s, "value": s} for s in sorted(df["sku"].unique())],
                        multi=True,
                        placeholder="Select SKU(s)",
                    ),
                    md=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="location-filter",
                        options=[{"label": l, "value": l} for l in sorted(df["location"].unique())],
                        multi=True,
                        placeholder="Select Location(s)",
                    ),
                    md=4,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="valuation-over-time"), md=8),
                dbc.Col(
                    [
                        html.H4("Total Inventory Value"),
                        html.Div(id="total-valuation", style={"fontSize": "24px", "fontWeight": "bold"}),
                    ],
                    md=4,
                ),
            ]
        ),
    ],
    fluid=True,
)


