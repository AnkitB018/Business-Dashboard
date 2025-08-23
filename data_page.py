import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table




# Helper functions
EXCEL_FILE = "business_data.xlsx"

def load_employees():
    df = pd.read_excel(EXCEL_FILE, sheet_name = "Employees")
    return df






# START OF FUNCTIONS FOR EMPLOYEES TAB

# For storing states (Global assigning)
df = load_employees()
state_list = []
for col in df.columns:
    if col.lower() == "joining date":
        state_list.append(State(f"input-{col}", "date"))
    else:
        state_list.append(State(f"input-{col}", "value"))


# For rendering and editing employees tab
def render_employees_tab():
    df = load_employees()

    # build form fields (UI only)
    form_fields = []
    for col in df.columns:
        if col.lower() == "joining date":
            form_fields.append(
                dbc.Col(
                    dcc.DatePickerSingle(
                        id=f"input-{col}",
                        display_format="YYYY-MM-DD",
                        placeholder="joining date",
                        date=None
                    ),
                    md=3
                )
            )
        else:
            form_fields.append(
                dbc.Col(
                    dbc.Input(id=f"input-{col}", type="text", placeholder=col),
                    md=3
                )
            )

    return dbc.Container([
        html.H4("Add Employee"),
        dbc.Form([
            dbc.Row(form_fields, className="mb-2"),
            dbc.Button("Add Employee", id="add-employee-btn", color="success", className="mt-2"),
            html.Div(id="add-employee-msg", className="mt-2")
        ]),
        html.Hr(),
        html.H4("Employee Details"),
        dash_table.DataTable(
            id="employee-table",
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            row_selectable="multi",
            sort_action= "native",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
        ),
        dbc.Button("Delete Selected", id="Delete-employee-btn", color="danger", className="mt-2"),
        html.Div(id="Delete-employee-msg", className="mt-2")
    ])

# END OF FUNCTIONS FOR EMPLOYEES TAB



# START OF FUNCTIONS FOR ATTENDANCE TAB

def render_attendance_tab():
    # Load employees for dropdowns
    employees_df = load_employees()

    # Dropdown options for employee names
    employee_name_options = [
        {"label": row["Name"], "value": row["Name"]} for _, row in employees_df.iterrows()
    ]

    # Load attendance sheet (create if missing)
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Attendance")
    except Exception:
        df = pd.DataFrame(columns=["Date", "Employee id", "Name", "Status", "Overtime Hours"])

    return dbc.Container([
        html.H4("Add Attendance"),
        dbc.Form([
            dbc.Row([
                # Employee Name
                dbc.Col(
                    dcc.Dropdown(
                        id="attendance-name",
                        options=employee_name_options,
                        placeholder="Select Employee Name"
                    ),
                    md=3
                ),
                # Employee ID (auto-populated based on Name)
                dbc.Col(
                    dcc.Dropdown(
                        id="attendance-id",
                        placeholder="Select Employee ID"
                    ),
                    md=3
                ),
                # Date
                dbc.Col(
                    dcc.DatePickerSingle(
                        id="attendance-date",
                        display_format="YYYY-MM-DD",
                        placeholder="Select Date"
                    ),
                    md=3
                ),
                # Status
                dbc.Col(
                    dcc.Dropdown(
                        id="attendance-status",
                        options=[
                            {"label": "Present", "value": "Present"},
                            {"label": "Absent", "value": "Absent"},
                            {"label": "Leave", "value": "Leave"},
                            {"label": "Half Day", "value": "Half Day"},
                            {"label": "Overtime", "value": "Overtime"},
                        ],
                        placeholder="Select Status"
                    ),
                    md=3
                ),
                # Overtime Hours (only enabled if status=Overtime)
                dbc.Col(
                    dbc.Input(
                        id="attendance-overtime",
                        type="number",
                        placeholder="Overtime Hours",
                        disabled=True
                    ),
                    md=3
                ),
            ], className="mb-2"),
            dbc.Button("Add Attendance", id="add-attendance-btn", color="success", className="mt-2"),
            html.Div(id="add-attendance-msg", className="mt-2")
        ]),
        html.Hr(),
        html.H4("Attendance Records"),
        dash_table.DataTable(
            id="attendance-table",
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            row_selectable="multi",
            sort_action="native",
            editable= True,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
        ),
        dbc.Button("Delete Selected", id="delete-attendance-btn", color="danger", className="mt-2"),
        html.Div(id="delete-attendance-msg", className="mt-2")
    ])

# END OF FUNCTIONS FOR ATTENDANCE TAB


# START OF FUNCTIONS FOR Stock TAB

def render_stock_tab():
    # Load stock sheet (create if missing)
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Stock")
    except Exception:
        df = pd.DataFrame(columns=["Category", "Item Name", "Current Quantity", "Unit Cost on Average"])

    return dbc.Container([
        html.H4("Stock Management"),
        dash_table.DataTable(
            id="stock-table",
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            sort_action="native",
            row_selectable="multi",
            editable=True,  # Allow manual edits if required
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
        ),

        dbc.Button("Delete Selected", id="delete-stock-btn", color="danger", className="mt-2"),
        html.Div(id="delete-stock-msg", className="mt-2")
    ])

    

# END OF FUNCTIONS FOR Stock TAB


# START OF FUNCTIONS FOR PURCHASES TAB

def render_purchases_tab():
    # Load purchases data
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Purchases")
    except Exception:
        df = pd.DataFrame(columns=["Date", "Item Name", "Category", "Quantity", "Unit Price", "Total Price"])

    return dbc.Container([
        html.H4("Add Purchase"),
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
        ]),

        html.Hr(),
        html.H4("Purchase Records"),
        dash_table.DataTable(
            id="purchase-table",
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            row_selectable = "multi",
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
        ),

        dbc.Button("Delete Selected", id="delete-purchase-btn", color="danger", className="mt-2"),
        html.Div(id="delete-purchase-msg", className="mt-2")
        
    ])



# END OF FUNCTIONS FOR PURCHASES TAB


# START OF FUNCTIONS FOR SALES TAB

def load_sales():
    return pd.read_excel(EXCEL_FILE, sheet_name= "Sales")

def load_stock():
    return pd.read_excel(EXCEL_FILE, sheet_name= "Stock")

def render_sales_tab():
    df_sales = load_sales()
    df_stock = load_stock()  # to allow dropdown of items

    form_fields = [
        dbc.Col(dcc.DatePickerSingle(
            id="input-sales-Date",
            display_format="YYYY-MM-DD",
            placeholder="Select Date"
        ), md=3),

        dbc.Col(dbc.Input(id="input-sales-Customer Name", type="text", placeholder="Customer Name"), md=3),
        dbc.Col(dbc.Input(id="input-sales-Customer Phone", type="text", placeholder="Customer Phone"), md=3),

        dbc.Col(dcc.Dropdown(
            id="input-sales-Item Name",
            options=[{"label": f"{row['Item Name']} ({row['Category']})", "value": row['Item Name']}
                     for _, row in df_stock.iterrows()],
            placeholder="Select Item"
        ), md=3),

        dbc.Col(dbc.Input(id="input-sales-Category", type="text", placeholder="Category", readonly=True), md=3),

        dbc.Col(dbc.Input(id="input-sales-Quantity", type="number", placeholder="Quantity"), md=2),
        dbc.Col(dbc.Input(id="input-sales-Unit Price", type="number", placeholder="Unit Price"), md=2),
    ]

    return dbc.Container([
        html.H4("Add Sale"),
        dbc.Form([
            dbc.Row(form_fields, className="mb-2"),
            dbc.Button("Add Sale", id="add-sale-btn", color="success", className="mt-2"),
            html.Div(id="add-sale-msg", className="mt-2")
        ]),
        html.Hr(),
        html.H4("Sales Records"),
        dash_table.DataTable(
            id="sales-table",
            data=df_sales.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df_sales.columns],
            page_size=10,
            row_selectable= "multi",
            sort_action= "native",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"}
        ),

        dbc.Button("Delete Selected", id="delete-sales-btn", color="danger", className="mt-2"),
        html.Div(id="delete-sales-msg", className="mt-2")
    ])



# END OF FUNCTIONS FOR SALES TAB




# Start layout from here

layout = dbc.Container([
    html.H2("Data Management"),

    dbc.Tabs([
        dbc.Tab(label = "Employees", tab_id= "tab-employees"),
        dbc.Tab(label= "Attendance", tab_id= "tab-attendance"),
        dbc.Tab(label= "Purchases", tab_id = "tab-purchases"),
        dbc.Tab(label= "Stock", tab_id= "tab-stock"),
        dbc.Tab(label= "Sales", tab_id= "tab-sales"),
    ], id= "data-tabs", active_tab= "tab-employees"),

    html.Div(id = "tab-content", className= "mt-4")
], fluid= True)





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


    
    # For filling up employee details
    @app.callback(
        Output("employee-table", "data", allow_duplicate= True),
        Output("add-employee-msg", "children"),
        [Input("add-employee-btn", "n_clicks")],
        state_list,
        prevent_initial_call=True
    )
    def add_employee(n_clicks, *values):
        df = load_employees()
        new_row = dict(zip(df.columns, values))
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
        # Write back to Excel
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Employees", index=False)
    
        return df.to_dict("records"), "✅ Employee added successfully!"


    
    # For deleting from employee table
    @app.callback(
    Output("employee-table", "data", allow_duplicate= True),
    Output("Delete-employee-msg", "children"),
    Input("Delete-employee-btn", "n_clicks"),
    State("employee-table", "selected_rows"),
    prevent_initial_call=True
    )
    def delete_employee(n_clicks, selected_rows):
        if not selected_rows:
            return dash.no_update, "⚠️ No row selected."
    
        df = load_employees()
        df = df.drop(df.index[selected_rows])  # drop first selected row
        df.reset_index(drop=True, inplace=True)
    
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Employees", index=False)
    
        return df.to_dict("records"), "🗑️ Employee deleted successfully!"


    # Callbacks for attendance tab
    # 1. Auto-populate Employee ID when selecting Name
    @app.callback(
        Output("attendance-id", "options"),
        Output("attendance-id", "value"),
        Input("attendance-name", "value")
    )
    def update_employee_id_options(selected_name):
        if not selected_name:
            return [], None
    
        employees_df = load_employees()
        matched_ids = employees_df[employees_df["Name"] == selected_name]["Employee id"].astype(str).tolist()
    
        if len(matched_ids) == 1:
            return [{"label": matched_ids[0], "value": matched_ids[0]}], matched_ids[0]
        else:
            return [{"label": eid, "value": eid} for eid in matched_ids], None
    
    
    # 2. Enable/disable Overtime Hours input based on Status
    @app.callback(
        Output("attendance-overtime", "disabled"),
        Input("attendance-status", "value")
    )
    def toggle_overtime_hours(status):
        return status != "Overtime"
    
    
    # 3. Add Attendance Record
    @app.callback(
        Output("attendance-table", "data", allow_duplicate=True),
        Output("add-attendance-msg", "children"),
        Input("add-attendance-btn", "n_clicks"),
        State("attendance-date", "date"),
        State("attendance-id", "value"),
        State("attendance-name", "value"),
        State("attendance-status", "value"),
        State("attendance-overtime", "value"),
        prevent_initial_call=True
    )
    def add_attendance(n_clicks, date, emp_id, name, status, overtime_hours):
        df = pd.read_excel(EXCEL_FILE, sheet_name="Attendance")
    
        new_row = {
            "Date": date,
            "Employee id": emp_id,
            "Name": name,
            "Status": status,
            "Overtime Hours": overtime_hours if status == "Overtime" else None
        }
    
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
        # Save back to Excel
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Attendance", index=False)
    
        return df.to_dict("records"), "✅ Attendance added successfully!"
    
    
    # 4. Delete Selected Attendance Records
    @app.callback(
        Output("attendance-table", "data", allow_duplicate=True),
        Output("delete-attendance-msg", "children"),
        Input("delete-attendance-btn", "n_clicks"),
        State("attendance-table", "selected_rows"),
        State("attendance-table", "data"),
        prevent_initial_call=True
    )
    def delete_attendance(n_clicks, selected_rows, table_data):
        if not selected_rows:
            return table_data, "⚠️ No row selected to delete."
    
        df = pd.DataFrame(table_data)
        df = df.drop(selected_rows).reset_index(drop=True)
    
        # Save updated sheet
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Attendance", index=False)
    
        return df.to_dict("records"), "🗑️ Selected records deleted."


    # Callbacks for stock tab
    # 1. Allow manual changing for stock table
    @app.callback(
    Output("stock-table", "data"),
    Input("stock-table", "data"),
    State("stock-table", "data_previous"),
    prevent_initial_call=True
    )
    def update_stock_table(current_data, previous_data):
        if previous_data is None:
            raise dash.exceptions.PreventUpdate
    
        # Save the new data (after edit) to Excel
        df = pd.DataFrame(current_data)
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Stock", index=False)
    
        # Return updated data so table doesn't reset
        return current_data
    
    
    # 2. Delete selected rows from Stock table
    @app.callback(
        Output("stock-table", "data", allow_duplicate=True),
        Output("delete-stock-msg", "children"),
        Input("delete-stock-btn", "n_clicks"),
        State("stock-table", "selected_rows"),
        State("stock-table", "data"),
        prevent_initial_call=True
    )
    def delete_stock(n_clicks, selected_rows, table_data):
        if not selected_rows:
            return table_data, "⚠️ No row selected to delete."
    
        df = pd.DataFrame(table_data)
        df = df.drop(selected_rows).reset_index(drop=True)
    
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Stock", index=False)
    
        return df.to_dict("records"), "🗑️ Selected stock items deleted."


    
    # Callbacks for purchases tab
    @app.callback(
    Output("purchase-table", "data", allow_duplicate=True),
    Output("add-purchase-msg", "children"),
    Input("add-purchase-btn", "n_clicks"),
    State("purchase-date", "date"),
    State("purchase-item", "value"),
    State("purchase-category", "value"),
    State("purchase-quantity", "value"),
    State("purchase-unitprice", "value"),
    State("purchase-table", "data"),
    prevent_initial_call=True
    )
    def add_purchase(n_clicks, date, item, category, qty, unit_price, table_data):
        if not all([date, item, category, qty, unit_price]):
            return table_data, "⚠️ Please fill all fields."
    
        df_purchases = pd.DataFrame(table_data)
    
        # compute total price
        total_price = qty * unit_price
    
        # add purchase row
        new_row = {
            "Date": date,
            "Item Name": item,
            "Category": category,
            "Quantity": qty,
            "Unit Price": unit_price,
            "Total Price": total_price
        }
        df_purchases = pd.concat([df_purchases, pd.DataFrame([new_row])], ignore_index=True)
    
        # save Purchases
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df_purchases.to_excel(writer, sheet_name="Purchases", index=False)
    
        # ---- update Stock ----
        try:
            df_stock = pd.read_excel(EXCEL_FILE, sheet_name="Stock")
        except Exception:
            df_stock = pd.DataFrame(columns=["Category", "Item Name", "Current Quantity", "Unit Cost on Average"])
    
        if item in df_stock["Item Name"].values:
            # existing stock item
            idx = df_stock[df_stock["Item Name"] == item].index[0]
            q_old = df_stock.at[idx, "Current Quantity"]
            uc_old = df_stock.at[idx, "Unit Cost on Average"]
    
            q_new = qty
            uc_new = unit_price
    
            q_total = q_old + q_new
            uc_total = ((q_old * uc_old) + (q_new * uc_new)) / q_total
    
            df_stock.at[idx, "Current Quantity"] = q_total
            df_stock.at[idx, "Unit Cost on Average"] = uc_total.round(2)
        else:
            # new item
            new_stock_row = {
                "Category": category,
                "Item Name": item,
                "Current Quantity": qty,
                "Unit Cost on Average": unit_price
            }
            df_stock = pd.concat([df_stock, pd.DataFrame([new_stock_row])], ignore_index=True)
    
        # save Stock
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df_stock.to_excel(writer, sheet_name="Stock", index=False)
    
        return df_purchases.to_dict("records"), "✅ Purchase added and Stock updated!"

    @app.callback(
        Output("purchase-table", "data", allow_duplicate=True),
        Output("delete-purchase-msg", "children"),
        Input("delete-purchase-btn", "n_clicks"),
        State("purchase-table", "selected_rows"),
        State("purchase-table", "data"),
        prevent_initial_call=True
    )
    def delete_stock(n_clicks, selected_rows, table_data):
        if not selected_rows:
            return table_data, "⚠️ No row selected to delete."
    
        df = pd.DataFrame(table_data)
        df = df.drop(selected_rows).reset_index(drop=True)
    
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Purchases", index=False)
    
        return df.to_dict("records"), "🗑️ Selected purchase items deleted."


    

    # Callbacks for sales tab
    @app.callback(
    Output("input-sales-Category", "value"),
    Input("input-sales-Item Name", "value")
    )
    def autofill_category(item_name):
        if not item_name:
            return ""
        df_stock = load_stock()
        row = df_stock[df_stock["Item Name"] == item_name]
        if not row.empty:
            return row.iloc[0]["Category"]
        return ""


    @app.callback(
    Output("sales-table", "data", allow_duplicate=True),
    Output("add-sale-msg", "children"),
    Input("add-sale-btn", "n_clicks"),
    State("input-sales-Date", "date"),
    State("input-sales-Item Name", "value"),
    State("input-sales-Category", "value"),
    State("input-sales-Quantity", "value"),
    State("input-sales-Unit Price", "value"),
    State("input-sales-Customer Name", "value"),
    State("input-sales-Customer Phone", "value"),
    prevent_initial_call=True
    )
    def add_sale(n_clicks, date, item, category, qty, price, cust_name, cust_phone):
        if not all([date, item, category, qty, price, cust_name, cust_phone]):
            return dash.no_update, "⚠️ Please fill all fields"
    
        df_sales = load_sales()
        df_stock = load_stock()
    
        # check stock availability
        row = df_stock[df_stock["Item Name"] == item]
        if row.empty:
            return dash.no_update, f"❌ Item '{item}' not found in stock."
    
        current_qty = row.iloc[0]["Current Quantity"]
        if qty > current_qty:
            return dash.no_update, f"❌ Not enough stock. Available: {current_qty}"
    
        # update stock
        df_stock.loc[df_stock["Item Name"] == item, "Current Quantity"] = current_qty - qty
        df_stock["Unit Cost on Average"] = df_stock["Unit Cost on Average"].round(2)
    
        # add sale record
        new_row = {
            "Date": date,
            "Item Name": item,
            "Category": category,
            "Quantity": qty,
            "Unit Price": price,
            "Customer Name": cust_name,
            "Customer Phone": cust_phone
        }
        df_sales = pd.concat([df_sales, pd.DataFrame([new_row])], ignore_index=True)
    
        # save both sheets
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df_sales.to_excel(writer, sheet_name="Sales", index=False)
            df_stock.to_excel(writer, sheet_name="Stock", index=False)
    
        return df_sales.to_dict("records"), "✅ Sale recorded successfully!"


    @app.callback(
        Output("sales-table", "data", allow_duplicate=True),
        Output("delete-sales-msg", "children"),
        Input("delete-sales-btn", "n_clicks"),
        State("sales-table", "selected_rows"),
        State("sales-table", "data"),
        prevent_initial_call=True
    )
    def delete_stock(n_clicks, selected_rows, table_data):
        if not selected_rows:
            return table_data, "⚠️ No row selected to delete."
    
        df = pd.DataFrame(table_data)
        df = df.drop(selected_rows).reset_index(drop=True)
    
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sales", index=False)
    
        return df.to_dict("records"), "🗑️ Selected sales items deleted."


            