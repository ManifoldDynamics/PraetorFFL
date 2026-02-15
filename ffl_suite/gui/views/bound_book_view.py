import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ffl_suite.logic.inventory_manager import get_bound_book
from ffl_suite.reports.pdf_generator import generate_bound_book_pdf

class BoundBookView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        columns = ('id', 'make', 'model', 'serial', 'type', 'caliber', 'acq_date', 'source', 'disp_date', 'dest')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        headers = ['ID', 'Make', 'Model', 'Serial', 'Type', 'Caliber', 'Acq Date', 'From', 'Disp Date', 'To']
        for col, text in zip(columns, headers):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=90)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both', padx=10, pady=10)

        # Bottom frame for refresh
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', pady=5)
        ttk.Button(bottom_frame, text="Refresh Log", command=self.load_data).pack(side='left', padx=5)
        ttk.Button(bottom_frame, text="Export PDF", command=self.export_pdf).pack(side='left', padx=5)

    def export_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                generate_bound_book_pdf(filename)
                messagebox.showinfo("Success", "PDF Exported Successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {e}")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = get_bound_book()
        if data:
            for row in data:
                # Row structure from inventory_manager:
                # id, make, model, serial, type, caliber, acq_date, source_name, disp_date, dest_name
                values = list(row)
                if values[7] is None: values[7] = "Unknown" # Source Name
                if values[8] is None: values[8] = "" # Disp Date
                if values[9] is None: values[9] = "" # Dest Name

                self.tree.insert('', 'end', values=values)
