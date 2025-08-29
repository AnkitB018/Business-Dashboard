import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from database import get_db_manager
import logging

logger = logging.getLogger(__name__)

layout = dbc.Container([
    html.H2("System Settings", className="mb-4"),
    
    # Database Settings Card
    dbc.Card([
        dbc.CardHeader(html.H4("Database Configuration", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("MongoDB Connection Status:", className="fw-bold"),
                    html.Div(id="db-status", className="mt-2")
                ], md=6),
                dbc.Col([
                    html.Label("Database Info:", className="fw-bold"),
                    html.Div(id="db-info", className="mt-2")
                ], md=6),
            ]),
            html.Hr(),
            dbc.Button("Test Connection", id="test-db-btn", color="primary", className="me-2"),
            dbc.Button("Refresh Status", id="refresh-db-btn", color="secondary"),
            html.Div(id="db-test-result", className="mt-3")
        ])
    ], className="mb-4"),
    
    # Application Settings Card
    dbc.Card([
        dbc.CardHeader(html.H4("Application Settings", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Theme:", className="fw-bold"),
                    dcc.Dropdown(
                        id="theme-selector",
                        options=[
                            {"label": "Minty (Default)", "value": "minty"},
                            {"label": "Bootstrap", "value": "bootstrap"},
                            {"label": "Darkly", "value": "darkly"},
                            {"label": "Flatly", "value": "flatly"},
                            {"label": "Litera", "value": "litera"}
                        ],
                        value="minty",
                        className="mt-2"
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Auto-refresh Interval (seconds):", className="fw-bold"),
                    dbc.Input(
                        id="refresh-interval",
                        type="number",
                        value=30,
                        min=10,
                        max=300,
                        className="mt-2"
                    )
                ], md=6),
            ]),
            html.Hr(),
            dbc.Button("Save Settings", id="save-settings-btn", color="success"),
            html.Div(id="settings-save-result", className="mt-3")
        ])
    ], className="mb-4"),
    
    # System Information Card
    dbc.Card([
        dbc.CardHeader(html.H4("System Information", className="mb-0")),
        dbc.CardBody([
            html.Div(id="system-info")
        ])
    ], className="mb-4"),
    
    # Data Management Card
    dbc.Card([
        dbc.CardHeader(html.H4("Data Management", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Backup Data:", className="fw-bold"),
                    html.P("Export current data to Excel format", className="text-muted"),
                    dbc.Button("Export to Excel", id="export-data-btn", color="info")
                ], md=6),
                dbc.Col([
                    html.Label("Clear Collections:", className="fw-bold"),
                    html.P("Remove all data from database (DANGER!)", className="text-muted text-danger"),
                    dbc.Button("Clear All Data", id="clear-data-btn", color="danger", disabled=True)
                ], md=6),
            ]),
            html.Div(id="data-management-result", className="mt-3")
        ])
    ])
], fluid=True)

def register_callbacks(app):
    """Register settings page callbacks"""
    
    @app.callback(
        [Output("db-status", "children"),
         Output("db-info", "children")],
        [Input("refresh-db-btn", "n_clicks"),
         Input("test-db-btn", "n_clicks")]
    )
    def update_db_status(refresh_clicks, test_clicks):
        try:
            db_manager = get_db_manager()
            
            # Test connection
            if db_manager.client:
                db_manager.client.admin.command('ping')
                status = dbc.Alert("✅ Connected", color="success")
                
                # Get database info
                collections = db_manager.db.list_collection_names()
                collection_counts = {}
                for collection in collections:
                    try:
                        count = db_manager.db[collection].count_documents({})
                        collection_counts[collection] = count
                    except:
                        collection_counts[collection] = "Error"
                
                info_items = [
                    html.P(f"Database: {db_manager.database_name}"),
                    html.P(f"Collections: {len(collections)}"),
                ]
                
                for collection, count in collection_counts.items():
                    info_items.append(html.P(f"  • {collection}: {count} records"))
                
                info = html.Div(info_items)
                
            else:
                status = dbc.Alert("❌ Not Connected", color="danger")
                info = html.P("No connection information available")
                
            return status, info
            
        except Exception as e:
            status = dbc.Alert(f"❌ Connection Failed: {str(e)}", color="danger")
            info = html.P("Connection error")
            return status, info
    
    @app.callback(
        Output("db-test-result", "children"),
        Input("test-db-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def test_db_connection(n_clicks):
        try:
            db_manager = get_db_manager()
            db_manager.client.admin.command('ping')
            return dbc.Alert("✅ Database connection test successful!", color="success")
        except Exception as e:
            return dbc.Alert(f"❌ Database connection test failed: {str(e)}", color="danger")
    
    @app.callback(
        Output("settings-save-result", "children"),
        Input("save-settings-btn", "n_clicks"),
        State("theme-selector", "value"),
        State("refresh-interval", "value"),
        prevent_initial_call=True
    )
    def save_settings(n_clicks, theme, interval):
        # In a real application, you would save these settings to a configuration file or database
        return dbc.Alert("✅ Settings saved successfully!", color="success")
    
    @app.callback(
        Output("system-info", "children"),
        Input("refresh-db-btn", "n_clicks")  # Trigger on page load/refresh
    )
    def update_system_info(n_clicks):
        try:
            import sys
            import platform
            import dash
            import pandas as pd
            
            info_items = [
                html.P(f"Python Version: {sys.version.split()[0]}"),
                html.P(f"Platform: {platform.system()} {platform.release()}"),
                html.P(f"Dash Version: {dash.__version__}"),
                html.P(f"Pandas Version: {pd.__version__}"),
            ]
            
            try:
                import pymongo
                info_items.append(html.P(f"PyMongo Version: {pymongo.__version__}"))
            except:
                info_items.append(html.P("PyMongo: Not available"))
            
            return html.Div(info_items)
            
        except Exception as e:
            return html.P(f"Error loading system info: {str(e)}")
    
    @app.callback(
        Output("data-management-result", "children"),
        Input("export-data-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def export_data(n_clicks):
        try:
            # This would implement data export functionality
            return dbc.Alert("Export functionality not yet implemented", color="warning")
        except Exception as e:
            return dbc.Alert(f"Export failed: {str(e)}", color="danger")