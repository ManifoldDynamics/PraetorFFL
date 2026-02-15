import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import date
from ffl_suite.logic.inventory_manager import search_inventory, record_disposition
from ffl_suite.database.db_manager import execute_query
from ffl_suite.logic.settings_manager import get_ffl_info

class DispositionView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.selected_firearm_id = None
        self.contact_map = {}

    def create_widgets(self):
        # Top: Search
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill='x', padx=20, pady=20)

        ctk.CTkLabel(search_frame, text="Search Inventory:").pack(side='left', padx=10)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=10)
        self.search_entry.bind('<Return>', self.perform_search)
        ctk.CTkButton(search_frame, text="Search", command=self.perform_search).pack(side='left', padx=10)

        # Middle: Treeview (Using standard Tkinter treeview for now wrapped in CTK Frame)
        # Note: CustomTkinter doesn't have a Treeview yet.
        import tkinter as tk
        from tkinter import ttk

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Style treeview to match dark mode somewhat
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ('id', 'make', 'model', 'serial', 'type', 'caliber')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both')
        self.tree.bind('<<TreeviewSelect>>', self.on_select_firearm)

        # Bottom: Disposition Form
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill='x', padx=20, pady=20)

        ctk.CTkLabel(form_frame, text="Disposition Details", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(form_frame, text="Disposed To:").grid(row=1, column=0, sticky='e', padx=10, pady=5)
        self.contact_combo = ctk.CTkComboBox(form_frame, width=300, values=["No Contacts"])
        self.contact_combo.grid(row=1, column=1, sticky='w', padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='e', padx=10, pady=5)
        self.date_entry = ctk.CTkEntry(form_frame, width=300)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=2, column=1, sticky='w', padx=10, pady=5)

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.dispose_btn = ctk.CTkButton(btn_frame, text="Confirm Disposition", command=self.submit_disposition, state='disabled')
        self.dispose_btn.pack(side='left', padx=10)

        self.print_btn = ctk.CTkButton(btn_frame, text="4473 Wizard", command=self.open_4473_wizard, state='disabled')
        self.print_btn.pack(side='left', padx=10)

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

        if values:
            self.contact_combo.configure(values=values)
            self.contact_combo.set(values[0])

    def perform_search(self, event=None):
        query = self.search_entry.get()
        results = search_inventory(query)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if results:
            for r in results:
                # r: id, make, model, serial, type, caliber, importer, condition, upc ...
                self.tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4], r[5]))

    def on_select_firearm(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.selected_firearm_id = item['values'][0]
            self.dispose_btn.configure(state='normal')
            self.print_btn.configure(state='normal')
        else:
            self.selected_firearm_id = None
            self.dispose_btn.configure(state='disabled')
            self.print_btn.configure(state='disabled')

    def open_4473_wizard(self):
        if not self.selected_firearm_id: return

        vals = self.tree.item(self.tree.selection()[0])['values']
        firearm_data = {'make': str(vals[1]), 'model': str(vals[2]), 'serial': str(vals[3])}

        contact_name = self.contact_combo.get()
        if not contact_name or contact_name not in self.contact_map:
             messagebox.showerror("Error", "Select a contact first.")
             return

        contact_id = self.contact_map.get(contact_name)

        from ffl_suite.gui.views.wizard_4473 import Wizard4473
        Wizard4473(self, self.selected_firearm_id, firearm_data, contact_name, contact_id)

    def submit_disposition(self):
        if not self.selected_firearm_id: return

        contact_name = self.contact_combo.get()
        if not contact_name or contact_name not in self.contact_map:
            messagebox.showerror("Error", "Please select a valid contact.")
            return

        disposal_date = self.date_entry.get()
        contact_id = self.contact_map[contact_name]

        try:
            record_disposition(self.selected_firearm_id, contact_id, disposal_date)
            messagebox.showinfo("Success", "Disposition recorded.")
            self.perform_search() # Refresh
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record disposition: {e}")
