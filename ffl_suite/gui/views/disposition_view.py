import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from ffl_suite.logic.inventory_manager import search_inventory, record_disposition
from ffl_suite.database.db_manager import execute_query
from ffl_suite.reports.pdf_generator import generate_4473_pdf
from ffl_suite.logic.settings_manager import get_ffl_info

class DispositionView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.selected_firearm_id = None
        self.contact_map = {}

    def create_widgets(self):
        # Top: Search
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(search_frame, text="Search Inventory:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.search_entry.bind('<Return>', self.perform_search)
        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side='left')

        # Middle: Treeview
        columns = ('id', 'make', 'model', 'serial', 'type', 'caliber')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill='both', padx=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_firearm)

        # Bottom: Disposition Form
        self.form_frame = ttk.LabelFrame(self, text="Disposition Details")
        self.form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(self.form_frame, text="Disposed To:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.contact_combo = ttk.Combobox(self.form_frame, width=40, state="readonly")
        self.contact_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.contact_combo['postcommand'] = self.load_contacts

        ttk.Label(self.form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.date_entry = ttk.Entry(self.form_frame, width=40)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        self.dispose_btn = ttk.Button(self.form_frame, text="Confirm Disposition", command=self.submit_disposition, state='disabled')
        self.dispose_btn.grid(row=2, column=1, pady=10, sticky='w')

        self.print_btn = ttk.Button(self.form_frame, text="Print 4473", command=self.print_4473, state='disabled')
        self.print_btn.grid(row=2, column=2, pady=10, padx=5, sticky='w')

    def perform_search(self, event=None):
        query = self.search_entry.get()
        # inventory_manager.search_inventory returns list of tuples/rows
        # Need to know index of columns in schema
        # id, make, model, serial, type, caliber...
        # Let's check schema/query again.
        # SELECT * FROM firearms ...
        # id (0), make (1), model (2), serial (3), type (4), caliber (5) ...

        results = search_inventory(query)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if results:
            for r in results:
                self.tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4], r[5]))

    def on_select_firearm(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.selected_firearm_id = item['values'][0]
            self.dispose_btn['state'] = 'normal'
            self.print_btn['state'] = 'normal'
        else:
            self.selected_firearm_id = None
            self.dispose_btn['state'] = 'disabled'
            self.print_btn['state'] = 'disabled'

    def print_4473(self):
        if not self.selected_firearm_id: return

        vals = self.tree.item(self.tree.selection()[0])['values']
        firearm_data = {'make': str(vals[1]), 'model': str(vals[2]), 'serial': str(vals[3])}

        contact_name = self.contact_combo.get()
        buyer_data = {'name': contact_name if contact_name else "Unknown Buyer"}
        ffl_data = get_ffl_info()

        contact_id = self.contact_map.get(contact_name)

        from ffl_suite.gui.views.wizard_4473 import Wizard4473
        Wizard4473(self, self.selected_firearm_id, firearm_data, contact_name, contact_id)

    def load_contacts(self):
        sql = "SELECT id, name, license_number FROM contacts"
        contacts = execute_query(sql, fetch=True)
        values = []
        self.contact_map = {}
        if contacts:
            for c in contacts:
                display = c[1]
                if c[2]:
                    display += f" ({c[2]})"
                values.append(display)
                self.contact_map[display] = c[0]
        self.contact_combo['values'] = values

    def submit_disposition(self):
        if not self.selected_firearm_id:
            return

        contact_name = self.contact_combo.get()
        if not contact_name or contact_name not in self.contact_map:
            messagebox.showerror("Error", "Please select a valid contact.")
            return

        disposal_date = self.date_entry.get()
        contact_id = self.contact_map[contact_name]

        try:
            record_disposition(self.selected_firearm_id, contact_id, disposal_date)
            messagebox.showinfo("Success", "Disposition recorded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record disposition: {e}")
            return

        # Refresh list
        self.perform_search()
        self.selected_firearm_id = None
        self.dispose_btn['state'] = 'disabled'
        self.contact_combo.set('')
