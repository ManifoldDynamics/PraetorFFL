import customtkinter as ctk
from tkinter import ttk, messagebox
from ffl_suite.logic.transaction_manager import get_recent_4473s

class Forms4473View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=20)

        ctk.CTkLabel(header_frame, text="4473 Forms Archive", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')

        ctk.CTkButton(header_frame, text="Refresh", height=40, font=ctk.CTkFont(weight="bold"), command=self.load_data).pack(side='right', padx=10)

        # Treeview (Wrapped)
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ('id', 'name', 'date', 'serial', 'firearm')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Transferee')
        self.tree.heading('date', text='Date')
        self.tree.heading('serial', text='Serial')
        self.tree.heading('firearm', text='Firearm')

        self.tree.column('id', width=50)
        self.tree.column('name', width=200)
        self.tree.column('date', width=100)
        self.tree.column('serial', width=150)
        self.tree.column('firearm', width=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both')

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = get_recent_4473s()
        if data:
            for row in data:
                # id, name, date, serial, make, model
                firearm_str = f"{row[4]} {row[5]}"
                self.tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], firearm_str))
