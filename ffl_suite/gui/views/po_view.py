import customtkinter as ctk
from tkinter import messagebox
from ffl_suite.logic.po_manager import get_open_pos, create_po

class POView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(header, text="Purchase Orders", font=ctk.CTkFont(size=24, weight="bold")).pack(side='left')
        ctk.CTkButton(header, text="New PO", height=40, font=ctk.CTkFont(weight="bold"), command=self.new_po).pack(side='right')

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill='both', expand=True, padx=20)

    def load_data(self):
        for w in self.list_frame.winfo_children(): w.destroy()

        pos = get_open_pos()
        if pos:
            for po in pos:
                # po: id, vendor, date, status, count
                row = ctk.CTkFrame(self.list_frame)
                row.pack(fill='x', pady=5)
                ctk.CTkLabel(row, text=f"PO #{po[0]}", width=80).pack(side='left', padx=10)
                ctk.CTkLabel(row, text=po[1], width=200).pack(side='left', padx=10)
                ctk.CTkLabel(row, text=po[2], width=100).pack(side='left', padx=10)
                ctk.CTkLabel(row, text=f"{po[4]} Items", width=100).pack(side='left', padx=10)
                ctk.CTkLabel(row, text=po[3], width=100).pack(side='left', padx=10)
                ctk.CTkButton(row, text="Receive", width=80, command=lambda pid=po[0]: self.receive(pid)).pack(side='right', padx=10)

    def new_po(self):
        # MVP Dialog
        d = ctk.CTkToplevel(self)
        d.title("New PO")
        d.geometry("300x200")
        ctk.CTkLabel(d, text="Vendor ID:").pack(pady=10)
        vid = ctk.CTkEntry(d)
        vid.pack()
        def save():
            create_po(vid.get())
            self.load_data()
            d.destroy()
        ctk.CTkButton(d, text="Create Draft", command=save).pack(pady=20)

    def receive(self, po_id):
        from ffl_suite.logic.po_manager import receive_po
        receive_po(po_id)
        self.load_data()
        messagebox.showinfo("Success", "PO marked Received")
