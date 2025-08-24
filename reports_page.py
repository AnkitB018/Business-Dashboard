import dash
import calendar
import datetime
from datetime import date
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import html, dcc, Input, Output




EXCEL_FILE = "business_data.xlsx"
# Helper loading data functions
def load_employees():
    df = pd.read_excel(EXCEL_FILE, sheet_name="Employees")
    return df

def load_attendance():
    df = pd.read_excel(EXCEL_FILE, sheet_name="Attendance")
    return df

def load_purchase():
    df = pd.read_excel(EXCEL_FILE, sheet_name= "Purchases")
    return df

def render_finance_tab():
    return dbc.Card(
        dbc.CardBody([
            html.H4("Finance Reports", className="card-title"),
            html.P("Summary of revenue, expenses, and profits will appear here."),
        ])
    )

def render_stock_tab():
    return dbc.Card(
        dbc.CardBody([
            html.H4("Stock Reports", className="card-title"),
            html.P("Current stock valuation and category breakdown will appear here."),
        ])
    )

def render_sales_tab():
    return dbc.Card(
        dbc.CardBody([
            html.H4("Sales Reports", className="card-title"),
            html.P("Sales trends and customer insights will appear here."),
        ])
    )


# Start of render function for purchase tab


def render_purchase_tab():
    return dbc.Container([
        # 🔹 Filters row
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

        # 🔹 Graphs
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

        # 🔹 Optional insights
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


# End of render function for purchsae tab


# Start of render function for attendance tab 


def render_attendance_tab():
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

        # ✅ Smaller KPI cards
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

        # ✅ Calendar placeholder
        dbc.Row([
            dbc.Col(html.Div(id="attendance-calendar"), md=12)
        ], className="mb-4"),

        # ✅ Legend
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Legend"),
                html.Div([
                    html.Span("⬜ No Record / Future Date", style={"marginRight": "15px"}),
                    html.Span("🟩 Present", style={"marginRight": "15px", "color": "green"}),
                    html.Span("🟩 Dark Green Overtime", style={"marginRight": "15px", "color": "darkgreen"}),
                    html.Span("🟨 Leave", style={"marginRight": "15px", "color": "orange"}),
                    html.Span("🟥 Absent", style={"marginRight": "15px", "color": "red"}),
                    html.Span("🟩 Light Green Half Day", style={"marginRight": "15px", "color": "lightgreen"}),
                ])
            ])))
        ])
    ], fluid=True)
    
# End of render function for attendance tab

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




    # Call backs for attendance tab
    @app.callback(
        Output("attendance-employee-name", "options"),
        Input("attendance-employee-name", "id")  # dummy input to trigger once
    )
    def populate_name_dropdown(_):
        employees_df = load_employees()
        return [{"label": n, "value": n} for n in employees_df["Name"].unique()]

    # update Employee ID dropdown when Name is selected
    @app.callback(
        Output("attendance-employee-id", "options"),
        Input("attendance-employee-name", "value")
    )
    def update_employee_id_dropdown(selected_name):
        employees_df = load_employees()
        if not selected_name:
            return []
        ids = employees_df.loc[employees_df["Name"] == selected_name, "Employee id"].unique()
        return [{"label": str(i), "value": i} for i in ids]

    # set default date range once employee is selected
    @app.callback(
        [Output("attendance-date-range", "start_date"),
         Output("attendance-date-range", "end_date")],
        Input("attendance-employee-id", "value")
    )
    def set_default_range(emp_id):
        attendance_df = load_attendance()
        if not emp_id or attendance_df.empty:
            return None, None
        return attendance_df["Date"].min(), attendance_df["Date"].max()

    # calendar + summary
    @app.callback(
        [
            Output("attendance-calendar", "children"),
            Output("summary-present", "children"),
            Output("summary-absent", "children"),
            Output("summary-leave", "children"),
            Output("summary-halfday", "children"),
            Output("summary-overtime", "children"),
        ],
        [
            Input("attendance-employee-id", "value"),
            Input("attendance-date-range", "start_date"),
            Input("attendance-date-range", "end_date"),
        ]
    )
    def update_calendar(employee_id, start_date, end_date):
        if not employee_id or not start_date or not end_date:
            return (
                html.Div("Please select Employee ID and Date Range."),
                "", "", "", "", ""
            )
    
        employees_df = load_employees()
        attendance_df = load_attendance()
    
        # Match employee row
        emp_row = employees_df[employees_df["Employee id"] == employee_id]
        if emp_row.empty:
            return html.Div("Employee not found."), "", "", "", "", ""
    
        employee_name = emp_row.iloc[0]["Name"]
        joining_date = pd.to_datetime(emp_row.iloc[0]["Joining Date"]).date()
    
        # Convert dates
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
    
        # Filter attendance for this employee
        df = attendance_df[
            (attendance_df["Employee id"] == employee_id)
        ].copy()
        df["Date"] = pd.to_datetime(df["Date"])
    
        df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]
    
        # Attendance map
        att_map = {
            d.date(): (s, oh if not pd.isna(oh) else 0)
            for d, s, oh in zip(df["Date"], df["Status"], df.get("Overtime Hours", [0]*len(df)))
        }
    
        colors = {
            "Present": "green",
            "Overtime": "darkgreen",
            "Half Day": "lightgreen",
            "Absent": "red",
            "Leave": "yellow",
        }
    
        present_days = 0
        absent_days = 0
        leave_days = 0
        half_days = 0
        overtime_hours = 0
    
        # Build calendar view (month by month in range)
        cal = calendar.Calendar()
        months = pd.period_range(start=start_date, end=end_date, freq="M")
    
        calendar_tables = []
        for period in months:
            year, month = period.year, period.month
            weeks = cal.monthdatescalendar(year, month)
    
            table_rows = []
            for week in weeks:
                row = []
                for d in week:
                    color = "lightgray"
                    label = str(d.day)
    
                    if d in att_map:
                        status, ot = att_map[d]
                        color = colors.get(status, "lightgray")
                        if status == "Present":
                            present_days += 1
                        elif status == "Absent":
                            absent_days += 1
                        elif status == "Leave":
                            leave_days += 1
                        elif status == "Half Day":
                            half_days += 1
                        if status == "Overtime":
                            present_days += 1
                            overtime_hours += ot
                    elif d < joining_date or d < start_date or d > end_date:
                        color = "white"
    
                    row.append(html.Td(label, style={
                        "backgroundColor": color,
                        "textAlign": "center",
                        "width": "40px",
                        "height": "40px",
                        "border": "1px solid #ccc"
                    }))
                table_rows.append(html.Tr(row))
    
            calendar_table = dbc.Table(
                [html.Thead(html.Tr([html.Th(day) for day in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]]))] +
                [html.Tbody(table_rows)],
                bordered=True
            )
            calendar_tables.append(html.Div([
                html.H5(f"{calendar.month_name[month]} {year}"),
                calendar_table
            ], style={"marginBottom": "20px"}))
    
        return (
            html.Div(calendar_tables),
            f"Present Days: {present_days}",
            f"Absent Days: {absent_days}",
            f"Leave Days: {leave_days}",
            f"Half Days: {half_days}",
            f"Overtime Hours: {overtime_hours}",
        )

    # Callbacks for purchase tab
    
    @app.callback(
        Output("purchase-product", "options"),
        Input("purchase-product", "id")   # dummy input to refresh once
    )
    def update_product_dropdown(_):
        purchases_df = load_purchase()
        products = sorted(purchases_df["Item Name"].dropna().unique())
        return [{"label": p, "value": p} for p in products]

    # Purchases over time (bar chart for selected product)
    @app.callback(
        Output("purchase-trend-graph", "figure"),
        Input("purchase-product", "value"),
        Input("purchase-date-range", "start_date"),
        Input("purchase-date-range", "end_date"),
    )
    def update_trend_graph(product, start_date, end_date):
        purchases_df = load_purchase()
        if purchases_df.empty or not product:
            return px.bar(title="No data")

        df = purchases_df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date) & (df["Item Name"] == product)
        df = df.loc[mask]

        if df.empty:
            return px.bar(title="No purchases found for this product")

        trend = df.groupby("Date").size().reset_index(name="Count")
        fig = px.bar(trend, x="Date", y="Count", title=f"Purchases of {product} Over Time")
        return fig

    # Product comparison (bar chart across products)
    @app.callback(
        Output("purchase-comparison-graph", "figure"),
        Input("purchase-date-range", "start_date"),
        Input("purchase-date-range", "end_date"),
    )
    def update_comparison_graph(start_date, end_date):
        purchases_df = load_purchase()
        if purchases_df.empty:
            return px.bar(title="No data")

        df = purchases_df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        df = df.loc[mask]

        if df.empty:
            return px.bar(title="No data in selected range")

        comparison = df.groupby("Item Name").size().reset_index(name="Quantity")
        fig = px.bar(comparison, x="Item Name", y="Quantity", title="Product Comparison")
        fig.update_xaxes(tickangle=45)
        return fig

    # Top 5 products
    @app.callback(
        Output("purchase-top-products", "figure"),
        Input("purchase-date-range", "start_date"),
        Input("purchase-date-range", "end_date"),
    )
    def update_top_products(start_date, end_date):
        purchases_df = load_purchase()
        if purchases_df.empty:
            return px.bar(title="No data")

        df = purchases_df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        df = df.loc[mask]

        top = df.groupby("Item Name").size().reset_index(name="Count").nlargest(5, "Count")
        fig = px.bar(top, x="Item Name", y="Count", title="Top 5 Purchased Products", text="Count")
        fig.update_traces(textposition="outside")
        return fig

    # Monthly trend (line chart)
    @app.callback(
        Output("purchase-monthly-trend", "figure"),
        Input("purchase-date-range", "start_date"),
        Input("purchase-date-range", "end_date"),
    )
    def update_monthly_trend(start_date, end_date):
        purchases_df = load_purchase()
        if purchases_df.empty:
            return px.line(title="No data")

        df = purchases_df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        df = df.loc[mask]

        monthly = df.resample("M", on="Date").size().reset_index(name="Count")
        fig = px.line(monthly, x="Date", y="Count", title="Monthly Purchase Trend", markers=True)
        return fig