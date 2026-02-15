import customtkinter as ctk
from tkinter import ttk, messagebox
from ffl_suite.logic.nfa_manager import get_nfa_entities, get_responsible_persons, create_nfa_form
from ffl_suite.logic.inventory_manager import search_inventory
from ffl_suite.gui.views.nfa_dialogs import AddEntityDialog, AddRPDialog

class NFAVaultView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_entities()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(header, text="NFA Vault & E-Forms Helper", font=ctk.CTkFont(size=20, weight="bold")).pack(side='left')

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side='right')
        ctk.CTkButton(btn_frame, text="New Entity", command=lambda: AddEntityDialog(self)).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Draft Form 4", command=self.open_form4_wizard).pack(side='left', padx=10)

        # Entities Tree
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")

        cols = ('id', 'name', 'type', 'rps')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Entity Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('rps', text='Responsible Persons')
        self.tree.pack(side='left', expand=True, fill='both')

        # Context Menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Add Responsible Person", command=self.add_rp_action)

    def load_entities(self):
        for i in self.tree.get_children(): self.tree.delete(i)

        ents = get_nfa_entities()
        if ents:
            for e in ents:
                # e: id, name, type
                # Count RPs
                rps = get_responsible_persons(e[0])
                count = len(rps) if rps else 0
                self.tree.insert('', 'end', values=(e[0], e[1], e[2], count))

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def add_rp_action(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            eid = item['values'][0]
            AddRPDialog(self, eid)

    def open_form4_wizard(self):
        # MVP: Simple dialog to link Entity + Firearm + CLEO
        Form4Wizard(self)

import tkinter as tk
from ffl_suite.reports.nfa_pdf_generator import generate_form4_helper
from ffl_suite.logic.nfa_manager import get_nfa_form_details

class Form4Wizard(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Form 4 Generator")
        self.geometry("600x700")
        self.attributes("-topmost", True)
        self.create_widgets()

    def create_widgets(self):
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(main, text="Step 1: Select Transferee (Entity)", font=("Arial", 14, "bold")).pack(pady=10)
        self.entity_combo = ctk.CTkComboBox(main, values=[])
        self.entity_combo.pack(pady=5)

        # Load entities
        self.ent_map = {}
        ents = get_nfa_entities()
        if ents:
            vals = []
            for e in ents:
                vals.append(e[1])
                self.ent_map[e[1]] = e[0]
            self.entity_combo.configure(values=vals)

        ctk.CTkLabel(main, text="Step 2: Select Firearm (Inventory ID)", font=("Arial", 14, "bold")).pack(pady=10)
        self.firearm_entry = ctk.CTkEntry(main, placeholder_text="Enter ID or Serial")
        self.firearm_entry.pack(pady=5)
        # In real app, use search combo. MVP: manual ID

        ctk.CTkLabel(main, text="Step 3: CLEO Info", font=("Arial", 14, "bold")).pack(pady=10)
        self.cleo_entries = {}
        cleo_fields = [("Name", "cleo_name"), ("Title", "cleo_title"), ("Agency", "cleo_agency"),
                       ("Street", "cleo_address_street"), ("City", "cleo_address_city"), ("State", "cleo_address_state"), ("Zip", "cleo_address_zip")]
        for lbl, key in cleo_fields:
            ctk.CTkLabel(main, text=lbl).pack()
            e = ctk.CTkEntry(main)
            e.pack(pady=2)
            self.cleo_entries[key] = e

        ctk.CTkButton(main, text="Generate Helper PDF", command=self.generate).pack(pady=20)

    def generate(self):
        ename = self.entity_combo.get()
        if not ename or ename not in self.ent_map: return
        eid = self.ent_map[ename]

        fid = self.firearm_entry.get()
        if not fid.isdigit():
            messagebox.showerror("Error", "Enter numeric Firearm ID")
            return

        cleo_data = {k: v.get() for k, v in self.cleo_entries.items()}

        try:
            # Create Record
            fid_int = int(fid)
            row_id = create_nfa_form("Form 4", eid, fid_int, cleo_data)

            # Fetch full details
            full_data = get_nfa_form_details(row_id)

            # Generate PDF
            from tkinter import filedialog
            path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Form4_Helper_{row_id}.pdf")
            if path:
                generate_form4_helper(path, full_data)
                messagebox.showinfo("Success", "Helper PDF Generated!")
                self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
