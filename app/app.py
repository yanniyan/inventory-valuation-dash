from app_instance import app
import dash_bootstrap_components as dbc
from layout import layout
import callbacks

app.layout = layout

if __name__ == "__main__":
    app.run(debug=True, port=8053)
