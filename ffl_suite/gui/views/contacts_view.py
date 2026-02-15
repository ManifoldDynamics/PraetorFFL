import tkinter as tk
from tkinter import ttk, messagebox
from ffl_suite.database.db_manager import execute_query

class ContactsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_contacts()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(top_frame, text="Add New Contact", command=self.open_add_dialog).pack(side='left')
        ttk.Button(top_frame, text="Refresh", command=self.load_contacts).pack(side='left', padx=5)

        columns = ('id', 'name', 'license', 'type', 'phone')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('license', text='FFL #')
        self.tree.heading('type', text='Type')
        self.tree.heading('phone', text='Phone')

        self.tree.column('id', width=30)
        self.tree.column('name', width=200)
        self.tree.column('license', width=150)
        self.tree.column('type', width=80)

        self.tree.pack(expand=True, fill='both', padx=10, pady=5)

    def load_contacts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Assuming is_ffl is boolean 1/0
        sql = "SELECT id, name, license_number, is_ffl, phone FROM contacts"
        contacts = execute_query(sql, fetch=True)
        if contacts:
            for contact in contacts:
                c_type = "FFL" if contact[3] else "Individual"
                self.tree.insert('', 'end', values=(contact[0], contact[1], contact[2], c_type, contact[4]))

    def open_add_dialog(self):
        AddContactDialog(self)

class AddContactDialog(tk.Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Add Contact")
        self.geometry("400x400")

        self.create_form()

    def create_form(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="Address (Street):").grid(row=1, column=0, sticky='e', pady=5)
        self.street_entry = ttk.Entry(frame)
        self.street_entry.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="City:").grid(row=2, column=0, sticky='e', pady=5)
        self.city_entry = ttk.Entry(frame)
        self.city_entry.grid(row=2, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="State:").grid(row=3, column=0, sticky='e', pady=5)
        self.state_entry = ttk.Entry(frame)
        self.state_entry.grid(row=3, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="Zip:").grid(row=4, column=0, sticky='e', pady=5)
        self.zip_entry = ttk.Entry(frame)
        self.zip_entry.grid(row=4, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="License #:").grid(row=5, column=0, sticky='e', pady=5)
        self.license_entry = ttk.Entry(frame)
        self.license_entry.grid(row=5, column=1, sticky='w', pady=5)

        self.is_ffl_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Is FFL?", variable=self.is_ffl_var).grid(row=6, column=1, sticky='w', pady=5)

        ttk.Button(frame, text="Save", command=self.save_contact).grid(row=7, column=1, pady=20)

    def save_contact(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        sql = """
            INSERT INTO contacts (name, address_street, address_city, address_state, address_zip, license_number, is_ffl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name,
            self.street_entry.get(),
            self.city_entry.get(),
            self.state_entry.get(),
            self.zip_entry.get(),
            self.license_entry.get(),
            self.is_ffl_var.get()
        )
        try:
            execute_query(sql, params)
            self.parent_view.load_contacts()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save contact: {e}")
