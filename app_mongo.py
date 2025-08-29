import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from data_page_mongo import layout as data_layout
from reports_page_mongo import layout as reports_layout
from settings_page import layout as settings_layout
from database import initialize_database, get_db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the callbacks
from data_page_mongo import register_callbacks as data_page_callbacks
from reports_page_mongo import register_callbacks as reports_page_callbacks
from settings_page import register_callbacks as settings_page_callbacks

# Initialize database connection
logger.info("Initializing database connection...")
db_manager = get_db_manager()
if not db_manager.connect():
    logger.error("Failed to connect to MongoDB. Please ensure MongoDB is running.")
    # You might want to show a more user-friendly error here in production

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)
app.title = "HR Management System - MongoDB Edition"

# Navbar at the top
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                "HR Management System",
                href="/",
                className="fw-bold fs-3 text-white",  # bigger & bold
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Data", href="/data", className="fs-5 mx-2")),
                    dbc.NavItem(dbc.NavLink("Reports", href="/reports", className="fs-5 mx-2")),
                    dbc.NavItem(dbc.NavLink("Settings", href="/settings", className="fs-5 mx-2")),
                ],
                className="ms-auto",  # push nav items to right
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
    className="mb-4 shadow-sm",  # subtle shadow & spacing
)

# Layout
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dbc.Container(id="page-content", className="mt-4", fluid=True),
    ]
)

# Page routing callback
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == '/reports':
        return reports_layout
    elif pathname == '/settings':
        return settings_layout
    else:
        return data_layout  # Default set to data page

# Register callbacks from all pages
data_page_callbacks(app)
reports_page_callbacks(app)
settings_page_callbacks(app)

# Database health check endpoint (for monitoring)
@app.callback(
    Output("url", "search"),  # Dummy output to make callback valid
    Input("url", "pathname"),
    prevent_initial_call=True
)
def health_check(pathname):
    """Check database connection health"""
    try:
        if pathname == "/health":
            db_manager = get_db_manager()
            if db_manager.client:
                db_manager.client.admin.command('ping')
                logger.info("Database health check: OK")
            else:
                logger.warning("Database health check: No connection")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    return ""  # Return empty string for dummy output

# Run the app
if __name__ == "__main__":
    try:
        logger.info("Starting HR Management System...")
        logger.info("Dashboard will be available at: http://127.0.0.1:8050")
        
        # Check if database is properly initialized
        try:
            db_manager = get_db_manager()
            collections = db_manager.db.list_collection_names()
            if not collections:
                logger.warning("No collections found in database. You may need to initialize the database.")
            else:
                logger.info(f"Found collections: {collections}")
        except Exception as e:
            logger.error(f"Database check failed: {e}")
        
        app.run(debug=True, host='127.0.0.1', port=8050)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error: {e}")
        print("Please ensure MongoDB is running and accessible.")
    finally:
        # Clean up database connection
        try:
            db_manager = get_db_manager()
            if db_manager:
                db_manager.disconnect()
        except:
            pass
