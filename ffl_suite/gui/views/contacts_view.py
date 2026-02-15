import customtkinter as ctk
from tkinter import ttk, messagebox
from ffl_suite.database.db_manager import execute_query

class ContactsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_contacts()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=20)

        ctk.CTkLabel(header_frame, text="Contacts", font=ctk.CTkFont(size=20, weight="bold")).pack(side='left')

        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side='right')

        ctk.CTkButton(btn_frame, text="Add New Contact", command=self.open_add_dialog).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.load_contacts).pack(side='left', padx=10)

        # Treeview (Wrapped in Frame)
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Style treeview to match dark mode somewhat
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ('id', 'name', 'license', 'type', 'phone')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('license', text='FFL #')
        self.tree.heading('type', text='Type')
        self.tree.heading('phone', text='Phone')

        self.tree.column('id', width=30)
        self.tree.column('name', width=200)
        self.tree.column('license', width=150)
        self.tree.column('type', width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both')

    def load_contacts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sql = "SELECT id, name, license_number, is_ffl, phone FROM contacts"
        contacts = execute_query(sql, fetch=True)
        if contacts:
            for contact in contacts:
                c_type = "FFL" if contact[3] else "Individual"
                self.tree.insert('', 'end', values=(contact[0], contact[1], contact[2], c_type, contact[4]))

    def open_add_dialog(self):
        AddContactDialog(self)

class AddContactDialog(ctk.CTkToplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Add Contact")
        self.geometry("450x500")

        # Make modal
        self.attributes("-topmost", True)
        self.create_form()

    def create_form(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        fields = [
            ("Name:", "name_entry"),
            ("Address (Street):", "street_entry"),
            ("City:", "city_entry"),
            ("State:", "state_entry"),
            ("Zip:", "zip_entry"),
            ("License #:", "license_entry")
        ]

        self.entries = {}
        for i, (label, name) in enumerate(fields):
            ctk.CTkLabel(frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=10)
            entry = ctk.CTkEntry(frame, width=200)
            entry.grid(row=i, column=1, sticky="w", padx=10, pady=10)
            self.entries[name] = entry

        self.is_ffl_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Is FFL?", variable=self.is_ffl_var).grid(row=len(fields), column=1, sticky="w", padx=10, pady=10)

        ctk.CTkButton(frame, text="Save", command=self.save_contact).grid(row=len(fields)+1, column=1, pady=20)

    def save_contact(self):
        name = self.entries['name_entry'].get()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        sql = """
            INSERT INTO contacts (name, address_street, address_city, address_state, address_zip, license_number, is_ffl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name,
            self.entries['street_entry'].get(),
            self.entries['city_entry'].get(),
            self.entries['state_entry'].get(),
            self.entries['zip_entry'].get(),
            self.entries['license_entry'].get(),
            self.is_ffl_var.get()
        )
        try:
            execute_query(sql, params)
            self.parent_view.load_contacts()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save contact: {e}")
