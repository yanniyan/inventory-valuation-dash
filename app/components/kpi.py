
from dash import html
import dash_bootstrap_components as dbc

def kpi_card(id, title, extra=None):
    header = html.Div(
        [
            html.H6(title, className="text-muted mb-0"),
            extra if extra else html.Div()
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "width": "100%"
        }
    )

    return dbc.Card(
        dbc.CardBody(
            [
                header,
                html.H3(id=id, className="kpi-value")
            ]
        ),
        className="shadow-sm p-3 kpi-card"
    )

