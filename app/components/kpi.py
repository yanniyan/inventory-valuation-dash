from dash import html
import dash_bootstrap_components as dbc

def kpi_card(id, title):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(id=id, className="fw-bold")   
        ]),
        className="shadow-sm p-3"
    )
