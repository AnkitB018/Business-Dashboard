import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from data_page import layout as data_layout
from reports_page import layout as reports_layout
from settings_page import layout as settings_layout



# Import the callbacks
from data_page import register_callbacks as data_page_callbacks
    


# Read data
EXCEL_FILE = "business_data.xlsx"
data = pd.read_excel(EXCEL_FILE, sheet_name= None)

# Initialize app 
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions= True)
app.title = "Business Dashboard"






# Navbar at the top
navbar= dbc.NavbarSimple(
    brand = "Business Dashboard",
    brand_href= "/",
    color= "primary",
    dark= True,
    children= [
          dbc.NavItem(dbc.NavLink("Data", href= "/data")),
          dbc.NavItem(dbc.NavLink("Reports", href= "/reports")),
          dbc.NavItem(dbc.NavLink("Settings", href= "/settings")),
    ],
)



# Layout
app.layout = dbc.Container([
    dcc.Location(id= "url"),
    navbar,
    html.Div(id= "page-content", className= "mt-4"),
], fluid = True)







# Now we start callbacks from here
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

def display_page(pathname):
    if pathname == '/reports':
        return reports_layout
    if pathname == '/settings':
        return settings_layout
    else:
        return data_layout # Default set to data page
 



data_page_callbacks(app)



# Run the app 
if __name__ == "__main__":
    app.run(debug= True)