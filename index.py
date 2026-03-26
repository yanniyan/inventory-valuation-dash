from app.app_instance import app as dash_app
from app.layout import layout

dash_app.layout = layout

import app.callbacks

if __name__ == "__main__":
    dash_app.run(debug=True, port=8053)
