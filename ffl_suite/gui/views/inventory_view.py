import customtkinter as ctk
from tkinter import ttk, messagebox
from ffl_suite.database.db_manager import execute_query

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(header, text="Inventory Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side='right')
        ctk.CTkButton(btn_frame, text="Refresh", height=40, font=ctk.CTkFont(weight="bold"), command=self.load_data).pack(side='left', padx=10)

        # Filters
        filter_frame = ctk.CTkFrame(self, corner_radius=10)
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))

        ctk.CTkLabel(filter_frame, text="Search:").pack(side='left', padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(filter_frame, width=300, placeholder_text="Make, Model, Serial, or UPC")
        self.search_entry.pack(side='left', padx=10)
        self.search_entry.bind("<Return>", self.load_data)

        ctk.CTkButton(filter_frame, text="Go", width=50, command=self.load_data).pack(side='left', padx=5)

        # Datagrid
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white", rowheight=25)
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ('id', 'make', 'model', 'serial', 'type', 'caliber', 'status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        self.tree.heading('id', text='ID')
        self.tree.heading('make', text='Make')
        self.tree.heading('model', text='Model')
        self.tree.heading('serial', text='Serial')
        self.tree.heading('type', text='Type')
        self.tree.heading('caliber', text='Caliber')
        self.tree.heading('status', text='Status')

        self.tree.column('id', width=50)
        self.tree.column('status', width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both')

        # Context Menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Details", command=self.edit_item)
        self.context_menu.add_command(label="Print Label", command=self.print_label)

    def load_data(self, event=None):
        for i in self.tree.get_children(): self.tree.delete(i)

        query = self.search_entry.get()
        sql = """
            SELECT id, make, model, serial_number, type, caliber
            FROM firearms
            WHERE disposition_date IS NULL
        """
        params = ()

        if query:
            sql += " AND (make LIKE ? OR model LIKE ? OR serial_number LIKE ? OR upc LIKE ?)"
            p = f"%{query}%"
            params = (p, p, p, p)

        rows = execute_query(sql, params, fetch=True)
        if rows:
            for r in rows:
                # Basic status logic (could be enhanced with NFA hold check)
                status = "Available"
                self.tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4], r[5], status))

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_item(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        fid = item['values'][0]
        EditInventoryDialog(self, fid)

    def print_label(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        vals = item['values']
        info = f"{vals[1]} {vals[2]}\nSN: {vals[3]}"
        messagebox.showinfo("Label", f"Printing:\n{info}")

import tkinter as tk
class EditInventoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, firearm_id):
        super().__init__(parent)
        self.parent = parent
        self.firearm_id = firearm_id
        self.title("Edit Inventory Item")
        self.geometry("400x500")
        self.attributes("-topmost", True)
        self.create_widgets()
        self.load()

    def create_widgets(self):
        main = ctk.CTkFrame(self)
        main.pack(fill='both', expand=True, padx=20, pady=20)

        self.entries = {}
        fields = ["Make", "Model", "Serial Number", "Type", "Caliber", "UPC"]
        db_cols = ["make", "model", "serial_number", "type", "caliber", "upc"]
        self.col_map = dict(zip(fields, db_cols))

        for f in fields:
            ctk.CTkLabel(main, text=f).pack(anchor='w')
            e = ctk.CTkEntry(main)
            e.pack(fill='x', pady=5)
            self.entries[f] = e

        ctk.CTkButton(main, text="Save Changes", command=self.save).pack(pady=20)

    def load(self):
        res = execute_query("SELECT make, model, serial_number, type, caliber, upc FROM firearms WHERE id=?", (self.firearm_id,), fetch=True)
        if res:
            row = res[0]
            # Map index to field name
            # 0:make, 1:model, 2:serial, 3:type, 4:caliber, 5:upc
            self.entries["Make"].insert(0, row[0])
            self.entries["Model"].insert(0, row[1])
            self.entries["Serial Number"].insert(0, row[2])
            self.entries["Type"].insert(0, row[3])
            self.entries["Caliber"].insert(0, row[4])
            if row[5]: self.entries["UPC"].insert(0, row[5])

    def save(self):
        sql = "UPDATE firearms SET make=?, model=?, serial_number=?, type=?, caliber=?, upc=? WHERE id=?"
        params = (
            self.entries["Make"].get(),
            self.entries["Model"].get(),
            self.entries["Serial Number"].get(),
            self.entries["Type"].get(),
            self.entries["Caliber"].get(),
            self.entries["UPC"].get(),
            self.firearm_id
        )
        execute_query(sql, params)
        self.parent.load_data()
        self.destroy()
