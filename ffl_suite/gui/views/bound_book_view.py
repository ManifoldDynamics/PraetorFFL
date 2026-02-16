import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from ffl_suite.logic.inventory_manager import get_bound_book
from ffl_suite.reports.pdf_generator import generate_bound_book_pdf

class BoundBookView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=20)

        ctk.CTkLabel(header_frame, text="Acquisition & Disposition Bound Book", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')

        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side='right')

        ctk.CTkButton(btn_frame, text="Export PDF", height=40, font=ctk.CTkFont(weight="bold"), command=self.export_pdf).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Refresh", height=40, font=ctk.CTkFont(weight="bold"), command=self.load_data).pack(side='left', padx=10)

        # Treeview (Wrapped in Frame)
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Style treeview to match dark mode somewhat
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ('id', 'make', 'model', 'serial', 'type', 'caliber', 'acq_date', 'source', 'disp_date', 'dest')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        headers = ['ID', 'Make', 'Model', 'Serial', 'Type', 'Caliber', 'Acq Date', 'From', 'Disp Date', 'To']
        for col, text in zip(columns, headers):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=90)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', expand=True, fill='both')

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = get_bound_book()
        if data:
            for row in data:
                values = list(row)
                if values[7] is None: values[7] = "Unknown"
                if values[8] is None: values[8] = ""
                if values[9] is None: values[9] = ""
                self.tree.insert('', 'end', values=values)

    def export_pdf(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                generate_bound_book_pdf(filename)
                messagebox.showinfo("Success", "PDF Exported Successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {e}")
