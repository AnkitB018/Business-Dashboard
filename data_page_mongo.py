import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc, State, Input, Output, dash_table
from datetime import datetime, date
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
        return pd.DataFrame(columns=["employee_id", "name", "email", "phone", "department", "position", "joining_date", "salary"])

def load_attendance():
    """Load attendance from MongoDB"""
    try:
        return hr_service.get_attendance()
    except Exception as e:
        logger.error(f"Error loading attendance: {e}")
        return pd.DataFrame(columns=["date", "employee_id", "employee_name", "status", "overtime_hours"])

def load_stock():
    """Load stock from MongoDB"""
    try:
        return hr_service.get_stock()
    except Exception as e:
        logger.error(f"Error loading stock: {e}")
        return pd.DataFrame(columns=["item_name", "category", "current_quantity", "unit_cost_average"])

def load_purchases():
    """Load purchases from MongoDB"""
    try:
        return hr_service.get_purchases()
    except Exception as e:
        logger.error(f"Error loading purchases: {e}")
        return pd.DataFrame(columns=["date", "item_name", "category", "quantity", "unit_price", "total_price"])

def load_sales():
    """Load sales from MongoDB"""
    try:
        return hr_service.get_sales()
    except Exception as e:
        logger.error(f"Error loading sales: {e}")
        return pd.DataFrame(columns=["date", "item_name", "category", "quantity", "unit_price", "customer_name", "customer_phone"])

# START OF FUNCTIONS FOR EMPLOYEES TAB

def render_employees_tab():
    df = load_employees()

    # Define form fields based on the employee schema
    form_fields = [
        dbc.Col(dbc.Input(id="input-employee_id", type="text", placeholder="Employee ID", className="w-100"), md=3),
        dbc.Col(dbc.Input(id="input-name", type="text", placeholder="Full Name", className="w-100"), md=3),
        dbc.Col(dbc.Input(id="input-email", type="email", placeholder="Email Address", className="w-100"), md=3),
        dbc.Col(dbc.Input(id="input-phone", type="text", placeholder="Phone Number", className="w-100"), md=3),
        dbc.Col(dbc.Input(id="input-department", type="text", placeholder="Department", className="w-100"), md=3),
        dbc.Col(dbc.Input(id="input-position", type="text", placeholder="Position", className="w-100"), md=3),
        dbc.Col(dcc.DatePickerSingle(
            id="input-joining_date",
            display_format="YYYY-MM-DD",
            placeholder="Joining Date",
            date=None,
            className="w-100"
        ), md=3),
        dbc.Col(dbc.Input(id="input-salary", type="number", placeholder="Salary", className="w-100"), md=3),
    ]

    return dbc.Container([
        dbc.Card([
            dbc.CardHeader(html.H4("Add Employee", className="mb-0")),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row(form_fields[:4], className="mb-2"),
                    dbc.Row(form_fields[4:], className="mb-2"),
                    dbc.Button("Add Employee", id="add-employee-btn", color="success", className="mt-2"),
                    html.Div(id="add-employee-msg", className="mt-2")
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader(html.H4("Employee Details", className="mb-0")),
            dbc.CardBody([
                dash_table.DataTable(
                    id="employee-table",
                    data=df.to_dict("records"),
                    columns=[
                        {"name": "Employee ID", "id": "employee_id"},
                        {"name": "Name", "id": "name"},
                        {"name": "Email", "id": "email"},
                        {"name": "Phone", "id": "phone"},
                        {"name": "Department", "id": "department"},
                        {"name": "Position", "id": "position"},
                        {"name": "Joining Date", "id": "joining_date"},
                        {"name": "Salary", "id": "salary", "type": "numeric", "format": {"specifier": ",.0f"}},
                    ],
                    page_size=10,
                    row_selectable="multi",
                    sort_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
                ),
                dbc.Button("Delete Selected", id="delete-employee-btn", color="danger", className="mt-3"),
                html.Div(id="delete-employee-msg", className="mt-2")
            ])
        ], className="shadow-sm")
    ])

# END OF FUNCTIONS FOR EMPLOYEES TAB


# START OF FUNCTIONS FOR ATTENDANCE TAB

def render_attendance_tab():
    employees_df = load_employees()
    employee_name_options = [{"label": row["name"], "value": row["name"]} for _, row in employees_df.iterrows()]

    df = load_attendance()

    return dbc.Container([
        dbc.Card([
            dbc.CardHeader(html.H4("Add Attendance", className="mb-0")),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id="attendance-name", options=employee_name_options,
                                             placeholder="Select Employee Name"), md=3),
                        dbc.Col(dcc.Dropdown(id="attendance-id", placeholder="Select Employee ID"), md=3),
                        dbc.Col(dcc.DatePickerSingle(id="attendance-date", display_format="YYYY-MM-DD",
                                                     placeholder="Select Date"), md=3),
                        dbc.Col(dcc.Dropdown(
                            id="attendance-status",
                            options=[
                                {"label": "Present", "value": "Present"},
                                {"label": "Absent", "value": "Absent"},
                                {"label": "Leave", "value": "Leave"},
                                {"label": "Half Day", "value": "Half Day"},
                                {"label": "Overtime", "value": "Overtime"},
                            ],
                            placeholder="Select Status"
                        ), md=3),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col(dbc.Input(id="attendance-overtime", type="number",
                                          placeholder="Overtime Hours", disabled=True), md=3),
                    ], className="mb-2"),
                    dbc.Button("Add Attendance", id="add-attendance-btn", color="success", className="mt-2"),
                    html.Div(id="add-attendance-msg", className="mt-2")
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader(html.H4("Attendance Records", className="mb-0")),
            dbc.CardBody([
                dash_table.DataTable(
                    id="attendance-table",
                    data=df.to_dict("records"),
                    columns=[
                        {"name": "Date", "id": "date"},
                        {"name": "Employee ID", "id": "employee_id"},
                        {"name": "Name", "id": "employee_name"},
                        {"name": "Status", "id": "status"},
                        {"name": "Overtime Hours", "id": "overtime_hours", "type": "numeric"},
                    ],
                    page_size=10,
                    row_selectable="multi",
                    sort_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
                ),
                dbc.Button("Delete Selected", id="delete-attendance-btn", color="danger", className="mt-3"),
                html.Div(id="delete-attendance-msg", className="mt-2")
            ])
        ], className="shadow-sm")
    ])

# END OF FUNCTIONS FOR ATTENDANCE TAB


# START OF FUNCTIONS FOR STOCK TAB

def render_stock_tab():
    df = load_stock()

    return dbc.Container([
        dbc.Card([
            dbc.CardHeader(html.H4("Add Stock Item", className="mb-0")),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col(dbc.Input(id="stock-item-name", type="text", placeholder="Item Name"), md=3),
                        dbc.Col(dbc.Input(id="stock-category", type="text", placeholder="Category"), md=3),
                        dbc.Col(dbc.Input(id="stock-quantity", type="number", placeholder="Quantity"), md=3),
                        dbc.Col(dbc.Input(id="stock-cost", type="number", placeholder="Unit Cost"), md=3),
                    ], className="mb-2"),
                    dbc.Button("Add Stock Item", id="add-stock-btn", color="success", className="mt-2"),
                    html.Div(id="add-stock-msg", className="mt-2")
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader(html.H4("Stock Management", className="mb-0")),
            dbc.CardBody([
                dash_table.DataTable(
                    id="stock-table",
                    data=df.to_dict("records"),
                    columns=[
                        {"name": "Item Name", "id": "item_name"},
                        {"name": "Category", "id": "category"},
                        {"name": "Current Quantity", "id": "current_quantity", "type": "numeric"},
                        {"name": "Unit Cost Average", "id": "unit_cost_average", "type": "numeric", "format": {"specifier": ",.2f"}},
                    ],
                    page_size=10,
                    sort_action="native",
                    row_selectable="multi",
                    editable=True,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
                ),
                dbc.Button("Delete Selected", id="delete-stock-btn", color="danger", className="mt-3"),
                html.Div(id="delete-stock-msg", className="mt-2")
            ])
        ], className="shadow-sm")
    ])

# END OF FUNCTIONS FOR STOCK TAB


# START OF FUNCTIONS FOR PURCHASES TAB

def render_purchases_tab():
    df = load_purchases()

    return dbc.Container([
        dbc.Card([
            dbc.CardHeader(html.H4("Add Purchase", className="mb-0")),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col(dcc.DatePickerSingle(id="purchase-date", display_format="YYYY-MM-DD"), md=2),
                        dbc.Col(dbc.Input(id="purchase-item", type="text", placeholder="Item Name"), md=2),
                        dbc.Col(dbc.Input(id="purchase-category", type="text", placeholder="Category"), md=2),
                        dbc.Col(dbc.Input(id="purchase-quantity", type="number", placeholder="Quantity"), md=2),
                        dbc.Col(dbc.Input(id="purchase-unitprice", type="number", placeholder="Unit Price"), md=2),
                    ], className="mb-2"),
                    dbc.Button("Add Purchase", id="add-purchase-btn", color="success", className="mt-2"),
                    html.Div(id="add-purchase-msg", className="mt-2")
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader(html.H4("Purchase Records", className="mb-0")),
            dbc.CardBody([
                dash_table.DataTable(
                    id="purchase-table",
                    data=df.to_dict("records"),
                    columns=[
                        {"name": "Date", "id": "date"},
                        {"name": "Item Name", "id": "item_name"},
                        {"name": "Category", "id": "category"},
                        {"name": "Quantity", "id": "quantity", "type": "numeric"},
                        {"name": "Unit Price", "id": "unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                        {"name": "Total Price", "id": "total_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                    ],
                    page_size=10,
                    row_selectable="multi",
                    sort_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
                ),
                dbc.Button("Delete Selected", id="delete-purchase-btn", color="danger", className="mt-3"),
                html.Div(id="delete-purchase-msg", className="mt-2")
            ])
        ], className="shadow-sm")
    ])

# END OF FUNCTIONS FOR PURCHASES TAB


# START OF FUNCTIONS FOR SALES TAB

def render_sales_tab():
    df_sales = load_sales()
    df_stock = load_stock()

    form_fields = [
        dbc.Col(dcc.DatePickerSingle(id="input-sales-date", display_format="YYYY-MM-DD",
                                     placeholder="Select Date"), md=3),
        dbc.Col(dbc.Input(id="input-sales-customer-name", type="text", placeholder="Customer Name"), md=3),
        dbc.Col(dbc.Input(id="input-sales-customer-phone", type="text", placeholder="Customer Phone"), md=3),
        dbc.Col(dcc.Dropdown(
            id="input-sales-item-name",
            options=[{"label": f"{row['item_name']} ({row['category']})", "value": row['item_name']}
                     for _, row in df_stock.iterrows()],
            placeholder="Select Item"
        ), md=3),
        dbc.Col(dbc.Input(id="input-sales-category", type="text", placeholder="Category", readonly=True), md=3),
        dbc.Col(dbc.Input(id="input-sales-quantity", type="number", placeholder="Quantity"), md=2),
        dbc.Col(dbc.Input(id="input-sales-unit-price", type="number", placeholder="Unit Price"), md=2),
    ]

    return dbc.Container([
        dbc.Card([
            dbc.CardHeader(html.H4("Add Sale", className="mb-0")),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row(form_fields, className="mb-2"),
                    dbc.Button("Add Sale", id="add-sale-btn", color="success", className="mt-2"),
                    html.Div(id="add-sale-msg", className="mt-2")
                ])
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader(html.H4("Sales Records", className="mb-0")),
            dbc.CardBody([
                dash_table.DataTable(
                    id="sales-table",
                    data=df_sales.to_dict("records"),
                    columns=[
                        {"name": "Date", "id": "date"},
                        {"name": "Item Name", "id": "item_name"},
                        {"name": "Category", "id": "category"},
                        {"name": "Quantity", "id": "quantity", "type": "numeric"},
                        {"name": "Unit Price", "id": "unit_price", "type": "numeric", "format": {"specifier": ",.2f"}},
                        {"name": "Customer Name", "id": "customer_name"},
                        {"name": "Customer Phone", "id": "customer_phone"},
                    ],
                    page_size=10,
                    row_selectable="multi",
                    sort_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
                ),
                dbc.Button("Delete Selected", id="delete-sales-btn", color="danger", className="mt-3"),
                html.Div(id="delete-sales-msg", className="mt-2")
            ])
        ], className="shadow-sm")
    ])

# END OF FUNCTIONS FOR SALES TAB


# Layout
layout = dbc.Container([
    html.H2("Data Management", className="mb-4"),

    dbc.Tabs([
        dbc.Tab(label="Employees", tab_id="tab-employees"),
        dbc.Tab(label="Attendance", tab_id="tab-attendance"),
        dbc.Tab(label="Purchases", tab_id="tab-purchases"),
        dbc.Tab(label="Stock", tab_id="tab-stock"),
        dbc.Tab(label="Sales", tab_id="tab-sales"),
    ], id="data-tabs", active_tab="tab-employees"),

    html.Div(id="tab-content", className="mt-4")
], fluid=True)


# Wrapper function for callbacks
def register_callbacks(app):
    @app.callback(
        Output("tab-content", "children"),
        Input("data-tabs", "active_tab")
    )
    def render_tab_content(active_tab):
        if active_tab == "tab-employees":
            return render_employees_tab()
        elif active_tab == "tab-attendance":
            return render_attendance_tab()
        elif active_tab == "tab-purchases":
            return render_purchases_tab()
        elif active_tab == "tab-stock":
            return render_stock_tab()
        elif active_tab == "tab-sales":
            return render_sales_tab()
        return html.Div([html.P("Select a tab to continue.")])

    # Employee callbacks
    @app.callback(
        [Output("employee-table", "data", allow_duplicate=True),
         Output("add-employee-msg", "children")],
        [Input("add-employee-btn", "n_clicks")],
        [State("input-employee_id", "value"),
         State("input-name", "value"),
         State("input-email", "value"),
         State("input-phone", "value"),
         State("input-department", "value"),
         State("input-position", "value"),
         State("input-joining_date", "date"),
         State("input-salary", "value")],
        prevent_initial_call=True
    )
    def add_employee(n_clicks, emp_id, name, email, phone, dept, position, joining_date, salary):
        if not all([emp_id, name, email]):
            return dash.no_update, "⚠️ Please fill required fields (ID, Name, Email)."

        try:
            employee_data = {
                "employee_id": emp_id,
                "name": name,
                "email": email,
                "phone": phone or "",
                "department": dept or "",
                "position": position or "",
                "salary": salary or 0
            }

            if joining_date:
                employee_data["joining_date"] = datetime.strptime(joining_date, "%Y-%m-%d")

            hr_service.add_employee(employee_data)
            df = load_employees()
            return df.to_dict("records"), "✅ Employee added successfully!"

        except ValueError as e:
            return dash.no_update, f"❌ {str(e)}"
        except Exception as e:
            logger.error(f"Error adding employee: {e}")
            return dash.no_update, "❌ Error adding employee."

    @app.callback(
        [Output("employee-table", "data", allow_duplicate=True),
         Output("delete-employee-msg", "children")],
        [Input("delete-employee-btn", "n_clicks")],
        [State("employee-table", "selected_rows"),
         State("employee-table", "data")],
        prevent_initial_call=True
    )
    def delete_employee(n_clicks, selected_rows, table_data):
        if not selected_rows:
            return dash.no_update, "⚠️ No row selected."

        try:
            for row_idx in selected_rows:
                employee_id = table_data[row_idx]["employee_id"]
                hr_service.delete_employee(employee_id)

            df = load_employees()
            return df.to_dict("records"), "🗑️ Employee(s) deleted successfully!"

        except Exception as e:
            logger.error(f"Error deleting employee: {e}")
            return dash.no_update, "❌ Error deleting employee."

    # Attendance callbacks
    @app.callback(
        [Output("attendance-id", "options"),
         Output("attendance-id", "value")],
        [Input("attendance-name", "value")]
    )
    def update_employee_id_options(selected_name):
        if not selected_name:
            return [], None

        employees_df = load_employees()
        matched_ids = employees_df[employees_df["name"] == selected_name]["employee_id"].tolist()

        if len(matched_ids) == 1:
            return [{"label": matched_ids[0], "value": matched_ids[0]}], matched_ids[0]
        else:
            return [{"label": eid, "value": eid} for eid in matched_ids], None

    @app.callback(
        Output("attendance-overtime", "disabled"),
        [Input("attendance-status", "value")]
    )
    def toggle_overtime_hours(status):
        return status != "Overtime"

    @app.callback(
        [Output("attendance-table", "data", allow_duplicate=True),
         Output("add-attendance-msg", "children")],
        [Input("add-attendance-btn", "n_clicks")],
        [State("attendance-date", "date"),
         State("attendance-id", "value"),
         State("attendance-name", "value"),
         State("attendance-status", "value"),
         State("attendance-overtime", "value")],
        prevent_initial_call=True
    )
    def add_attendance(n_clicks, date, emp_id, name, status, overtime_hours):
        if not all([date, emp_id, name, status]):
            return dash.no_update, "⚠️ Please fill all required fields."

        try:
            attendance_data = {
                "employee_id": emp_id,
                "employee_name": name,
                "date": datetime.strptime(date, "%Y-%m-%d"),
                "status": status,
                "overtime_hours": overtime_hours if status == "Overtime" else 0
            }

            hr_service.add_attendance(attendance_data)
            df = load_attendance()
            return df.to_dict("records"), "✅ Attendance added successfully!"

        except ValueError as e:
            return dash.no_update, f"❌ {str(e)}"
        except Exception as e:
            logger.error(f"Error adding attendance: {e}")
            return dash.no_update, "❌ Error adding attendance."

    # Stock callbacks
    @app.callback(
        [Output("stock-table", "data", allow_duplicate=True),
         Output("add-stock-msg", "children")],
        [Input("add-stock-btn", "n_clicks")],
        [State("stock-item-name", "value"),
         State("stock-category", "value"),
         State("stock-quantity", "value"),
         State("stock-cost", "value")],
        prevent_initial_call=True
    )
    def add_stock_item(n_clicks, item_name, category, quantity, cost):
        if not all([item_name, category, quantity, cost]):
            return dash.no_update, "⚠️ Please fill all fields."

        try:
            stock_data = {
                "item_name": item_name,
                "category": category,
                "current_quantity": quantity,
                "unit_cost_average": cost,
                "minimum_stock": 10
            }

            hr_service.add_stock_item(stock_data)
            df = load_stock()
            return df.to_dict("records"), "✅ Stock item added successfully!"

        except Exception as e:
            logger.error(f"Error adding stock item: {e}")
            return dash.no_update, "❌ Error adding stock item."

    # Purchase callbacks
    @app.callback(
        [Output("purchase-table", "data", allow_duplicate=True),
         Output("add-purchase-msg", "children")],
        [Input("add-purchase-btn", "n_clicks")],
        [State("purchase-date", "date"),
         State("purchase-item", "value"),
         State("purchase-category", "value"),
         State("purchase-quantity", "value"),
         State("purchase-unitprice", "value")],
        prevent_initial_call=True
    )
    def add_purchase(n_clicks, date, item, category, qty, unit_price):
        if not all([date, item, category, qty, unit_price]):
            return dash.no_update, "⚠️ Please fill all fields."

        try:
            purchase_data = {
                "date": datetime.strptime(date, "%Y-%m-%d"),
                "item_name": item,
                "category": category,
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": qty * unit_price
            }

            hr_service.add_purchase(purchase_data)
            df = load_purchases()
            return df.to_dict("records"), "✅ Purchase added and stock updated!"

        except Exception as e:
            logger.error(f"Error adding purchase: {e}")
            return dash.no_update, "❌ Error adding purchase."

    # Sales callbacks
    @app.callback(
        Output("input-sales-category", "value"),
        [Input("input-sales-item-name", "value")]
    )
    def autofill_category(item_name):
        if not item_name:
            return ""
        df_stock = load_stock()
        row = df_stock[df_stock["item_name"] == item_name]
        if not row.empty:
            return row.iloc[0]["category"]
        return ""

    @app.callback(
        [Output("sales-table", "data", allow_duplicate=True),
         Output("add-sale-msg", "children")],
        [Input("add-sale-btn", "n_clicks")],
        [State("input-sales-date", "date"),
         State("input-sales-item-name", "value"),
         State("input-sales-category", "value"),
         State("input-sales-quantity", "value"),
         State("input-sales-unit-price", "value"),
         State("input-sales-customer-name", "value"),
         State("input-sales-customer-phone", "value")],
        prevent_initial_call=True
    )
    def add_sale(n_clicks, date, item, category, qty, price, cust_name, cust_phone):
        if not all([date, item, category, qty, price, cust_name, cust_phone]):
            return dash.no_update, "⚠️ Please fill all fields"

        try:
            sales_data = {
                "date": datetime.strptime(date, "%Y-%m-%d"),
                "item_name": item,
                "category": category,
                "quantity": qty,
                "unit_price": price,
                "total_price": qty * price,
                "customer_name": cust_name,
                "customer_phone": cust_phone
            }

            hr_service.add_sale(sales_data)
            df = load_sales()
            return df.to_dict("records"), "✅ Sale recorded successfully!"

        except ValueError as e:
            return dash.no_update, f"❌ {str(e)}"
        except Exception as e:
            logger.error(f"Error adding sale: {e}")
            return dash.no_update, "❌ Error recording sale."
