import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
from datetime import datetime, timedelta
import csv
import os

class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("1000x800")
        
        # Configure professional styling
        self.configure(bg='#f3f4f6')
        self.setup_styles()
        
        database.init_db()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.dashboard_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.transactions_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.categories_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        
        self.notebook.add(self.dashboard_frame, text='   Dashboard   ')
        self.notebook.add(self.transactions_frame, text='   Transactions   ')
        self.notebook.add(self.categories_frame, text='   Categories & Budgets   ')
        
        self.setup_dashboard()
        self.setup_transactions()
        self.setup_categories()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def setup_styles(self):
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        # General
        style.configure('.', font=('Segoe UI', 10), background='#ffffff', foreground='#111827')
        
        # Notebook & Tabs
        style.configure('TNotebook', background='#f3f4f6', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 11, 'bold'), borderwidth=0, background='#e5e7eb')
        style.map('TNotebook.Tab', 
                  background=[('selected', '#ffffff')], 
                  foreground=[('selected', '#4f46e5')],
                  expand=[('selected', [0, 0, 0, 0])])
        
        # Frames
        style.configure('Card.TFrame', background='#ffffff')
        style.configure('Bg.TFrame', background='#f3f4f6')
        
        # Labels
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#111827')
        style.configure('SubHeader.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#374151')
        style.configure('Income.TLabel', font=('Segoe UI', 28, 'bold'), foreground='#10b981')
        style.configure('Expense.TLabel', font=('Segoe UI', 28, 'bold'), foreground='#ef4444')
        style.configure('Net.TLabel', font=('Segoe UI', 28, 'bold'), foreground='#4f46e5')
        
        # Buttons
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background='#4f46e5', foreground='white', borderwidth=0, focuscolor='#4f46e5', padding=8)
        style.map('Primary.TButton', background=[('active', '#4338ca')])
        
        style.configure('Secondary.TButton', font=('Segoe UI', 10, 'bold'), background='#e5e7eb', foreground='#374151', borderwidth=0, focuscolor='#e5e7eb', padding=8)
        style.map('Secondary.TButton', background=[('active', '#d1d5db')])
        
        style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'), background='#ef4444', foreground='white', borderwidth=0, focuscolor='#ef4444', padding=8)
        style.map('Danger.TButton', background=[('active', '#dc2626')])
        
        # Inputs
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)

    def on_tab_change(self, event):
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_categories()

    # --- DASHBOARD ---
    def setup_dashboard(self):
        # Header Area
        header_frame = ttk.Frame(self.dashboard_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="Financial Overview", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="📄 Generate Report", style='Primary.TButton', command=self.generate_report).pack(side=tk.RIGHT)
        
        # Summary Cards
        self.summary_frame = ttk.Frame(self.dashboard_frame, style='Card.TFrame')
        self.summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Income Card
        inc_card = tk.Frame(self.summary_frame, bg='#f9fafb', padx=20, pady=20, highlightbackground="#e5e7eb", highlightthickness=1)
        inc_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        ttk.Label(inc_card, text="Total Income (Month)", style='SubHeader.TLabel', background='#f9fafb').pack(anchor=tk.W)
        self.lbl_income = ttk.Label(inc_card, text="+$0.00", style='Income.TLabel', background='#f9fafb')
        self.lbl_income.pack(anchor=tk.W, pady=(5, 0))
        
        # Expense Card
        exp_card = tk.Frame(self.summary_frame, bg='#f9fafb', padx=20, pady=20, highlightbackground="#e5e7eb", highlightthickness=1)
        exp_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ttk.Label(exp_card, text="Total Expenses (Month)", style='SubHeader.TLabel', background='#f9fafb').pack(anchor=tk.W)
        self.lbl_expense = ttk.Label(exp_card, text="-$0.00", style='Expense.TLabel', background='#f9fafb')
        self.lbl_expense.pack(anchor=tk.W, pady=(5, 0))
        
        # Net Card
        net_card = tk.Frame(self.summary_frame, bg='#f9fafb', padx=20, pady=20, highlightbackground="#e5e7eb", highlightthickness=1)
        net_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        ttk.Label(net_card, text="Net Balance (Month)", style='SubHeader.TLabel', background='#f9fafb').pack(anchor=tk.W)
        self.lbl_net = ttk.Label(net_card, text="$0.00", style='Net.TLabel', background='#f9fafb')
        self.lbl_net.pack(anchor=tk.W, pady=(5, 0))
        
        # Charts Area
        self.charts_frame = ttk.Frame(self.dashboard_frame, style='Card.TFrame')
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.pie_canvas = tk.Canvas(self.charts_frame, width=400, height=350, bg='white', highlightthickness=0)
        self.pie_canvas.pack(side=tk.LEFT, padx=(0, 10), pady=10, expand=True, fill=tk.BOTH)
        
        self.bar_canvas = tk.Canvas(self.charts_frame, width=400, height=350, bg='white', highlightthickness=0)
        self.bar_canvas.pack(side=tk.RIGHT, padx=(10, 0), pady=10, expand=True, fill=tk.BOTH)

    def draw_pie_chart(self, expenses):
        self.pie_canvas.delete("all")
        self.pie_canvas.create_text(20, 20, text="Expenses by Category", font=('Segoe UI', 14, 'bold'), fill='#111827', anchor=tk.W)
        if not expenses:
            self.pie_canvas.create_text(200, 175, text="No expense data", fill='#6b7280', font=('Segoe UI', 12))
            return
            
        total = sum(expenses.values())
        colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']
        start_angle = 90
        
        # Center of canvas
        cx, cy, r = 200, 200, 120
        legend_x = 360
        legend_y = 100
        color_idx = 0
        
        for cat, amt in expenses.items():
            if amt <= 0: continue
            extent = -(amt / total) * 360
            color = colors[color_idx % len(colors)]
            self.pie_canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_angle, extent=extent, fill=color, outline='white', width=2)
            start_angle += extent
            
            # Legend
            self.pie_canvas.create_rectangle(legend_x, legend_y, legend_x+12, legend_y+12, fill=color, outline='')
            self.pie_canvas.create_text(legend_x+20, legend_y+6, text=f"{cat} ({amt/total*100:.0f}%)", anchor=tk.W, font=('Segoe UI', 10), fill='#374151')
            legend_y += 24
            color_idx += 1

    def draw_bar_chart(self, data):
        self.bar_canvas.delete("all")
        self.bar_canvas.create_text(20, 20, text="Income vs Expense (6 Months)", font=('Segoe UI', 14, 'bold'), fill='#111827', anchor=tk.W)
        
        if not data['labels']: return
        
        max_val = max(max(data['income']), max(data['expense']))
        if max_val == 0: max_val = 1
        
        c_width, c_height = 450, 350
        margin_x, margin_y = 60, 40
        plot_w = c_width - 2 * margin_x
        plot_h = c_height - margin_y - 80 # Leave room for header
        
        # Draw background grid lines
        for i in range(5):
            y = (c_height - margin_y) - (i * (plot_h / 4))
            self.bar_canvas.create_line(margin_x, y, c_width - margin_x + 20, y, fill='#e5e7eb')
            val = (i / 4) * max_val
            self.bar_canvas.create_text(margin_x - 10, y, text=f"${val:,.0f}", anchor=tk.E, font=('Segoe UI', 9), fill='#6b7280')
            
        bar_w = plot_w / (len(data['labels']) * 2.5)
        gap = bar_w / 2
        
        for i in range(len(data['labels'])):
            x_base = margin_x + i * (bar_w * 2 + gap * 2) + gap
            
            # Income bar
            inc_h = (data['income'][i] / max_val) * plot_h
            self.bar_canvas.create_rectangle(x_base, c_height - margin_y - inc_h, x_base + bar_w, c_height - margin_y, fill='#10b981', outline='')
            
            # Expense bar
            exp_h = (data['expense'][i] / max_val) * plot_h
            self.bar_canvas.create_rectangle(x_base + bar_w, c_height - margin_y - exp_h, x_base + 2*bar_w, c_height - margin_y, fill='#ef4444', outline='')
            
            # Label
            self.bar_canvas.create_text(x_base + bar_w, c_height - margin_y + 15, text=data['labels'][i], font=('Segoe UI', 9), fill='#374151')

        # Legend
        self.bar_canvas.create_rectangle(c_width/2 - 60, 30, c_width/2 - 48, 42, fill='#10b981', outline='')
        self.bar_canvas.create_text(c_width/2 - 40, 36, text="Income", anchor=tk.W, font=('Segoe UI', 9), fill='#374151')
        self.bar_canvas.create_rectangle(c_width/2 + 20, 30, c_width/2 + 32, 42, fill='#ef4444', outline='')
        self.bar_canvas.create_text(c_width/2 + 40, 36, text="Expense", anchor=tk.W, font=('Segoe UI', 9), fill='#374151')

    def refresh_dashboard(self):
        today = datetime.today()
        month_txs = database.get_monthly_transactions(today.year, today.month)
        
        income = sum(t['amount'] for t in month_txs if t['type'] == 'income')
        expense = sum(t['amount'] for t in month_txs if t['type'] == 'expense')
        net = income - expense
        
        self.lbl_income.config(text=f"+${income:,.2f}")
        self.lbl_expense.config(text=f"-${expense:,.2f}")
        self.lbl_net.config(text=f"${net:,.2f}", foreground='#4f46e5' if net >= 0 else '#ef4444')
        
        # Pie Chart
        cats = {c['id']: c['name'] for c in database.get_all_categories()}
        expenses_by_cat = {}
        for t in month_txs:
            if t['type'] == 'expense':
                cname = cats.get(t['category_id'], 'Unknown')
                expenses_by_cat[cname] = expenses_by_cat.get(cname, 0) + t['amount']
        self.draw_pie_chart(expenses_by_cat)
        
        # Bar Chart
        six_months_data = {'labels': [], 'income': [], 'expense': []}
        for i in range(5, -1, -1):
            target = today.replace(day=1) - timedelta(days=30*i)
            target = target.replace(day=1)
            six_months_data['labels'].append(target.strftime('%b'))
            txs = database.get_monthly_transactions(target.year, target.month)
            six_months_data['income'].append(sum(t['amount'] for t in txs if t['type'] == 'income'))
            six_months_data['expense'].append(sum(t['amount'] for t in txs if t['type'] == 'expense'))
            
        self.draw_bar_chart(six_months_data)

    def generate_report(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML Files', '*.html')], initialfile=f"Finance_Report_{datetime.now().strftime('%Y-%m-%d')}.html")
        if not filepath: return
        
        txs = database.get_all_transactions()
        
        # Calculate totals
        total_in = sum(t['amount'] for t in txs if t['type'] == 'income')
        total_out = sum(t['amount'] for t in txs if t['type'] == 'expense')
        net = total_in - total_out
        
        # Build HTML Report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Personal Finance Report</title>
            <style>
                body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: #f3f4f6; color: #111827; padding: 40px; margin: 0; }}
                .container {{ background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); max-width: 900px; margin: auto; }}
                .header {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; text-align: center; }}
                h1 {{ color: #4f46e5; margin: 0 0 10px 0; font-size: 32px; }}
                .date {{ color: #6b7280; font-size: 14px; margin: 0; }}
                .summary {{ display: flex; justify-content: space-between; margin-bottom: 40px; gap: 20px; }}
                .card {{ background: #f9fafb; padding: 25px; border-radius: 8px; flex: 1; text-align: center; border: 1px solid #e5e7eb; }}
                .card h3 {{ margin: 0 0 10px 0; color: #374151; font-size: 16px; text-transform: uppercase; letter-spacing: 0.05em; }}
                .income {{ color: #10b981; font-size: 32px; font-weight: bold; margin: 0; }}
                .expense {{ color: #ef4444; font-size: 32px; font-weight: bold; margin: 0; }}
                .net {{ color: #4f46e5; font-size: 32px; font-weight: bold; margin: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
                th, td {{ padding: 15px 20px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                th {{ background-color: #f9fafb; color: #374151; font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em; }}
                tr:hover {{ background-color: #f3f4f6; }}
                .type-income {{ color: #10b981; font-weight: 500; }}
                .type-expense {{ color: #ef4444; font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Personal Finance Report</h1>
                    <p class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="summary">
                    <div class="card">
                        <h3>Total Income</h3>
                        <p class="income">+${total_in:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>Total Expenses</h3>
                        <p class="expense">-${total_out:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>Net Balance</h3>
                        <p class="net" style="color: {'#4f46e5' if net >= 0 else '#ef4444'}">${net:,.2f}</p>
                    </div>
                </div>
                
                <h2 style="color: #111827; font-size: 20px; margin-bottom: 15px;">Transaction History</h2>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Category</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Note</th>
                    </tr>
                    {"".join(f"<tr><td>{t['date']}</td><td>{t['category']}</td><td class='type-{t['type']}'>{t['type'].capitalize()}</td><td style='font-weight: 600;'>${t['amount']:,.2f}</td><td style='color: #6b7280;'>{t['note']}</td></tr>" for t in txs)}
                </table>
            </div>
        </body>
        </html>
        """
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            messagebox.showinfo("Success", "Report generated successfully! Opening in browser...")
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate report: {e}")

    # --- TRANSACTIONS ---
    def setup_transactions(self):
        ttk.Label(self.transactions_frame, text="Manage Transactions", style='Header.TLabel').pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # Form
        form_frame = tk.Frame(self.transactions_frame, bg='#f9fafb', padx=20, pady=20, highlightbackground="#e5e7eb", highlightthickness=1)
        form_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(form_frame, text="Amount:", background='#f9fafb').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ent_amount = ttk.Entry(form_frame, width=15)
        self.ent_amount.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date:", background='#f9fafb').grid(row=0, column=2, padx=15, pady=5, sticky=tk.W)
        self.ent_date = ttk.Entry(form_frame, width=15)
        self.ent_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.ent_date.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type:", background='#f9fafb').grid(row=0, column=4, padx=15, pady=5, sticky=tk.W)
        self.cb_tx_type = ttk.Combobox(form_frame, values=['expense', 'income'], state='readonly', width=12)
        self.cb_tx_type.set('expense')
        self.cb_tx_type.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Category:", background='#f9fafb').grid(row=1, column=0, padx=5, pady=15, sticky=tk.W)
        self.cb_tx_cat = ttk.Combobox(form_frame, state='readonly', width=13)
        self.cb_tx_cat.grid(row=1, column=1, padx=5, pady=15)
        
        ttk.Label(form_frame, text="Note:", background='#f9fafb').grid(row=1, column=2, padx=15, pady=15, sticky=tk.W)
        self.ent_note = ttk.Entry(form_frame, width=35)
        self.ent_note.grid(row=1, column=3, columnspan=3, padx=5, pady=15, sticky=tk.W)
        
        btn_frame = tk.Frame(form_frame, bg='#f9fafb')
        btn_frame.grid(row=2, column=0, columnspan=6, pady=(10, 0), sticky=tk.E)
        ttk.Button(btn_frame, text="Clear", style='Secondary.TButton', command=self.clear_tx_form).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="+ Add Transaction", style='Primary.TButton', command=self.save_transaction).pack(side=tk.LEFT)
        
        # Table
        table_frame = ttk.Frame(self.transactions_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 5))
        
        self.tree_tx = ttk.Treeview(table_frame, columns=('ID', 'Date', 'Type', 'Category', 'Amount', 'Note'), show='headings')
        self.tree_tx.heading('ID', text='ID')
        self.tree_tx.column('ID', width=50, anchor=tk.CENTER)
        self.tree_tx.heading('Date', text='Date')
        self.tree_tx.column('Date', width=100)
        self.tree_tx.heading('Type', text='Type')
        self.tree_tx.column('Type', width=80)
        self.tree_tx.heading('Category', text='Category')
        self.tree_tx.column('Category', width=120)
        self.tree_tx.heading('Amount', text='Amount')
        self.tree_tx.column('Amount', width=100, anchor=tk.E)
        self.tree_tx.heading('Note', text='Note')
        self.tree_tx.column('Note', width=250)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_tx.yview)
        self.tree_tx.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_tx.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        action_frame = ttk.Frame(self.transactions_frame, style='Card.TFrame')
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        ttk.Button(action_frame, text="🗑 Delete Selected", style='Danger.TButton', command=self.delete_transaction).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="💾 Export to CSV", style='Secondary.TButton', command=self.export_csv).pack(side=tk.RIGHT)

    def refresh_transactions(self):
        cats = database.get_all_categories()
        self.cat_dict = {c['name']: c['id'] for c in cats}
        self.cb_tx_cat['values'] = list(self.cat_dict.keys())
        if self.cb_tx_cat['values']:
            self.cb_tx_cat.set(self.cb_tx_cat['values'][0])
            
        for item in self.tree_tx.get_children():
            self.tree_tx.delete(item)
            
        for tx in database.get_all_transactions():
            self.tree_tx.insert('', tk.END, values=(tx['id'], tx['date'], tx['type'].capitalize(), tx['category'], f"${tx['amount']:,.2f}", tx['note']))

    def clear_tx_form(self):
        self.ent_amount.delete(0, tk.END)
        self.ent_date.delete(0, tk.END)
        self.ent_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.ent_note.delete(0, tk.END)
        self.cb_tx_type.set('expense')

    def save_transaction(self):
        amount_str = self.ent_amount.get()
        try:
            amount = float(amount_str)
            if amount < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return
            
        date = self.ent_date.get()
        if not date:
            messagebox.showerror("Error", "Date is required.")
            return
            
        cat_name = self.cb_tx_cat.get()
        if not cat_name:
            messagebox.showerror("Error", "Category is required.")
            return
            
        database.add_transaction(amount, date, self.cb_tx_type.get(), self.cat_dict[cat_name], self.ent_note.get())
        messagebox.showinfo("Success", "Transaction added successfully!")
        self.clear_tx_form()
        self.refresh_transactions()
        self.check_budget_alerts()

    def delete_transaction(self):
        selected = self.tree_tx.selection()
        if not selected: 
            messagebox.showwarning("Warning", "Please select a transaction to delete.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected transaction?"):
            tx_id = self.tree_tx.item(selected[0])['values'][0]
            database.delete_transaction(tx_id)
            self.refresh_transactions()

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files', '*.csv')], initialfile=f"Transactions_{datetime.now().strftime('%Y-%m-%d')}.csv")
        if not filepath: return
        try:
            txs = database.get_all_transactions()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Date', 'Category', 'Type', 'Amount', 'Note'])
                for t in txs:
                    writer.writerow([t['id'], t['date'], t['category'], t['type'], t['amount'], t['note']])
            messagebox.showinfo("Success", "Data exported to CSV successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    # --- CATEGORIES & BUDGETS ---
    def setup_categories(self):
        ttk.Label(self.categories_frame, text="Manage Categories & Budgets", style='Header.TLabel').pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # Form
        form_frame = tk.Frame(self.categories_frame, bg='#f9fafb', padx=20, pady=20, highlightbackground="#e5e7eb", highlightthickness=1)
        form_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(form_frame, text="Name:", background='#f9fafb').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ent_cat_name = ttk.Entry(form_frame, width=20)
        self.ent_cat_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type:", background='#f9fafb').grid(row=0, column=2, padx=15, pady=5, sticky=tk.W)
        self.cb_cat_type = ttk.Combobox(form_frame, values=['expense', 'income'], state='readonly', width=12)
        self.cb_cat_type.set('expense')
        self.cb_cat_type.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Monthly Budget Limit ($):", background='#f9fafb').grid(row=0, column=4, padx=15, pady=5, sticky=tk.W)
        self.ent_cat_budget = ttk.Entry(form_frame, width=15)
        self.ent_cat_budget.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(form_frame, text="+ Add Category", style='Primary.TButton', command=self.save_category).grid(row=0, column=6, padx=20, pady=5)
        
        # List
        self.cat_list_canvas = tk.Canvas(self.categories_frame, bg='#ffffff', highlightthickness=0)
        self.cat_scrollbar = ttk.Scrollbar(self.categories_frame, orient="vertical", command=self.cat_list_canvas.yview)
        self.cat_list_frame = tk.Frame(self.cat_list_canvas, bg='#ffffff')
        
        self.cat_list_frame.bind(
            "<Configure>",
            lambda e: self.cat_list_canvas.configure(
                scrollregion=self.cat_list_canvas.bbox("all")
            )
        )
        
        self.cat_list_canvas.create_window((0, 0), window=self.cat_list_frame, anchor="nw")
        self.cat_list_canvas.configure(yscrollcommand=self.cat_scrollbar.set)
        
        self.cat_list_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=15)
        self.cat_scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=15)

    def refresh_categories(self):
        for widget in self.cat_list_frame.winfo_children():
            widget.destroy()
            
        cats = database.get_all_categories()
        today = datetime.today()
        month_txs = database.get_monthly_transactions(today.year, today.month)
        
        for i, cat in enumerate(cats):
            frame = tk.Frame(self.cat_list_frame, bg='#f9fafb', padx=15, pady=15, highlightbackground="#e5e7eb", highlightthickness=1)
            frame.grid(row=i, column=0, sticky=tk.W+tk.E, pady=5, padx=5)
            self.cat_list_frame.columnconfigure(0, weight=1)
            
            lbl_type = '📈 Income' if cat['type'] == 'income' else '📉 Expense'
            ttk.Label(frame, text=f"{cat['name']}", font=('Segoe UI', 12, 'bold'), background='#f9fafb').pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(frame, text=lbl_type, background='#f9fafb', foreground='#6b7280').pack(side=tk.LEFT)
            
            if cat['type'] == 'expense' and cat['budget_limit']:
                spent = sum(t['amount'] for t in month_txs if t['category_id'] == cat['id'])
                limit = cat['budget_limit']
                pct = min((spent / limit) * 100, 100)
                
                status_color = '#ef4444' if pct >= 100 else ('#f59e0b' if pct >= 80 else '#10b981')
                
                info_frame = tk.Frame(frame, bg='#f9fafb')
                info_frame.pack(side=tk.LEFT, padx=40, fill=tk.X, expand=True)
                
                txt_frame = tk.Frame(info_frame, bg='#f9fafb')
                txt_frame.pack(fill=tk.X)
                ttk.Label(txt_frame, text=f"Spent: ${spent:,.2f}", background='#f9fafb', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
                ttk.Label(txt_frame, text=f"Limit: ${limit:,.2f}", background='#f9fafb', foreground='#6b7280').pack(side=tk.RIGHT)
                
                pb_style = ttk.Style()
                pb_style.configure("Horizontal.TProgressbar", background=status_color)
                
                pb = ttk.Progressbar(info_frame, length=300, value=pct, style="Horizontal.TProgressbar")
                pb.pack(fill=tk.X, pady=(5,0))
                
            if not cat['is_default']:
                ttk.Button(frame, text="🗑 Delete", style='Danger.TButton', command=lambda cid=cat['id']: self.delete_category(cid)).pack(side=tk.RIGHT, padx=10)

    def save_category(self):
        name = self.ent_cat_name.get()
        if not name: 
            messagebox.showwarning("Warning", "Category name is required.")
            return
        
        budget_str = self.ent_cat_budget.get()
        budget = None
        if budget_str:
            try:
                budget = float(budget_str)
                if budget < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid budget amount.")
                return
                
        database.add_category(name, self.cb_cat_type.get(), budget)
        self.ent_cat_name.delete(0, tk.END)
        self.ent_cat_budget.delete(0, tk.END)
        messagebox.showinfo("Success", "Category created successfully!")
        self.refresh_categories()

    def delete_category(self, cat_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this category?"):
            database.delete_category(cat_id)
            self.refresh_categories()

    def check_budget_alerts(self):
        today = datetime.today()
        month_txs = database.get_monthly_transactions(today.year, today.month)
        cats = database.get_all_categories()
        
        for cat in cats:
            if cat['type'] == 'expense' and cat['budget_limit']:
                spent = sum(t['amount'] for t in month_txs if t['category_id'] == cat['id'])
                limit = cat['budget_limit']
                
                if spent > limit:
                    messagebox.showwarning("Budget Exceeded", f"🚨 You have exceeded your budget for {cat['name']}! (${spent:,.2f} / ${limit:,.2f})")
                elif spent >= limit * 0.8:
                    messagebox.showinfo("Budget Alert", f"⚠️ You have reached {spent/limit*100:.0f}% of your budget for {cat['name']}.")

if __name__ == "__main__":
    app = FinanceTrackerApp()
    app.mainloop()
