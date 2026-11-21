from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from collections import defaultdict
import csv

import database
import document_processor


# ---------------- APPLICATION SETUP ----------------

database.create_tables()

CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Education",
    "Healthcare",
    "Bills",
    "Entertainment",
    "Other"
]


class ExpenseTracker:

    def __init__(self, root):

        self.root = root
        self.root.title("Smart Personal Expense Tracker")
        self.root.geometry("1050x700")
        self.root.minsize(850, 600)

        self.imported_expenses = []

        # Application heading
        heading = tk.Label(
            root,
            text="Smart Personal Expense Tracker",
            font=("Arial", 20, "bold"),
            pady=15
        )
        heading.pack()

        # Create notebook tabs
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_tab = ttk.Frame(self.tabs)
        self.add_tab = ttk.Frame(self.tabs)
        self.manage_tab = ttk.Frame(self.tabs)
        self.import_tab = ttk.Frame(self.tabs)
        self.budget_tab = ttk.Frame(self.tabs)
        self.reports_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.add_tab, text="Add Expense")
        self.tabs.add(self.manage_tab, text="Manage Expenses")
        self.tabs.add(self.import_tab, text="Import Documents")
        self.tabs.add(self.budget_tab, text="Monthly Budget")
        self.tabs.add(self.reports_tab, text="Reports")

        # Build each section
        self.create_dashboard()
        self.create_add_expense()
        self.create_manage_expenses()
        self.create_import_section()
        self.create_budget_section()
        self.create_reports_section()

        self.refresh_all()


    # ---------------- DASHBOARD ----------------

    def create_dashboard(self):

        frame = self.dashboard_tab

        tk.Label(
            frame,
            text="Expense Overview",
            font=("Arial", 17, "bold")
        ).pack(pady=20)

        self.total_label = tk.Label(
            frame,
            text="Total Expenses: ₹0.00",
            font=("Arial", 14)
        )
        self.total_label.pack(pady=15)

        self.month_label = tk.Label(
            frame,
            text="This Month's Expenses: ₹0.00",
            font=("Arial", 14)
        )
        self.month_label.pack(pady=15)

        self.budget_label = tk.Label(
            frame,
            text="Monthly Budget: ₹0.00",
            font=("Arial", 14)
        )
        self.budget_label.pack(pady=15)

        self.remaining_label = tk.Label(
            frame,
            text="Remaining Budget: ₹0.00",
            font=("Arial", 14)
        )
        self.remaining_label.pack(pady=15)

        ttk.Button(
            frame,
            text="Refresh Dashboard",
            command=self.refresh_all
        ).pack(pady=20)


    def refresh_dashboard(self):

        today = date.today()
        month = today.strftime("%Y-%m")

        total = database.get_total_expenses()
        monthly_total = database.get_monthly_expenses(month)
        budget = database.get_budget(month)
        remaining = budget - monthly_total

        self.total_label.config(
            text=f"Total Expenses: ₹{total:,.2f}"
        )

        self.month_label.config(
            text=f"This Month's Expenses: ₹{monthly_total:,.2f}"
        )

        self.budget_label.config(
            text=f"Monthly Budget: ₹{budget:,.2f}"
        )

        self.remaining_label.config(
            text=f"Remaining Budget: ₹{remaining:,.2f}"
        )


    # ---------------- ADD EXPENSE ----------------

    def create_add_expense(self):

        frame = self.add_tab

        tk.Label(
            frame,
            text="Add a New Expense",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        form = ttk.Frame(frame)
        form.pack(pady=10)

        self.title_entry = self.create_entry(
            form, "Expense Title:", 0
        )

        self.amount_entry = self.create_entry(
            form, "Amount (₹):", 1
        )

        tk.Label(form, text="Category:").grid(
            row=2, column=0, sticky="w", padx=10, pady=8
        )

        self.category_box = ttk.Combobox(
            form,
            values=CATEGORIES,
            state="readonly",
            width=27
        )
        self.category_box.grid(
            row=2, column=1, padx=10, pady=8
        )
        self.category_box.set("Other")

        self.date_entry = self.create_entry(
            form, "Date (YYYY-MM-DD):", 3
        )
        self.date_entry.insert(0, date.today().isoformat())

        self.payment_entry = self.create_entry(
            form, "Payment Method:", 4
        )

        self.description_entry = self.create_entry(
            form, "Description:", 5
        )

        ttk.Button(
            frame,
            text="Save Expense",
            command=self.save_expense
        ).pack(pady=20)


    def create_entry(self, parent, label_text, row):

        tk.Label(
            parent,
            text=label_text
        ).grid(row=row, column=0, sticky="w", padx=10, pady=8)

        entry = ttk.Entry(parent, width=30)

        entry.grid(
            row=row, column=1, padx=10, pady=8
        )

        return entry


    def save_expense(self):

        title = self.title_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        category = self.category_box.get()
        expense_date = self.date_entry.get().strip()
        payment = self.payment_entry.get().strip()
        description = self.description_entry.get().strip()

        if not title or not amount_text:
            messagebox.showerror(
                "Error",
                "Please enter the expense title and amount."
            )
            return

        try:
            amount = float(amount_text)

            if amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid amount greater than zero."
            )
            return

        try:
            datetime.strptime(expense_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter the date in YYYY-MM-DD format."
            )
            return

        database.add_expense(
            title,
            amount,
            category,
            expense_date,
            payment,
            description
        )

        messagebox.showinfo(
            "Success",
            "Expense added successfully!"
        )

        # Clear the form
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_box.set("Other")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())
        self.payment_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

        self.refresh_all()


    # ---------------- MANAGE EXPENSES ----------------

    def create_manage_expenses(self):

        frame = self.manage_tab

        tk.Label(
            frame,
            text="Manage Your Expenses",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        columns = (
            "ID",
            "Title",
            "Amount",
            "Category",
            "Date",
            "Payment"
        )

        self.expense_table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=18
        )

        for column in columns:
            self.expense_table.heading(
                column,
                text=column
            )
            self.expense_table.column(
                column,
                width=130,
                anchor="center"
            )

        self.expense_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = ttk.Frame(frame)
        buttons.pack(pady=10)

        ttk.Button(
            buttons,
            text="Edit Selected",
            command=self.edit_selected_expense
        ).pack(side="left", padx=10)

        ttk.Button(
            buttons,
            text="Delete Selected",
            command=self.delete_selected_expense
        ).pack(side="left", padx=10)

        ttk.Button(
            buttons,
            text="Refresh",
            command=self.refresh_expense_table
        ).pack(side="left", padx=10)


    def refresh_expense_table(self):

        for item in self.expense_table.get_children():
            self.expense_table.delete(item)

        records = database.get_expenses()

        for record in records:

            self.expense_table.insert(
                "",
                tk.END,
                values=(
                    record["id"],
                    record["title"],
                    f"₹{record['amount']:,.2f}",
                    record["category"],
                    record["expense_date"],
                    record["payment_method"]
                )
            )


    def delete_selected_expense(self):

        selected = self.expense_table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select an expense first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this expense?"
        )

        if confirm:

            item = self.expense_table.item(selected[0])
            expense_id = int(item["values"][0])

            database.delete_expense(expense_id)

            messagebox.showinfo(
                "Deleted",
                "Expense deleted successfully."
            )

            self.refresh_all()


    def edit_selected_expense(self):

        selected = self.expense_table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select an expense first."
            )
            return

        item = self.expense_table.item(selected[0])
        expense_id = int(item["values"][0])

        records = database.get_expenses()

        record = next(
            (r for r in records if r["id"] == expense_id),
            None
        )

        if record is None:
            messagebox.showerror("Error", "Expense not found.")
            return

        window = tk.Toplevel(self.root)
        window.title("Edit Expense")
        window.geometry("400x430")
        window.transient(self.root)
        window.grab_set()

        form = ttk.Frame(window)
        form.pack(padx=15, pady=15)

        title_entry = self.create_entry(
            form, "Title:", 0
        )
        title_entry.insert(0, record["title"])

        amount_entry = self.create_entry(
            form, "Amount:", 1
        )
        amount_entry.insert(0, str(record["amount"]))

        tk.Label(form, text="Category:").grid(
            row=2, column=0, sticky="w", padx=10, pady=8
        )

        category_box = ttk.Combobox(
            form,
            values=CATEGORIES,
            state="readonly",
            width=27
        )
        category_box.grid(row=2, column=1, padx=10, pady=8)
        category_box.set(record["category"])

        date_entry = self.create_entry(
            form, "Date:", 3
        )
        date_entry.insert(0, record["expense_date"])

        payment_entry = self.create_entry(
            form, "Payment:", 4
        )
        payment_entry.insert(0, record["payment_method"] or "")

        description_entry = self.create_entry(
            form, "Description:", 5
        )
        description_entry.insert(0, record["description"] or "")

        def save_changes():

            title = title_entry.get().strip()

            try:
                amount = float(amount_entry.get())

                if amount <= 0 or not title:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Enter a title and a valid amount."
                )
                return

            expense_date = date_entry.get().strip()

            try:
                datetime.strptime(expense_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    "Use YYYY-MM-DD format."
                )
                return

            database.update_expense(
                expense_id,
                title,
                amount,
                category_box.get(),
                expense_date,
                payment_entry.get().strip(),
                description_entry.get().strip()
            )

            window.destroy()
            self.refresh_all()

            messagebox.showinfo(
                "Updated",
                "Expense updated successfully."
            )

        ttk.Button(
            window,
            text="Save Changes",
            command=save_changes
        ).pack(pady=10)


    # ---------------- IMPORT DOCUMENTS ----------------

    def create_import_section(self):

        frame = self.import_tab

        tk.Label(
            frame,
            text="Import Expenses from Documents",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(
            frame,
            text="Supported formats: PDF and Word (.docx)\n"
                 "Only readable text is supported. Scanned PDFs and images "
                 "are not supported.",
            justify="center"
        ).pack(pady=10)

        ttk.Button(
            frame,
            text="Choose PDF or Word Document",
            command=self.import_document
        ).pack(pady=10)

        self.import_file_label = tk.Label(
            frame,
            text="No document selected."
        )
        self.import_file_label.pack(pady=5)

        columns = ("Title", "Amount", "Category", "Date")

        self.import_table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=13
        )

        for column in columns:
            self.import_table.heading(
                column,
                text=column
            )
            self.import_table.column(
                column,
                width=180,
                anchor="center"
            )

        self.import_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = ttk.Frame(frame)
        buttons.pack(pady=10)

        ttk.Button(
            buttons,
            text="Remove Selected Row",
            command=self.remove_imported_row
        ).pack(side="left", padx=10)

        ttk.Button(
            buttons,
            text="Save Imported Expenses",
            command=self.save_imported_expenses
        ).pack(side="left", padx=10)


    def import_document(self):

        file_path = filedialog.askopenfilename(
            title="Select a Document",
            filetypes=[
                ("Supported Documents", "*.pdf *.docx"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx")
            ]
        )

        if not file_path:
            return

        try:
            text = document_processor.read_document(file_path)

            expenses = document_processor.extract_expenses(text)

            self.imported_expenses = expenses

            self.import_file_label.config(
                text=Path(file_path).name
            )

            self.refresh_import_table()

            if not expenses:
                messagebox.showwarning(
                    "No Expenses Found",
                    "No supported currency amounts were found. "
                    "Check that the document contains readable text "
                    "and amounts such as ₹250 or Rs. 250."
                )
            else:
                messagebox.showinfo(
                    "Import Complete",
                    f"Found {len(expenses)} possible expenses.\n"
                    "Review the rows before saving them."
                )

        except Exception as error:

            messagebox.showerror(
                "Import Error",
                str(error)
            )


    def refresh_import_table(self):

        for item in self.import_table.get_children():
            self.import_table.delete(item)

        for expense in self.imported_expenses:

            self.import_table.insert(
                "",
                tk.END,
                values=(
                    expense["title"],
                    f"₹{expense['amount']:,.2f}",
                    expense["category"],
                    expense["expense_date"]
                )
            )


    def remove_imported_row(self):

        selected = self.import_table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a row to remove."
            )
            return

        index = self.import_table.index(selected[0])

        self.imported_expenses.pop(index)

        self.refresh_import_table()


    def save_imported_expenses(self):

        if not self.imported_expenses:
            messagebox.showwarning(
                "Nothing to Save",
                "There are no imported expenses to save."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Import",
            f"Save {len(self.imported_expenses)} expenses to the database?"
        )

        if not confirm:
            return

        for expense in self.imported_expenses:

            database.add_expense(
                expense["title"],
                expense["amount"],
                expense["category"],
                expense["expense_date"],
                expense["payment_method"],
                expense["description"]
            )

        count = len(self.imported_expenses)

        self.imported_expenses.clear()
        self.refresh_import_table()
        self.refresh_all()

        messagebox.showinfo(
            "Import Saved",
            f"{count} expenses saved successfully."
        )


    # ---------------- MONTHLY BUDGET ----------------

    def create_budget_section(self):

        frame = self.budget_tab

        tk.Label(
            frame,
            text="Set Your Monthly Budget",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        month = date.today().strftime("%Y-%m")

        tk.Label(
            frame,
            text=f"Current Month: {month}",
            font=("Arial", 12)
        ).pack(pady=10)

        tk.Label(
            frame,
            text="Enter Budget Amount (₹):"
        ).pack(pady=10)

        self.budget_entry = ttk.Entry(
            frame,
            width=30
        )
        self.budget_entry.pack(pady=10)

        ttk.Button(
            frame,
            text="Save Budget",
            command=self.save_budget
        ).pack(pady=15)

        self.current_budget_label = tk.Label(
            frame,
            text="Current Budget: ₹0.00",
            font=("Arial", 13)
        )
        self.current_budget_label.pack(pady=15)

        self.refresh_budget()


    def save_budget(self):

        try:
            amount = float(self.budget_entry.get())

            if amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Budget",
                "Enter a valid budget greater than zero."
            )
            return

        month = date.today().strftime("%Y-%m")

        database.set_budget(month, amount)

        self.budget_entry.delete(0, tk.END)

        self.refresh_all()

        messagebox.showinfo(
            "Budget Saved",
            "Your monthly budget has been saved."
        )


    def refresh_budget(self):

        month = date.today().strftime("%Y-%m")
        budget = database.get_budget(month)

        self.current_budget_label.config(
            text=f"Current Budget: ₹{budget:,.2f}"
        )


    # ---------------- REPORTS ----------------

    def create_reports_section(self):

        frame = self.reports_tab

        tk.Label(
            frame,
            text="Expense Reports",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        buttons = ttk.Frame(frame)
        buttons.pack(pady=10)

        ttk.Button(
            buttons,
            text="Show Category Chart",
            command=self.show_chart
        ).pack(side="left", padx=10)

        ttk.Button(
            buttons,
            text="Export to CSV",
            command=self.export_csv
        ).pack(side="left", padx=10)

        self.report_text = tk.Text(
            frame,
            height=15,
            width=70,
            state="disabled"
        )
        self.report_text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.refresh_reports()


    def refresh_reports(self):

        records = database.get_expenses()

        category_totals = defaultdict(float)

        for record in records:
            category_totals[record["category"]] += record["amount"]

        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)

        if not category_totals:
            self.report_text.insert(
                tk.END,
                "No expenses available for reports."
            )
        else:
            self.report_text.insert(
                tk.END,
                "CATEGORY-WISE EXPENSE SUMMARY\n\n"
            )

            for category, amount in sorted(category_totals.items()):
                self.report_text.insert(
                    tk.END,
                    f"{category}: ₹{amount:,.2f}\n"
                )

        self.report_text.config(state="disabled")


    def show_chart(self):

        records = database.get_expenses()

        category_totals = defaultdict(float)

        for record in records:
            category_totals[record["category"]] += record["amount"]

        if not category_totals:
            messagebox.showwarning(
                "No Data",
                "Add some expenses before creating a chart."
            )
            return

        try:
            import matplotlib.pyplot as plt

            categories = list(category_totals.keys())
            amounts = list(category_totals.values())

            plt.figure(figsize=(8, 5))

            plt.pie(
                amounts,
                labels=categories,
                autopct="%1.1f%%",
                startangle=90
            )

            plt.title("Category-wise Expense Distribution")
            plt.tight_layout()
            plt.show()

        except ImportError:
            messagebox.showerror(
                "Missing Library",
                "Install matplotlib using:\n"
                "python -m pip install matplotlib"
            )


    # ---------------- CSV EXPORT ----------------

    def export_csv(self):

        records = database.get_expenses()

        if not records:
            messagebox.showwarning(
                "No Data",
                "There are no expenses to export."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Expense Report"
        )

        if not file_path:
            return

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "ID",
                "Title",
                "Amount",
                "Category",
                "Date",
                "Payment Method",
                "Description"
            ])

            for record in records:

                writer.writerow([
                    record["id"],
                    record["title"],
                    record["amount"],
                    record["category"],
                    record["expense_date"],
                    record["payment_method"],
                    record["description"]
                ])

        messagebox.showinfo(
            "Export Complete",
            "Your expense report has been exported."
        )


    # ---------------- REFRESH ALL SECTIONS ----------------

    def refresh_all(self):

        self.refresh_dashboard()
        self.refresh_expense_table()
        self.refresh_budget()
        self.refresh_reports()


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    root = tk.Tk()

    app = ExpenseTracker(root)

    root.mainloop()
