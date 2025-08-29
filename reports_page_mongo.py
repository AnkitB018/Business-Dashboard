import dash
import calendar
import datetime
from datetime import date
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc, Input, Output
from data_service import get_hr_service
import logging

logger = logging.getLogger(__name__)

# Get HR service instance
hr_service = get_hr_service()

def load_employees():
    """Load employees from MongoDB"""
    try:
        return hr_service.get_employees()
    except Exception as e:
        logger.error(f"Error loading employees: {e}")
        return pd.DataFrame()

def load_attendance():
    """Load attendance from MongoDB"""
    try:
        return hr_service.get_attendance()
    except Exception as e:
        logger.error(f"Error loading attendance: {e}")
        return pd.DataFrame()

def load_purchase():
    """Load purchases from MongoDB"""
    try:
        return hr_service.get_purchases()
    except Exception as e:
        logger.error(f"Error loading purchases: {e}")
        return pd.DataFrame()

def load_sales():
    """Load sales from MongoDB"""
    try:
        return hr_service.get_sales()
    except Exception as e:
        logger.error(f"Error loading sales: {e}")
        return pd.DataFrame()

def load_stock():
    """Load stock from MongoDB"""
    try:
        return hr_service.get_stock()
    except Exception as e:
        logger.error(f"Error loading stock: {e}")
        return pd.DataFrame()

def render_finance_tab():
    """Render finance reports with revenue, expenses, and profit analysis"""
    try:
        sales_df = load_sales()
        purchases_df = load_purchase()
        
        # Calculate basic financial metrics
        total_revenue = sales_df['total_price'].sum() if not sales_df.empty else 0
        total_expenses = purchases_df['total_price'].sum() if not purchases_df.empty else 0
        profit = total_revenue - total_expenses
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Revenue", className="card-title text-success"),
                            html.H2(f"${total_revenue:,.2f}", className="text-success"),
                        ])
                    ], color="light", className="mb-3")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Expenses", className="card-title text-danger"),
                            html.H2(f"${total_expenses:,.2f}", className="text-danger"),
                        ])
                    ], color="light", className="mb-3")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Net Profit", className="card-title text-primary"),
                            html.H2(f"${profit:,.2f}", className="text-primary"),
                        ])
                    ], color="light", className="mb-3")
                ], md=4),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Revenue vs Expenses", className="card-title"),
                            dcc.Graph(id="finance-overview-chart")
                        ])
                    ])
                ], md=12)
            ])
        ], fluid=True)
        
    except Exception as e:
        logger.error(f"Error rendering finance tab: {e}")
        return html.Div("Error loading finance data")

def render_stock_tab():
    """Render stock reports with valuation and analysis"""
    try:
        stock_df = load_stock()
        
        if stock_df.empty:
            return dbc.Card(
                dbc.CardBody([
                    html.H4("Stock Reports", className="card-title"),
                    html.P("No stock data available."),
                ])
            )
        
        # Calculate stock valuation
        stock_df['total_value'] = stock_df['current_quantity'] * stock_df['unit_cost_average']
        total_stock_value = stock_df['total_value'].sum()
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Stock Value", className="card-title"),
                            html.H2(f"${total_stock_value:,.2f}", className="text-primary"),
                        ])
                    ], color="light", className="mb-3")
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Items", className="card-title"),
                            html.H2(f"{len(stock_df)}", className="text-info"),
                        ])
                    ], color="light", className="mb-3")
                ], md=6),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Stock by Category", className="card-title"),
                            dcc.Graph(id="stock-category-chart")
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Low Stock Items", className="card-title"),
                            html.Div(id="low-stock-items")
                        ])
                    ])
                ], md=6),
            ])
        ], fluid=True)
        
    except Exception as e:
        logger.error(f"Error rendering stock tab: {e}")
        return html.Div("Error loading stock data")

def render_sales_tab():
    """Render sales reports with trends and customer insights"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id="sales-date-range",
                    display_format="YYYY-MM-DD",
                    start_date=date.today().replace(day=1),
                    end_date=date.today()
                )
            ], md=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Sales Trends", className="card-title"),
                        dcc.Graph(id="sales-trend-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Top Selling Products", className="card-title"),
                        dcc.Graph(id="top-products-chart")
                    ])
                ])
            ], md=6),
        ])
    ], fluid=True)

def render_purchase_tab():
    """Render purchase reports with analysis"""
    return dbc.Container([
        # Filters row
        dbc.Row([
            dbc.Col([
                html.Label("Select Product:"),
                dcc.Dropdown(id="purchase-product", placeholder="Select product")
            ], md=4),
            dbc.Col([
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id="purchase-date-range",
                    display_format="YYYY-MM-DD",
                    start_date=date.today().replace(day=1),
                    end_date=date.today()
                )
            ], md=8),
        ], className="mb-4"),

        # Graphs
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Purchases Over Time", className="card-title"),
                        dcc.Graph(id="purchase-trend-graph")
                    ])
                ])
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Product Comparison", className="card-title"),
                        dcc.Graph(id="purchase-comparison-graph")
                    ])
                ])
            ], md=6),
        ], className="mb-4"),

        # Additional insights
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Top 5 Purchased Products", className="card-title"),
                        dcc.Graph(id="purchase-top-products")
                    ])
                ])
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Monthly Purchase Trend", className="card-title"),
                        dcc.Graph(id="purchase-monthly-trend")
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
    ], fluid=True)

def render_attendance_tab():
    """Render attendance reports with employee analytics"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Label("Select Employee:"),
                dcc.Dropdown(id="attendance-employee-name", placeholder="Select employee"),
            ], md=6),
            dbc.Col([
                html.Label("Select Employee ID:"),
                dcc.Dropdown(id="attendance-employee-id", placeholder="Select ID"),
            ], md=6),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id="attendance-date-range",
                    display_format="YYYY-MM-DD",
                    start_date=date.today().replace(day=1),
                    end_date=date.today(),
                )
            ], md=12),
        ], className="mb-3"),

        # KPI cards
        dbc.Row([
            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H6("Present", className="card-title"),
                    html.H4(id="summary-present", className="text-success")
                ]), color="light", inverse=False, 
                className="shadow-sm rounded-3",
                style={"width": "160px", "textAlign": "center"}
            ), width="auto"),

            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H6("Absent", className="card-title"),
                    html.H4(id="summary-absent", className="text-danger")
                ]), color="light",
                className="shadow-sm rounded-3",
                style={"width": "160px", "textAlign": "center"}
            ), width="auto"),

            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H6("Leave", className="card-title"),
                    html.H4(id="summary-leave", style={"color": "orange"})
                ]), color="light",
                className="shadow-sm rounded-3",
                style={"width": "160px", "textAlign": "center"}
            ), width="auto"),

            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H6("Half Day", className="card-title"),
                    html.H4(id="summary-halfday", style={"color": "seagreen"})
                ]), color="light",
                className="shadow-sm rounded-3",
                style={"width": "160px", "textAlign": "center"}
            ), width="auto"),

            dbc.Col(dbc.Card(
                dbc.CardBody([
                    html.H6("Overtime", className="card-title"),
                    html.H4(id="summary-overtime", style={"color": "darkgreen"})
                ]), color="light",
                className="shadow-sm rounded-3",
                style={"width": "160px", "textAlign": "center"}
            ), width="auto"),
        ], className="mb-4 g-2", justify="center"),

        # Calendar and charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Attendance Calendar", className="card-title"),
                        html.Div(id="attendance-calendar")
                    ])
                ])
            ], md=12)
        ], className="mb-4"),
    ], fluid=True)

# Main layout 
layout = dbc.Container([
    html.H2("Reports Dashboard", className="mb-4 text-center fw-bold"),

    dcc.Tabs(
        id="reports-tabs",
        value="finance",
        children=[
            dcc.Tab(label="Finance", value="finance"),
            dcc.Tab(label="Stock", value="stock"),
            dcc.Tab(label="Sales", value="sales"),
            dcc.Tab(label="Purchases", value="purchases"),
            dcc.Tab(label="Attendance", value="attendance"),
        ],
        className="mb-4"
    ),

    html.Div(id="reports-content")  # tab content gets loaded here
], fluid=True)

# Functions for callbacks
def register_callbacks(app):
    @app.callback(
        Output("reports-content", "children"),
        Input("reports-tabs", "value")
    )
    def render_tab(tab):
        if tab == "finance":
            return render_finance_tab()
        elif tab == "stock":
            return render_stock_tab()
        elif tab == "sales":
            return render_sales_tab()
        elif tab == "purchases":
            return render_purchase_tab()
        elif tab == "attendance":
            return render_attendance_tab()
        return html.P("Select a report tab.")

    # Finance tab callbacks
    @app.callback(
        Output("finance-overview-chart", "figure"),
        Input("reports-tabs", "value")
    )
    def update_finance_chart(tab):
        if tab != "finance":
            return px.bar()
        
        try:
            sales_df = load_sales()
            purchases_df = load_purchase()
            
            total_revenue = sales_df['total_price'].sum() if not sales_df.empty else 0
            total_expenses = purchases_df['total_price'].sum() if not purchases_df.empty else 0
            
            data = {
                'Category': ['Revenue', 'Expenses'],
                'Amount': [total_revenue, total_expenses],
                'Color': ['green', 'red']
            }
            
            fig = px.bar(data, x='Category', y='Amount', color='Color',
                        title="Revenue vs Expenses Overview")
            fig.update_layout(showlegend=False)
            return fig
        except Exception as e:
            logger.error(f"Error creating finance chart: {e}")
            return px.bar(title="Error loading data")

    # Stock tab callbacks
    @app.callback(
        [Output("stock-category-chart", "figure"),
         Output("low-stock-items", "children")],
        Input("reports-tabs", "value")
    )
    def update_stock_charts(tab):
        if tab != "stock":
            return px.pie(), html.Div()
        
        try:
            stock_df = load_stock()
            
            if stock_df.empty:
                return px.pie(title="No stock data"), html.P("No stock data available")
            
            # Category chart
            category_data = stock_df.groupby('category')['current_quantity'].sum().reset_index()
            fig = px.pie(category_data, values='current_quantity', names='category',
                        title="Stock Distribution by Category")
            
            # Low stock items (assuming minimum stock is 10)
            low_stock = stock_df[stock_df['current_quantity'] <= 10]
            if not low_stock.empty:
                low_stock_items = [
                    html.Li(f"{row['item_name']}: {row['current_quantity']} units")
                    for _, row in low_stock.iterrows()
                ]
                low_stock_content = html.Ul(low_stock_items)
            else:
                low_stock_content = html.P("All items are adequately stocked", className="text-success")
            
            return fig, low_stock_content
            
        except Exception as e:
            logger.error(f"Error creating stock charts: {e}")
            return px.pie(title="Error loading data"), html.Div("Error loading data")

    # Sales tab callbacks
    @app.callback(
        [Output("sales-trend-chart", "figure"),
         Output("top-products-chart", "figure")],
        Input("sales-date-range", "start_date"),
        Input("sales-date-range", "end_date")
    )
    def update_sales_charts(start_date, end_date):
        try:
            sales_df = load_sales()
            
            if sales_df.empty:
                return px.line(title="No sales data"), px.bar(title="No sales data")
            
            # Convert date column
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            
            # Filter by date range
            if start_date and end_date:
                mask = (sales_df['date'] >= start_date) & (sales_df['date'] <= end_date)
                sales_df = sales_df.loc[mask]
            
            # Sales trend
            daily_sales = sales_df.groupby('date')['total_price'].sum().reset_index()
            trend_fig = px.line(daily_sales, x='date', y='total_price',
                               title="Daily Sales Trend", markers=True)
            
            # Top products
            top_products = sales_df.groupby('item_name')['quantity'].sum().reset_index()
            top_products = top_products.nlargest(5, 'quantity')
            products_fig = px.bar(top_products, x='item_name', y='quantity',
                                 title="Top 5 Selling Products")
            
            return trend_fig, products_fig
            
        except Exception as e:
            logger.error(f"Error creating sales charts: {e}")
            return px.line(title="Error loading data"), px.bar(title="Error loading data")

    # Purchase tab callbacks
    @app.callback(
        Output("purchase-product", "options"),
        Input("purchase-product", "id")
    )
    def update_product_dropdown(_):
        try:
            purchases_df = load_purchase()
            if purchases_df.empty:
                return []
            products = sorted(purchases_df["item_name"].dropna().unique())
            return [{"label": p, "value": p} for p in products]
        except Exception as e:
            logger.error(f"Error updating product dropdown: {e}")
            return []

    @app.callback(
        [Output("purchase-trend-graph", "figure"),
         Output("purchase-comparison-graph", "figure"),
         Output("purchase-top-products", "figure"),
         Output("purchase-monthly-trend", "figure")],
        Input("purchase-product", "value"),
        Input("purchase-date-range", "start_date"),
        Input("purchase-date-range", "end_date")
    )
    def update_purchase_charts(selected_product, start_date, end_date):
        try:
            purchases_df = load_purchase()
            
            if purchases_df.empty:
                empty_fig = px.bar(title="No purchase data")
                return empty_fig, empty_fig, empty_fig, empty_fig
            
            purchases_df['date'] = pd.to_datetime(purchases_df['date'])
            
            # Filter by date range
            if start_date and end_date:
                mask = (purchases_df['date'] >= start_date) & (purchases_df['date'] <= end_date)
                purchases_df = purchases_df.loc[mask]
            
            # Trend graph for selected product
            if selected_product:
                product_data = purchases_df[purchases_df['item_name'] == selected_product]
                trend_fig = px.line(product_data, x='date', y='quantity',
                                   title=f"Purchase Trend: {selected_product}", markers=True)
            else:
                daily_purchases = purchases_df.groupby('date')['quantity'].sum().reset_index()
                trend_fig = px.line(daily_purchases, x='date', y='quantity',
                                   title="Overall Purchase Trend", markers=True)
            
            # Product comparison
            comparison = purchases_df.groupby("item_name")['quantity'].sum().reset_index()
            comparison_fig = px.bar(comparison, x="item_name", y="quantity",
                                   title="Product Purchase Comparison")
            comparison_fig.update_xaxes(tickangle=45)
            
            # Top 5 products
            top_products = comparison.nlargest(5, 'quantity')
            top_fig = px.bar(top_products, x="item_name", y="quantity",
                            title="Top 5 Purchased Products")
            
            # Monthly trend
            monthly = purchases_df.resample("M", on="date")['quantity'].sum().reset_index()
            monthly_fig = px.line(monthly, x="date", y="quantity",
                                 title="Monthly Purchase Trend", markers=True)
            
            return trend_fig, comparison_fig, top_fig, monthly_fig
            
        except Exception as e:
            logger.error(f"Error creating purchase charts: {e}")
            empty_fig = px.bar(title="Error loading data")
            return empty_fig, empty_fig, empty_fig, empty_fig

    # Attendance tab callbacks
    @app.callback(
        Output("attendance-employee-name", "options"),
        Input("attendance-employee-name", "id")
    )
    def populate_name_dropdown(_):
        try:
            employees_df = load_employees()
            if employees_df.empty:
                return []
            return [{"label": n, "value": n} for n in employees_df["name"].unique()]
        except Exception as e:
            logger.error(f"Error populating employee dropdown: {e}")
            return []

    @app.callback(
        Output("attendance-employee-id", "options"),
        Input("attendance-employee-name", "value")
    )
    def update_employee_id_dropdown(selected_name):
        if not selected_name:
            return []
        
        try:
            employees_df = load_employees()
            matched_employees = employees_df[employees_df["name"] == selected_name]
            return [{"label": row["employee_id"], "value": row["employee_id"]} 
                   for _, row in matched_employees.iterrows()]
        except Exception as e:
            logger.error(f"Error updating employee ID dropdown: {e}")
            return []

    @app.callback(
        [Output("summary-present", "children"),
         Output("summary-absent", "children"),
         Output("summary-leave", "children"),
         Output("summary-halfday", "children"),
         Output("summary-overtime", "children"),
         Output("attendance-calendar", "children")],
        [Input("attendance-employee-id", "value"),
         Input("attendance-date-range", "start_date"),
         Input("attendance-date-range", "end_date")]
    )
    def update_attendance_summary(employee_id, start_date, end_date):
        if not employee_id or not start_date or not end_date:
            return "", "", "", "", "", html.Div("Please select Employee ID and Date Range.")
        
        try:
            attendance_df = load_attendance()
            
            if attendance_df.empty:
                return "", "", "", "", "", html.Div("No attendance data available.")
            
            # Filter by employee and date range
            attendance_df['date'] = pd.to_datetime(attendance_df['date'])
            mask = (
                (attendance_df['employee_id'] == employee_id) &
                (attendance_df['date'] >= start_date) &
                (attendance_df['date'] <= end_date)
            )
            filtered_df = attendance_df.loc[mask]
            
            if filtered_df.empty:
                return "", "", "", "", "", html.Div("No attendance records found for selected criteria.")
            
            # Calculate summaries
            status_counts = filtered_df['status'].value_counts()
            
            present = status_counts.get('Present', 0)
            absent = status_counts.get('Absent', 0)
            leave = status_counts.get('Leave', 0)
            halfday = status_counts.get('Half Day', 0)
            overtime = status_counts.get('Overtime', 0)
            
            # Create simple calendar view
            calendar_data = []
            for _, row in filtered_df.iterrows():
                calendar_data.append(
                    html.P(f"{row['date'].strftime('%Y-%m-%d')}: {row['status']}")
                )
            
            calendar_content = html.Div(calendar_data) if calendar_data else html.P("No records to display")
            
            return str(present), str(absent), str(leave), str(halfday), str(overtime), calendar_content
            
        except Exception as e:
            logger.error(f"Error updating attendance summary: {e}")
            return "", "", "", "", "", html.Div("Error loading attendance data")
